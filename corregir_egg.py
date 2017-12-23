#!/usr/bin/python

import argparse
import sys, os, os.path
import tempfile
import logging

logging.basicConfig(level=logging.INFO)
log=logging.getLogger("corregir_egg")

ruta_actual=os.getcwd()
log.info("ruta actual: %s"%ruta_actual)

ruta_dir_temp=tempfile.gettempdir()
log.info("directorio temporal: %s"%ruta_dir_temp)

argsp=argparse.ArgumentParser(description="Ejecutar egg-trans -F en archivos exportados desde YABEE")
argsp.add_argument("--egg")
args=argsp.parse_args()

ruta_archivo_origen=os.path.join(ruta_actual, args.egg)
log.info("ruta de archivo a corregir: %s"%ruta_archivo_origen)
if not os.path.exists(ruta_archivo_origen):
    log.error("el archivo especificado no existe...")
    sys.exit()

ruta_arch_temp=os.path.join(ruta_dir_temp, os.path.basename(args.egg)+".tmp")
log.info("ruta de archivo temporal: %s"%ruta_arch_temp)
if os.path.exists(ruta_arch_temp):
    log.warning("el archivo temporal existe, se lo eliminará")
    os.remove(ruta_arch_temp)

cmd0="egg-trans -F -o %s %s"%(ruta_arch_temp, ruta_archivo_origen)
log.info("> "+cmd0)
os.system(cmd0)

cmd1="mv %s %s"%(ruta_arch_temp, ruta_archivo_origen)
log.info("> "+cmd1)
os.system(cmd1)
