from panda3d.bullet import *
from panda3d.core import *
from heightmap import HeightMap
from parcela import Parcela

import logging
log=logging.getLogger(__name__)

class Terreno(NodePath):

    altura_maxima=300.0
    cantidad_parcelas_expandir=2
    
    def __init__(self,  mundo, foco):
        NodePath.__init__(self, "terreno")
        self.reparentTo(mundo)
        self.setSz(Terreno.altura_maxima)
        # componentes
        self.mundo=mundo
        self.base=mundo.base
        self.foco=foco
        # variables externas
        self.idx_pos_parcela_actual=None
        self.nivel_agua=-25.0
        # variables internas
        self._ajuste_altura=-0.5
        self._height_map_id=589
        self._height_map=HeightMap(self._height_map_id)
        self._parcelas={} # {idx_pos:cuerpo_parcela_node_path,...}
        #
        self.update()
    
    def rayo(self, pos):
        z=None
        test=self.mundo.mundo_fisico.rayTestAll(LPoint3(pos[0], pos[1], 1000.0), LPoint3(pos[0], pos[1], -1000.0), BitMask32.bit(1))
        for hit in test.getHits():
            #log.debug("rayo %s at %s"%(str(hit.getNode()), str(hit.getHitPos())))    
            if hit.getNode().getName().startswith("parcela_") and z==None:
                z=hit.getHitPos().getZ()
                break
        return z

    def obtener_altitud(self, pos):
        #x_ajustada=pos[0]+Parcela.pos_offset-0.5
        #y_ajustada=pos[1]+Parcela.pos_offset-0.5
        #altitud=(self._height_map.getHeight(x_ajustada, y_ajustada)+self._ajuste_altura)*Terreno.altura_maxima
        altitud=self.rayo(pos)
        return altitud
    
    def obtener_indice_parcela_foco(self):
        pos_foco=self.foco.getPos().getXy()
        pos_foco[0]+=-Parcela.pos_offset if pos_foco[0]<0.0 else Parcela.pos_offset
        pos_foco[1]+=-Parcela.pos_offset if pos_foco[1]<0.0 else Parcela.pos_offset
        return (int(pos_foco[0]/Parcela.tamano), int(pos_foco[1]/Parcela.tamano))
    
    def _cargar_parcela(self, idx_pos):
        log.info("cargando parcela "+str(idx_pos))
        #
        if idx_pos in self._parcelas:
            log.error("se solicito la carga de la parcela %s, que ya se encuentra en self._parcelas"%str(idx_pos))
            return
        #
        #m=Material()
        #m.setDiffuse((0.5+0.35*idx_pos[0], 0.0, 0.0, 1.0))
        #m.setShininess(5.0)
        #
        p=Parcela(self._height_map, idx_pos[0], idx_pos[1], self.foco)
        p.setBruteforce(True)
        p.generate()
        _pN=p.getRoot()
        #
        tsArena=TextureStage("ts_terreno_arena")
        texArena=self.base.loader.loadTexture("texturas/arena.png")
        _pN.setTexture(tsArena, texArena)
        tsTierra=TextureStage("ts_terreno_tierra")
        texTierra=self.base.loader.loadTexture("texturas/tierra.png")
        _pN.setTexture(tsTierra, texTierra)
        tsPasto=TextureStage("ts_terreno_pasto")
        texPasto=self.base.loader.loadTexture("texturas/pasto.png")
        _pN.setTexture(tsPasto, texPasto)
        tsNieve=TextureStage("ts_terreno_nieve")
        texNieve=self.base.loader.loadTexture("texturas/nieve.png")
        _pN.setTexture(tsNieve, texNieve)
        #
        shader=Shader.load(Shader.SL_GLSL, vertex="shaders/terreno.v.glsl", fragment="shaders/terreno.f.glsl")
        _pN.setShader(shader)
        #_pN.setShaderAuto()
        #_pN.setMaterial(m)
        #_pN.setRenderModeWireframe()
        #
        _rbody=BulletRigidBodyNode("%s_rigid_body"%p.nombre)
        for geom_node in _pN.findAllMatches("**/+GeomNode"):
            #logging.debug("geom? %s transform=%s"%(str(geom_node), str(geom_node.getTransform(_pN))))
            _tri_mesh=BulletTriangleMesh()
            _tri_mesh.addGeom(geom_node.node().getGeom(0))
            _shape=BulletTriangleMeshShape(_tri_mesh, dynamic=False)
            _rbody.addShape(_shape, geom_node.getTransform())
        _rbodyN=self.attachNewNode(_rbody)
        _rbodyN.setPos(Parcela.tamano*idx_pos[0]-Parcela.pos_offset, Parcela.tamano*idx_pos[1]-Parcela.pos_offset, self._ajuste_altura)
        _rbodyN.setCollideMask(BitMask32.bit(1))
        _pN.reparentTo(_rbodyN)
        p.setBruteforce(False)
        p.generate()
        p.update()
        self.mundo.mundo_fisico.attachRigidBody(_rbody)
        log.debug("parcela cargada "+str(_rbodyN.getPos()))
        #
        self._parcelas[idx_pos]=(_rbodyN, p)

    def _descargar_parcela(self, idx_pos):
        log.info("descargando parcela "+str(idx_pos))
        if idx_pos not in self._parcelas:
            log.error("se solicito la descarga de la parcela %s, que no se encuentra en self._parcelas"%str(idx_pos))
            return
        # no es suficiente... quedan las parcelas anteriores y se siuperponen.
        _rbodyN, p=self._parcelas[idx_pos]
        _rbodyN.removeNode()
        del self._parcelas[idx_pos]
        
    def update(self):
        #
        idx_pos=self.obtener_indice_parcela_foco()
        if idx_pos!=self.idx_pos_parcela_actual:
            self.idx_pos_parcela_actual=idx_pos
            #self._cargar_parcela(idx_pos)
            #return
            log.debug("foco sobre parcela "+str(idx_pos))
            #
            idxs_pos_parcelas_obj=[]
            idxs_pos_parcelas_cargar=[]
            idxs_pos_parcelas_descargar=[]
            #
            for idx_pos_x in range(idx_pos[0]-Terreno.cantidad_parcelas_expandir, idx_pos[0]+Terreno.cantidad_parcelas_expandir+1):
                for idx_pos_y in range(idx_pos[1]-Terreno.cantidad_parcelas_expandir, idx_pos[1]+Terreno.cantidad_parcelas_expandir+1):
                    idxs_pos_parcelas_obj.append((idx_pos_x, idx_pos_y))
            log.debug("indices de parcelas a cargar: "+str(idxs_pos_parcelas_obj))
            #
            for idx_pos in self._parcelas.keys():
                if idx_pos not in idxs_pos_parcelas_obj:
                    idxs_pos_parcelas_descargar.append(idx_pos)
                    log.debug("se descargara parcela "+str(idx_pos))
            for idx_pos in idxs_pos_parcelas_obj:
                if idx_pos not in self._parcelas:
                    idxs_pos_parcelas_cargar.append(idx_pos)
                    log.debug("se cargara parcela "+str(idx_pos))
            #
            for idx_pos in idxs_pos_parcelas_descargar:
                self._descargar_parcela(idx_pos)
            for idx_pos in idxs_pos_parcelas_cargar:
                self._cargar_parcela(idx_pos)
        # poco eficiente?
        for _p in self._parcelas.values():
            _p[1].update()
