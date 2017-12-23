from panda3d.core import *
import sqlite3
import csv
import os.path

import logging
log=logging.getLogger(__name__)

# db
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
CREATE TABLE naturaleza (_id INTEGER PRIMARY KEY, gpo_altitud INTEGER, gpo_temp_base INTEGER, tipo INTEGER, densidad FLOAT, radio FLOAT,nombre_archivo VARCHAR(32));
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
                sql="INSERT INTO %s (gpo_temp_base,gpo_altitud,tipo,densidad,radio,nombre_archivo) VALUES (%s,%s,%s,%s,%s,'%s')"%(fila["tabla"], fila["gpo_temp_base"], fila["gpo_altitud"], fila["tipo"], fila["densidad"], fila["radio"], fila["nombre_archivo"])
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
# NATURALEZA
#
#
class Naturaleza:
    
    # ruido de distribucion de objetos
    ParamsRuido=[128.0, 345]
    
    # tipos de objeto
    TipoObjetoNulo=0
    TipoObjetoArbol=1
    TipoObjetoArbusto=2
    TipoObjetoYuyo=3
    TipoObjetoRocaPequena=4
    TipoObjetoRocaMediana=5
    TipoObjetoRocaGrande=6
    
    def __init__(self, altura_maxima_terreno, tamano):
        # componentes:
        self.ruido=PerlinNoise2(Naturaleza.ParamsRuido[0], Naturaleza.ParamsRuido[0], 256, Naturaleza.ParamsRuido[1])
        # variables internas:
        self._altura_maxima_terreno=altura_maxima_terreno
        self._tamano=tamano
        self._data=None
    
    def iniciar(self):
        #log.debug("iniciar")
        # db
        iniciar_db()
        # matriz
        self._data=list() # x,y -> [[(altitud,temperatura_base),...],...]
        for x in range(self._tamano):
            fila=list()
            for y in range(self._tamano):
                fila.append((0.0, 0.0))
            self._data.append(fila)
    
    def terminar(self):
        #log.debug("terminar")
        pass

    def cargar_datos(self, pos, temperatura_base):
        x=int(pos[0])
        y=int(pos[1])
        altitud=pos[2]
        self._data[x][y]=(altitud, temperatura_base)

    def generar(self):
        # obtener informacion sobre los distintos grupos
        info_gpos=dict() # {gpo_altitud:{gpo_temp_base:(cant_tipos,factor_densidad),...},...}
        for x in range(self._tamano):
            for y in range(self._tamano):
                altitud, temperatura_base=self._data[x][y]
                gpo_altitud=int(9.9*altitud/self._altura_maxima_terreno)
                gpo_temp_base=int(4.9*temperatura_base)
                #log.debug("generar altitud=%.2f temperatura_base=%.2f gpo_altitud=%i gpo_temp_base=%i"%(altitud, temperatura_base, gpo_altitud, gpo_temp_base))
                if not gpo_altitud in info_gpos:
                    info_gpos[gpo_altitud]=dict()
                if not gpo_temp_base in info_gpos[gpo_altitud]:
                    sql="SELECT * FROM naturaleza WHERE gpo_altitud=%i AND gpo_temp_base=%i ORDER BY densidad"%(gpo_altitud, gpo_temp_base)
                    log.debug(sql)
                    cursor=conexion_db.execute(sql)
                    filas=cursor.fetchall()
                    log.debug(str(filas))
                    cant=len(filas)
                    factor_densidad=0.0
                    for fila in filas:
                        factor_densidad+=fila[4]
                    if cant>0 and factor_densidad>1.0:
                        factor_densidad=1.0/factor_densidad
                    else:
                        factor_densidad=1.0
                    info_gpos[gpo_altitud][gpo_temp_base]=(cant, factor_densidad)
                    log.debug(info_gpos[gpo_altitud][gpo_temp_base])
        log.debug(str(info_gpos))
        #
