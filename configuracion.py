import configparser
import os, os.path

import logging
log=logging.getLogger(__name__)

class Configuracion:
    
    DefaultConfig={
        "shader":       {
                        "luz":True, 
                        "phong":False, 
                        "sombras":False, 
                        "fog":False, 
                        "fog_rango_distancias":"70 120", 
                        "sombras_tamano_buffer":512, 
                        "sombras_fov":30, 
                        "agua_reflejo_refraccion":True, 
                        "agua_tamano_buffer":512, 
                        "sol_blur":True, 
                        "sol_tamano_buffer":512
                        }, 
        "sistema":      {
                        "pos_cursor_inicial":"14.0 14.0", 
                        "radio_expansion_parcelas":2, 
                        "dir_cache":"cache"
                        }, 
        "generico":     {
                        "sombras":True, 
                        "profundidad_agua":True, 
                        "normal_map":True
                        }, 
        "terreno":      {
                        "color_debug":False, 
                        "debug_info":"terreno",  # [terreno|bioma]
                        "normal_map":False, 
                        "dibujar_normales":False, 
                        "sombras":True, 
                        "wireframe":False
                        }, 
        "objetos":      {
                        "lod0":"20.0 0.0", 
                        "lod1":"48.0 20.0", 
                        "lod2":"76.0 48.0", 
                        "lod3":"5000.0 76.0"
                        }
        }

    def __init__(self):
        # componentes
        self._config_parser=None
        # variables externas
        self.nombre_archivo="mundo.ini"
    
    def iniciar(self):
        log.info("iniciar")
        if self._config_parser!=None:
            log.warning("self._config_parser!=None")
            return False
        # default
        self._config_parser=configparser.ConfigParser()
        self._config_parser.read_dict(Configuracion.DefaultConfig)
        # leer de archivo
        log.info("self.nombre_archivo"%self.nombre_archivo)
        if not os.path.exists(self.nombre_archivo):
            log.warning("os.path.exists(self.nombre_archivo)==False"%self.nombre_archivo)
            if not self.escribir_archivo():
                return False
        self._config_parser.read(self.nombre_archivo)
        #
        return True
    
    def terminar(self):
        log.info("terminar")

    def escribir_archivo(self):
        log.info("escribir_archivo")
        #
        if not self._config_parser:
            log.error("self._config_parser==None")
            return False
        with open(self.nombre_archivo, "w") as archivo:
            self._config_parser.write(archivo)
        #
        return True

    def establecer(self, variable, valor):
        if self._config_parser==None:
            log.error("self._config_parser==None")
            return
        #
        partes=variable.split(".")
        if len(partes)<2:
            log.error("nombre de variable erroneo '%s'"%variable)
            return
        seccion=partes[0]
        nombre_variable=partes[1]
        try:
            self._config_parser.set(seccion, nombre_variable, str(valor))
        except configparser.NosectionError:
            log.exception("la seccion especificada no existe '%s'"%variable)
        except Exception as e:
            log.exception(str(e))

    def valbool(self, variable):
        valor=self.val(variable).lower()
        return True if valor=="true" else False

    def valint(self, variable):
        try:
            valor=int(self.val(variable))
        except Exception as e:
            log.exception(str(e))
            return 0
        return valor

    def valfloat(self, variable):
        try:
            valor=float(self.val(variable))
        except Exception as e:
            log.exception(str(e))
            return 0
        return valor

    def vallist(self, variable, separador=" "):
        valor=self.val(variable)
        if valor:
            return valor.split(separador)
        return None

    def val(self, variable):
        if self._config_parser==None:
            log.error("self._config_parser==None")
            return None
        partes=variable.split(".")
        if len(partes)<2:
            log.error("nombre de variable erroneo '%s'"%variable)
            return None
        seccion=partes[0]
        nombre_variable=partes[1]
        valor=None
        try:
            valor=self._config_parser[seccion][nombre_variable]
        except:
            log.error("error al intentar obtener valor de configuracion '%s'"%variable)
        return valor
