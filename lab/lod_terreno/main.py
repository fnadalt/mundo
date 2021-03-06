from panda3d.bullet import *
from panda3d.core import *

import math

import logging
log=logging.getLogger(__name__)

#
# TERRENO
#
class Terreno:
    
    # altura maxima
    AlturaMaxima=300

    # tamaño de la parcela
    TamanoParcela=32

    # radio de expansion
    RadioExpansion=0

    # topografia
    SemillaTopografia=4069
    NoiseObjsScales=[1024.0, 64.0, 32.0, 16.0, 8.0]
    NoiseObjsWeights=[1.0, 0.2, 0.075, 0.005, 0.001] # scale_0>scale_1>scale_n

    # biomasa:
    # temperatura; 0->1 => calor->frio
    ParamsRuidoTemperatura=[8*1024.0, 5643] # [scale, seed]
    # tipo de terreno
    ParamsRuidoIntervalo=[8.0, 1133] # [scale, seed]
    TipoNulo=0
    TipoNieve=1
    TipoTierra1=2
    TipoPasto=3
    TipoTierra2=4
    TipoArena=5

    def __init__(self, base, bullet_world):
        # referencias:
        self.base=base
        self.bullet_world=bullet_world
        # componentes:
        self.nodo=self.base.render.attachNewNode("terreno")
        #self.nodo.setRenderModeWireframe()
        self.parcelas={} # {idx_pos:parcela_node_path,...}
        self._noise_objs=list() # [PerlinNoise2, ...]
        self._ruido_temperatura=None
        self._ruido_intervalos_tipo_terreno=None
        # variables externas:
        self.pos_foco=None
        self.pos_foco_inicial=[0, 0]
        self.idx_pos_parcela_actual=None # (x,y)
        self.altitud_agua=Terreno.AlturaMaxima * 0.5
        self.altura_sobre_agua=Terreno.AlturaMaxima-self.altitud_agua
        # debug
        self.dibujar_normales=False # cada update
        # variables internas:
        self._noise_scaled_weights=list() # normalizado
        self._intervalos_tipo_terreno_escalados=[] # valores de altitud

    def iniciar(self):
        log.info("iniciar")
        #
        self._generar_noise_objs()
        #
        log.info("altitud (%s)=%.3f"%(str((0, 0)), self.obtener_altitud((0, 0))))
    
    def terminar(self):
        log.info("terminar")
        objetos.terminar()
    
    def obtener_indice_parcela(self, idx_pos):
        x=int(idx_pos[0]/Terreno.TamanoParcela)
        y=int(idx_pos[1]/Terreno.TamanoParcela)
        return (x, y)
    
    def obtener_indice_parcela_foco(self):
        return self.obtener_indice_parcela(self.pos_foco)
    
    def obtener_pos_parcela(self, idx_pos):
        x=idx_pos[0]*Terreno.TamanoParcela
        y=idx_pos[1]*Terreno.TamanoParcela
        return (x, y)

    def obtener_altitud(self, pos):
        #
        altitud=0
        # perlin noise object
        for _i_noise_obj in range(len(self._noise_objs)):
            altitud+=(self._noise_objs[_i_noise_obj].noise(pos[0], pos[1]) * self._noise_scaled_weights[_i_noise_obj])
        altitud+=1
        altitud/=2
        altitud*=Terreno.AlturaMaxima
        if altitud>self.altura_sobre_agua+0.25:
            altura_sobre_agua=altitud-self.altitud_agua
            altura_sobre_agua_n=altura_sobre_agua/self.altura_sobre_agua
            altitud=self.altitud_agua
            altitud+=0.25+altura_sobre_agua*altura_sobre_agua_n*altura_sobre_agua_n
            altitud+=75.0*altura_sobre_agua_n*altura_sobre_agua_n
            if altitud>Terreno.AlturaMaxima:
                log.warning("obtener_altitud altitud>Terreno.AlturaMaxima, recortando...")
                altitud=Terreno.AlturaMaxima
        #
        return altitud

    def obtener_temperatura_base(self, pos):
        temperatura=self._ruido_temperatura.noise(*pos)
        temperatura+=1.0
        temperatura/=2.0
        return temperatura

    def obtener_temperatura_actual(self, temperatura_base, altitud, hora_normalizada):
        # f()-> grados_c
        #
        altura_sobre_agua_n=(altitud-self.altitud_agua)/self.altura_sobre_agua
        #
        amplitud=15.0+25.0*altura_sobre_agua_n
        amplitud*=0.5+0.75*temperatura_base
        #
        factor_horario=0.5+math.sin(2.0*(hora_normalizada-0.5)*math.pi)/2.0
        #
        temperatura_base_c=-5.0+(40.0*temperatura_base)
        temperatura=temperatura_base_c-(amplitud/2.0)+(amplitud*factor_horario)
        #
        #log.debug("obtener_temperatura_actual tb=%.2f hn=%.2f tbc=%.2f asa=%.2f ampl=%.2f fh=%.2f t=%.2f"%(temperatura_base, hora_normalizada, temperatura_base_c, altura_sobre_agua_n, amplitud, factor_horario, temperatura))
        #
        return temperatura

    def obtener_tipo_terreno_tuple(self, pos, temperatura_base, altitud, debug=False):
        # f()->(tipo1,tipo2,factor_mix); factor_mix: [0,1)
        if debug: # ineficiente
            info="obtener_tipo_terreno_tuple tb=%.2f alt=%.2f "%(temperatura_base, altitud)
        c0=0.3 # ineficiente?
        c1=1.0-c0 # ineficiente?
        a=(altitud-self.altitud_agua)/self.altura_sobre_agua
        #
        offset_medio=2.0*temperatura_base-1.0
        tipo_t=c1+4.5*temperatura_base # 4.5==4+2*c0?
        if debug: # ineficiente
            info+="a=%.2f of_m=%.2f tipo_t=%.2f "%(a, offset_medio, tipo_t)
        tipo_t+=-0.35+1.5*a*a*offset_medio
        if debug: # ineficiente
            info+="tipo_t_=%.2f "%tipo_t
        if tipo_t<Terreno.TipoNieve: # ineficiente?
            tipo_t=Terreno.TipoNieve
        if tipo_t>Terreno.TipoArena: # ineficiente?
            tipo_t=Terreno.TipoArena
        #
        fract, tipo_0=math.modf(tipo_t)
        tipo_1=Terreno.TipoNulo
        if fract>c0:
            if fract>c1:
                tipo_0=math.floor(tipo_t)+1
                fract=0.0
            else:
                tipo_1=math.floor(tipo_t)+1
                # no perlin
                #fract-=c0
                #fract/=c1-c0
                # perlin
                fract=self._ruido_intervalos_tipo_terreno(*pos)
                fract+=1.0
                fract/=2.0
                fract+=fract*fract
                fract/=2.0
        else:
            fract=0.0
        #
        tipo=(int(tipo_0), int(tipo_1), fract)
        if debug: # ineficiente
            info+="tipo=%s"%str(tipo)
            log.debug(info)
        return tipo

    def obtener_tipo_terreno_float(self, pos, temperatura_base, altitud, debug=False):
        # f()->tipo1*10 + tipo2 + factor_mix; factor_mix: [0,1)
        tipo=self.obtener_tipo_terreno_tuple(pos, temperatura_base, altitud, debug)
        return 10.0*tipo[0]+tipo[1]+tipo[2]

    def dentro_radio(self, pos_1, pos_2, radio):
        dx=pos_2[0]-pos_1[0]
        dy=pos_2[1]-pos_1[1]
        if math.sqrt((dx**2)+(dy**2))<=radio:
            return True
        else:
            return False

    def obtener_info(self):
        pos_parcela_actual=None
        temp=None
        if len(self.parcelas)>0:
            parcela_actual=self.parcelas[self.idx_pos_parcela_actual]
            pos_parcela_actual=parcela_actual.getPos() 
            temp=self.obtener_temperatura_base(pos_parcela_actual.getXy())
        #
        info="Terreno\n"
        info+="idx_pos_parcela_actual=%s pos=%s\n"%(str(self.idx_pos_parcela_actual), str(pos_parcela_actual))
        info+="RadioExpansion=%i pos_foco=%s altitud=%.2f temp_base=%s\n"%(Terreno.RadioExpansion, str(self.pos_foco), self.obtener_altitud(self.pos_foco), str(temp))
        return info

    def update(self, pos_foco):
        if self.pos_foco!=pos_foco:
            self.pos_foco=pos_foco
        #
        idx_pos=self.obtener_indice_parcela_foco()
        if idx_pos!=self.idx_pos_parcela_actual:
            self.idx_pos_parcela_actual=idx_pos
            #
            idxs_pos_parcelas_obj=[]
            idxs_pos_parcelas_cargar=[]
            idxs_pos_parcelas_descargar=[]
            # determinar parcelas que deben estar cargadas
            for idx_pos_x in range(idx_pos[0]-Terreno.RadioExpansion, idx_pos[0]+Terreno.RadioExpansion+1):
                for idx_pos_y in range(idx_pos[1]-Terreno.RadioExpansion, idx_pos[1]+Terreno.RadioExpansion+1):
                    idxs_pos_parcelas_obj.append((idx_pos_x, idx_pos_y))
            # crear listas de parcelas a descargar y a cargar
            for idx_pos in self.parcelas.keys():
                if idx_pos not in idxs_pos_parcelas_obj:
                    idxs_pos_parcelas_descargar.append(idx_pos)
            for idx_pos in idxs_pos_parcelas_obj:
                if idx_pos not in self.parcelas:
                    idxs_pos_parcelas_cargar.append(idx_pos)
            # descarga y carga de parcelas
            for idx_pos in idxs_pos_parcelas_descargar:
                self._descargar_parcela(idx_pos)
            for idx_pos in idxs_pos_parcelas_cargar:
                self._generar_parcela(idx_pos)

    def _generar_parcela(self, idx_pos):
        log.info("_generar_parcela %s"%str(idx_pos))
        # posición y nombre
        pos=self.obtener_pos_parcela(idx_pos)
        nombre="parcela_%i_%i"%(int(pos[0]), int(pos[1]))
        # nodo
        parcela_node_path=self.nodo.attachNewNode(nombre)
        parcela_node_path.setPos(pos[0], pos[1], 0.0)
        # geometría
        datos_parcela=self._generar_datos_parcela(idx_pos)
        geom_node=self._generar_geometria_parcela(nombre, idx_pos, datos_parcela)
        #
        parcela_node_path.attachNewNode(geom_node)
        # debug: normales
        if self.dibujar_normales:
            geom_node_normales=self._generar_lineas_normales("normales_%i_%i"%(int(pos[0]), int(pos[1])), geom_node)
            parcela_node_path.attachNewNode(geom_node_normales)
        # agregar a parcelas
        self.parcelas[idx_pos]=parcela_node_path

    def _descargar_parcela(self, idx_pos):
        log.info("_descargar_parcela %s"%str(idx_pos))
        #
        parcela=self.parcelas[idx_pos]
        parcela.removeNode()
        del self.parcelas[idx_pos]
    
    def _generar_datos_parcela(self, idx_pos):
        # obtener posición
        pos=self.obtener_pos_parcela(idx_pos)
        # matriz de DatosLocalesTerreno; x,y->TamanoParcela +/- 1
        data=list() # x,y: [[n, ...], ...]
        _pos=(0, 0)
        for x in range(Terreno.TamanoParcela+3):
            data.append(list())
            for y in range(Terreno.TamanoParcela+3):
                d=DatosLocalesTerreno()
                #data.index=None # no establecer en esta instancia
                _pos=(pos[0]+x-1, pos[1]+y-1)
                temperatura_base=self.obtener_temperatura_base(_pos)
                d.pos=Vec3(x-1, y-1, self.obtener_altitud(_pos))
                d.tipo=self.obtener_tipo_terreno_float(_pos, temperatura_base, d.pos[2], False)
                d.temperatura_base=temperatura_base
                #log.debug(str(d.tipo))
                data[x].append(d)
        # calcular normales
        for x in range(Terreno.TamanoParcela+1):
            for y in range(Terreno.TamanoParcela+1):
                v0=data[x+1][y+1].pos
                v1=data[x+2][y+1].pos
                v2=data[x+1][y+2].pos
                v3=data[x+2][y].pos
                v4=data[x][y+2].pos
                v5=data[x][y+1].pos
                v6=data[x+1][y].pos
                n0=self._calcular_normal(v0, v1, v2)
                n1=self._calcular_normal(v0, v3, v1)
                n2=self._calcular_normal(v0, v2, v4)
                n3=self._calcular_normal(v0, v5, v6)
                n_avg=(n0+n1+n2+n3)/4.0
                data[x+1][y+1].normal=n_avg
        #
        return data

    def _generar_geometria_parcela(self, nombre, idx_pos, data):
        # formato
        co_info_tipo_terreno=InternalName.make("info_tipo_terreno") # int()->tipo; fract()->intervalo
        format_array=GeomVertexArrayFormat()
        format_array.addColumn(InternalName.getVertex(), 3, Geom.NT_stdfloat, Geom.C_point)
        format_array.addColumn(InternalName.getNormal(), 3, Geom.NT_stdfloat, Geom.C_normal)
        format_array.addColumn(InternalName.getTexcoord(), 2, Geom.NT_stdfloat, Geom.C_texcoord)
        format_array.addColumn(co_info_tipo_terreno, 1, Geom.NT_stdfloat, Geom.C_other)
        formato=GeomVertexFormat()
        formato.addArray(format_array)
        # iniciar vértices y primitivas
        vdata=GeomVertexData("vertex_data", GeomVertexFormat.registerFormat(formato), Geom.UHStatic)
        vdata.setNumRows((Terreno.TamanoParcela+1)*(Terreno.TamanoParcela+1)) # +1 ?
        prim=GeomTriangles(Geom.UHStatic)
        # vertex writers
        wrt_v=GeomVertexWriter(vdata, InternalName.getVertex())
        wrt_n=GeomVertexWriter(vdata, InternalName.getNormal())
        wrt_t=GeomVertexWriter(vdata, InternalName.getTexcoord())
        wrt_i=GeomVertexWriter(vdata, co_info_tipo_terreno)
        # llenar datos de vertices
        i_vertice=0
        tc_x, tc_y=1.0, 1.0
        for x in range(Terreno.TamanoParcela+1):
            tc_x=0.0 if tc_x==1.0 else 1.0
            for y in range(Terreno.TamanoParcela+1):
                tc_y=0.0 if tc_y==1.0 else 1.0
                # data
                d=data[x+1][y+1]
                d.index=i_vertice # aqui se define el indice
                # llenar vertex data
                wrt_v.addData3(d.pos)
                wrt_n.addData3(d.normal)
                wrt_t.addData2(tc_x, tc_y)
                wrt_i.addData1(d.tipo)
                i_vertice+=1
        # debug data
        #for fila in data:
        #    for _d in fila:
        #        log.debug(str(_d))
        # llenar datos de primitivas
        for x in range(Terreno.TamanoParcela):
            for y in range(Terreno.TamanoParcela):
                # vertices
                i0=data[x+1][y+1].index
                i1=data[x+2][y+1].index
                i2=data[x+1][y+2].index
                i3=data[x+2][y+2].index
                # primitivas
                prim.addVertex(i0)
                prim.addVertex(i1)
                prim.addVertex(i2)
                prim.closePrimitive()
                prim.addVertex(i2)
                prim.addVertex(i1)
                prim.addVertex(i3)
                prim.closePrimitive()
        # geom
        geom=Geom(vdata)
        geom.addPrimitive(prim)
        geom.setBoundsType(BoundingVolume.BT_box)
        # nodo
        geom_node=GeomNode(nombre)
        geom_node.addGeom(geom)
        geom_node.setBoundsType(BoundingVolume.BT_box)
        return geom_node
    
    def _generar_nodo_objetos(self, pos, idx_pos, data):
        #
        tamano=Terreno.TamanoParcela+1
        naturaleza=Naturaleza(self.base, pos, Terreno.AlturaMaxima, tamano, self.altitud_agua)
        naturaleza.iniciar()
        for x in range(tamano):
            for y in range(tamano):
                _d=data[x+1][y+1]
                #log.debug(str(_d))
                naturaleza.cargar_datos(_d.pos, _d.temperatura_base)
        nodo=naturaleza.generar("nodo_objetos_%i_%i"%(idx_pos[0], idx_pos[1]))
        return nodo

    def _calcular_normal(self, v0, v1, v2):
        U=v1-v0
        V=v2-v0
        return U.cross(V)
    
    def _generar_lineas_normales(self, nombre, geom_node_parcela):
        #
        geom=LineSegs(nombre)
        geom.setColor((0, 0, 1, 1))
        #
        geom_parcela=geom_node_parcela.getGeom(0)
        vdata=geom_parcela.getVertexData()
        v_reader=GeomVertexReader(vdata, InternalName.getVertex())
        n_reader=GeomVertexReader(vdata, InternalName.getNormal())
        #
        while(not v_reader.isAtEnd()):
            vertex=v_reader.getData3f()
            normal1=n_reader.getData3f()
            geom.moveTo(vertex)
            geom.drawTo(vertex+normal1)
        #
        return geom.create()

    def _generar_noise_objs(self):
        # topografia:
        # normalizar coeficientes
        suma_coefs=0
        for k in Terreno.NoiseObjsWeights:
            suma_coefs+=k
        for k in Terreno.NoiseObjsWeights:
            self._noise_scaled_weights.append(k/suma_coefs)
        # noise objects
        escala_general=1.0
        escalas=list()
        for scale in Terreno.NoiseObjsScales:
            escalas.append(scale*escala_general)
        # lista
        self._noise_objs.append(PerlinNoise2(escalas[0], escalas[0], 256, Terreno.SemillaTopografia))
        self._noise_objs.append(PerlinNoise2(escalas[1], escalas[1], 256, Terreno.SemillaTopografia+(128*1)))
        self._noise_objs.append(PerlinNoise2(escalas[2], escalas[2], 256, Terreno.SemillaTopografia+(128*2)))
        self._noise_objs.append(PerlinNoise2(escalas[3], escalas[3], 256, Terreno.SemillaTopografia+(128*3)))
        self._noise_objs.append(PerlinNoise2(escalas[4], escalas[4], 256, Terreno.SemillaTopografia+(128*4)))
        # biomasa:
        # temperatura
        self._ruido_temperatura=PerlinNoise2(Terreno.ParamsRuidoTemperatura[0], Terreno.ParamsRuidoTemperatura[0], 256, Terreno.ParamsRuidoTemperatura[1])
        # intervalos de tipos de terreno
        self._ruido_intervalos_tipo_terreno=PerlinNoise2(Terreno.ParamsRuidoIntervalo[0], Terreno.ParamsRuidoIntervalo[0], 256, Terreno.ParamsRuidoIntervalo[1])

