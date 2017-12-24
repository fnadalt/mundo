from panda3d.core import *
import sqlite3
import csv
import os, os.path
import random

import logging
log=logging.getLogger(__name__)

#
#
# GLOBAL
#
#
def terminar():
    log.info("terminar")
    terminar_pool_modelos()
    cerrar_db()

#
#
# DB
#
#
conexion_db=None
NombreArchivoDB="objetos.sql"
NombreArchivoLlenadoDB="objetos.csv"
# objetos segun parametros climaticos (temperatura_base, altitud).
#  rangos temperatura_base [0,1], cada 0.2 (5 grupos) [0,4].
#  rangos altitud [0,altura_maxima_terreno], cada 10% (10 grupos) [0,9].
#  se conforman asi un total de 50 grupos.
# distinta densidad de objetos segun grupo y tipo de objeto.
#  densidad [0,1); se usara como umbral en el ruido Perlin.
SqlCreacionDB="""
DROP TABLE IF EXISTS naturaleza;
CREATE TABLE naturaleza (_id INTEGER PRIMARY KEY, gpo_altitud INTEGER, gpo_temp_base INTEGER, tipo INTEGER, densidad FLOAT, radio_inferior FLOAT, radio_superior FLOAT, nombre_archivo VARCHAR(32));
"""
#
def iniciar_db():
    global conexion_db
    if conexion_db!=None:
        return
    #
    log.info("iniciar_db")
    #
    if not os.path.exists(NombreArchivoDB):
        if not os.path.exists(NombreArchivoLlenadoDB):
            raise Exception("no se encuentra el archivo %s"%NombreArchivoLlenadoDB)
        #
        log.info("crear base de datos en archivo %s"%NombreArchivoDB)
        con=sqlite3.connect(NombreArchivoDB)
        con.executescript(SqlCreacionDB)
        con.commit()
        #
        log.info("abrir archivo %s"%NombreArchivoLlenadoDB)
        with open(NombreArchivoLlenadoDB, "r") as archivo_csv:
            lector_csv=csv.DictReader(archivo_csv)
            for fila in lector_csv:
                sql="INSERT INTO %s (gpo_altitud,gpo_temp_base,tipo,densidad,radio_inferior,radio_superior,nombre_archivo) VALUES (%s,%s,%s,%s,%s,%s,'%s')"%(fila["tabla"], fila["gpo_altitud"], fila["gpo_temp_base"], fila["tipo"], fila["densidad"], fila["radio_inferior"], fila["radio_superior"], fila["nombre_archivo"])
                con.execute(sql)
        con.commit()
        con.close()
        log.info("base de datos creada con exito")
        #
    #
    log.info("abrir db %s"%NombreArchivoDB)
    conexion_db=sqlite3.connect(NombreArchivoDB)
    log.info("conexion de datos establecida")
#
def cerrar_db():
    log.info("cerrar_db")
    global conexion_db
    if conexion_db==None:
        return
    conexion_db.close()
    conexion_db=None

#
#
# POOL DE MODELOS
#
#
pool=dict() # {id:modelo,...}; id="nombre_archivo"
#
def iniciar_pool_modelos(loader):
    global pool
    if len(pool)>0:
        return
    log.info("iniciar_pool_modelos")
    #
    tablas=["naturaleza"]
    for tabla in tablas:
        log.info("tabla '%s'"%tabla)
        sql="SELECT * FROM %s"%tabla
        cursor=conexion_db.execute(sql)
        filas=cursor.fetchall()
        for fila in filas:
            if fila[7] in pool:
                continue
            ruta_archivo_modelo=os.path.join("objetos", "%s.egg"%fila[7])
            log.info("-cargar %s"%ruta_archivo_modelo)
            modelo=loader.loadModel(ruta_archivo_modelo)
            pool[fila[7]]=modelo
#
def terminar_pool_modelos():
    log.info("terminar_pool_modelos")
    global pool
    for id, modelo in pool.items():
        modelo.removeNode()
    for id in pool.keys():
        del pool[id]

