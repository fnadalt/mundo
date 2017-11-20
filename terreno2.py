from panda3d.bullet import *
from panda3d.core import *

import logging
log=logging.getLogger(__name__)

class Terreno2:
    
    # altura maxima
    AlturaMaxima=150

    # tamaño de la parcela
    TamanoParcela=32

    # radio de expansion
    RadioExpansion=5

    # topografia
    Semilla=435
    NoiseObjsScales=[256.0, 128.0, 64.0, 32.0, 16.0]
    NoiseObjsWeights=[1.0, 0.02, 0.01, 0.075, 0.025] # scale_0>scale_1>scale_n

    def __init__(self, base, bullet_world):
        # referencias:
        self.base=base
        self.bullet_world=bullet_world
        # componentes:
        self.nodo=self.base.render.attachNewNode("terreno2")
        self._parcelas={} # {idx_pos:cuerpo_parcela_node_path,...}
        # 2 abordajes
        #self._noise_obj=None # StackedPerlinNoise2
        self._noise_objs=list() # [PerlinNoise2, ...]
        # variables externas:
        self.pos_foco=None
        self.idx_pos_parcela_actual=None # (x,y)
        self.nivel_agua=Terreno2.AlturaMaxima * 0.3
        # debug
        self.dibujar_normales=False # cada update
        self.escribir_archivo=False # cada update
        # variables internas:
        self._noise_scaled_weights=list() # normalizado
        # init:
        self._generar_noise_objs()

    def obtener_indice_parcela_foco(self):
        x=int(self.pos_foco[0]/Terreno2.TamanoParcela)
        y=int(self.pos_foco[1]/Terreno2.TamanoParcela)
        return (x, y)

    def obtener_altitud(self, pos):
        altitud=0
        for _i_noise_obj in range(len(self._noise_objs)):
            altitud+=(self._noise_objs[_i_noise_obj].noise(pos[0], pos[1]) * self._noise_scaled_weights[_i_noise_obj])
        altitud+=1
        altitud/=2
        altitud*=Terreno2.AlturaMaxima
        return altitud

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
            for idx_pos in self._parcelas.keys():
                if idx_pos not in idxs_pos_parcelas_obj:
                    idxs_pos_parcelas_descargar.append(idx_pos)
            for idx_pos in idxs_pos_parcelas_obj:
                if idx_pos not in self._parcelas:
                    idxs_pos_parcelas_cargar.append(idx_pos)
            # descarga y carga de parcelas
            for idx_pos in idxs_pos_parcelas_descargar:
                self._descargar_parcela(idx_pos)
            for idx_pos in idxs_pos_parcelas_cargar:
                self._cargar_parcela(idx_pos)
        #
        if self.escribir_archivo:
            self.nodo.writeBamFile("terreno2.bam")

    def _cargar_parcela(self, idx_pos):
        log.info("_cargar_parcela %s"%str(idx_pos))
        # posición y nombre
        pos=Vec2(idx_pos[0]*Terreno2.TamanoParcela, idx_pos[1]*Terreno2.TamanoParcela)
        nombre="parcela_%i_%i"%(int(pos[0]), int(pos[1]))
        # nodo
        parcela=self.nodo.attachNewNode(nombre)
        parcela.setPos(pos[0], pos[1], 0.0)
        # geometría
        geom_node=self._crear_geometria(nombre, idx_pos)
        #
        parcela.attachNewNode(geom_node)
        # debug: normales
        if self.dibujar_normales:
            geom_node_normales=self._crear_lineas_normales("normales_%i_%i"%(int(pos[0]), int(pos[1])), geom_node)
            parcela.attachNewNode(geom_node_normales)
        #
        self._parcelas[idx_pos]=parcela

    def _descargar_parcela(self, idx_pos):
        log.info("_descargar_parcela %s"%str(idx_pos))
        parcela=self._parcelas[idx_pos]
        parcela.removeNode()
        del self._parcelas[idx_pos]
    
    def _crear_geometria(self, nombre, idx_pos):
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
        #
        self._noise_objs.append(PerlinNoise2(escalas[0], escalas[0], 256, Terreno2.Semilla))
        self._noise_objs.append(PerlinNoise2(escalas[1], escalas[1], 256, Terreno2.Semilla+(128*1)))
        self._noise_objs.append(PerlinNoise2(escalas[2], escalas[2], 256, Terreno2.Semilla++(128*2)))
        self._noise_objs.append(PerlinNoise2(escalas[3], escalas[3], 256, Terreno2.Semilla++(128*3)))
        self._noise_objs.append(PerlinNoise2(escalas[4], escalas[4], 256, Terreno2.Semilla++(128*4)))

#
# TESTER
#
from direct.showbase.ShowBase import ShowBase
import math
class Tester(ShowBase):

    def __init__(self):
        #
        super(Tester, self).__init__()
        self.disableMouse()
        #
        bullet_world=BulletWorld()
        #
        self.pos_foco=[0, 0, 0]
        self.cam_pitch=30.0
        #
        self.terreno=Terreno2(self, bullet_world)
        #
        plano=CardMaker("plano_agua")
        r=Terreno2.TamanoParcela*6
        plano.setFrame(-r, r, -r, r)
        plano.setColor((0, 0, 1, 1))
        self.plano_agua=self.render.attachNewNode(plano.generate())
        self.plano_agua.setP(-90.0)
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
        self.taskMgr.add(self.update, "update")
        self.accept("wheel_up", self.zoom, [1])
        self.accept("wheel_down", self.zoom, [-1])
        #
        self.terreno.update((0, 0))
        
    def update(self, task):
        nueva_pos_foco=self.pos_foco[:]
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
            self.pos_foco=nueva_pos_foco
            log.info("update")
            #
            self.terreno.update(self.pos_foco)
            self.plano_agua.setPos(Vec3(self.pos_foco[0], self.pos_foco[1], self.terreno.nivel_agua))
            #
            self.cam_driver.setPos(Vec3(self.pos_foco[0], self.pos_foco[1], 50))
            #
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
        
if __name__=="__main__":
    logging.basicConfig(level=logging.INFO)
    PStatClient.connect()
    tester=Tester()
    tester.terreno.dibujar_normales=False
    tester.terreno.escribir_archivo=False
    tester.run()
