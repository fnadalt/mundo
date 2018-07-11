# -*- coding: utf-8 -*-

import os.path
from configparser import ConfigParser
from direct.showbase.ShowBase import ShowBase
from panda3d.core import *

from proveedores import Topografia

# log
import logging
log = logging.getLogger(__name__)


class Contexto:  # Context
    """
    * contiene referencia a ShowBase
    * contiene ConfigParser
    * conecta a pstats
    * administra "proveedores" de datos, disponiendo de algunos por defecto:
        - topografía
        - etc...
    """

    ConfigDefault = {
        "aplicacion":
            {
                "escenas_basicas": "inicio",  # basic scenes: main, ...
                "escena_primera": "inicio"  # first scene
                },
        "mundo":
            {
                "atmosfera": "true",
                "terreno": "true"
                },
        "input":
            {
                "periodo_refresco": "30"  # 1/refresh_rate
                },
        "terreno":
            {
                "heightmap": "heightmap.png",
                "altura": 100,  # height
                "factor_estiramiento": 1,  # horizontal stretch factor
                "wireframe": "false",
                "brute_force": "false",
                "fisica": "false"  # enable physics
                }
        }

    ConfigFileName = "mundo.ini"

    def __init__(self):
        # referencias externos  # extrenal references
        self.base = ShowBase()
        # referencias internas  # internal references
        self._proveedores = dict()
        # componentes externos  # external components
        self.config = ConfigParser()
        # componentes internos  # internal components
        self._proveedores_defecto = dict()  # default providers

    def iniciar(self):  # init
        log.info("iniciar")
        # config
        self.config.read_dict(Contexto.ConfigDefault)
        if os.path.exists(Contexto.ConfigFileName):
            self.config.read(Contexto.ConfigFileName)
        # base
        self.base.disableMouse()
        self.base.setFrameRateMeter(True)
        # engine config
        # pstats
        PStatClient.connect()
        # proveedores por defecto (default providers)
        self._proveedores_defecto[Topografia.Nombre] = Topografia()
        #
        return True

    def terminar(self):  # terminate
        log.info("terminar")
        self.config = None
        self.base = None
        # proveedores
        log.info("quitar proveedores; "
                 "al ser referencias,"
                 "debe garantizarse su correcta terminación")
        for nombre, proveedor in list(self._proveedores.items()):
            self._proveedores[nombre] = None
            del self._proveedores[nombre]

    def registrar_proveedor(self, nombre, interfaz):  # register
        log.info("registrar_proveedor %s" % nombre)
        if nombre in self._proveedores:
            log.info("ya existe el proveedor, se lo reemplazará")
        self._proveedores[nombre] = interfaz

    def remover_proveedor(self, nombre):  # remove
        log.info("remover_proveedor %s" % nombre)
        if nombre not in self._proveedores_defecto:
            log.error("no existe un proveedor por defecto con este nombre")
            return
        if nombre in self._proveedores_defecto:
            log.info("se establece provedor por defecto %s" % nombre)
            self._proveedores[nombre] = self._proveedores_defecto[nombre]
        else:
            log.info("ya no existe proveedor %s" % nombre)
            self._proveedores[nombre] = None
            del self._proveedores[nombre]

    def obtener_proveedor(self, nombre):  # get provider
        log.debug("obtener_proveedor %s" % nombre)
        proveedor = None
        if nombre in self._proveedores:
            proveedor = self._proveedores[nombre]
        else:
            log.warning("no se registró explícitamente un proveedor"
                        "con este nombre %s, buscar uno por defecto")
            if nombre in self._proveedores_defecto:
                proveedor = self._proveedores_defecto[nombre]
            else:
                raise Exception("no existe un proveedor por defecto "
                                "con este nombre %s" % nombre)
        return proveedor
