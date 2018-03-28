from panda3d.core import *
import os, os.path

import sistema, config
from shader import GestorShader

import logging
log=logging.getLogger(__name__)

#
#
# OBJETOS
#
#
class Objetos:

    #
    DirectorioCache="objetos"
    
    # lods por defecto
    LODs=((75.0, 0.0), (150.0, 75.0), (1000.0, 150.0))

    def __init__(self, base):
        # referencias:
        self.base=base
        self.sistema=None
        # componentes:
        self.nodo=self.base.render.attachNewNode("objetos")
        self.nodo_parcelas_vegetacion=None
        self.nodo_parcelas_yuyos=None
        self.parcelas={} # {idx_pos_lod:(parcela_vegetacion_node_path,parcela_yuyos_node_path),...} # {idx_pos:(parcela_vegetacion_node_path,parcela_yuyos_node_path),...}
        self.pool_modelos=dict() # {id:Model,...}; id="nombre_archivo" <- hashear!!!
        # variables externas:
        self.directorio_cache="cache/objetos"
        self.idx_pos_parcela_actual=None # (x,y)
        # variables internas
        self._lods=list()

    def iniciar(self):
        log.info("iniciar")
        # sistema
        self.sistema=sistema.obtener_instancia()
        #
        self.directorio_cache=os.path.join(self.sistema.directorio_general_cache, Objetos.DirectorioCache)
        if not os.path.exists(self.directorio_cache):
            log.warning("se crea directorio_cache: %s"%self.directorio_cache)
            os.mkdir(self.directorio_cache)
        # config
        for i_lod in range(len(Objetos.LODs)):
            config_lod=config.vallist("objetos.lod%i"%i_lod)
            lod=()
            if config_lod:
                lod=(float(config_lod[0]), float(config_lod[1]))
                log.debug("se carga lod de configuracion en indice %i %s"%(i_lod, str(lod)))
            else:
                lod=Objetos.LODs[i_lod]
                log.debug("se carga lod pos defecto en indice %i %s"%(i_lod, str(lod)))
            self._lods.append(lod)
        # db
        # self.pool_modelos
        self._iniciar_pool_modelos()
        #
        self.nodo_parcelas_vegetacion=self.nodo.attachNewNode("parcelas_vegetacion")
        self.nodo_parcelas_yuyos=self.nodo.attachNewNode("parcelas_yuyos")
        #self.nodo_parcelas_yuyos.node().adjustDrawMask(DrawMask(0), DrawMask(8), DrawMask(0))
        #
        self._establecer_shader()
        #
        self.base.accept("o-up", self._log_debug_info)

    def terminar(self):
        log.info("terminar")
        #
        self.base.ignore("o-up")
        #
        self.nodo.removeNode()
        self.nodo=None
        #
        self._terminar_pool_modelos()
        #
        self.sistema=None

    def obtener_info(self):
        info="Objetos\n"
        return info

    def _log_debug_info(self):
        texto=self.obtener_info()
        self.nodo.analyze()
        #self.nodo.ls()
        log.debug(texto)

    def update(self):
        if self.idx_pos_parcela_actual==self.sistema.idx_pos_parcela_actual:
            return
        self.idx_pos_parcela_actual=self.sistema.idx_pos_parcela_actual
        #
        log.debug("update")
        #
        parcelas_sistema=list(self.sistema.parcelas.keys())
        idxs_necesarias=list()
        idxs_cargar=list()
        idxs_descargar=list()
        #
        for idx in parcelas_sistema:
            # lod
            dx=abs(self.sistema.idx_pos_parcela_actual[0]-idx[0])
            dy=abs(self.sistema.idx_pos_parcela_actual[1]-idx[1])
            dist=dx if dx>dy else dy
            lod=0
            if dist>=2:
                lod=dist-1
                if lod>3:
                    lod=3
            #
            idx=(idx[0], idx[1], lod)
            idxs_necesarias.append(idx)
        #
        for idx in idxs_necesarias:
            if idx not in self.parcelas:
                idxs_cargar.append(idx)
        for idx in self.parcelas:
            if idx not in idxs_necesarias:
                idxs_descargar.append(idx)
        #
        for idx in idxs_cargar:
            self._generar_parcela(idx)
        for idx in idxs_descargar:
            self._descargar_parcela(idx)

    def _generar_parcela(self, idx):
        # posicion y nombre
        idx_pos, lod=(idx[0], idx[1]), idx[2]
        pos=self.sistema.obtener_pos_parcela(idx_pos)
        altitud_suelo=self.sistema.obtener_altitud_suelo(pos)
        nombre="parcela_objetos_%i_%i"%(int(idx_pos[0]), int(idx_pos[1]))
        log.info("_generar_parcela idx=%s pos=%s lod=%i nombre=%s"%(str(idx), str(pos), lod,  nombre))
        # datos de parcela
        datos_parcela=self.sistema.parcelas[idx_pos]
        # nodo vegetacion
        parcela_vegetacion_node_path=self.nodo_parcelas_vegetacion.attachNewNode("%s_vegetacion"%nombre)
        parcela_vegetacion_node_path.setPos(pos[0], pos[1], 0.0)
        # nodo yuyos
        parcela_yuyos_node_path=self.nodo_parcelas_yuyos.attachNewNode("%s_yuyos"%nombre)
        parcela_yuyos_node_path.setPos(pos[0], pos[1], 0.0)
        # lod vegetacion
        lod_vegetacion=LODNode("%s_vegetacion_lod"%nombre)
        lod_vegetacion_np=NodePath(lod_vegetacion) # reparentTo(self.nodo_parcelas_vegetacion)?!
        lod_vegetacion_np.reparentTo(parcela_vegetacion_node_path)
        lod_vegetacion_np.setPos(0.0, 0.0, altitud_suelo)
        # lod yuyos
        lod_yuyos=LODNode("%s_yuyos_lod"%nombre)
        lod_yuyos_np=NodePath(lod_yuyos)
        lod_yuyos_np.reparentTo(parcela_yuyos_node_path) # reparentTo(self.nodo_parcelas_yuyos)?!
        lod_yuyos_np.setPos(0.0, 0.0, altitud_suelo)
        # agregar a parcelas
        self.parcelas[idx]=(parcela_vegetacion_node_path, parcela_yuyos_node_path)
        # colocar objetos
        cntr_objs=0
        # nodos lod vegetacion
        concentradores_lod_vegetacion=list()
        for i_lod in range(len(self._lods)):
            lod_vegetacion.addSwitch(self._lods[i_lod][0], self._lods[i_lod][1])
            lod_vegetacion.setCenter(Vec3(sistema.Sistema.TopoTamanoParcela/2, sistema.Sistema.TopoTamanoParcela/2, 0.0))
            concentrador_lod=lod_vegetacion_np.attachNewNode("concentrador_lod%i_vegetacion"%i_lod)
            concentradores_lod_vegetacion.append(concentrador_lod)
        # nodos lod yuyos
        concentradores_lod_yuyos=list()
        for i_lod in range(len(self._lods)):
            lod_yuyos.addSwitch(self._lods[i_lod][0], self._lods[i_lod][1])
            lod_yuyos.setCenter(Vec3(sistema.Sistema.TopoTamanoParcela/2, sistema.Sistema.TopoTamanoParcela/2, 0.0))
            concentrador_lod=lod_yuyos_np.attachNewNode("concentrador_lod%i_yuyos"%i_lod)
            concentradores_lod_yuyos.append(concentrador_lod)
        #
        for fila in datos_parcela:
            for loc in fila:
                if not loc.datos_objeto:
                    continue
                concentradores_lod=None
                parcela_node_path=None
                if loc.datos_objeto[2]==sistema.Sistema.ObjetoTipoYuyo:
                    concentradores_lod=concentradores_lod_yuyos
                    parcela_node_path=parcela_yuyos_node_path
                else:
                    concentradores_lod=concentradores_lod_vegetacion
                    parcela_node_path=parcela_vegetacion_node_path
                #
                for i_lod in range(len(self._lods)):
                    if i_lod>0:
                        break
                    nombre_modelo="%s.lod%i"%(loc.datos_objeto[11], i_lod)
                    if nombre_modelo not in self.pool_modelos:
                        continue
                    instancia=concentradores_lod[i_lod].attachNewNode("copia_%s_%i"%(nombre_modelo, cntr_objs))
                    modelo=self.pool_modelos[nombre_modelo]
                    modelo.copyTo(instancia)
                    altitud_suelo=self.sistema.obtener_altitud_suelo(loc.posicion+loc.delta_pos)
                    instancia.setPos(parcela_node_path, loc.posicion_rel_parcela+loc.delta_pos)
                    instancia.setZ(parcela_node_path, altitud_suelo)
                    instancia.setHpr(loc.delta_hpr)
                    instancia.setScale(loc.delta_scl)
                    if i_lod>1:
                        instancia.setBillboardAxis()
                    #log.debug("se coloco un '%s' en posicion_rel_parcela=%s..."%(loc.datos_objeto[11], str(loc.posicion_rel_parcela)))
                    cntr_objs+=1
        #
        for concentrador_lod in concentradores_lod_vegetacion:
            pass#concentrador_lod.flattenStrong()
            #self._unificar_geometria(concentrador_lod)
        for concentrador_lod in concentradores_lod_yuyos:
            pass#concentrador_lod.flattenStrong()
            self._unificar_geometria(concentrador_lod)

    def _descargar_parcela(self, idx):
        log.info("_descargar_parcela %s"%str(idx))
        #
        parcela_vegetacion=self.parcelas[idx][0]
        parcela_yuyos=self.parcelas[idx][1]
        parcela_vegetacion.removeNode()
        parcela_yuyos.removeNode()
        del self.parcelas[idx]

    def _unificar_geometria(self, node_path):
        #
        geoms_consolidadas=dict() # {nombre:[Geom,vdata,prim,RenderState],...}
        sum_idxs=dict() # {nombre:cant,...}
        for objeto in node_path.findAllMatches("**/copia_*"):
            geom_nodes=objeto.findAllMatches("**/+GeomNode")
            for geom_node in geom_nodes:
                nombre=geom_node.getName()
                geom=geom_node.node().getGeom(0)
                if geom.getNumPrimitives()>1:
                    log.warning("_unificar_geometria %s num_prims=%i"%(nombre, geom.getNumPrimitives()))
                #
                if nombre not in geoms_consolidadas:
                    formato=geom.getVertexData().getFormat()
                    geoms_consolidadas[nombre]=list()
                    geoms_consolidadas[nombre].append(None)
                    geoms_consolidadas[nombre].append(GeomVertexData("vdata", formato, Geom.UHStatic))
                    geoms_consolidadas[nombre].append(GeomTriangles(Geom.UHStatic))
                    geoms_consolidadas[nombre].append(objeto.getState())
                    sum_idxs[nombre]=0
                #
                geom_consolidada=geoms_consolidadas[nombre]
                vdata=GeomVertexData(geom.getVertexData())
                #mat=LMatrix4f.rotateMatNormaxis(objeto.getH(), Vec3(0, 0, 1))
                mat=LMatrix4f.translateMat(objeto.getPos())#Vec3(14, 14, 0))
                #mat.transposeInPlace()
                log.debug("OBJ %s MAT %s"%(str(objeto.getPos()), str(mat)))
                vdata.transformVertices(mat)
                prim_vidxs=geom.getPrimitive(0).decompose().getVertexList()
                sum=0
                for i_row in range(vdata.getNumRows()):
                    geom_consolidada[1].copyRowFrom(sum_idxs[nombre]+i_row, vdata, i_row, Thread.getCurrentThread())
                    sum+=1
                for vidx in prim_vidxs:
                    geom_consolidada[2].addVertex(sum_idxs[nombre]+vidx)
                sum_idxs[nombre]+=sum
        #
        node_path.node().removeAllChildren()
        for nombre, data in geoms_consolidadas.items():
            data[0]=Geom(data[1])
            log.debug(str(data[1].getNumRows()))
            data[0].addPrimitive(data[2])
            geom_node=GeomNode(nombre)
            geom_node.addGeom(data[0])
            geom_node.setState(data[3])
            node_path.attachNewNode(geom_node)
        #
        return node_path

    def _establecer_shader(self):
        #
        #GestorShader.aplicar(self.nodo_parcelas_vegetacion, GestorShader.ClaseGenerico, 2)
        #GestorShader.aplicar(self.nodo_parcelas_yuyos, GestorShader.ClaseGenerico, 2)
        #
        self.nodo.setTwoSided(True)
        GestorShader.aplicar(self.nodo, GestorShader.ClaseGenerico, 2)

    def _iniciar_pool_modelos(self):
        log.info("_iniciar_pool_modelos")
        #
        if len(self.pool_modelos)>0:
            log.warning("pool_modelos ya iniciado")
            return
        #
        tablas=["objetos"]
        for tabla in tablas:
            log.info("tabla '%s'"%tabla)
            sql="SELECT * FROM %s"%tabla
            cursor=self.sistema.db.execute(sql)
            filas=cursor.fetchall()
            for fila in filas:
                #if fila[11]=="yuyo":
                #    continue
                ids_modelos=list()
                for i_lod in range(len(self._lods)):
                    ids_modelos.append("%s.lod%i"%(fila[11], i_lod))
                    ruta_archivo_modelo=os.path.join("objetos", "%s.egg"%ids_modelos[i_lod])
                    if i_lod==0:
                        if not os.path.exists(ruta_archivo_modelo):
                            ruta_archivo_modelo=os.path.join("objetos", "%s.egg"%fila[11])
                    if not os.path.exists(ruta_archivo_modelo):
                        continue
                    if not ids_modelos[i_lod] in self.pool_modelos:
                        log.info("-cargar %s"%ruta_archivo_modelo)
                        modelo=self.base.loader.loadModel(ruta_archivo_modelo)
                        modelo.clearModelNodes()
                        self.pool_modelos[ids_modelos[i_lod]]=modelo

    def _terminar_pool_modelos(self):
        log.info("_terminar_pool_modelos")
        for id, modelo in self.pool_modelos.items():
            modelo.removeNode()
        for id in [id for id in self.pool_modelos.keys()]:
            del self.pool_modelos[id]

