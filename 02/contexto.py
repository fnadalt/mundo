# -*- coding: utf-8 -*-

import os.path
from configparser import ConfigParser
from direct.showbase.ShowBase import ShowBase

# log
import logging
log = logging.getLogger(__name__)


class Contexto:  # Context
    """
    * contiene referencia a ShowBase
    * contiene ConfigParser
    """

    ConfigDefault = {
        "aplicacion":
            {
                "escenas_basicas": "inicio",  # basic scenes: main, ...
                "escena_primera": "inicio"  # first scene
                }
            }

    ConfigFileName = "mundo.ini"

    def __init__(self):
        # referencias
        self.base = ShowBase()
        # componentes
        self.config = ConfigParser()

    def iniciar(self):  # init
        log.info("iniciar")
        # config
        self.config.read_dict(Contexto.ConfigDefault)
        if os.path.exists(Contexto.ConfigFileName):
            self.config.read(Contexto.ConfigFileName)
        #
        return True

    def terminar(self):  # terminate
        log.info("terminar")
        self.config = None
        self.base = None
