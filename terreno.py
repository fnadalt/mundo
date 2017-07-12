from panda3d.bullet import *
from panda3d.core import *
from heightmap import HeightMap
from parcela import Parcela

import logging
log=logging.getLogger(__name__)

class Terreno(NodePath):

    altura_maxima=300.0
    
    def __init__(self,  mundo, foco):
        NodePath.__init__(self, "terreno")
        self.reparentTo(mundo)
        self.setSz(Terreno.altura_maxima)
        #
        self.mundo=mundo
        self.base=mundo.base
        self.foco=foco
        #
        self._ajuste_altura=-0.5
        self._nivel_agua=0.3
        self._height_map_id=589
        self._height_map=HeightMap(self._height_map_id, self._nivel_agua)
        #
        self._parcelas={} # {idx_pos:cuerpo_parcela_node_path,...}
        #
        self.actualizar_parcelas()
    
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
        return (int(pos_foco.getX()/Parcela.tamano), int(pos_foco.getY())/Parcela.tamano)
    
    def _cargar_parcela(self, idx_pos):
        log.info("cargando parcela "+str(idx_pos))
        #
        if idx_pos in self._parcelas:
            log.error("se solicito la carga de la parcela %s, que ya se encuentra en self._parcelas"%str(idx_pos))
            return
        #
        m=Material()
        m.setDiffuse((0.5+0.35*idx_pos[0], 0.0, 0.0, 1.0))
        m.setShininess(5.0)
        #
        p=Parcela(self._height_map, idx_pos[0], idx_pos[1], self.foco)
        p.setBruteforce(True)
        p.generate()
        _pN=p.getRoot()
        _pN.setMaterial(m)
        _pN.setRenderModeWireframe()
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
        logging.debug("parcela at "+str(_rbodyN.getPos()))
        #
        self._parcelas[idx_pos]=_rbodyN

    def _descargar_parcela(self, idx_pos):
        log.info("descargando parcela "+str(idx_pos))
        if idx_pos not in self._parcelas:
            log.error("se solicito la descarga de la parcela %s, que no se encuentra en self._parcelas"%str(idx_pos))
            return
        #
        del self._parcelas[idx_pos]
        
    def actualizar_parcelas(self):
        #
        idxs_pos_parcelas_obj=[]
        idxs_pos_parcelas_cargar=[]
        idxs_pos_parcelas_descargar=[]
        #
        idx_pos=self.obtener_indice_parcela_foco()
        self._cargar_parcela(idx_pos)
        return
        log.debug("foco sobre parcela "+str(idx_pos))
        #
        for idx_pos_x in range(idx_pos[0]-1, 2):
            for idx_pos_y in range(idx_pos[1]-1, 2):
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
