import configparser
import os, os.path

import logging
log=logging.getLogger(__name__)

_default_config={
        "shader":   {
                    "sombras":False
                    }
        }

nombre_archivo="mundo.ini"
configuracion=None

def valbool(variable):
    valor=val(variable).lower()
    return True if valor=="true" else False

def val(variable):
    if configuracion==None:
        raise Exception("sistema de configuraciones no iniciado")
    partes=variable.split(".")
    if len(partes)<2:
        log.error("nombre de variable erroneo '%s'"%variable)
        return None
    seccion=partes[0]
    nombre_variable=partes[1]
    valor=None
    try:
        valor=configuracion[seccion][nombre_variable]
    except:
        log.exception("error al intentar obtener valor de configuracion '%s'"%variable)
    return valor

def establecer(variable, valor):
    if configuracion==None:
        raise Exception("sistema de configuraciones no iniciado")
    partes=variable.split(".")
    if len(partes)<2:
        log.error("nombre de variable erroneo '%s'"%variable)
        return None
    seccion=partes[0]
    nombre_variable=partes[1]
    try:
        configuracion.set(seccion, nombre_variable, str(valor))
    except configparser.NosectionError:
        log.exception("la seccion especificada no existe '%s'"%variable)
    except Exception as e:
        log.exception(str(e))

def iniciar():
    global configuracion
    log.info("iniciar")
    if configuracion!=None:
        raise Exception("sistema de configuraciones ya iniciado")
    #
    configuracion=configparser.ConfigParser()
    configuracion.read_dict(_default_config)
    if not os.path.exists(nombre_archivo):
        log.warning("no existe el archivo de configuracion '%s', se lo creara..."%nombre_archivo)
        escribir_archivo()
    log.info("leer archivo de configuracion '%s'"%nombre_archivo)
    configuracion.read(nombre_archivo)

def escribir_archivo():
    log.info("escribir_archivo '%s'"%nombre_archivo)
    if not configuracion:
        log.error("sistema de configuracion no iniciado")
        return
    with open(nombre_archivo, "w") as archivo:
        configuracion.write(archivo)
