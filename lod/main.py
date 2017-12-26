from direct.showbase.ShowBase import ShowBase
from direct.gui.DirectGui import *
from panda3d.core import *

import logging
log=logging.getLogger(__name__)

#
# TESTER
#
class Tester(ShowBase):

    def __init__(self):
        #
        super(Tester, self).__init__()
        self.disableMouse()
        self.win.setClearColor(Vec4(0.9, 1.0, 1.0, 1.0))
        self.render.setShaderAuto()
        #
        self.pos_foco=None
        self.cam_pitch=30.0
        # lod0
        self.lod0=self.render.attachNewNode(LODNode("lod0"))
        self.lod0.node().addSwitch(200.0, 0.0)
        self.arbol=self.loader.loadModel("../objetos/arbol.01.egg")
        self.arbol.reparentTo(self.lod0)
        # lod1
        self.lod0=self.render.attachNewNode(LODNode("lod0"))
        self.lod0.node().addSwitch(400.0, 200.0)
        self.arbol=self.loader.loadModel("../objetos/horrendof.egg")
        self.arbol.reparentTo(self.lod0)
        #
        plano=CardMaker("plano_base")
        r=40
        plano.setFrame(-r, r, -r, r)
        self.plano_base=self.render.attachNewNode(plano.generate())
        self.plano_base.setP(-90.0)
        self.plano_base.setColor((0, 0, 1, 1))
        #
        self.cam_driver=self.render.attachNewNode("cam_driver")
        self.camera.reparentTo(self.cam_driver)
        self.camera.setPos(0, 400, 50)
        self.camera.lookAt(self.cam_driver)
        self.cam_driver.setP(self.cam_pitch)
        #
        self.ambiental=self.render.attachNewNode(AmbientLight("ambiental"))
        self.ambiental.node().setColor(Vec4(0.1, 0.1, 0.1, 1))
        #
        self.sun=self.render.attachNewNode(DirectionalLight("sun"))
        self.sun.node().setColor(Vec4(1, 1, 1, 1))
        self.sun.setPos(self.plano_base, 100, 100, 100)
        self.sun.lookAt(self.plano_base)
        #
        self.render.setLight(self.ambiental)
        self.render.setLight(self.sun)
        #
        self.taskMgr.add(self.update, "update")
        self.accept("wheel_up", self.zoom, [1])
        self.accept("wheel_down", self.zoom, [-1])
        #
        #self._cargar_ui()
        
    def update(self, task):
        #
        mwn=self.mouseWatcherNode
        if mwn.isButtonDown(KeyboardButton.up()):
            pass
        elif mwn.isButtonDown(KeyboardButton.down()):
            pass
        elif mwn.isButtonDown(KeyboardButton.left()):
            pass
        elif mwn.isButtonDown(KeyboardButton.right()):
            pass
        #
        return task.cont
    
    def zoom(self, dir):
        dy=25*dir
        self.camera.setY(self.camera, dy)

    def _cargar_ui(self):
        # frame
        self.frame=DirectFrame(parent=self.aspect2d, pos=(0, 0, -0.85), frameSize=(-1, 1, -0.15, 0.25), frameColor=(1, 1, 1, 0.5))
        # info
        self.lblInfo=DirectLabel(parent=self.frame, pos=(-1, 0, 0.15), scale=0.05, text="info terreno?", frameColor=(1, 1, 1, 0.2), frameSize=(0, 40, -2, 2), text_align=TextNode.ALeft, text_pos=(0, 1, 1))
        # idx_pos
        DirectLabel(parent=self.frame, pos=(-1, 0, 0), scale=0.05, text="idx_pos_x", frameColor=(1, 1, 1, 0), frameSize=(0, 2, -1, 1), text_align=TextNode.ALeft)
        DirectLabel(parent=self.frame, pos=(-1, 0, -0.1), scale=0.05, text="idx_pos_y", frameColor=(1, 1, 1, 0), frameSize=(0, 2, -1, 1), text_align=TextNode.ALeft)
        self.entry_x=DirectEntry(parent=self.frame, pos=(-0.7, 0, 0), scale=0.05)
        self.entry_y=DirectEntry(parent=self.frame, pos=(-0.7, 0, -0.1), scale=0.05)
        DirectButton(parent=self.frame, pos=(0, 0, -0.1), scale=0.075, text="actualizar", command=self._ir_a_idx_pos)
        #
        self.frmImagen=DirectFrame(parent=self.frame, pos=(0.8, 0, 0.2), state=DGG.NORMAL, frameSize=(-0.4, 0.4, -0.4, 0.4))
        self.frmImagen.bind(DGG.B1PRESS, self._click_imagen)
        DirectButton(parent=self.frame, pos=(0.5, 0, 0.65), scale=0.1, text="acercar", command=self._acercar_zoom_imagen, frameSize=(-1, 1, -0.4, 0.4), text_scale=0.5)
        DirectButton(parent=self.frame, pos=(0.725, 0, 0.65), scale=0.1, text="alejar", command=self._alejar_zoom_imagen, frameSize=(-1, 1, -0.4, 0.4), text_scale=0.5)

if __name__=="__main__":
    logging.basicConfig(level=logging.DEBUG)
    PStatClient.connect()
    tester=Tester()
    tester.run()
