from direct.actor.Actor import Actor
from panda3d.bullet import *
from panda3d.core import *

import logging
log=logging.getLogger(__name__)

class Hombre(NodePath):
    
    def __init__(self, mundo):
        NodePath.__init__(self, "hombre")
        self.reparentTo(mundo)
        #
        self.mundo=mundo
        self.base=mundo.base
        #
        _shape=BulletBoxShape(Vec3(0.5, 0.5, 0.5))
        _cuerpo=BulletRigidBodyNode("hombre_rigid_body")
        _cuerpo.addShape(_shape)
        #_cuerpo.setMass(1.0)
        self.attachNewNode(_cuerpo)
        self.mundo.mundo_fisico.attachRigidBody(_cuerpo)
        #
        self.actor=Actor("player")
        self.actor.reparentTo(self)
        #
        self.foco_camara=self.actor.attachNewNode("foco_camara")
        self.foco_camara.setZ(1.0)
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
        #
        return task.cont