#
#
# NATURALEZA
#
#
class Naturaleza:
    
    # ruido de distribucion de objetos
    ParamsRuido=[16.0, 345]
    
    # tipos de objeto
    TipoObjetoNulo=0
    TipoObjetoArbol=1
    TipoObjetoArbusto=2
    TipoObjetoPlanta=3
    TipoObjetoYuyo=4
    TipoObjetoRocaPequena=5
    TipoObjetoRocaMediana=6
    TipoObjetoRocaGrande=7
    
    # parametros
    RadioMaximo=4.0
    
    def __init__(self, base, altura_maxima_terreno, tamano):
        # referencias:
        self.base=base
        # componentes:
        self.ruido_perlin=PerlinNoise2(Naturaleza.ParamsRuido[0], Naturaleza.ParamsRuido[0], 256, Naturaleza.ParamsRuido[1])
        # variables internas:
        self._altura_maxima_terreno=altura_maxima_terreno
        self._tamano=tamano
        self._data=None
    
    def iniciar(self):
        #log.debug("iniciar")
        if os.path.exists(NombreArchivoDB):
            os.remove(NombreArchivoDB)
        # db
        iniciar_db()
        # pool de modelos
        iniciar_pool_modelos(self.base.loader)
        # matriz
        self._data=list() # x,y -> [[(altitud,temperatura_base),...],...]
        for x in range(self._tamano):
            fila=list()
            for y in range(self._tamano):
                fila.append((0.0, 0.0))
            self._data.append(fila)
    
    def cargar_datos(self, pos, temperatura_base):
        x=int(pos[0])
        y=int(pos[1])
        altitud=pos[2]
        self._data[x][y]=(altitud, temperatura_base)

    def generar(self, nombre):
        # ruido generico
        random.seed(Naturaleza.ParamsRuido[1])
        # nodo central
        nodo_central=NodePath(nombre)
        # representacion espacial
        espacio=list()
        for x in range(self._tamano):
            fila=list()
            for y in range(self._tamano):
                fila.append((0.0, 0.0, (0.0, 0.0))) # radios inferior y superior de objeto en esa posicion, (dx,dy) aleatorio; 0.0==vacio
            espacio.append(fila)
        # normalizar densidad de objetos de mismo grupo
        info_gpos=dict() # {gpo_altitud:{gpo_temp_base:(descripcion_tipo_objeto,factor_densidad,[pos,...]),...},...}
        for x in range(self._tamano):
            for y in range(self._tamano):
                altitud, temperatura_base=self._data[x][y]
                gpo_altitud=int(9.9*altitud/self._altura_maxima_terreno)
                gpo_temp_base=int(4.9*temperatura_base)
                #log.debug("generar altitud=%.2f temperatura_base=%.2f gpo_altitud=%i gpo_temp_base=%i"%(altitud, temperatura_base, gpo_altitud, gpo_temp_base))
                if not gpo_altitud in info_gpos:
                    info_gpos[gpo_altitud]=dict()
                if not gpo_temp_base in info_gpos[gpo_altitud]:
                    sql="SELECT * FROM naturaleza WHERE gpo_altitud=%i AND gpo_temp_base=%i ORDER BY densidad DESC"%(gpo_altitud, gpo_temp_base)
                    log.debug(sql)
                    cursor=conexion_db.execute(sql)
                    filas_objetos=cursor.fetchall()
                    #log.debug(str(filas_objetos))
                    cant=len(filas_objetos)
                    factor_densidad=0.0
                    for fila in filas_objetos:
                        factor_densidad+=fila[4]
                    if cant>0 and factor_densidad>1.0:
                        factor_densidad=1.0/factor_densidad
                    else:
                        factor_densidad=1.0
                    info_gpos[gpo_altitud][gpo_temp_base]=(filas_objetos, factor_densidad, [(x, y, altitud)])
                else:
                    info_gpos[gpo_altitud][gpo_temp_base][2].append((x, y, altitud))
        # distribuir objetos
        for gpo_altitud, gpos_temp_base in info_gpos.items(): # para cada grupo de altitud
            for gpo_temp_base, datos in gpos_temp_base.items(): # para cada grupo de temperatura_base por grupo de altitud
                #log.debug(str(datos))
                descripciones_tipo_objeto, factor_densidad, lista_pos=datos
                for descripcion_tipo_objeto in descripciones_tipo_objeto: # para cada tipo de objeto en cada grupo altitud/temperatura_base
                    for pos in lista_pos: # testear para cada posicion posible
                        ruido=(self.ruido_perlin(pos[0], pos[1])+1.0)/2.0
                        trigger=descripcion_tipo_objeto[4]*factor_densidad
                        if ruido>trigger: # testear colocacion de objeto en una posicion
                            log.debug("colocar objeto %s en posicion %s?"%(str(descripcion_tipo_objeto), str(pos)))
                            radio_inferior=descripcion_tipo_objeto[5]
                            radio_superior=descripcion_tipo_objeto[6]
                            # si hay espacio inferior y superior colocar objeto
                            if self._chequear_espacio(pos, radio_inferior, radio_superior, espacio):
                                log.debug("se agregara")
                                # desplazamiento aleatorio
                                dpos=[random.random(), random.random()]
                                # colocar modelo
                                modelo=pool[descripcion_tipo_objeto[7]]
                                dummy=nodo_central.attachNewNode("dummy")
                                dummy.setPos(self.base.render, Vec3(pos[0]+dpos[0], pos[1]+dpos[1], pos[2]))
                                modelo.instanceTo(dummy)
                                # establecer informacion espacial de radios
                                self._establecer_informacion_espacial(pos, radio_inferior, radio_superior, espacio)
        #log.debug(str(espacio))
        #
        nodo_central.setShaderAuto()
        nodo_central.flattenStrong()
        #
        return nodo_central

    def _chequear_espacio(self, pos, radio_inferior, radio_superior, espacio):
        return True

    def _establecer_informacion_espacial(self, pos, radio_inferior, radio_superior, espacio):
        pass
