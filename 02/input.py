# -*- coding: utf-8 -*-

from direct.showbase.DirectObject import DirectObject
from panda3d.core import *

# log
import logging
log = logging.getLogger(__name__)


class Input(DirectObject):
    """
    * administra input
    * provee información acción y parámetros
    """

    # acciones (actions)
    AccionNula = 0
    AccionMover = 1  # move
    AccionGirar = 2  # turn
    AccionAsir = 4  # grab
    AccionUsar = 8  # use

    # parametros (parameters)
    ParamNulo = 0
    ParamAdelante = 1  # forward
    ParamAtras = 2  # backwards
    ParamIzquierda = 4  # left
    ParamDerecha = 8  # right
    ParamArriba = 16  # upwards
    ParamAbajo = 32  # downwards
    ParamModif1 = 64  # parameter modifier 1
    ParamModif2 = 128  # parameter modifier 2

    # teclas accion defecto (default action keys)
    TeclasAccion = {
        KeyboardButton.space(): AccionUsar,
        KeyboardButton.tab(): AccionAsir,
        KeyboardButton.asciiKey(b"w"): AccionMover,
        KeyboardButton.asciiKey(b"a"): AccionMover,
        KeyboardButton.asciiKey(b"s"): AccionMover,
        KeyboardButton.asciiKey(b"d"): AccionMover,
        KeyboardButton.asciiKey(b"r"): AccionMover,
        KeyboardButton.asciiKey(b"f"): AccionMover,
        KeyboardButton.asciiKey(b"q"): AccionGirar,
        KeyboardButton.asciiKey(b"e"): AccionGirar
        }

    # teclas parametro defecto (default parameter keys)
    TeclasParam = {
        KeyboardButton.asciiKey(b"w"): ParamAdelante,
        KeyboardButton.asciiKey(b"a"): ParamIzquierda,
        KeyboardButton.asciiKey(b"s"): ParamAtras,
        KeyboardButton.asciiKey(b"d"): ParamDerecha,
        KeyboardButton.asciiKey(b"r"): ParamArriba,
        KeyboardButton.asciiKey(b"f"): ParamAbajo,
        KeyboardButton.asciiKey(b"q"): ParamIzquierda,
        KeyboardButton.asciiKey(b"e"): ParamDerecha,
        KeyboardButton.control(): ParamModif1,
        KeyboardButton.shift(): ParamModif2
        }

    def __init__(self, contexto):
        DirectObject.__init__(self)
        # referencias
        self.contexto = contexto
        self.isButtonDown = None
        # parameters
        self.periodo_refresco = 1 / 30
        # variables externas  (external variables)
        self.acciones = Input.AccionNula
        self.parametros = Input.ParamNulo

    def iniciar(self):
        log.info("iniciar")
        #
        self._establecer_parametros()
        # isButtonDown
        self.isButtonDown = self.contexto.base.mouseWatcherNode.isButtonDown
        # tasks
        self.contexto.base.taskMgr.doMethodLater(
            self.periodo_refresco,
            self._update,
            "Input_update")
        #
        return True

    def terminar(self):
        log.info("terminar")
        # tasks
        self.contexto.base.taskMgr.remove("Input_update")

    def obtener_info(self):
        info = "Input acciones=%i params=%i" \
            % (self.acciones, self.parametros)
        return info

    def accion(self, accion):
        return (acion & self.acciones) == accion

    def parametro(self, param):
        return (param & self.parametros) == param

    def _establecer_parametros(self):
        log.info("_establecer_parametros")
        try:
            cfg = self.contexto.config["input"]
            self.periodo_refresco = 1 / cfg.getfloat("periodo_refresco")
        except ValueError as e:
            log.exception("error en el análisis de la configuración: " + str(e))

    def _update(self, task):
        # parametros
        self.parametros = Input.ParamNulo
        for tecla, parametro in list(Input.TeclasParam.items()):
            if self.isButtonDown(tecla):
                self.parametros |= parametro
        # acciones
        self.acciones = Input.AccionNula
        for tecla, accion in list(Input.TeclasAccion.items()):
            if self.isButtonDown(tecla):
                self.acciones |= accion
        return task.again
