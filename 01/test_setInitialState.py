from panda3d.core import *

import logging
log=logging.getLogger(__name__)

from direct.showbase.ShowBase import ShowBase
from direct.gui.DirectGui import *

class Tester(ShowBase):

    def __init__(self):
        #
        super(Tester, self).__init__()
        self.disableMouse()
        #self.win.setClearColor(Vec4(1.0, 1.0, 1.0, 1.0))
        #
        self.pos_foco=None
        self.cam_pitch=0.0
        #
        self.object=self.loader.loadModel("objetos/horrendof.egg")
        self.object.reparentTo(self.render)
        shader=Shader.load(Shader.SL_GLSL, vertex="shaders/debug.v.glsl", fragment="shaders/debug.f.glsl")
        self.object.setShader(shader, 1)
        self.object.setShaderInput("dummy_input", 1.0, 0.0, 0.0, 0.0, priority=10)
        #
        self.cam_driver=self.render.attachNewNode("cam_driver")
        self.camera.reparentTo(self.cam_driver)
        self.camera.setPos(10.0, 0.0, 0.0)
        self.camera.lookAt(self.cam_driver)
        self.cam_driver.setP(self.cam_pitch)
        #
        self.sun=self.render.attachNewNode(DirectionalLight("sun"))
        self.sun.node().setColor(Vec4(1, 1, 1, 1))
        self.sun.setPos(self.object, 100, 100, 100)
        self.sun.lookAt(self.object)
        #
        self.render.setLight(self.sun)
        #
        self.texturaImagen=None
        self.imagen=None
        self.zoom_imagen=16
        #
        self.taskMgr.add(self.update, "update")
        self.accept("wheel_up", self.zoom, [1])
        self.accept("wheel_down", self.zoom, [-1])
        #
        #self._cargar_ui()
        #
        self.texbuf2=self.win.makeTextureBuffer('camera_2', 512, 512)
        self.camera2=self.makeCamera(self.texbuf2)
        self.camera2.reparentTo(self.render)
        self.camera2.setPos(self.camera.getPos()+Vec3(0, 0, 0))
        self.camera2.lookAt(self.object)
        self.camera2.node().getLens().setFov(self.camera.find("+Camera").node().getLens().getFov())
        _plane=Plane(Vec3(0.0, 0.0, 1.0), Vec3(0.0, 0.0, 0.0))
        _plane_node=PlaneNode("clip_plane")
        _plane_node.setPlane(_plane)
        _plane_node_np=self.render.attachNewNode(_plane_node)
        #_plane_node_np.show()
        dummy=NodePath("dummy")
        #dummy.setClipPlane(_plane_node_np)
        #dummy_shader=Shader.load(Shader.SL_GLSL, vertex="shaders/debug.v.glsl",  fragment="shaders/debug.f.glsl")
        #dummy.setShader(dummy_shader, 2)
        dummy.setShaderInput("dummy_input", -1.0, 0.0, 0.0, 0.0, priority=11)
        self.camera2.node().setInitialState(dummy.getState())
        #
        frame_refl=DirectFrame(image=self.texbuf2.getTexture(0), scale=0.25, pos=LVector3f(-1.05, -0.7))
        frame_refl.reparentTo(self.aspect2d)
        
    def update(self, task):
        nueva_pos_foco=self.pos_foco[:] if self.pos_foco else [0, 0]
        #
        mwn=self.mouseWatcherNode
        if mwn.isButtonDown(KeyboardButton.up()):
            nueva_pos_foco[1]-=32
        elif mwn.isButtonDown(KeyboardButton.down()):
            nueva_pos_foco[1]+=32
        elif mwn.isButtonDown(KeyboardButton.left()):
            nueva_pos_foco[0]+=32
        elif mwn.isButtonDown(KeyboardButton.right()):
            nueva_pos_foco[0]-=32
        #
        if nueva_pos_foco!=self.pos_foco:
            log.info("update pos_foco=%s"%str(nueva_pos_foco))
            self.pos_foco=nueva_pos_foco
        return task.cont
    
    def zoom(self, dir):
        log.info("zoom")
        dy=25*dir
        self.camera.setY(self.camera, dy)

    def _cargar_ui(self):
        #
        self.frmImagen=DirectFrame(pos=(0.8, 0, -0.5), state=DGG.NORMAL, frameSize=(-0.4, 0.4, -0.4, 0.4))
        self.frmImagen.bind(DGG.B1PRESS, self._click_imagen)

    def _click_imagen(self, *args):
        log.info("_click_imagen %s"%str(args))

    def _acercar_zoom_imagen(self):
        log.info("_acercar_zoom_imagen")
        if self.zoom_imagen>1:
            self.zoom_imagen/=2
            self._generar_imagen()

    def _alejar_zoom_imagen(self):
        log.info("_alejar_zoom_imagen")
        if self.zoom_imagen<512:
            self.zoom_imagen*=2
            self._generar_imagen()

if __name__=="__main__":
    logging.basicConfig(level=logging.INFO)
    PStatClient.connect()
    tester=Tester()
    tester.run()
