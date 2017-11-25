from panda3d.bullet import *
from panda3d.core import *

import math

import logging
log=logging.getLogger(__name__)

class Terreno2:
    
    # altura maxima
    AlturaMaxima=300

    # tamaño de la parcela
    TamanoParcela=32

    # radio de expansion
    RadioExpansion=3
    DistanciaRadioExpansion=RadioExpansion*TamanoParcela

    # topografia
    Semilla=4069
    NoiseObjsScales=[1024.0, 128.0, 32.0, 16.0, 8.0]
    NoiseObjsWeights=[1.0, 0.55, 0.1, 0.005, 0.001] # scale_0>scale_1>scale_n

    # biomasa
    RuidoTemperatura=[512.0, 1100] # [scale, seed]

    def __init__(self, base, bullet_world):
        # referencias:
        self.base=base
        self.bullet_world=bullet_world
        # componentes:
        self.nodo=self.base.render.attachNewNode("terreno2")
        self.parcelas={} # {idx_pos:parcela_node_path,...}
        self._noise_objs=list() # [PerlinNoise2, ...]
        self._ruido_temperatura=None
        # variables externas:
        self.pos_foco=None
        self.pos_foco_inicial=[0, 0]
        self.idx_pos_parcela_actual=None # (x,y)
        self.nivel_agua=Terreno2.AlturaMaxima * 0.6
        # debug
        self.dibujar_normales=False # cada update
        # variables internas:
        self._noise_scaled_weights=list() # normalizado
        # init:
        self._generar_noise_objs()
        #
        log.info("altitud (%s)=%.3f"%(str((0, 0)), self.obtener_altitud((0, 0))))

    def obtener_indice_parcela(self, idx_pos):
        x=int(idx_pos[0]/Terreno2.TamanoParcela)
        y=int(idx_pos[1]/Terreno2.TamanoParcela)
        return (x, y)
    
    def obtener_indice_parcela_foco(self):
        return self.obtener_indice_parcela(self.pos_foco)
    
    def obtener_pos_parcela(self, idx_pos):
        x=idx_pos[0]*Terreno2.TamanoParcela
        y=idx_pos[1]*Terreno2.TamanoParcela
        return (x, y)

    def obtener_altitud(self, pos):
        #
        altitud=0
        # perlin noise object
        for _i_noise_obj in range(len(self._noise_objs)):
            altitud+=(self._noise_objs[_i_noise_obj].noise(pos[0], pos[1]) * self._noise_scaled_weights[_i_noise_obj])
        altitud+=1
        altitud/=2
        altitud*=Terreno2.AlturaMaxima
        #
        return altitud

    def obtener_temperatura_base(self, pos):
        t=self._ruido_temperatura.noise(pos)
        t+=1
        t/=2
        return t

    def dentro_radio(self, pos_1, pos_2, radio):
        dx=pos_2[0]-pos_1[0]
        dy=pos_2[1]-pos_1[1]
        if math.sqrt((dx**2)+(dy**2))<=radio:
            return True
        else:
            return False

    def obtener_info(self):
        pos_parcela_actual=None
        if len(self.parcelas)>0:
            parcela_actual=self.parcelas[self.idx_pos_parcela_actual]
            pos_parcela_actual=parcela_actual.getPos() 
        #
        info="Terreno2\n"
        info+="idx_pos_parcela_actual=%s pos=%s\n"%(str(self.idx_pos_parcela_actual), str(pos_parcela_actual))
        info+="RadioExpansion=%i\n"%(Terreno2.RadioExpansion)
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
            for idx_pos_x in range(idx_pos[0]-Terreno2.RadioExpansion, idx_pos[0]+Terreno2.RadioExpansion+1):
                for idx_pos_y in range(idx_pos[1]-Terreno2.RadioExpansion, idx_pos[1]+Terreno2.RadioExpansion+1):
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
                self._cargar_parcela(idx_pos)

    def _cargar_parcela(self, idx_pos):
        log.info("_cargar_parcela %s"%str(idx_pos))
        # posición y nombre
        pos=Vec2(idx_pos[0]*Terreno2.TamanoParcela, idx_pos[1]*Terreno2.TamanoParcela)
        nombre="parcela_%i_%i"%(int(pos[0]), int(pos[1]))
        # nodo
        parcela=self.nodo.attachNewNode(nombre)
        parcela.setPos(pos[0], pos[1], 0.0)
        # geometría
        geom_node=self._crear_geometria_parcela_opt(nombre, idx_pos)
        #
        parcela.attachNewNode(geom_node)
        # debug: normales
        if self.dibujar_normales:
            geom_node_normales=self._crear_lineas_normales("normales_%i_%i"%(int(pos[0]), int(pos[1])), geom_node)
            parcela.attachNewNode(geom_node_normales)
        # textura
        ts0=TextureStage("ts0")
        textura0=self.base.loader.loadTexture("texturas/arena.png")
        parcela.setTexture(ts0, textura0)
        # agregar a parcelas
        self.parcelas[idx_pos]=parcela

    def _descargar_parcela(self, idx_pos):
        log.info("_descargar_parcela %s"%str(idx_pos))
        #
        parcela=self.parcelas[idx_pos]
        parcela.removeNode()
        del self.parcelas[idx_pos]
    
    def _crear_geometria_parcela_opt(self, nombre, idx_pos):
        # posicion de la parcela
        pos=self.obtener_pos_parcela(idx_pos)
        # matrix de altitudes; x,y: [i(-1)<i(0)<i(...)<i(tamano-1)<i(tamano)]
        altitud=list() # [[n, ...], ...]
        for x in range(Terreno2.TamanoParcela+3):
            altitud.append(list())
            for y in range(Terreno2.TamanoParcela+3):
                data=altitud[x]
                data.append(self.obtener_altitud((pos[0]+x-1, pos[1]+y-1)))
        # normales # [[n, ...], ...]
        normales=list()
        for x in range(Terreno2.TamanoParcela+1):
            normales.append(list())
            for y in range(Terreno2.TamanoParcela+1):
                v0=Vec3(x, y, altitud[x+1][y+1])
                v1=Vec3(x+1, y, altitud[x+2][y+1])
                v2=Vec3(x, y+1, altitud[x+1][y+2])
                v3=Vec3(x+1, y-1, altitud[x+2][y])
                v4=Vec3(x-1, y+1, altitud[x][y+2])
                v5=Vec3(x-1, y, altitud[x][y+1])
                v6=Vec3(x, y-1, altitud[x+1][y])
                n0=self._calcular_normal(v0, v1, v2)
                n1=self._calcular_normal(v0, v3, v1)
                n2=self._calcular_normal(v0, v2, v4)
                n3=self._calcular_normal(v0, v5, v6)
                n_avg=(n0+n1+n2+n3)/4.0
                #log.info("n0=%s n1=%s n2=%s n3=%s n_avg=%s"%(str(n0), str(n1), str(n2), str(n3), str(n_avg)))
                normales[x].append(n_avg)
        # formato
        formato=GeomVertexFormat.getV3n3t2()
        # iniciar vértices y primitivas
        vdata=GeomVertexData("vertex_data", formato, Geom.UHStatic)
        vdata.setNumRows((Terreno2.TamanoParcela+1)*(Terreno2.TamanoParcela+1))
        prim=GeomTriangles(Geom.UHStatic)
        # vertex writers
        wrt_v=GeomVertexWriter(vdata, InternalName.getVertex())
        wrt_n=GeomVertexWriter(vdata, InternalName.getNormal())
        wrt_t=GeomVertexWriter(vdata, InternalName.getTexcoord())
        # llenar vértices y primitivas
        i_vertice=0
        for x in range(0, Terreno2.TamanoParcela):
            for y in range(0, Terreno2.TamanoParcela):
                # vértices
                v=list()
                v.append(Vec3(x, y, altitud[x+1][y+1])) # 4, para geometría
                v.append(Vec3(x+1, y, altitud[x+2][y+1]))
                v.append(Vec3(x, y+1, altitud[x+1][y+2]))
                v.append(Vec3(x+1, y+1, altitud[x+2][y+2]))
                # llenar vertex data
                # v0
                wrt_v.addData3(v[0])
                wrt_n.addData3(normales[x][y])
                wrt_t.addData2(x, y)
                # v1
                wrt_v.addData3(v[1])
                wrt_n.addData3(normales[x+1][y])
                wrt_t.addData2(x+1, y)
                # v2
                wrt_v.addData3(v[2])
                wrt_n.addData3(normales[x][y+1])
                wrt_t.addData2(x, y+1)
                # v3
                wrt_v.addData3(v[3])
                wrt_n.addData3(normales[x+1][y+1])
                wrt_t.addData2(x+1, y+1)
                # primitivas
                prim.addVertex(i_vertice)
                prim.addVertex(i_vertice+1)
                prim.addVertex(i_vertice+2)
                prim.closePrimitive()
                prim.addVertex(i_vertice+2)
                prim.addVertex(i_vertice+1)
                prim.addVertex(i_vertice+3)
                prim.closePrimitive()
                #
                i_vertice+=4
        # geom
        geom=Geom(vdata)
        geom.addPrimitive(prim)
        geom.setBoundsType(BoundingVolume.BT_box)
        # nodo
        geom_node=GeomNode(nombre)
        geom_node.addGeom(geom)
        geom_node.setBoundsType(BoundingVolume.BT_box)
        return geom_node
        
    def _crear_geometria_parcela(self, nombre, idx_pos):
        # formato
        formato=GeomVertexFormat.getV3n3t2()
        # iniciar vértices y primitivas
        vdata=GeomVertexData("vertex_data", formato, Geom.UHStatic)
        vdata.setNumRows((Terreno2.TamanoParcela+1)*(Terreno2.TamanoParcela+1))
        prim=GeomTriangles(Geom.UHStatic)
        # vertex writers
        wrt_v=GeomVertexWriter(vdata, InternalName.getVertex())
        wrt_n=GeomVertexWriter(vdata, InternalName.getNormal())
        wrt_t=GeomVertexWriter(vdata, InternalName.getTexcoord())
        # llenar vértices y primitivas
        i_vertice=0
        for x in range(0, Terreno2.TamanoParcela):
            for y in range(0, Terreno2.TamanoParcela):
                # vértices
                v0=Vec3(x, y, self.obtener_altitud((Terreno2.TamanoParcela*idx_pos[0]+x, Terreno2.TamanoParcela*idx_pos[1]+y)))
                v1=Vec3(x+1, y, self.obtener_altitud((Terreno2.TamanoParcela*idx_pos[0]+x+1, Terreno2.TamanoParcela*idx_pos[1]+y)))
                v2=Vec3(x, y+1, self.obtener_altitud((Terreno2.TamanoParcela*idx_pos[0]+x, Terreno2.TamanoParcela*idx_pos[1]+y+1)))
                v3=Vec3(x+1, y+1, self.obtener_altitud((Terreno2.TamanoParcela*idx_pos[0]+x+1, Terreno2.TamanoParcela*idx_pos[1]+y+1)))
                normal1=self._calcular_normal(v0, v1, v2)
                normal2=normal1 #self._calcular_normal(v2, v1, v3)
                # llenar vertex data
                # v0
                wrt_v.addData3(v0)
                wrt_n.addData3(normal1)
                wrt_t.addData2(x, y)
                # v1
                wrt_v.addData3(v1)
                wrt_n.addData3(normal1)
                wrt_t.addData2(x+1, y)
                # v2
                wrt_v.addData3(v2)
                wrt_n.addData3(normal1)
                wrt_t.addData2(x, y+1)
                # v2
                wrt_v.addData3(v2)
                wrt_n.addData3(normal2)
                wrt_t.addData2(x, y+1)
                # v1
                wrt_v.addData3(v1)
                wrt_n.addData3(normal2)
                wrt_t.addData2(x+1, y)
                # v3
                wrt_v.addData3(v3)
                wrt_n.addData3(normal2)
                wrt_t.addData2(x+1, y+1)
                # primitivas
                prim.addVertex(i_vertice)
                prim.addVertex(i_vertice+1)
                prim.addVertex(i_vertice+2)
                prim.closePrimitive()
                prim.addVertex(i_vertice+3)
                prim.addVertex(i_vertice+4)
                prim.addVertex(i_vertice+5)
                prim.closePrimitive()
                #
                i_vertice+=6
        # geom
        geom=Geom(vdata)
        geom.addPrimitive(prim)
        geom.setBoundsType(BoundingVolume.BT_box)
        # nodo
        geom_node=GeomNode(nombre)
        geom_node.addGeom(geom)
        geom_node.setBoundsType(BoundingVolume.BT_box)
        return geom_node

    def _calcular_normal(self, v0, v1, v2):
        U=v1-v0
        V=v2-v0
        return U.cross(V)
    
    def _crear_lineas_normales(self, nombre, geom_node_parcela):
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
        for k in Terreno2.NoiseObjsWeights:
            suma_coefs+=k
        for k in Terreno2.NoiseObjsWeights:
            self._noise_scaled_weights.append(k/suma_coefs)
        # noise objects
        escala_general=1.0
        escalas=list()
        for scale in Terreno2.NoiseObjsScales:
            escalas.append(scale*escala_general)
        # lista
        self._noise_objs.append(PerlinNoise2(escalas[0], escalas[0], 256, Terreno2.Semilla))
        self._noise_objs.append(PerlinNoise2(escalas[1], escalas[1], 256, Terreno2.Semilla+(128*1)))
        self._noise_objs.append(PerlinNoise2(escalas[2], escalas[2], 256, Terreno2.Semilla++(128*2)))
        self._noise_objs.append(PerlinNoise2(escalas[3], escalas[3], 256, Terreno2.Semilla++(128*3)))
        self._noise_objs.append(PerlinNoise2(escalas[4], escalas[4], 256, Terreno2.Semilla++(128*4)))
        # biomasa:
        # temperatura
        self._ruido_temperatura=PerlinNoise2(Terreno2.RuidoTemperatura[0], Terreno2.RuidoTemperatura[0], 256, Terreno2.RuidoTemperatura[1])