#
# DATOS LOCALES TERRENO
#
class DatosLocalesTerreno:
    
    def __init__(self):
        #
        self.index=None # vertex array index
        self.pos=None
        self.normal=None
        self.tipo=0.0
        self.temperatura_base=0.0
    
    def __str__(self):
        return "DatosLocalesTerreno: i=%s; pos=%s; normal=%s; tipo=%.3f; temp_b=%.3f"%(str(self.index), str(self.pos), str(self.normal), self.tipo, self.temperatura_base)

#
# TESTER
#
from direct.showbase.ShowBase import ShowBase
from direct.gui.DirectGui import *
class Tester(ShowBase):

    ColoresTipoTerreno={Terreno.TipoNulo:Vec4(0, 0, 0, 255), 
                        Terreno.TipoArena:Vec4(240, 230, 0, 255), 
                        Terreno.TipoTierra1:Vec4(70, 60, 0, 255), 
                        Terreno.TipoPasto:Vec4(0, 190, 10, 255), 
                        Terreno.TipoTierra2:Vec4(70, 60, 0, 255), 
                        Terreno.TipoNieve:Vec4(250, 250, 250, 255)
                        }

    def __init__(self):
        #
        super(Tester, self).__init__()
        self.disableMouse()
        self.win.setClearColor(Vec4(0.95, 1.0, 1.0, 1.0))
        #
        bullet_world=BulletWorld()
        #
        self.pos_foco=None
        self.cam_pitch=90.0
        self.escribir_archivo=False # cada update
        #
        self.terreno=Terreno(self, bullet_world)
        self.terreno.iniciar()
        self.terreno.nodo.setRenderModeWireframe()
        #
        plano=CardMaker("plano_agua")
        r=Terreno.TamanoParcela*6
        plano.setFrame(-r, r, -r, r)
        plano.setColor((0, 0, 1, 1))
        self.plano_agua=self.render.attachNewNode(plano.generate())
        self.plano_agua.setP(-90.0)
        #self.plano_agua.hide()
        #
        self.cam_driver=self.render.attachNewNode("cam_driver")
        self.camera.reparentTo(self.cam_driver)
        self.camera.setPos(0, 260, 0)
        self.camera.lookAt(self.cam_driver)
        self.cam_driver.setPos(Terreno.TamanoParcela/2, Terreno.TamanoParcela/2, 0)
        self.cam_driver.setP(self.cam_pitch)
        #
        self.sun=self.render.attachNewNode(DirectionalLight("sun"))
        self.sun.node().setColor(Vec4(1, 1, 1, 1))
        self.sun.setPos(self.terreno.nodo, 100, 100, 100)
        self.sun.lookAt(self.terreno.nodo)
        #
        self.render.setLight(self.sun)
        #
        self.texturaImagen=None
        self.imagen=None
        self.zoom_imagen=16
        #
        self.taskMgr.add(self.update, "update")
        self.accept("wheel_up", self.zoom, [1])
        self.accept("wheel_down", self.zoom, [-1])
        #
        #self._cargar_ui()
        
    def update(self, task):
        nueva_pos_foco=self.pos_foco[:] if self.pos_foco else self.terreno.pos_foco_inicial
        #
        mwn=self.mouseWatcherNode
        if mwn.isButtonDown(KeyboardButton.up()):
            nueva_pos_foco[1]-=32
        elif mwn.isButtonDown(KeyboardButton.down()):
            nueva_pos_foco[1]+=32
        elif mwn.isButtonDown(KeyboardButton.left()):
            nueva_pos_foco[0]+=32
        elif mwn.isButtonDown(KeyboardButton.right()):
            nueva_pos_foco[0]-=32
        #
        if nueva_pos_foco!=self.pos_foco:
            log.info("update pos_foco=%s"%str(nueva_pos_foco))
            self.pos_foco=nueva_pos_foco
            self._actualizar_terreno(self.pos_foco)
        return task.cont
    
    def zoom(self, dir):
        dy=25*dir
        self.camera.setY(self.camera, dy)

    def analizar_altitudes(self, pos_foco, tamano=1024):
        log.info("analizar_altitudes en %ix%i"%(tamano, tamano))
        i=0
        media=0
        vals=list()
        min=999999
        max=-999999
        for x in range(tamano):
            for y in range(tamano):
                a=self.terreno.obtener_altitud((pos_foco[0]+x, pos_foco[1]+y))
                vals.append(a)
                if a>max:
                    max=a
                if a<min:
                    min=a
                media=((media*i)+a)/(i+1)
                i+=1
        sd=0
        for val in vals:  sd+=((val-media)*(val-media))
        sd/=(tamano*tamano)
        sd=math.sqrt(sd)
        log.info("analizar_altitudes rango:[%.3f/%.3f] media=%.3f sd=%.3f"%(min, max, media, sd))

    def _actualizar_terreno(self, pos):
            log.info("_actualizar_terreno pos=%s"%(str(pos)))
            #
            self.terreno.update(pos)
            if self.escribir_archivo:
                log.info("escribir_archivo")
                self.terreno.nodo.writeBamFile("terreno.bam")
            self.plano_agua.setPos(Vec3(pos[0], pos[1], self.terreno.altitud_agua))
            #
            #self.cam_driver.setPos(Vec3(pos[0], pos[1], 100))
            #
            #self.lblInfo["text"]=self.terreno.obtener_info()
            #
            self.pos_foco=pos
            #
            #self._generar_imagen()
            #self._generar_imagen_tipos_terreno()

    def _generar_imagen(self):
        #
        tamano=128
        if not self.imagen:
            self.imagen=PNMImage(tamano+1, tamano+1)
            self.texturaImagen=Texture()
            self.frmImagen["image"]=self.texturaImagen
            self.frmImagen["image_scale"]=0.4
        #
        for x in range(tamano+1):
            for y in range(tamano+1):
                _x=self.pos_foco[0]-(x-(tamano/2))*self.zoom_imagen
                _y=self.pos_foco[1]+(y-(tamano/2))*self.zoom_imagen
                a=self.terreno.obtener_altitud((_x, _y))
                c=int(255*a/Terreno.AlturaMaxima)
                if a>self.terreno.altitud_agua:
                    tb=self.terreno.obtener_temperatura_base((_x, _y))
                    tt=self.terreno.obtener_tipo_terreno_tuple((_x, _y), tb, a)
                    c0=None
                    c1=None
                    if tt[2]==0.0:
                        c=Tester.ColoresTipoTerreno[tt[0]]
                    elif tt[2]==1.0:
                        c=Tester.ColoresTipoTerreno[tt[1]]
                    else:
                        c0=Tester.ColoresTipoTerreno[tt[0]]
                        c1=Tester.ColoresTipoTerreno[tt[1]]
                        c=(c0*(1-tt[2]))+(c1*tt[2])
                    #log.debug("_generar_imagen tt=%s c0=%s c1=%s c=%s"%(str(tt), str(c0), str(c1), str(c)))
                    self.imagen.setPixel(x, y, PNMImageHeader.PixelSpec(int(c[0]), int(c[1]), int(c[2]), 255))
                else:
                    self.imagen.setPixel(x, y, PNMImageHeader.PixelSpec(0, 0, c, 255))
        #
        self.texturaImagen.load(self.imagen)

    def _generar_imagen_tipos_terreno(self):
        #
        tamano=128
        if not self.imagen:
            self.imagen=PNMImage(tamano+1, tamano+1)
            self.texturaImagen=Texture()
            self.frmImagen["image"]=self.texturaImagen
            self.frmImagen["image_scale"]=0.4
        #
        for x in range(tamano+1):
            for y in range(tamano+1):
                t=x/(tamano+1)
                a=(y/(tamano+1))*Terreno.AlturaMaxima
                tt=self.terreno.obtener_tipo_terreno_tuple((0, 0), t, a)
                c0=Tester.ColoresTipoTerreno[tt[0]]
                c1=Tester.ColoresTipoTerreno[tt[1]]
                color=None
                if tt[2]>0.0:
                    color=(c0*(1.0-tt[2]))+(c1*tt[2])
                else:
                    color=c0
                color=(int(color[0]), int(color[1]), int(color[2]), 255)
                self.imagen.setPixel(x, y, PNMImageHeader.PixelSpec(color[0], color[1], color[2], 255))
        #
        self.texturaImagen.load(self.imagen)

    def _ir_a_idx_pos(self):
        log.info("_ir_a_idx_pos")
        try:
            idx_x=int(self.entry_x.get())
            idx_y=int(self.entry_y.get())
            pos=self.terreno.obtener_pos_parcela((idx_x, idx_y))
            log.info("idx_pos:(%i,%i); pos:%s"%(idx_x, idx_y, str(pos)))
            self._actualizar_terreno(list(pos))
        except Exception as e:
            log.exception(str(e))

    def _cargar_ui(self):
        # frame
        self.frame=DirectFrame(parent=self.aspect2d, pos=(0, 0, -0.85), frameSize=(-1, 1, -0.15, 0.25), frameColor=(1, 1, 1, 0.5))
        # info
        self.lblInfo=DirectLabel(parent=self.frame, pos=(-1, 0, 0.15), scale=0.05, text="info terreno?", frameColor=(1, 1, 1, 0.2), frameSize=(0, 40, -2, 2), text_align=TextNode.ALeft, text_pos=(0, 1, 1))
        # idx_pos
        DirectLabel(parent=self.frame, pos=(-1, 0, 0), scale=0.05, text="idx_pos_x", frameColor=(1, 1, 1, 0), frameSize=(0, 2, -1, 1), text_align=TextNode.ALeft)
        DirectLabel(parent=self.frame, pos=(-1, 0, -0.1), scale=0.05, text="idx_pos_y", frameColor=(1, 1, 1, 0), frameSize=(0, 2, -1, 1), text_align=TextNode.ALeft)
        self.entry_x=DirectEntry(parent=self.frame, pos=(-0.7, 0, 0), scale=0.05)
        self.entry_y=DirectEntry(parent=self.frame, pos=(-0.7, 0, -0.1), scale=0.05)
        DirectButton(parent=self.frame, pos=(0, 0, -0.1), scale=0.075, text="actualizar", command=self._ir_a_idx_pos)
        #
        self.frmImagen=DirectFrame(parent=self.frame, pos=(0.8, 0, 0.2), state=DGG.NORMAL, frameSize=(-0.4, 0.4, -0.4, 0.4))
        self.frmImagen.bind(DGG.B1PRESS, self._click_imagen)
        DirectButton(parent=self.frame, pos=(0.5, 0, 0.65), scale=0.1, text="acercar", command=self._acercar_zoom_imagen, frameSize=(-1, 1, -0.4, 0.4), text_scale=0.5)
        DirectButton(parent=self.frame, pos=(0.725, 0, 0.65), scale=0.1, text="alejar", command=self._alejar_zoom_imagen, frameSize=(-1, 1, -0.4, 0.4), text_scale=0.5)

    def _click_imagen(self, *args):
        log.info("_click_imagen %s"%str(args))

    def _acercar_zoom_imagen(self):
        log.info("_acercar_zoom_imagen")
        if self.zoom_imagen>1:
            self.zoom_imagen/=2
            #self._generar_imagen()

    def _alejar_zoom_imagen(self):
        log.info("_alejar_zoom_imagen")
        if self.zoom_imagen<512:
            self.zoom_imagen*=2
            #self._generar_imagen()

