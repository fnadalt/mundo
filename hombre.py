from direct.actor.Actor import Actor
from personaje import Personaje

import logging
log=logging.getLogger(__name__)

class Hombre(Personaje):

    def __init__(self, mundo):
        actor=Actor("player")
        actor.setName("hombre")
        Personaje.__init__(self, mundo, actor)
        #
