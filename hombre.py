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
        _rbody=BulletRigidBodyNode(_shape, 0.4, "hombre_rigid_body")
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
        self.factor_movimiento=1.0
        # variables internas
        self._quieto=True
        self._vel_lineal=LVector3()
        self._vel_angular=0.0
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
            #
            self.cuerpo.node().setLinearMovement(self._vel_lineal*self.factor_movimiento, True)
            self.cuerpo.node().setAngularMovement(self._vel_angular*self.factor_movimiento)
            #
            if self._vel_lineal==LVector3.zero() and self._vel_angular==0.0:
                self._quieto=True
        #
        return task.cont

    def avanzar(self, flag):
        self._vel_lineal.setY(-self.max_vel_lineal[0] if flag else 0.0)
        if flag:
            self._quieto=False
    
    def retroceder(self, flag):
        self._vel_lineal.setY(self.max_vel_lineal[1] if flag else 0.0)
        if flag:
            self._quieto=False
    
    def desplazar_izquierda(self, flag):
        self._vel_lineal.setX(self.max_vel_lineal[2] if flag else 0.0)
        if flag:
            self._quieto=False
    
    def desplazar_derecha(self, flag):
        self._vel_lineal.setX(-self.max_vel_lineal[2] if flag else 0.0)
        if flag:
            self._quieto=False
    
    def girar_izquierda(self, flag):
        self._vel_angular=self.max_vel_angular if flag else 0.0
        if flag:
            self._quieto=False
    
    def girar_derecha(self, flag):
        self._vel_angular=-self.max_vel_angular if flag else 0.0
        if flag:
            self._quieto=False
    
    def saltar(self):
        self.cuerpo.node().doJump()
    
    def agachar(self, flag):
        pass

    
