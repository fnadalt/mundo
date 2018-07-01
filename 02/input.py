# -*- coding: utf-8 -*-

from direct.showbase.DirectObject import DirectObject

# log
import logging
log = logging.getLogger(__name__)


class Input(DirectObject):
    """
    * administra input
    * provee estado de input a objeto bajo control y a cámara
    """

    def __init__(self, contexto):
        DirectObject.__init__(self)
        # referencias
        self.contexto = contexto

    def iniciar(self):
        log.info("iniciar")
        # tasks
        self.contexto.base.taskMgr.add(self._update, "Input_update")
        #
        return True

    def terminar(self):
        log.info("terminar")
        # tasks
        self.contexto.base.taskMgr.remove("Input_update")

    def _update(self, task):
        return task.cont
