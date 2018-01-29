from panda3d.bullet import *
from panda3d.core import *

from shader import GeneradorShader
from objetos import *
from sistema import *

import math

import logging
log=logging.getLogger(__name__)

#
# TERRENO
#
class Terreno:
    
    # tamaño de la parcela
    TamanoParcela=32

    # radio de expansion
    RadioExpansion=1 #4

    def __init__(self, base, bullet_world):
        # referencias:
        self.base=base
        self.bullet_world=bullet_world
        self.sistema=None
        # componentes:
        self.nodo=self.base.render.attachNewNode("terreno")
        self.nodo_parcelas=self.nodo.attachNewNode("parcelas")
        self.nodo_naturaleza=self.nodo.attachNewNode("naturaleza")
        #self.nodo.setRenderModeWireframe()
        self.parcelas={} # {idx_pos:parcela_node_path,...}
        self.naturaleza={} # {idx_pos:naturaleza_node_path,...}
        # variables externas:
        self.idx_pos_parcela_actual=None # (x,y)
        self.switch_lod_naturaleza=(6.0*Terreno.TamanoParcela, 0.0)
        # debug
        self.dibujar_normales=False # cada update

    def iniciar(self):
        log.info("iniciar")
        #
        self.sistema=obtener_instancia_sistema()
        #
        self._establecer_shader()
        #
        log.info("altitud (%s)=%.3f"%(str((0, 0)), self.sistema.obtener_altitud_suelo((0, 0))))
    
    def terminar(self):
        log.info("terminar")
        objetos.terminar()
        self.sistema=None
    
    def obtener_indice_parcela(self, pos):
        x=pos[0]/Terreno.TamanoParcela
        y=pos[1]/Terreno.TamanoParcela
        if x<0.0: x=math.floor(x)
        if y<0.0: y=math.floor(y)
        return (int(x), int(y))
    
    def obtener_pos_parcela(self, idx_pos):
        x=idx_pos[0]*Terreno.TamanoParcela
        y=idx_pos[1]*Terreno.TamanoParcela
        return (x, y)

    def obtener_info(self):
        pos_parcela_actual=None
        temp=None
        if len(self.parcelas)>0:
            parcela_actual=self.parcelas[self.idx_pos_parcela_actual]
            pos_parcela_actual=parcela_actual.getPos() 
            temp=self.sistema.obtener_temperatura_anual_media_norm(pos_parcela_actual.getXy())
        #
        info="Terreno\n"
        info+="idx_pos_parcela_actual=%s pos=%s\n"%(str(self.idx_pos_parcela_actual), str(pos_parcela_actual))
        info+="RadioExpansion=%i altitud=%.2f temp_base=%s\n"%(Terreno.RadioExpansion, self.sistema.obtener_altitud_suelo_cursor(), str(temp))
        return info

    def update(self, forzar=False):
        #
        idx_pos=self.obtener_indice_parcela(self.sistema.posicion_cursor)
        #log.debug("idx_pos=%s"%(str(idx_pos)))
        if forzar or idx_pos!=self.idx_pos_parcela_actual:
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
        # posición y nombre
        pos=self.obtener_pos_parcela(idx_pos)
        nombre="parcela_%i_%i"%(int(idx_pos[0]), int(idx_pos[1]))
        log.info("_generar_parcela idx_pos=%s pos=%s nombre=%s"%(str(idx_pos), str(pos), nombre))
        # nodo
        parcela_node_path=self.nodo_parcelas.attachNewNode(nombre)
        parcela_node_path.setPos(pos[0], pos[1], 0.0)
        # geometría
        datos_parcela=self._generar_datos_parcela(idx_pos)
        geom_node=self._generar_nodo_parcela(nombre, idx_pos, datos_parcela)
        #
        parcela_node_path.attachNewNode(geom_node)
        # debug: normales
        if self.dibujar_normales:
            geom_node_normales=self._generar_lineas_normales("normales_%i_%i"%(int(pos[0]), int(pos[1])), geom_node)
            parcela_node_path.attachNewNode(geom_node_normales)
        # agregar a parcelas
        self.parcelas[idx_pos]=parcela_node_path
        # naturaleza
        naturaleza_node_path=self._generar_nodo_naturaleza(pos, idx_pos, datos_parcela) # datos_parcela es obsoleto
        naturaleza_node_path.setPos(pos[0], pos[1], 0.0)
        naturaleza_node_path.reparentTo(self.nodo_naturaleza)
        self.naturaleza[idx_pos]=naturaleza_node_path

    def _descargar_parcela(self, idx_pos):
        log.info("_descargar_parcela %s"%str(idx_pos))
        #
        naturaleza=self.naturaleza[idx_pos]
        naturaleza.removeNode()
        del self.naturaleza[idx_pos]
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
                temperatura_base=self.sistema.obtener_temperatura_anual_media_norm(_pos)
                d.pos=Vec3(x-1, y-1, self.sistema.obtener_altitud_suelo(_pos))
                d.tipo=self.sistema.obtener_tipo_terreno_float(_pos)
                d.temperatura_base=temperatura_base
                #log.debug("_generar_datos_parcela pos=%s tipo_terreno=%s"%(str(_pos), str(d.tipo)))
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

    def _generar_nodo_parcela(self, nombre, idx_pos, data):
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
        tc_x, tc_y=0.999, 0.999 # 1.0, 1.0
        for x in range(Terreno.TamanoParcela+1):
            tc_x=0.001 if tc_x==0.999 else 0.999
            for y in range(Terreno.TamanoParcela+1):
                tc_y=0.001 if tc_y==0.999 else 0.999
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
    
    def _generar_nodo_naturaleza(self, pos, idx_pos, data):
        #
        tamano=Terreno.TamanoParcela+1
        naturaleza=Naturaleza(self.base, pos, tamano)
        naturaleza.iniciar()
        for x in range(tamano):
            for y in range(tamano):
                _d=data[x+1][y+1]
                #log.debug(str(_d))
                naturaleza.cargar_datos(_d.pos, _d.temperatura_base)
        #
        nombre="nodo_naturaleza_%i_%i"%(idx_pos[0], idx_pos[1])
        #
        nodo=naturaleza.generar("%s_objetos"%nombre)
        #
        naturaleza.terminar()
        #
        lod0=NodePath(LODNode("%s_lod"%nombre))
        lod0.node().addSwitch(*self.switch_lod_naturaleza)
        nodo.reparentTo(lod0)
        #
        return lod0

    def _establecer_shader(self):
        #
        ts_terreno=TextureStage("ts_terreno")
        textura_terreno=self.base.loader.loadTexture("texturas/terreno2.png")
        self.nodo_parcelas.setTexture(ts_terreno, textura_terreno)
        #
        GeneradorShader.aplicar(self.nodo_parcelas, GeneradorShader.ClaseTerreno, 2)
        GeneradorShader.aplicar(self.nodo_naturaleza, GeneradorShader.ClaseGenerico, 2)

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

