from direct.gui.OnscreenText import OnscreenText
from panda3d.bullet import *
from panda3d.core import *
from terreno import Terreno
from hombre import Hombre

import logging
log=logging.getLogger(__name__)

class Mundo(NodePath):
    
    def __init__(self, base):
        NodePath.__init__(self, "mundo")
        self.reparentTo(base.render)
        #
        self.base=base
        #
        self._configurar_fisica()
        #
        self._cargar_debug_info()
        self._cargar_hombre()
        self._cargar_terreno()
        self._cargar_luces()
        self._cargar_camara()
    
    def _configurar_fisica(self):
        self.mundo_fisico=BulletWorld()
        #
        debug_fisica=BulletDebugNode("debug_fisica")
        debug_fisica.showNormals(True)
        self.debug_fisicaN=self.attachNewNode(debug_fisica)
        self.debug_fisicaN.hide()
        self.base.accept("f3", self._toggle_debug_fisica)
        #
        self.mundo_fisico.setGravity(Vec3(0.0, 0.0, -9.81))
        self.mundo_fisico.setDebugNode(debug_fisica)
        self.base.taskMgr.add(self._update_phys, "_update_phys")
        #
        _shape=BulletBoxShape(Vec3(0.5, 0.5, 0.5))
        _cuerpo=BulletRigidBodyNode("caja_rigid_body")
        _cuerpo.setMass(1.0)
        _cuerpo.addShape(_shape)
        _cuerpoN=self.attachNewNode(_cuerpo)
        _cuerpoN.setPos(0.0, 0.0, 200.0)
        self.mundo_fisico.attachRigidBody(_cuerpo)
        _cuerpoN.reparentTo(self)
        caja=self.base.loader.loadModel("box.egg")
        caja.reparentTo(_cuerpoN)
    
    def _cargar_debug_info(self):
        self.texto1=OnscreenText(text="info?", pos=(0.9, 0.9), scale=0.05, mayChange=True)
    
    def _cargar_hombre(self):
        self.hombre=Hombre(self)
    
    def _cargar_terreno(self):
        self.terreno=Terreno(self, self.hombre)
        self.terreno.setPos(0.0, 0.0, 0.0)
        altitud=self.terreno.obtener_altitud(self.hombre.getPos())
        self.hombre.setZ(altitud)
        logging.debug("hombre at "+str(self.hombre.getPos()))
        test=self.mundo_fisico.rayTestAll(LPoint3(0.0, 0.0, 1000.0), LPoint3(0.0, 0.0, -1000.0))
        for hit in test.getHits():
            logging.debug("ray test hit %s at %s"%(str(hit.getNode()), str(hit.getHitPos())))

    def _cargar_luces(self):
        luz_d=DirectionalLight("sol0")
        luz_d.setColor(Vec4(0.55, 0.55, 0.55, 1.0))
        self.sol0=self.base.render.attachNewNode(luz_d)
        self.sol0.setHpr(45.0, -75.0, 0.0)
        self.setLight(self.sol0)
    
    def _cargar_camara(self):
        self.base.cam.reparentTo(self.hombre.foco_camara)
        self.base.cam.setY(3.0)
        self.base.cam.lookAt(self.hombre.foco_camara)
        self.base.accept("wheel_up",self._zoom_cam,[-1])
        self.base.accept("wheel_down",self._zoom_cam,[1])
    
    def _zoom_cam(self, amount):
		cam_Y=self.base.cam.getY()
		cam_Y+=amount*5.0
		if cam_Y<1.2 or cam_Y>1600.0:
			return
		self.base.cam.setY(cam_Y)
    
    def _update_phys(self, task):
        dt=self.base.taskMgr.globalClock.getDt()
        self.mundo_fisico.doPhysics(dt)
        return task.cont
    
    def _toggle_debug_fisica(self):
        if self.debug_fisicaN.isHidden():
            self.debug_fisicaN.show()
        else:
            self.debug_fisicaN.hide()
