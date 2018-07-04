# -*- coding: utf-8 -*-

from direct.showbase.DirectObject import DirectObject
from panda3d.core import *

# log
import logging
log = logging.getLogger(__name__)


class Plantilla(DirectObject):

    def __init__(self, contexto):
        # referencias
        self.contexto = contexto
        #

    def iniciar(self):
        log.info("iniciar")
        # tasks
        self.contexto.base.taskMgr.add(self._update, "Plantilla_update")
        #
        return True

    def terminar(self):
        log.info("terminar")
        # tasks
        self.contexto.base.taskMgr.remove("Plantilla_update")

    def _update(self, task):
        return task.cont