#
# DATOS LOCALES TERRENO
#
class DatosLocalesTerreno:
    
    def __init__(self):
        #
        self.index=None # vertex array index
        self.pos=None
        self.normal=None
        self.tipo=0.0 # obsoleto?
        self.temperatura_base=0.0 # obsoleto?
    
    def __str__(self):
        return "DatosLocalesTerreno: i=%s; pos=%s; normal=%s; tipo=%.3f; temp_b=%.3f"%(str(self.index), str(self.pos), str(self.normal), self.tipo, self.temperatura_base)

#
# TESTER
#
from direct.showbase.ShowBase import ShowBase
from direct.gui.DirectGui import *
class Tester(ShowBase):

    TipoImagenNulo=0
    TipoImagenTopo=1
    TipoImagenTiposTerreno=2
    TipoImagenEspacios=3

    # obsoleto
#    ColoresTipoTerreno={Terreno.TipoNulo:Vec4(0, 0, 0, 255), 
#                        Terreno.TipoArena:Vec4(240, 230, 0, 255), 
#                        Terreno.TipoTierra1:Vec4(70, 60, 0, 255), 
#                        Terreno.TipoPasto:Vec4(0, 190, 10, 255), 
#                        Terreno.TipoTierra2:Vec4(70, 60, 0, 255), 
#                        Terreno.TipoNieve:Vec4(250, 250, 250, 255)
#                        }

    def __init__(self):
        #
        super(Tester, self).__init__()
        self.disableMouse()
        self.win.setClearColor(Vec4(0.95, 1.0, 1.0, 1.0))
        #
        bullet_world=BulletWorld()
        #
        self.cam_pitch=30.0
        self.escribir_archivo=False # cada update
        #
        self.sistema=Sistema()
        self.sistema.iniciar()
        establecer_instancia_sistema(self.sistema)
        #
        GeneradorShader.iniciar(self, Sistema.TopoAltitudOceano, Vec4(0, 0, 1, Sistema.TopoAltitudOceano))
        GeneradorShader.aplicar(self.render, GeneradorShader.ClaseGenerico, 1)
        self.render.setShaderInput("distancia_fog_maxima", 3000.0, 0, 0, 0, priority=3)
        #
        self.terreno=Terreno(self, bullet_world)
        self.terreno.iniciar()
        #self.terreno.nodo.setRenderModeWireframe()
        #
        plano=CardMaker("plano_agua")
        r=Terreno.TamanoParcela*6
        plano.setFrame(-r, r, -r, r)
        plano.setColor((0, 0, 1, 1))
        self.plano_agua=self.render.attachNewNode(plano.generate())
        self.plano_agua=self.loader.loadModel("objetos/plano_agua")
        self.plano_agua.reparentTo(self.render)
        self.plano_agua.setScale(0.5)
        #self.plano_agua.setP(-90.0)
        #self.plano_agua.hide()
        #
        self.cam_driver=self.render.attachNewNode("cam_driver")
        self.camera.reparentTo(self.cam_driver)
        self.camera.setPos(Terreno.TamanoParcela/2, 500, 100)
        self.camera.lookAt(self.cam_driver)
        self.cam_driver.setP(self.cam_pitch)
        #
        self.luz_ambiental=self.render.attachNewNode(AmbientLight("luz_ambiental"))
        self.luz_ambiental.node().setColor(Vec4(1, 1, 1, 1))
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
        self.zoom_imagen=1
        #
        self.tipo_imagen=Tester.TipoImagenTopo
        #
        self.taskMgr.add(self.update, "update")
        self.accept("wheel_up", self.zoom, [1])
        self.accept("wheel_down", self.zoom, [-1])
        #
        self._cargar_ui()
        
    def update(self, task):
        nueva_pos_foco=self.sistema.posicion_cursor
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
        if nueva_pos_foco!=self.sistema.posicion_cursor:
            log.info("update pos_foco=%s"%str(nueva_pos_foco))
            self._actualizar_terreno()
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
                a=self.terreno.sistema.obtener_altitud_suelo((pos_foco[0]+x, pos_foco[1]+y))
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
        self.terreno.update()
        if self.escribir_archivo:
            log.info("escribir_archivo")
            self.terreno.nodo.writeBamFile("terreno.bam")
        self.plano_agua.setPos(Vec3(pos[0], pos[1], Sistema.TopoAltitudOceano))
        #
        self.cam_driver.setPos(Vec3(pos[0]+Terreno.TamanoParcela/2, pos[1]-Terreno.TamanoParcela, Sistema.TopoAltitudOceano))
        #
        self.lblInfo["text"]=self.terreno.obtener_info()
        #
        self._generar_imagen()

    def _generar_imagen(self):
        log.info("_generar_imagen")
        if self.tipo_imagen==Tester.TipoImagenTopo:
            self._generar_imagen_topo()
        elif self.tipo_imagen==Tester.TipoImagenTiposTerreno:
            self._generar_imagen_tipos_terreno()
        elif self.tipo_imagen==Tester.TipoImagenEspacios:
            self._generar_imagen_espacios()

    def _generar_imagen_topo(self):
        log.info("_generar_imagen_topo")
        #
        tamano=128
        if not self.imagen:
            self.imagen=PNMImage(tamano+1, tamano+1)
            self.texturaImagen=Texture()
            self.frmImagen["image"]=self.texturaImagen
            self.frmImagen["image_scale"]=0.4
        #
        zoom=self.zoom_imagen*Terreno.TamanoParcela/tamano
        log.info("zoom: %.2f"%(zoom))
        for x in range(tamano+1):
            for y in range(tamano+1):
                _x=tamano-self.sistema.posicion_cursor[0]+x
                _y=tamano-self.sistema.posicion_cursor[1]+y
                a=self.terreno.sistema.obtener_altitud_suelo((_x, _y))
                c=int(255*a/Sistema.TopoAltura)
                if x==tamano/2 or y==tamano/2:
                    c=255
                else:
                    if a>Sistema.TopoAltitudOceano:
                        #tb=self.sistema.obtener_temperatura_anual_media_norm((_x, _y))
