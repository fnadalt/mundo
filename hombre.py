from personaje import Personaje

import logging
log=logging.getLogger(__name__)

class Hombre(Personaje):

    def __init__(self, mundo):
        Personaje.__init__(self, mundo, "hombre")
        #