def debug_tipos_terreno(terreno):
    log.debug("debug_tipos_terreno")
    tamano=10
    for t in range(tamano):
        for a in range(tamano):
            terreno.obtener_tipo_terreno_tuple((0, 0), t/tamano, a*Terreno.AlturaMaxima/tamano, True)

def debug_temperaturas(terreno):
    log.debug("debug_temperaturas")
    log.debug("frio:")
    terreno.obtener_temperatura_actual(0.0, 150, 0.25)
    terreno.obtener_temperatura_actual(0.0, 150, 0.75)
    terreno.obtener_temperatura_actual(0.0, 300, 0.25)
    terreno.obtener_temperatura_actual(0.0, 300, 0.75)
    log.debug("templado:")
    terreno.obtener_temperatura_actual(0.5, 150, 0.25)
    terreno.obtener_temperatura_actual(0.5, 150, 0.75)
    terreno.obtener_temperatura_actual(0.5, 300, 0.25)
    terreno.obtener_temperatura_actual(0.5, 300, 0.75)
    log.debug("caluroso:")
    terreno.obtener_temperatura_actual(1.0, 150, 0.25)
    terreno.obtener_temperatura_actual(1.0, 150, 0.75)
    terreno.obtener_temperatura_actual(1.0, 300, 0.25)
    terreno.obtener_temperatura_actual(1.0, 300, 0.75)

if __name__=="__main__":
    logging.basicConfig(level=logging.DEBUG)
    PStatClient.connect()
    tester=Tester()
    tester.terreno.dibujar_normales=False
    Terreno.RadioExpansion=0
    tester.escribir_archivo=False
    #debug_tipos_terreno(tester.terreno)
    #debug_temperaturas(tester.terreno)
    tester.run()