#                        tt=(1, 0, 0.0) # implementar sistema en shader #self.terreno.obtener_tipo_terreno_tuple((_x, _y), tb, a)
#                        c0=None
#                        c1=None
#                        if tt[2]==0.0:
#                            c=Tester.ColoresTipoTerreno[tt[0]]
#                        elif tt[2]==1.0:
#                            c=Tester.ColoresTipoTerreno[tt[1]]
#                        else:
#                            c0=Tester.ColoresTipoTerreno[tt[0]]
#                            c1=Tester.ColoresTipoTerreno[tt[1]]
#                            c=(c0*(1-tt[2]))+(c1*tt[2])
#                        #log.debug("_generar_imagen tt=%s c0=%s c1=%s c=%s"%(str(tt), str(c0), str(c1), str(c)))
                        c=Vec4(240, 230, 0, 255)
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
#                t=x/(tamano+1)
#                a=(y/(tamano+1))*Terreno.AlturaMaxima
#                tt=(1, 0, 0.0) # implementar sistema en shader #self.terreno.obtener_tipo_terreno_tuple((0, 0), t, a)
#                c0=Tester.ColoresTipoTerreno[tt[0]]
#                c1=Tester.ColoresTipoTerreno[tt[1]]
#                color=None
#                if tt[2]>0.0:
#                    color=(c0*(1.0-tt[2]))+(c1*tt[2])
#                else:
#                    color=c0
#                color=(int(color[0]), int(color[1]), int(color[2]), 255)
                color=Vec4(240, 230, 0, 255)
                self.imagen.setPixel(x, y, PNMImageHeader.PixelSpec(color[0], color[1], color[2], 255))
        #
        self.texturaImagen.load(self.imagen)

    def _generar_imagen_espacios(self):
        log.info("_generar_imagen_espacios no implementado")

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
        DirectButton(parent=self.frame, pos=(0.500, 0, 0.65), scale=0.1, text="acercar", command=self._acercar_zoom_imagen, frameSize=(-1, 1, -0.4, 0.4), text_scale=0.5)
        DirectButton(parent=self.frame, pos=(0.725, 0, 0.65), scale=0.1, text="alejar", command=self._alejar_zoom_imagen, frameSize=(-1, 1, -0.4, 0.4), text_scale=0.5)
        DirectButton(parent=self.frame, pos=(0.950, 0, 0.65), scale=0.1, text="cambiar", command=self._cambiar_tipo_imagen, frameSize=(-1, 1, -0.4, 0.4), text_scale=0.5)

    def _cambiar_tipo_imagen(self):
        log.info("_cambiar_tipo_imagen a:")
        if self.tipo_imagen==Tester.TipoImagenTopo:
            log.info("TipoImagenTiposTerreno")
            self.tipo_imagen=Tester.TipoImagenTiposTerreno
        elif self.tipo_imagen==Tester.TipoImagenTiposTerreno:
            log.info("TipoImagenEspacios")
            self.tipo_imagen=Tester.TipoImagenEspacios
        elif self.tipo_imagen==Tester.TipoImagenEspacios:
            log.info("TipoImagenTopo")
            self.tipo_imagen=Tester.TipoImagenTopo
        self._generar_imagen()

    def _click_imagen(self, *args):
        log.info("_click_imagen %s"%str(args))

    def _acercar_zoom_imagen(self):
        log.info("_acercar_zoom_imagen")
        self.zoom_imagen-=4
        if self.zoom_imagen<1:
            self.zoom_imagen=1
        self._generar_imagen()

    def _alejar_zoom_imagen(self):
        log.info("_alejar_zoom_imagen")
        self.zoom_imagen+=4
        if self.zoom_imagen>4096:
            self.zoom_imagen=4096
        self._generar_imagen()

if __name__=="__main__":
    logging.basicConfig(level=logging.DEBUG)
    PStatClient.connect()
    tester=Tester()
    tester.terreno.dibujar_normales=False
    Terreno.RadioExpansion=2
    tester.escribir_archivo=False
    tester.run()
