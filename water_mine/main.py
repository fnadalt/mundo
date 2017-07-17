from direct.gui.OnscreenText import OnscreenText
from direct.showbase.ShowBase import ShowBase
from panda3d.core import *

class Water(ShowBase):
    
    def __init__(self):
        ShowBase.__init__(self)
        self.disableMouse()
        #
        sun=DirectionalLight("sun")
        sun.setColor((0.5, 0.5, 0.5, 1.0))
        sunN=self.render.attachNewNode(sun)
        sunN.setHpr(-45, -45, 0)
        self.render.setLight(sunN)
        #
        plane=Plane(Vec3(0.0, 0.0, 1.0), Vec3(0.0, 0.0, 0.1))
        plane_node=PlaneNode("plane_node")
        plane_node.setPlane(plane)
        plane_nodeN=self.render.attachNewNode(plane_node)
        #
        self.terreno=self.loader.loadModel("terreno")
        self.terreno.reparentTo(self.render)
        #self.terreno.setClipPlane(plane_nodeN)
        #
        point=PointLight("foco")
        point.setColor((0.7, 0.7, 0.7, 1.0))
        pointN=self.render.attachNewNode(point)
        pointN.setPos(0.0, 0.0, 0.2)
        self.render.setLight(pointN)
        #
        self.horrendo=self.loader.loadModel("horrendo")
        self.horrendo.reparentTo(self.render)
        self.horrendo.setPos(0.0, 0.0, 3.0)
        #
        self.hombre=self.loader.loadModel("actor.egg")
        self.hombre.reparentTo(self.render)
        self.hombre.setPos(0.0, 3.0, 0.0)
        #
        self.agua=self.loader.loadModel("plano")
        self.agua.reparentTo(self.render)
        self.agua.setScale(0.5)
        self.agua.setTransparency(TransparencyAttrib.MAlpha)
        #
        self.camera.setPos(self.agua, 10.0, -24.0, 10.0)
        self.camera.lookAt(self.agua)
        #
        buffer=self.win.makeTextureBuffer('buffer', 4096, 4096)
        buffer.setClearColor(Vec4(0, 0, 0, 1))
        self.camera2=self.makeCamera(buffer)
        self.camera2.reparentTo(self.render)
        self.camera2.setPos(0.0, 0.0, -0.1)
        self.camera2.lookAt(self.horrendo)
        self.camera2.node().getLens().setFov(150.0, 150.0)
        dummy=NodePath("dummy")
        dummy.setTwoSided(False)
        dummy.setClipPlane(plane_nodeN)
        self.camera2.node().setInitialState(dummy.getState())
        #
        ts0=TextureStage("tsBuffer")
        tex0=buffer.getTexture()
        tex0.setWrapU(Texture.WMClamp)
        tex0.setWrapV(Texture.WMClamp)
        self.agua.setTexture(ts0, tex0)
        #self.agua.setTexRotate(ts0, 180.0)
        #
        self.texto1=OnscreenText(text="info?", pos=(0.9, 0.9), scale=0.05, mayChange=True)
        #
        shader=Shader.load(Shader.SL_GLSL, vertex="water.v.glsl", fragment="water.f.glsl")
        self.agua.setShader(shader)
        #
        self.taskMgr.add(self.update,"update")
    
    def update(self, task):
        self.camera2.setPos(self.camera.getPos())
        self.camera2.setZ(-self.camera.getZ())
        self.camera2.setP(-self.camera.getP())
        self.camera2.lookAt(self.agua)
        self.texto1.setText("cam %s\ncam2 %s"%(str(self.camera.getPos()), str(self.camera2.getPos())))
        #
        return task.cont

water=Water()
water.run()
