import configparser
import os, os.path

import logging
log=logging.getLogger(__name__)

nombre_archivo="mundo.ini"
nombre_archivo_mtime="mundo.ini.mtime"
configuracion=None

_sucio=False
_default_config={
        "shader":       {
                        "phong":True, 
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
                        "lod0":"65.0 0.0", 
                        "lod1":"130.0 65.0", 
                        "lod2":"500.0 130.0"
                        }
        }

def archivo_modificado():
    if os.path.exists(nombre_archivo):
        fecha_arch=str(os.path.getmtime(nombre_archivo))
        if os.path.exists(nombre_archivo_mtime):
            with open(nombre_archivo_mtime) as archivo:
                fecha_arch_mtime=archivo.read()
                if fecha_arch==fecha_arch_mtime:
                    return False
    return True

def valbool(variable):
    valor=val(variable).lower()
    return True if valor=="true" else False

def valint(variable):
    try:
        valor=int(val(variable))
    except Exception as e:
        log.exception(str(e))
        return 0
    return valor

def valfloat(variable):
    try:
        valor=float(val(variable))
    except Exception as e:
        log.exception(str(e))
        return 0
    return valor

def vallist(variable, separador=" "):
    valor=val(variable)
    if valor:
        return valor.split(separador)
    return None

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
        log.warning("error al intentar obtener valor de configuracion '%s'"%variable)
    return valor

def establecer(variable, valor):
    global _sucio
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
        _sucio=True
    except configparser.NosectionError:
        log.exception("la seccion especificada no existe '%s'"%variable)
    except Exception as e:
        log.exception(str(e))

def iniciar():
    global configuracion, _sucio
    log.info("iniciar")
    if configuracion!=None:
        raise Exception("sistema de configuraciones ya iniciado")
    #
    configuracion=configparser.ConfigParser()
    configuracion.read_dict(_default_config)
    if not os.path.exists(nombre_archivo):
        log.warning("no existe el archivo de configuracion '%s', se lo creara..."%nombre_archivo)
        _sucio=True
        escribir_archivo()
    log.info("leer archivo de configuracion '%s'"%nombre_archivo)
    configuracion.read(nombre_archivo)

def escribir_archivo():
    global configuracion
    #
    if _sucio:
        log.info("escribir_archivo '%s'"%nombre_archivo)
        if not configuracion:
            log.error("sistema de configuracion no iniciado")
            return
        with open(nombre_archivo, "w") as archivo:
            configuracion.write(archivo)
    #
    if archivo_modificado():
        log.info("escribir_archivo '%s'"%nombre_archivo_mtime)
        with open(nombre_archivo_mtime, "w") as archivo:
            archivo.write(str(os.path.getmtime(nombre_archivo)))
