import os, os.path
import sqlite3
import csv

import logging
log=logging.getLogger(__name__)

#
# Datos
#
class Datos:
    
    SqlCrearDb="""
    """
    
    def __init__(self):
        # componentes
        self.db=None
        self.cache=dict() # {idx_pos:[Parcela,contador_acceso],...}
        self.parcelas=dict() # {idx_pos:Parcela,...}
        # parametros
        self.tamano_parcela=64
        self.ruta_archivo="mundo.sql"
        self.cache_limite_inferior=(1+2*4)**2
        self.cache_limite_superior=(1+2*6)**2
        self.radio_extension_terreno_minimo=2
        self.radio_extension_terreno_optimo=6
        # variables externas
        self.idx_pos=(0, 0)
        
    
    def iniciar(self):
        log.info("iniciar")
        # db
        if not self._iniciar_db():
            return False
        #
        return True

    def terminar(self):
        log.info("terminar")
        self._cerrar_db()
    
    def establecer_parcelas(self, lista_idx_pos):
        #
        for idx_pos in lista_idx_pos:
            if idx_pos not in self.parcelas:
                parcela=self.cache.obtener_parcela(idx_pos)
                self.parcelas[idx_pos]=parcela
        #
        for idx_pos in [self.parcelas.keys()]:
            if idx_pos not in lista_idx_pos:
                parcela=self.parcelas[idx_pos]
                parcela.terminar()
                self.parcelas[idx_pos]=None
                del self.parcelas[idx_pos]
    
    def _iniciar_db(self):
        log.info("_iniciar_db %s"%self.ruta_archivo)
        # crear?
        if not os.path.exists(self.ruta_archivo) and not self._crear_db():
            return False
        # abrir
        try:
            db=sqlite3.connect(self.ruta_archivo)
            self.db=db
        except sqlite3.Error as e:
            log.exception(str(e))
            return False
        #
        return True
    
    def _crear_db(self):
        log.info("_crear_db")
        db=None
        try:
            db=sqlite3.connect(self.ruta_archivo)
            db.executescript(Datos.SqlCrearDb)
        except sqlite3.Error as e:
            log.exception(str(e))
            if db:
                db.close()
            return False
        db.close()
        return True

    def _cerrar_db(self):
        log.info("_cerrar_db")
        #
        if self.db:
            self.db.close()
            self.db=None

#
# Parcela
#
class Parcela:
    pass
