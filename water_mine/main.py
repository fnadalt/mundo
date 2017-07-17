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
        self.hombre.setPos(0.0, 3.0, -0.5)
        #
        self.agua=self.loader.loadModel("plano")
        self.agua.reparentTo(self.render)
        self.agua.setScale(0.5)
        self.agua.setTransparency(TransparencyAttrib.MAlpha)
        self.agua.setZ(-0.05)
        #
        self.rotador=self.render.attachNewNode("rotador")
        self.camera2=None
        self.camera3=None
        #
        self.configurar_reflejo()
        self.configurar_refraccion()
        #
        self.camera.reparentTo(self.rotador)
        self.camera.setPos(self.agua, 10.0, -24.0, 10.0)
        self.camera.lookAt(self.agua)
        if self.camera2!=None:
            self.camera2.reparentTo(self.rotador)
            self.camera2.setPos(self.agua, 10.0, -24.0, -10.0)
            self.camera2.lookAt(self.agua)
        if self.camera3!=None:
            self.camera3.reparentTo(self.rotador)
            self.camera3.setPos(self.agua, 10.0, -24.0, 10.0)
            self.camera3.lookAt(self.agua)
        # debug info text
        self.texto1=OnscreenText(text="info?", pos=(0.9, 0.9), scale=0.05, mayChange=True)
        #
        shader=Shader.load(Shader.SL_GLSL, vertex="water.v.glsl", fragment="water.f.glsl")
        self.agua.setShader(shader)
        #
        self.taskMgr.add(self.update,"update")

    def configurar_reflejo(self):
        # reflejo
        reflection_plane=Plane(Vec3(0.0, 0.0, 1.0), Vec3(0.0, 0.0, -0.15))
        reflection_plane_node=PlaneNode("reflection_plane_node")
        reflection_plane_node.setPlane(reflection_plane)
        reflection_plane_nodeN=self.render.attachNewNode(reflection_plane_node)
        #
        reflection_buffer=self.win.makeTextureBuffer('reflection_buffer', 512, 512)
        reflection_buffer.setClearColor(Vec4(0, 0, 0, 1))
        self.camera2=self.makeCamera(reflection_buffer)
        self.camera2.node().getLens().setFov(self.cam.node().getLens().getFov())
        dummy_reflection=NodePath("dummy_reflection")
        dummy_reflection.setTwoSided(False)
        dummy_reflection.setClipPlane(reflection_plane_nodeN)
        self.camera2.node().setInitialState(dummy_reflection.getState())
        #
        ts0=TextureStage("tsBuffer_reflection")
        tex0=reflection_buffer.getTexture()
        tex0.setWrapU(Texture.WMClamp)
        tex0.setWrapV(Texture.WMClamp)
        self.agua.setTexture(ts0, tex0)
        
    def configurar_refraccion(self):
        # refraccion
        refraction_plane=Plane(Vec3(0.0, 0.0, -1.0), Vec3(0.0, 0.0, -0.05))
        refraction_plane_node=PlaneNode("refraction_plane_node")
        refraction_plane_node.setPlane(refraction_plane)
        refraction_plane_nodeN=self.render.attachNewNode(refraction_plane_node)
        #
        refraction_buffer=self.win.makeTextureBuffer('refraction_buffer', 512, 512)
        refraction_buffer.setClearColor(Vec4(0, 0, 0, 1))
        self.camera3=self.makeCamera(refraction_buffer)
        self.camera3.node().getLens().setFov(self.cam.node().getLens().getFov())
        dummy_refraction=NodePath("dummy_refraction")
        dummy_refraction.setTwoSided(False)
        dummy_refraction.setClipPlane(refraction_plane_nodeN)
        self.camera3.node().setInitialState(dummy_refraction.getState())
        #
        ts1=TextureStage("tsBuffer_refraction")
        tex1=refraction_buffer.getTexture()
        tex1.setWrapU(Texture.WMClamp)
        tex1.setWrapV(Texture.WMClamp)
        self.agua.setTexture(ts1, tex1)
    
    def update(self, task):
        if self.camera2!=None:
            self.camera2.setPos(self.camera.getPos())
            self.camera2.setZ(-self.camera.getZ())
            self.camera2.setP(-self.camera.getP())
            self.camera2.lookAt(self.agua)
        if self.camera2!=None and self.camera3!=None:
            self.texto1.setText("cam %s\ncam2 %s\ncam3 %s"%(str(self.camera.getPos()), str(self.camera2.getPos()), str(self.camera3.getPos())))
        #
        dt=task.time
        #self.rotador.setH(self.rotador.getH()+0.1*dt)
        #
        return task.cont

water=Water()
water.run()
