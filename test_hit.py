from direct.showbase.ShowBase import ShowBase
from panda3d.core import *
from panda3d.bullet import *

class App(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        self.btWorld=BulletWorld()
        _shape=BulletBoxShape(Vec3(0.5, 0.5, 0.5))
        _cuerpo=BulletRigidBodyNode("caja_rigid_body")
        _cuerpo.setMass(1.0)
        _cuerpo.addShape(_shape)
        _cuerpoN=self.render.attachNewNode(_cuerpo)
        _cuerpoN.setPos(0, 0, 0)
        self.btWorld.attachRigidBody(_cuerpo)
        self.taskMgr.add(self.update,  "update")

    def update(self, task):
        test=self.btWorld.rayTestAll(LPoint3(0, 0, 10.0), LPoint3(0, 0, -10), BitMask32.bit(1))
        for hit in test.getHits():
            print(hit.getNode().getName())
            print(hit.getHitPos().getZ())
        return task.cont

app=App()
app.run()
