#!/usr/bin/python

import sys
import os, os.path

if __name__=="__main__":
    print("Formatear archivos egg exportados de editor:")
    print("-dir_nombre_archivo_egg/")
    print("-----actor.egg")
    print("-----accion0.egg")
    print("-----accionN.egg\n")
    #
    if len(sys.argv)!=2:
        print("error: parámetros de más o de menos, formato ./formatear_personaje.py nombre_dir")
        sys.exit()
    #
    nombre_dir=sys.argv[1]
    print("directorio: ./%s"%nombre_dir)
    if not os.path.exists(nombre_dir) or not os.path.isdir(nombre_dir):
        print("error: no existe el directorio o no es un directorio")
        sys.exit()
    #
    print("buscando archivos ./%s/%s*.egg..."%(nombre_dir, nombre_dir))
    archivos_origen=[archivo for archivo in os.listdir(nombre_dir) if archivo[:4].lower()==nombre_dir]
    print("se encontraron %i archivos"%len(archivos_origen))
    if len(archivos_origen)==0:
        print("error: no se encontraron archivos")
        sys.exit()
    #
    print("renombrando archivos y eliminando previos...")
    for archivo in archivos_origen:
        ruta_archivo_origen="./%s/%s"%(nombre_dir, archivo)
        ruta_archivo_destino="./%s/"%nombre_dir
        print("-archivo origen: %s"%ruta_archivo_origen)
        if archivo[:-4]==nombre_dir:
            ruta_archivo_destino+="actor.egg"
        elif archivo.startswith("%s-"%nombre_dir):
            archivo_accion=archivo[archivo.index("-")+1:]
            if archivo_accion=="":
                print("-error: ocurrió un error al extraer nombre de acción, salteando...")
                continue
            ruta_archivo_destino+=archivo_accion
        else:
            print("-error: archivo no identificable, salteando...")
            continue
        print("-archivo destino: %s"%ruta_archivo_destino)
        os.replace(ruta_archivo_origen, ruta_archivo_destino)
        print("-hecho")
    #
    print("listo?")

