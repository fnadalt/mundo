from panda3d.core import *
import sqlite3
import pickle, csv
import os, os.path
import random

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
    
    # tipos de objeto
    TipoObjetoNulo=0
    TipoObjetoArbol=1
    TipoObjetoArbusto=2
    TipoObjetoPlanta=3
    TipoObjetoYuyo=4
    TipoObjetoRocaPequena=5
    TipoObjetoRocaMediana=6
    TipoObjetoRocaGrande=7

    # radio maximo
    RadioMaximoInferior=1
    RadioMaximoSuperior=3

    # lods por defecto
    LODs=((75.0, 0.0), (150.0, 75.0), (1000.0, 150.0))

    # db
    NombreArchivoDB="objetos.sql"
    NombreArchivoLlenadoDB="objetos.csv"
    SqlCreacionDB="""
    DROP TABLE IF EXISTS objetos;
    CREATE TABLE objetos (_id INTEGER PRIMARY KEY, 
                          ambiente INTEGER, 
                          tipo INTEGER, 
                          densidad FLOAT, 
                          radio_inferior FLOAT, 
                          radio_superior FLOAT, 
                          terreno INTEGER,
                          temperatura_minima FLOAT, 
                          temperatura_maxima FLOAT, 
                          precipitacion_minima FLOAT, 
                          precipitacion_maxima FLOAT, 
                          nombre_archivo VARCHAR(32)
                         );
    """

    # ruido de distribucion de objetos
    ParamsRuido=[32.0, 345]

    def __init__(self, base):
        # referencias:
        self.base=base
        self.sistema=None
        # componentes:
        self.nodo=self.base.render.attachNewNode("objetos")
        self.nodo_parcelas=self.nodo.attachNewNode("parcelas")
        self.parcelas={} # {idx_pos:parcela_node_path,...}
        self.db=None
        self.pool_modelos=dict() # {id:Model,...}; id="nombre_archivo" <- hashear!!!
        self.ruido_perlin=PerlinNoise2(Objetos.ParamsRuido[0], Objetos.ParamsRuido[0], 256, Objetos.ParamsRuido[1])
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
        self.directorio_cache=os.path.join(self.sistema.directorio_cache, Objetos.DirectorioCache)
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
        self._iniciar_db()
        # self.pool_modelos de modelos
        self._iniciar_pool_modelos()
        #
        self._establecer_shader()

    def terminar(self):
        log.info("terminar")
        #
        self.nodo.removeNode()
        self.nodo=None
        #
        self._terminar_pool_modelos()
        self._terminar_db()
        #
        self.sistema=None

    def obtener_info(self):
        info="Objetos\n"
        return info

    def update(self, forzar=False):
        #
        idx_pos=self.sistema.obtener_indice_parcela(self.sistema.posicion_cursor)
        log.debug("idx_pos=%s"%(str(idx_pos)))
        if forzar or idx_pos!=self.idx_pos_parcela_actual:
            self.idx_pos_parcela_actual=idx_pos
            #
            idxs_pos_parcelas_obj=[]
            idxs_pos_parcelas_cargar=[]
            idxs_pos_parcelas_descargar=[]
            # determinar parcelas que deben estar cargadas
            for idx_pos_x in range(idx_pos[0]-self.sistema.radio_expansion_parcelas, idx_pos[0]+self.sistema.radio_expansion_parcelas+1):
                for idx_pos_y in range(idx_pos[1]-self.sistema.radio_expansion_parcelas, idx_pos[1]+self.sistema.radio_expansion_parcelas+1):
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
        # posicion y nombre
        pos=self.sistema.obtener_pos_parcela(idx_pos)
        altitud_suelo=self.sistema.obtener_altitud_suelo(pos)
        nombre="parcela_objetos_%i_%i"%(int(idx_pos[0]), int(idx_pos[1]))
        log.info("_generar_parcela idx_pos=%s pos=%s nombre=%s"%(str(idx_pos), str(pos), nombre))
        # nodo
        parcela_node_path=self.nodo_parcelas.attachNewNode(nombre)
        parcela_node_path.setPos(pos[0], pos[1], 0.0)
        # datos de parcela
        ruta_archivo_cache=os.path.join(self.directorio_cache, "%s.bin"%nombre)
        datos_parcela=None
        if not os.path.exists(ruta_archivo_cache):
            log.info(" generar parcela por primera vez -> %s"%ruta_archivo_cache)
            datos_parcela=self._generar_datos_parcela(pos, idx_pos)
            with open(ruta_archivo_cache, "wb") as arch:
                pickle.dump(datos_parcela, arch)
        else:
            log.info(" cargar parcela desde cache <- %s"%ruta_archivo_cache)
            with open(ruta_archivo_cache, "rb") as arch:
                datos_parcela=pickle.load(arch)
        # lod
        lod=LODNode("%s_lod"%nombre)
        lod_np=NodePath(lod)
        lod_np.reparentTo(parcela_node_path)
        lod_np.setPos(0.0, 0.0, altitud_suelo)
        # colocar objetos
        cntr_objs=0
        concentradores_lod=list()
        for i_lod in range(len(self._lods)):
            lod.addSwitch(self._lods[i_lod][0], self._lods[i_lod][1])
            concentrador_lod=lod_np.attachNewNode("concentrador_lod%i"%i_lod)
            concentrador_lod.setTwoSided(True) # aqui? asi?
            concentradores_lod.append(concentrador_lod)
        for fila in datos_parcela:
            for d in fila:
                if not d.datos_objeto:
                    continue
                #log.debug(d)
                for i_lod in range(len(self._lods)):
                    nombre_modelo="%s.lod%i"%(d.datos_objeto[11], i_lod)
                    if nombre_modelo not in self.pool_modelos:
                        continue
                    instancia=concentradores_lod[i_lod].attachNewNode("instancia_%s_%i_lod%i"%(nombre_modelo, cntr_objs, i_lod))
                    if i_lod>0:
                        instancia.setBillboardAxis()
                    modelo=self.pool_modelos[nombre_modelo]
                    modelo.instanceTo(instancia)
                    if i_lod==0: #if not instancia.hasBillboard():
                        d.generar_deltas()
                        altitud_suelo=self.sistema.obtener_altitud_suelo(d.posicion_global+d.delta_pos)
                        instancia.setPos(parcela_node_path, d.posicion_parcela+d.delta_pos)
                        instancia.setZ(parcela_node_path, altitud_suelo)
                        instancia.setHpr(d.delta_hpr)
                        instancia.setScale(d.delta_scl)
                    else:
                        instancia.setPos(parcela_node_path, d.posicion_parcela)
                    #log.debug("se coloco un '%s' en posicion_parcela=%s..."%(d.datos_objeto[11], str(d.posicion_parcela)))
                    cntr_objs+=1
        # flattenStrong()?
        parcela_node_path.flattenStrong()
        # agregar a parcelas
        self.parcelas[idx_pos]=parcela_node_path

    def _descargar_parcela(self, idx_pos):
        log.info("_descargar_parcela %s"%str(idx_pos))
        #
        parcela=self.parcelas[idx_pos]
        parcela.removeNode()
        del self.parcelas[idx_pos]

    def _generar_datos_parcela(self, pos, idx_pos):
        random.seed(Objetos.ParamsRuido[1])
        # obtener informacion de terreno
        cantidad_total_locaciones=sistema.Sistema.TopoTamanoParcela**2
        indexado_objetos=dict() # {ambiente:{tipo_terreno:GrupoObjetosLocaciones,...},...}
        datos_locales=list()
        ambientes=list()
        tipos_terreno=list()
        temperatura_minima, temperatura_maxima=1.0, 0.0
        precipitacion_minima, precipitacion_maxima=1.0, 0.0
        for x in range(sistema.Sistema.TopoTamanoParcela):
            fila=list()
            for y in range(sistema.Sistema.TopoTamanoParcela):
                _pos_parcela=Vec3(x, y, 0.0)
                _pos_global=Vec3(pos[0], pos[1], 0.0)+_pos_parcela
                # altitud suelo
                altitud_suelo=self.sistema.obtener_altitud_suelo(_pos_global)
                _pos_parcela.setZ(altitud_suelo)
                _pos_global.setZ(altitud_suelo)
                # ambiente
                ambiente=self.sistema.obtener_ambiente(_pos_global, altitud_suelo)
                if ambiente not in ambientes:
                    ambientes.append(ambiente)
                if ambiente not in indexado_objetos.keys():
                    #log.debug("agregando indexado_objetos[%i]"%ambiente)
                    indexado_objetos[ambiente]=dict()
                # tipo terreno
                tipo_terreno0, tipo_terreno1, factor_transicion=self.sistema.obtener_tipo_terreno(_pos_global)
                tipo_terreno=tipo_terreno0 if factor_transicion<0.5 else tipo_terreno1
                if not tipo_terreno in tipos_terreno:
                    tipos_terreno.append(tipo_terreno)
                if not tipo_terreno in indexado_objetos[ambiente]:
                    #log.debug("agregando indexado_objetos[%i][%i]"%(ambiente, tipo_terreno))
                    indexado_objetos[ambiente][tipo_terreno]=GrupoObjetosLocaciones(cantidad_total_locaciones)
                # temperatura anual media
                tam=self.sistema.obtener_temperatura_anual_media_norm(_pos_global, altitud_suelo)
                if tam<temperatura_minima:
                    temperatura_minima=tam
                if tam>temperatura_maxima:
                    temperatura_maxima=tam
                # precipitacion frecuencia anual
                prec_f=self.sistema.obtener_precipitacion_frecuencia_anual(_pos_global)
                if prec_f<precipitacion_minima:
                    precipitacion_minima=prec_f
                if prec_f>precipitacion_maxima:
                    precipitacion_maxima=prec_f
                #
                d=DatosLocalesObjetos(_pos_global, _pos_parcela, ambiente, tipo_terreno)
                d.factor_ruido=self.ruido_perlin(_pos_global[0], _pos_global[1])
                fila.append(d)
                indexado_objetos[ambiente][tipo_terreno].locaciones_disponibles.append(d)
            datos_locales.append(fila)
        # obtener tipos de objeto segun datos de terreno
        condicion_ambientes="(%s)"%(" OR ".join(["ambiente=%i"%amb for amb in ambientes]))
        condicion_tipos_terreno="(%s)"%(" OR ".join(["terreno=%i"%tipo for tipo in tipos_terreno]))
        condicion_temperatura=("(temperatura_minima<=%.2f AND temperatura_maxima>=%.2f)"%(temperatura_minima, temperatura_maxima))
        condicion_precipitacion=("(precipitacion_minima<=%.2f AND precipitacion_maxima>=%.2f)"%(precipitacion_minima, precipitacion_maxima))
        condiciones="%s AND %s AND %s AND %s"%(condicion_ambientes, condicion_tipos_terreno, condicion_temperatura, condicion_precipitacion)
        sql="SELECT * FROM objetos WHERE %(condiciones)s ORDER BY radio_superior DESC, densidad ASC"%{"condiciones":condiciones}
        #log.debug(sql)
        try:
            db_cursor=self.db.execute(sql)
        except Exception as e:
            log.exception(str(e))
            return list()
        filas_tipos_objeto=db_cursor.fetchall()
        #log.debug(str(filas_tipos_objeto))
        # distribuir los tipos de objeto segun datos de terreno
        for fila in filas_tipos_objeto:
            ambiente=fila[1]
            tipo_terreno=fila[6]
            #log.debug("solicitar indexado_objetos[%i][%i]"%(ambiente, tipo_terreno))
            try:
                grupo_objetos_locaciones=indexado_objetos[ambiente][tipo_terreno]
                grupo_objetos_locaciones.tipos_objeto.append(fila)
            except Exception as e:
                log.exception("tipo_objeto no posicionable en indexado_objetos[%i][%i] %s Mensaje: %s"%(ambiente, tipo_terreno, str(fila), str(e)))
                pass
        # recolectar grupos_objetos_locaciones
        grupos_objetos_locaciones=list()
        for ambiente in sorted(indexado_objetos.keys()):
            for tipo_terreno in sorted(indexado_objetos[ambiente].keys()):
                grupo_objetos_locaciones=indexado_objetos[ambiente][tipo_terreno]
                if len(grupo_objetos_locaciones.tipos_objeto)==0:
                    continue
                grupos_objetos_locaciones.append(grupo_objetos_locaciones)
        # realizar operaciones pertinentes sobre grupos_objetos_locaciones
        for grupo_objetos_locaciones in grupos_objetos_locaciones:
            grupo_objetos_locaciones.ordenar_locaciones_disponibles()
            grupo_objetos_locaciones.determinar_cantidades_tipos_objeto()
            #log.debug(str(grupo_objetos_locaciones))
            for tipo_objeto in grupo_objetos_locaciones.tipos_objeto:
                cant_obj_remanentes=grupo_objetos_locaciones.cantidades_tipos_objeto[tipo_objeto[2]]
                #log.debug("colocar %i objetos '%s' en ambiente=%i y tipo_terreno=%i"%(cant_obj_remanentes, tipo_objeto[11], tipo_objeto[1], tipo_objeto[6]))
                for d in grupo_objetos_locaciones.locaciones_disponibles:
                    if cant_obj_remanentes>0 and \
                       self._chequear_espacio_disponible(d.posicion_parcela, tipo_objeto[4], tipo_objeto[5], datos_locales):
                        cant_obj_remanentes-=1
                        #log.debug("hay espacio disponible, colocar en d=%s. quedan %i"%(str(d), cant_obj_remanentes))
                        d.datos_objeto=tipo_objeto
        #
        return datos_locales

    def _obtener_vecino(self, datos_locales, posicion_parcela, dx, dy):
        if (posicion_parcela[0]==0 and dx<0) or \
           (posicion_parcela[0]==(len(datos_locales[0])-1) and dx>0) or \
           (posicion_parcela[1]==0 and dy<0) or \
           (posicion_parcela[1]==(len(datos_locales[1])-1) and dy>0):
               return None
        return datos_locales[int(posicion_parcela[0])+dx][int(posicion_parcela[1])+dy]

    def _chequear_espacio_disponible(self, _pos_parcela, radio_inferior, radio_superior, datos_locales):
        radio_maximo=radio_superior if radio_superior>radio_inferior else radio_inferior
        # distancia del borde de parcela
        if abs(_pos_parcela[0]-sistema.Sistema.TopoTamanoParcela)<radio_maximo or \
           abs(_pos_parcela[1]-sistema.Sistema.TopoTamanoParcela)<radio_maximo:
               return False
        #
        #radio_maximo_total_inferior=Objetos.RadioMaximoInferior+radio_inferior
        radio_maximo_total_superior=Objetos.RadioMaximoSuperior+radio_superior
        for dx in range(round(radio_maximo_total_superior)):
            for dy in range(round(radio_maximo_total_superior)):
                #
                vecinos=list()
                vecinos.append(self._obtener_vecino(datos_locales, _pos_parcela, -1, -1))
                vecinos.append(self._obtener_vecino(datos_locales, _pos_parcela,  0, -1))
                vecinos.append(self._obtener_vecino(datos_locales, _pos_parcela,  1, -1))
                vecinos.append(self._obtener_vecino(datos_locales, _pos_parcela, -1,  0))
                vecinos.append(self._obtener_vecino(datos_locales, _pos_parcela,  1,  0))
                vecinos.append(self._obtener_vecino(datos_locales, _pos_parcela, -1,  1))
                vecinos.append(self._obtener_vecino(datos_locales, _pos_parcela,  0,  1))
                vecinos.append(self._obtener_vecino(datos_locales, _pos_parcela,  1,  1))
                #
                for vecino in vecinos:
                    if not vecino:
                        continue
                    datos_objeto=vecino.datos_objeto
                    if not datos_objeto:
                        continue
                    radio_inferior_vecino=datos_objeto[4]
                    radio_superior_vecino=datos_objeto[5]
                    #log.debug("_chequear_espacio_disponible: radios_maximos_totales(i/s)=(%.1f,%.1f) \n candidato _pos_parcela=%s radios(i/s)=(%.1f,%.1f)\n vecino _pos_parcela=%s radios(i/s)=(%.1f,%.1f)" \
                    #          %(0.0, radio_maximo_total_superior,  \
                    #            str(_pos_parcela), radio_inferior, radio_superior, \
                    #            str(vecino.posicion_parcela), radio_inferior_vecino, radio_superior_vecino))
                    dmax=dx if dx>dy else dy
                    radios_inferiores=(radio_inferior+radio_inferior_vecino)
                    if dmax>(radios_inferiores):
                    #    log.debug("False\n")
                        return False
                    elif radio_superior>0.0:
                        radios_superiores=(radio_superior+radio_superior_vecino)
                        if dmax>(radios_superiores):
                    #        log.debug("False\n")
                            return False
        #
        #log.debug("True\n")
        return True
        

    def _establecer_shader(self):
        #
        GestorShader.aplicar(self.nodo_parcelas, GestorShader.ClaseGenerico, 2)

    def _iniciar_db(self):
        log.info("_iniciar_db")
        #
        if self.db!=None:
            log.warning("base de datos ya iniciada")
            return
        #
        if os.path.exists(Objetos.NombreArchivoDB):
            log.warning("se elimina el archivo de base de datos %s"%Objetos.NombreArchivoDB)
            os.remove(Objetos.NombreArchivoDB)
        #
        if not os.path.exists(Objetos.NombreArchivoDB):
            if not os.path.exists(Objetos.NombreArchivoLlenadoDB):
                raise Exception("no se encuentra el archivo %s"%Objetos.NombreArchivoLlenadoDB)
            #
            log.info("crear base de datos en archivo %s"%Objetos.NombreArchivoDB)
            con=sqlite3.connect(Objetos.NombreArchivoDB)
            con.executescript(Objetos.SqlCreacionDB)
            con.commit()
            #
            log.info("abrir archivo %s"%Objetos.NombreArchivoLlenadoDB)
            with open(Objetos.NombreArchivoLlenadoDB, "r") as archivo_csv:
                lector_csv=csv.DictReader(archivo_csv)
                for fila in lector_csv:
                    sql="INSERT INTO %s (ambiente,tipo,densidad,radio_inferior,radio_superior,terreno,temperatura_minima,temperatura_maxima,precipitacion_minima,precipitacion_maxima,nombre_archivo) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,'%s')" \
                       %(fila["tabla"], fila["ambiente"], fila["tipo"], fila["densidad"], \
                         fila["radio_inferior"], fila["radio_superior"], fila["terreno"], fila["temperatura_minima"], \
                         fila["temperatura_maxima"], fila["precipitacion_minima"], fila["precipitacion_maxima"], \
                         fila["nombre_archivo"])
                    con.execute(sql)
            con.commit()
            con.close()
            log.info("base de datos creada con exito")
            #
        #
        log.info("abrir db %s"%Objetos.NombreArchivoDB)
        self.db=sqlite3.connect(Objetos.NombreArchivoDB)
        log.info("conexion de datos establecida")
    #
    def _terminar_db(self):
        log.info("_terminar_db")
        if self.db==None:
            log.warning("base de datos no iniciada")
            return
        self.db.close()
        self.db=None

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
            cursor=self.db.execute(sql)
            filas=cursor.fetchall()
            for fila in filas:
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
                        self.pool_modelos[ids_modelos[i_lod]]=modelo

    def _terminar_pool_modelos(self):
        log.info("_terminar_pool_modelos")
        for id, modelo in self.pool_modelos.items():
            modelo.removeNode()
        for id in [id for id in self.pool_modelos.keys()]:
            del self.pool_modelos[id]

