from panda3d.bullet import *
from panda3d.core import *
from heightmap import HeightMap
from parcela import *
import os.path

import logging
log=logging.getLogger(__name__)

class Terreno(NodePath):

    altura_maxima=300.0
    cantidad_parcelas_expandir=2
    
    def __init__(self, base, bullet_world):
        NodePath.__init__(self, "terreno")
        # variables internas
        self._ajuste_altura=-0.5
        self._height_map_id=589
        self._height_map=HeightMap(self._height_map_id)
        self._parcelas={} # {idx_pos:cuerpo_parcela_node_path,...}
        # variables externas
        self.idx_pos_parcela_actual=None
        self.nivel_agua=-25.0#-25.0,10.5
        # referencias
        self.foco=None
        self.base=base
        self.bullet_world=bullet_world
        #
        self.setSz(Terreno.altura_maxima)

    def rayTestAll(self, pos):
        test=self.bullet_world.rayTestAll(LPoint3(pos[0], pos[1], 1000.0), LPoint3(pos[0], pos[1], -1000.0), BitMask32.bit(1))
        return test.getHits()

    def obtener_altitud(self, pos): # <- get_height(pos)
        altitud=0
        # index based
        #x_ajustada=pos[0]+Parcela.pos_offset-0.5
        #y_ajustada=pos[1]+Parcela.pos_offset-0.5
        #altitud=(self._height_map.getHeight(x_ajustada, y_ajustada)+self._ajuste_altura)*Terreno.altura_maxima
        # ray test
        hits=self.rayTestAll(pos)
        for hit in hits:
            #log.debug("rayo %s at %s"%(str(hit.getNode()), str(hit.getHitPos())))    
            if hit.getNode().getName().startswith("cuerpo_suelo_") and altitud==0:
                altitud=hit.getHitPos().getZ()
                break
        return altitud
    
    def obtener_indice_parcela_foco(self):
        if self.foco==None:
            log.error("no está definido el foco")
            return (0, 0)
        pos_foco=self.foco.getPos().getXy()
        pos_foco[0]+=-Parcela.pos_offset if pos_foco[0]<0.0 else Parcela.pos_offset
        pos_foco[1]+=-Parcela.pos_offset if pos_foco[1]<0.0 else Parcela.pos_offset
        return (int(pos_foco[0]/Parcela.tamano), int(pos_foco[1]/Parcela.tamano))
    
    def _cargar_parcela(self, idx_pos):
        log.info("cargando parcela "+str(idx_pos))
        #
        if self.foco==None:
            log.error("no está definido el foco")
            return
        #
        if idx_pos in self._parcelas:
            log.error("se solicito la carga de la parcela %s, que ya se encuentra en self._parcelas"%str(idx_pos))
            return
        #
        p=ParcelaGeoMip(self._height_map, idx_pos[0], idx_pos[1], self.foco)
        #p=ParcelaVoxel(self._height_map, idx_pos[0], idx_pos[1], self.foco)
        _pN=p.generar()
        #
        self._aplicar_shader_parcela(_pN, p)
        #self._aplicar_shader_parcela2(_pN, p)
        _rbodyN=self._generar_cuerpo_fisico(_pN, p, idx_pos)
        #
        self._parcelas[idx_pos]=(NodePath(_rbodyN), p)

    def _descargar_parcela(self, idx_pos):
        log.info("descargando parcela "+str(idx_pos))
        if idx_pos not in self._parcelas:
            log.error("se solicito la descarga de la parcela %s, que no se encuentra en self._parcelas"%str(idx_pos))
            return
        # no es suficiente... quedan las parcelas anteriores y se siuperponen.
        _rbodyN=self._parcelas[idx_pos][0]
        _rbodyN.removeNode()
        del self._parcelas[idx_pos]
    
    def _corregir_geometria(self, nodo_parcela):
        return
        geom_nodes=nodo_parcela.findAllMatches("**/+GeomNode")
        for geom_node in geom_nodes:
            geom=geom_node.node().modifyGeom(0)
            v_data=geom.modifyVertexData().modifyArray(0)
            #vertex_rewriter=GeomVertexRewriter(v_data, 0)
            normal_rewriter=GeomVertexRewriter(v_data, "normal")
            with open("log.txt", "w") as f:
                while not normal_rewriter.isAtEnd():
                    vertex=Point3(normal_rewriter.getData3f())
                    vertex.setZ(vertex.getZ())
                    normal_rewriter.setData3f(vertex)
                    f.write(str(vertex)+"\n")
                f.write(str(geom.getVertexData().getArray(0)))
    
    def _aplicar_shader_parcela(self, nodo_parcela, parcela):
        #
        img_tex=None
        ruta_arch_tex=os.path.join(os.getcwd(), "parcelas", "%s_textura.png"%parcela.nombre)
        if os.path.exists(ruta_arch_tex):
            log.info("se encontro textura en %s"%ruta_arch_tex)
            img_tex=PNMImage(Filename(ruta_arch_tex))
        else:
            log.info("generando textura %s"%ruta_arch_tex)
            #
            img=list()
            img.append([0, 0, 8, 0.42, PNMImage(Filename("texturas/arena.png"))]) # {tipo:[x,y,step,cutval,img]}
            img.append([0, 0, 8, 0.44, PNMImage(Filename("texturas/tierra.png"))])
            img.append([0, 0, 8, 0.56, PNMImage(Filename("texturas/pasto.png"))])
            img.append([0, 0, 8, 0.62, PNMImage(Filename("texturas/tierra.png"))]) # altura_corte |0.8
            img.append([0, 0, 8, 0.70, PNMImage(Filename("texturas/nieve.png"))]) # altura_corte |1.0
            #
            tamano_tex=128
            img_tex=PNMImage(tamano_tex, tamano_tex)
            for x in range(tamano_tex):
                for y in range(tamano_tex):
                    pxl=PNMImageHeader.PixelSpec(0, 0, 0, 1)
                    altitud=parcela.obtener_altitud(x*Parcela.tamano/tamano_tex, y*Parcela.tamano/tamano_tex)
                    for img_data in img:
                        if altitud<img_data[3]:
                            imagen=img_data[4]
                            pxl=imagen.getPixel(img_data[0], img_data[1])
                            img_data[0]+=img_data[2]
                            if img_data[0]>=imagen.getXSize():
                                img_data[0]-=imagen.getXSize()
                            break
                    img_tex.setPixel(x, y, pxl)
                for img_data in img:
                    img_data[0]=0
                    img_data[1]+=img_data[2]
                    if img_data[1]>=img_data[4].getYSize():
                        img_data[1]-=img_data[4].getYSize()
            img_tex.write(Filename(ruta_arch_tex))
        #
        #material=Material(self.mundo.getMaterial())
        #material.setAmbient((0.75, 0.75, 0.75, 1.0))
        #if material!=None:
        #    log.debug("estableciendo material '%s'"%material.getName())
        #    nodo_parcela.setMaterial(material)
        #nodo_parcela.setMaterialOff(1000)
        #nodo_parcela.setLightOff(self.mundo.sol_a, 1000)
        #
        ts0=TextureStage("ts_parcela")
        tex0=Texture("tex_parcela")
        tex0.load(img_tex)
        #nodo_parcela.setLight(self.mundo.sol_a)
        nodo_parcela.setTexture(ts0, tex0)
        nodo_parcela.setShaderOff(1000)
        

    def _aplicar_shader_parcela2(self, nodo_parcela):
        tsArena=TextureStage("ts_terreno_arena")
        texArena=self.base.loader.loadTexture("texturas/arena.png")
        nodo_parcela.setTexture(tsArena, texArena)
        tsTierra=TextureStage("ts_terreno_tierra")
        texTierra=self.base.loader.loadTexture("texturas/tierra.png")
        nodo_parcela.setTexture(tsTierra, texTierra)
        tsPasto=TextureStage("ts_terreno_pasto")
        texPasto=self.base.loader.loadTexture("texturas/pasto.png")
        nodo_parcela.setTexture(tsPasto, texPasto)
        tsNieve=TextureStage("ts_terreno_nieve")
        texNieve=self.base.loader.loadTexture("texturas/nieve.png")
        nodo_parcela.setTexture(tsNieve, texNieve)
        #
        shader=Shader.load(Shader.SL_GLSL, vertex="shaders/terreno.v.glsl", fragment="shaders/terreno.f.glsl")
        inv_transform=LMatrix4f()
        inv_transform.invertFrom(self.getTransform().getMat())
        nodo_parcela.setShaderInput("M", inv_transform)
        nodo_parcela.setShaderInput("pos_sol", self.mundo.pointN.getPos(self.base.render))
        nodo_parcela.setShaderInput("color_sol", self.mundo.pointN.node().getColor())
        nodo_parcela.setShaderInput("intensidad_sol", Vec3(0.85, 0.85, 0.85))
        nodo_parcela.setShader(shader)

    def _generar_cuerpo_fisico(self, nodo_parcela, parcela, idx_pos):
        _rbody=BulletRigidBodyNode("cuerpo_suelo_%s"%parcela.nombre)
        for geom_node in nodo_parcela.findAllMatches("**/+GeomNode"):
            #logging.debug("geom? %s transform=%s"%(str(geom_node), str(geom_node.getTransform(nodo_parcela))))
            _tri_mesh=BulletTriangleMesh()
            _tri_mesh.addGeom(geom_node.node().getGeom(0))
            _shape=BulletTriangleMeshShape(_tri_mesh, dynamic=False)
            _rbody.addShape(_shape, geom_node.getTransform())
        _rbodyN=self.attachNewNode(_rbody)
        _rbodyN.setPos(Parcela.tamano*idx_pos[0]-Parcela.pos_offset, Parcela.tamano*idx_pos[1]-Parcela.pos_offset, self._ajuste_altura)
        _rbodyN.setCollideMask(BitMask32.bit(1))
        nodo_parcela.reparentTo(_rbodyN)
        parcela.establecer_optimizacion(True)
        parcela.generar()
        self.bullet_world.attachRigidBody(_rbody)
        log.debug("parcela cargada "+str(_rbodyN.getPos()))
        return _rbodyN

    def update(self):
        #
        idx_pos=self.obtener_indice_parcela_foco()
        if idx_pos!=self.idx_pos_parcela_actual:
            self.idx_pos_parcela_actual=idx_pos
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
            _p[1].actualizar()

    def dump_info(self):
        geom=self._parcelas[(0,0)][0].getChild(0).getChild(0).node().getGeom(0)
        return geom
