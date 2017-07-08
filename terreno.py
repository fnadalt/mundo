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
        self._nivel_agua=0.3
        self._height_map_id=589
        self._height_map=HeightMap(self._height_map_id, self._nivel_agua)
        #
        self._parcelas={} # {idx_pos:cuerpo_parcela_node_path,...}
        self._p=[]
        #
        self.actualizar_parcelas()
    
    def obtener_altitud(self, pos):
        x_ajustada=pos[0]+Parcela.pos_offset
        y_ajustada=pos[1]+Parcela.pos_offset
        altitud=self._height_map.getHeight(x_ajustada, y_ajustada)*Terreno.altura_maxima
        return altitud
    
    def obtener_indice_parcela_foco(self):
        pos_foco=self.foco.getPos().getXy()
        return (int(pos_foco.getX()/Parcela.tamano), int(pos_foco.getY())/Parcela.tamano)
    
    def _cargar_parcela(self, idx_pos):
        log.info("cargando parcela "+str(idx_pos))
        if idx_pos in self._parcelas:
            log.error("se solicito la carga de la parcela %s, que ya se encuentra en self._parcelas"%str(idx_pos))
            return
        #
        m=Material()
        m.setDiffuse((0.5+0.35*idx_pos[0], 0.0, 0.0, 1.0))
        m.setShininess(5.0)
        #
        p=Parcela(self._height_map, idx_pos[0], idx_pos[1], self.foco)
        pN=p.getRoot()
        pN.setMaterial(m)
        pN.setRenderModeWireframe()
        #pN.setPos(Parcela.tamano*idx_pos[0], Parcela.tamano*idx_pos[1], -0.5)
        p.update()
        logging.debug("parcela at "+str(pN.getPos()))
        #
        shape=BulletHeightfieldShape(p.imagen, Terreno.altura_maxima, ZUp)
        shape.setUseDiamondSubdivision(True)
        cuerpo=BulletRigidBodyNode("%s_rigid_body"%p.nombre)
        cuerpo.addShape(shape)
        cuerpoN=NodePath(cuerpo)
        cuerpoN.reparentTo(self)
        cuerpoN.setPos(Parcela.tamano*idx_pos[0], Parcela.tamano*idx_pos[1], 0.0)
        logging.debug("heightfield rigid body at "+str(cuerpoN.getPos()))
        pN.reparentTo(cuerpoN)
        self.mundo.mundo_fisico.attachRigidBody(cuerpo)
        #
        self._parcelas[idx_pos]=cuerpoN
        self._p.append((pN, cuerpoN))

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
        #self._cargar_parcela(idx_pos)
        #return
        log.debug("hombre sobre parcela "+str(idx_pos))
        #
        for idx_pos_x in range(1):#range(idx_pos[0]-1, 2):
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