#
#
# DATOS LOCALES DE OBJETOS
#
#
class DatosLocalesObjetos:
    
    def __init__(self, posicion_global, posicion_parcela, ambiente, tipo_terreno):
        self.posicion_global=posicion_global
        self.posicion_parcela=posicion_parcela
        self.ambiente=ambiente
        self.tipo_terreno=tipo_terreno
        self.datos_objeto=None
        self.factor_ruido=0.0
        self.delta_pos=Vec3(0.0, 0.0, 0.0)
        self.delta_hpr=Vec3(0.0, 0.0, 0.0)
        self.delta_scl=Vec3(0.0, 0.0, 0.0)
    
    def generar_deltas(self):
        self.delta_pos.setX(0.75*(random.random()*2.0-1.0))
        self.delta_pos.setY(0.75*(random.random()*2.0-1.0))
        self.delta_hpr.setX(180.0*(random.random()*2.0-1.0))
        self.delta_hpr.setY(3.50*(random.random()*2.0-1.0))
        self.delta_scl.setX(0.85+0.15*random.random())
        self.delta_scl.setY(0.85+0.15*random.random())
        self.delta_scl.setZ(0.75+0.25*random.random())
        #log.debug("generar_deltas dpos=%s dhpr=%s dscl=%s"%(str(self.delta_pos), str(self.delta_hpr), str(self.delta_scl)))
    
    def __str__(self):
        return "DatosLocalesObjetos: _pg=%s _pp=%s a=%i t=%i fr=%.3f %s" \
                %(str(self.posicion_global), str(self.posicion_parcela), self.ambiente, self.tipo_terreno, self.factor_ruido, str(self.datos_objeto))