#
# TESTER
#
from direct.showbase.ShowBase import ShowBase
from direct.gui.DirectGui import *
class Tester(ShowBase):

    def __init__(self):
        #
        super(Tester, self).__init__()
        self.disableMouse()
        self.win.setClearColor(Vec4(0.95, 1.0, 1.0, 1.0))
        #
        bullet_world=BulletWorld()
        #
        self.pos_foco=None
        self.cam_pitch=30.0
        self.escribir_archivo=False # cada update
        #
        self.terreno=Terreno2(self, bullet_world)
        #
        plano=CardMaker("plano_agua")
        r=Terreno2.TamanoParcela*6
        plano.setFrame(-r, r, -r, r)
        plano.setColor((0, 0, 1, 1))
        self.plano_agua=self.render.attachNewNode(plano.generate())
        self.plano_agua.setP(-90.0)
        #self.plano_agua.hide()
        #
        self.cam_driver=self.render.attachNewNode("cam_driver")
        self.camera.reparentTo(self.cam_driver)
        self.camera.setPos(Terreno2.TamanoParcela/2, 450, 0)
        self.camera.lookAt(self.cam_driver)
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
        self._cargar_ui()
        
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
                self.terreno.nodo.writeBamFile("terreno2.bam")
            self.plano_agua.setPos(Vec3(pos[0], pos[1], self.terreno.nivel_agua))
            #
            self.cam_driver.setPos(Vec3(pos[0], pos[1], 50))
            #
            self.lblInfo["text"]=self.terreno.obtener_info()
            #
            self.pos_foco=pos
            #
            self._generar_imagen()

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
                c=int(255*(1-((self.terreno.nivel_agua-a)/(self.terreno.nivel_agua))))
                if a>self.terreno.nivel_agua:
                    self.imagen.setPixel(x, y, PNMImageHeader.PixelSpec(c, c, 0, 255))
                else:
                    self.imagen.setPixel(x, y, PNMImageHeader.PixelSpec(0, 0, c, 255))
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
        self.lblInfo=DirectLabel(parent=self.frame, pos=(-1, 0, 0.15), scale=0.05, text=self.terreno.obtener_info(), frameColor=(1, 1, 1, 0.2), frameSize=(0, 40, -2, 2), text_align=TextNode.ALeft, text_pos=(0, 1, 1))
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
            self._generar_imagen()

    def _alejar_zoom_imagen(self):
        log.info("_alejar_zoom_imagen")
        if self.zoom_imagen<512:
            self.zoom_imagen*=2
            self._generar_imagen()

if __name__=="__main__":
    logging.basicConfig(level=logging.INFO)
    PStatClient.connect()
    tester=Tester()
    tester.terreno.dibujar_normales=False
    Terreno2.RadioExpansion=0
    tester.escribir_archivo=True
    tester.run()
