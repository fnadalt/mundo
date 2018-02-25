from panda3d.core import *
import sqlite3
import csv
import os, os.path

from sistema import *
from shader import GestorShader

import logging
log=logging.getLogger(__name__)

#
#
# OBJETOS
#
#
class Objetos:

    # ambiente
    AmbienteNulo=0
    AmbienteSubacuatico=1
    AmbienteTerrestre=2

    # tipos de objeto
    TipoObjetoNulo=0
    TipoObjetoArbol=1
    TipoObjetoArbusto=2
    TipoObjetoPlanta=3
    TipoObjetoYuyo=4
    TipoObjetoRocaPequena=5
    TipoObjetoRocaMediana=6
    TipoObjetoRocaGrande=7

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
    ParamsRuido=[16.0, 345]

    def __init__(self, base):
        # referencias:
        self.base=base
        self.sistema=None
        # componentes:
        self.nodo=self.base.render.attachNewNode("objetos")
        self.nodo_parcelas=self.nodo.attachNewNode("parcelas")
        #self.nodo.setRenderModeWireframe()
        self.parcelas={} # {idx_pos:parcela_node_path,...}
        self.db=None
        self.pool_modelos=dict() # {id:Model,...}; id="nombre_archivo" <- hashear!!!
        self.ruido_perlin=PerlinNoise2(Objetos.ParamsRuido[0], Objetos.ParamsRuido[0], 256, Objetos.ParamsRuido[1])
        # variables externas:
        self.idx_pos_parcela_actual=None # (x,y)

    def iniciar(self):
        log.info("iniciar")
        # sistema
        self.sistema=obtener_instancia()
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
        #log.debug("idx_pos=%s"%(str(idx_pos)))
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
        nombre="parcela_objetos_%i_%i"%(int(idx_pos[0]), int(idx_pos[1]))
        log.info("_generar_parcela idx_pos=%s pos=%s nombre=%s"%(str(idx_pos), str(pos), nombre))
        # nodo
        parcela_node_path=self.nodo_parcelas.attachNewNode(nombre)
        parcela_node_path.setPos(pos[0], pos[1], 0.0)
        # datos de parcela
        datos_parcela=self._generar_datos_parcela(pos, idx_pos)
        #
        # agregar a parcelas
        self.parcelas[idx_pos]=parcela_node_path

    def _descargar_parcela(self, idx_pos):
        log.info("_descargar_parcela %s"%str(idx_pos))
        #
        parcela=self.parcelas[idx_pos]
        parcela.removeNode()
        del self.parcelas[idx_pos]

    def _generar_datos_parcela(self, pos, idx_pos):
        # indices
        # grilla de datos
        datos=list()
        for x in range(sistema.Sistema.TamanoParcela+2): # +/- 1
            fila=list()
            for y in range(sistema.Sistema.TamanoParcela+2):
                pass
            datos.append(fila)
        #
        return datos

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
                if fila[11] in self.pool_modelos:
                    continue
                ruta_archivo_modelo=os.path.join("objetos", "%s.egg"%fila[11])
                log.info("-cargar %s"%ruta_archivo_modelo)
                modelo=self.base.loader.loadModel(ruta_archivo_modelo)
                self.pool_modelos[fila[11]]=modelo

    def _terminar_pool_modelos(self):
        log.info("_terminar_pool_modelos")
        for id, modelo in self.pool_modelos.items():
            modelo.removeNode()
        for id in [id for id in self.pool_modelos.keys()]:
            del self.pool_modelos[id]