#
#
# GRUPO OBJETOS LOCACIONES
#
#
class GrupoObjetosLocaciones:
    
    def __init__(self, cantidad_total_locaciones):
        self.cantidad_total_locaciones=cantidad_total_locaciones
        self.tipos_objeto=list() # [fila,...]
        self.locaciones_disponibles=list() # [DatosLocalesObjetos,...]
        self.cantidades_tipos_objeto=dict() # {tipo_objeto:n,...}
    
    def __str__(self):
        return "GrupoObjetosLocaciones:\ntipos_objeto:%s\nlocaciones_disponibles:%s\ncantidades_tipos_objeto:%s\n" \
                %(str(self.tipos_objeto), str(["%s\n"%str(loc) for loc in self.locaciones_disponibles]), str(self.cantidades_tipos_objeto))
    
    def ordenar_locaciones_disponibles(self):
        self.locaciones_disponibles.sort(key=lambda x:x.factor_ruido)

    def determinar_cantidades_tipos_objeto(self):
        cantidad_tipos_objeto=len(self.tipos_objeto)
        cantidad_locaciones_disponibles=len(self.locaciones_disponibles)
        #log.debug("determinar_cantidades_tipos_objeto cantidad_tipos_objeto=%i cantidad_locaciones_disponibles=%i cantidad_total_locaciones=%i" \
        #        %(cantidad_tipos_objeto, cantidad_locaciones_disponibles, self.cantidad_total_locaciones))
        for fila in self.tipos_objeto:
            tipo_objeto=fila[2]
            densidad=fila[3]/cantidad_tipos_objeto
            cantidad=densidad*cantidad_locaciones_disponibles#(self.cantidad_total_locaciones/cantidad_locaciones_disponibles)#cantidad_locaciones_disponibles/self.cantidad_total_locaciones)
            if tipo_objeto in self.cantidades_tipos_objeto:
                log.error("el tipo de objeto %i ya se encuentra en self.cantidades_tipos_objeto"%tipo_objeto)
                continue
            #log.debug("cantidad de objetos '%s' a colocar: %i"%(fila[11], cantidad))
            self.cantidades_tipos_objeto[tipo_objeto]=int(cantidad)
