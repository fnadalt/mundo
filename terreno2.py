from panda3d.bullet import *
from panda3d.core import *

import logging
log=logging.getLogger(__name__)

class Terreno2:

    # tamaño de la parcela
    TamanoParcela=128

    # radio de expansion
    RadioExpansion=2

    def __init__(self, base, bullet_world):
        # referencias:
        self.base=base
        self.bullet_world=bullet_world
        # componentes:
        self.nodo=self.base.render.attachNewNode("terreno2")
        # variables externas:
        self.pos_foco=None
        self.idx_pos_parcela_actual=None # (x,y)
        self.nivel_agua=0.0
        # variables internas:
        self._parcelas={} # {idx_pos:cuerpo_parcela_node_path,...}
        self._perlin1=StackedPerlinNoise2(256.0, 256.0, 4, 1.2, 1.2, 256, 785)

    def obtener_indice_parcela_foco(self):
        x=int(self.pos_foco[0]/Terreno2.TamanoParcela)
        y=int(self.pos_foco[1]/Terreno2.TamanoParcela)
        return (x, y)

    def obtener_altitud(self, pos):
        altitud=self._perlin1.noise(pos[0], pos[1])
        altitud+=2
        altitud/=2
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

    def _cargar_parcela(self, idx_pos):
        # posición y nombre
        pos=Vec2(idx_pos[0]*Terreno2.TamanoParcela, idx_pos[1]*Terreno2.TamanoParcela)
        nombre="parcela_%i_%i"%(int(pos[0]), int(pos[1]))
        # nodo
        parcela=self.nodo.attachNewNode(nombre)
        parcela.setPos(pos[0], pos[1], 0.0)
        # geometría
        geom_node=self._crear_geometria(nombre)
        #
        parcela.attachNewNode(geom_node)

    def _descargar_parcela(self, idx_pos):
        pass
    
    def _crear_geometria(self, nombre):
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
                v0=Vec3(x, y, 0)
                v1=Vec3(x+1, y, 0)
                v2=Vec3(x, y+1, 0)
                v3=Vec3(x+1, y+1, 0)
                normal=self._calcular_normal(v0, v1, v2)
                # quad triangle 1
                # v0
                wrt_v.addData3(v0)
                wrt_n.addData3(normal)
                wrt_t.addData2(x, y)
                # v1
                wrt_v.addData3(v1)
                wrt_n.addData3(normal)
                wrt_t.addData2(x+1, y)
                # v2
                wrt_v.addData3(v2)
                wrt_n.addData3(normal)
                wrt_t.addData2(x, y+1)
                # data
                # primitiva
                prim.addVertex(i_vertice)
                prim.addVertex(i_vertice+1)
                prim.addVertex(i_vertice+2)
                prim.closePrimitive()
                #
                # quad triangle 2
                normal=self._calcular_normal(v0, v1, v2)
                # v2
                wrt_v.addData3(v2)
                wrt_n.addData3(normal)
                wrt_t.addData2(x, y+1)
                # v1
                wrt_v.addData3(v1)
                wrt_n.addData3(normal)
                wrt_t.addData2(x+1, y)
                # v3
                wrt_v.addData3(v3)
                wrt_n.addData3(normal)
                wrt_t.addData2(x+1, y+1)
                # data
                # primitiva
                prim.addVertex(i_vertice+2)
                prim.addVertex(i_vertice+1)
                prim.addVertex(i_vertice+3)
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
        
