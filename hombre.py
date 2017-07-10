from direct.actor.Actor import Actor
from panda3d.bullet import *
from panda3d.core import *

import logging
log=logging.getLogger(__name__)

class Hombre:
    
    def __init__(self, mundo):
        #
        self.mundo=mundo
        self.base=mundo.base
        # fisica
        _shape=BulletCapsuleShape(0.25, 0.5, ZUp)
        _rbody=BulletCharacterControllerNode(_shape, 0.5, "hombre_rigid_body")
        self.cuerpo=self.mundo.attachNewNode(_rbody)
        self.mundo.mundo_fisico.attachCharacter(_rbody)
        # actor
        self.actor=Actor("player")
        self.actor.reparentTo(self.cuerpo)
        self.actor.setZ(-0.5)
        # foco de la camara
        self.foco_camara=self.actor.attachNewNode("foco_camara")
        self.foco_camara.setZ(1.0)
        # parametros
        self.max_vel_lineal=(1.0, 0.4, 0.7) # (max_adelante, max_atras, max_lateral)
        self.max_vel_angular=90.0
        self.resistencia=0.0
        #
        self.base.taskMgr.add(self._update, "hombre_update")

    def _update(self, task):
        # time
        dt=self.base.taskMgr.globalClock.getDt()
        # camara
        if self.base.mouseWatcherNode.hasMouse():
            pos_mouse=self.base.mouseWatcherNode.getMouse()
            if abs(pos_mouse.getX())>0.2:
                foco_cam_H=self.foco_camara.getH()
                foco_cam_H-=360.0*pos_mouse.getX()*dt
                self.foco_camara.setH(foco_cam_H)
            if abs(pos_mouse.getY())>0.2:
                foco_cam_P=self.foco_camara.getP()
                foco_cam_P-=180.0*pos_mouse.getY()*dt
                if foco_cam_P<-45.0: foco_cam_P=-45.0
                if foco_cam_P>90.0: foco_cam_P=90.0
                self.foco_camara.setP(foco_cam_P)
        # movimiento
        if not self._quieto:
            pass
        #
        return task.cont

    def avanzar(self, flag):
        pass
    
    def retroceder(self, flag):
        pass
    
    def avanzar_izquierda(self, flag):
        pass
    
    def avanzar_derecha(self, flag):
        pass
    
    def girar_izquierda(self, flag):
        pass
    
    def girar_derecha(self, flag):
        pass
    
    def saltar(self):
        pass
    
    def agachar(self, flag):
        pass

    
