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
        self.parcelas={} # {idx_pos_lod:parcela_node_path,...} # {idx_pos:(parcela_vegetacion_node_path,parcela_yuyos_node_path),...}
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
        log.debug(texto)
        self.nodo.analyze()
        #self.nodo.ls()

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
        nombre="parcela_objetos_%i_%i_lod%i"%(int(idx_pos[0]), int(idx_pos[1]), lod)
        log.info("_generar_parcela idx=%s pos=%s lod=%i nombre=%s"%(str(idx), str(pos), lod,  nombre))
        # datos de parcela
        datos_parcela=self.sistema.parcelas[idx_pos]
        #
        ruta_archivo_cache=os.path.join(self.directorio_cache, "%s.bam"%nombre)
        if os.path.exists(ruta_archivo_cache):
            log.info("cargar desde cache <- %s"%ruta_archivo_cache)
            parcela_node_path=self.base.loader.loadModel(ruta_archivo_cache)
            parcela_node_path.reparentTo(self.nodo)
            parcela_node_path.setPos(pos[0], pos[1], 0.0)
        else:
            # nodo
            parcela_node_path=self.nodo.attachNewNode("%s"%nombre)
            parcela_node_path.setPos(pos[0], pos[1], 0.0)
            # lod
            lod=LODNode("%s_lod"%nombre)
            lod_np=NodePath(lod)
            lod_np.reparentTo(parcela_node_path)
            lod_np.setPos(0.0, 0.0, altitud_suelo)
            # colocar objetos
            cntr_objs=0
            # unificadores
            unificadores=[None for i_lod in range(len(self._lods))]
            # nodos lod vegetacion
            concentradores_lod=list()
            for i_lod in range(len(self._lods)):
                lod.addSwitch(self._lods[i_lod][0], self._lods[i_lod][1])
                lod.setCenter(Vec3(sistema.Sistema.TopoTamanoParcela/2, sistema.Sistema.TopoTamanoParcela/2, 0.0))
                concentrador_lod=lod_np.attachNewNode("concentrador_lod%i"%i_lod)
                concentradores_lod.append(concentrador_lod)
                if i_lod>=0: # !!!
                    unificadores[i_lod]=Unificador(concentrador_lod)
            #
            for fila in datos_parcela:
                for loc in fila:
                    if not loc.datos_objeto:
                        continue
                    #
                    for i_lod in range(len(self._lods)):
                        if i_lod>0:
                            pass#break
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
                        if unificadores[i_lod]:
                            unificadores[i_lod].agregar_objeto(loc.datos_objeto[11], instancia, modelo)
                        if i_lod>1:
                            instancia.setBillboardAxis()
                        #log.debug("se coloco un '%s' en posicion_rel_parcela=%s..."%(loc.datos_objeto[11], str(loc.posicion_rel_parcela)))
                        cntr_objs+=1
            #
            [u.ejecutar() for u in unificadores]
            #
            log.info("generar por primera vez -> %s"%ruta_archivo_cache)
            parcela_node_path.writeBamFile(ruta_archivo_cache)
        # agregar a parcelas
        self.parcelas[idx]=parcela_node_path

    def _descargar_parcela(self, idx):
        log.info("_descargar_parcela %s"%str(idx))
        #
        parcela=self.parcelas[idx]
        parcela.removeNode()
        del self.parcelas[idx]

    def _establecer_shader(self):
        #
        self.nodo.setTwoSided(True)
        GestorShader.aplicar(self.nodo, GestorShader.ClaseVegetacion, 2)

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


#
#
# Unificador
#
#
class Unificador:
    
    def __init__(self, node_path):
        self.node_path=node_path
        self.clases=dict() # {nombre_clase:{nombre_geom:[Geom,vata,prim,RenderState,sum_idxs],...},...}
    
    def agregar_objeto(self, nombre_clase, objeto, modelo):
        # recolectar GeomNodes
        geom_nodes=modelo.findAllMatches("**/+GeomNode")
        # asegurar estructura de datos de clase
        if nombre_clase not in self.clases:
            clase=dict()
            self.clases[nombre_clase]=clase
            for geom_node in geom_nodes:
                nombre_geom=geom_node.getName()
                geom=geom_node.node().getGeom(0)
                formato=geom.getVertexData().getFormat()
                clase[nombre_geom]=list()
                clase[nombre_geom].append(None)
                clase[nombre_geom].append(GeomVertexData("vdata", formato, Geom.UHStatic))
                clase[nombre_geom].append(GeomTriangles(Geom.UHStatic))
                clase[nombre_geom].append(geom_node.node().getGeomState(0))
                #clase[nombre_geom].append(RenderState.makeEmpty())
                clase[nombre_geom].append(0)
        # llenar vdatas y primitivas
        clase=self.clases[nombre_clase]
        for geom_node in geom_nodes:
            nombre=geom_node.getName()
            geom=geom_node.node().getGeom(0)
            if geom.getNumPrimitives()>1:
                log.warning("agregar_objeto %s num_prims=%i"%(nombre, geom.getNumPrimitives()))
            #
            vdata=GeomVertexData(geom.getVertexData())
            mat=LMatrix4f.rotateMat(objeto.getH(), Vec3(0, 0, 1), CS_zup_right)
            mat*=LMatrix4f.rotateMat(objeto.getP(), Vec3(1, 0, 0), CS_zup_right)
            mat*=LMatrix4f.rotateMat(objeto.getR(), Vec3(0, 1, 0), CS_zup_right)
            mat*=LMatrix4f.scaleMat(objeto.getScale())
            mat*=LMatrix4f.translateMat(objeto.getPos())
            vdata.transformVertices(mat)
            prim_vidxs=geom.getPrimitive(0).decompose().getVertexList()
            sum=0
            for i_row in range(vdata.getNumRows()):
                clase[nombre][1].copyRowFrom(clase[nombre][4]+i_row, vdata, i_row, Thread.getCurrentThread())
                sum+=1
            for vidx in prim_vidxs:
                clase[nombre][2].addVertex(clase[nombre][4]+vidx)
            clase[nombre][4]+=sum
    
    def ejecutar(self):
        self.node_path.node().removeAllChildren()
        for nombre_clase, data_clase in self.clases.items():
            for nombre_geom, data_geom in data_clase.items():
                geom_node=GeomNode("%s_%s"%(nombre_clase, nombre_geom))
                data_geom[0]=Geom(data_geom[1])
                data_geom[0].addPrimitive(data_geom[2])
                geom_node.addGeom(data_geom[0])
                geom_node.setState(data_geom[3])
                self.node_path.attachNewNode(geom_node)
        return self.node_path

