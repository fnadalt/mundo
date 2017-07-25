from panda3d.core import *

import logging
log=logging.getLogger(__name__)

class Agua:
    
    def __init__(self, mundo, luz, longitud_lado):
        self.mundo=mundo
        self.camara=mundo.base.camera
        self.cam=self.camara.find("+Camera")
        self.luz=luz
        #
        self.plano=self.mundo.base.loader.loadModel("objetos/plano_agua")
        self.plano.setScale(1.0)
        #self.plano.setTransparency(TransparencyAttrib.MAlpha)
        #
        self.move_factor=0.0
        #
        self._configurar_reflejo()
        self._configurar_refraccion()
        self._configurar_dudv()
        self._configurar_normal()
        #
        shader=Shader.load(Shader.SL_GLSL, vertex="shaders/water.v.glsl", fragment="shaders/water.f.glsl")
        self.plano.setShader(shader)
        self.plano.setShaderInput("light_pos", self.luz.getPos())
        self.plano.setShaderInput("light_color", self.luz.node().getColor())
    
    def _configurar_reflejo(self):
        reflection_plane=Plane(Vec3(0.0, 0.0, 1.0), Vec3(0.0, 0.0, -0.15)) #-0.15
        reflection_plane_node=PlaneNode("reflection_plane_node")
        reflection_plane_node.setPlane(reflection_plane)
        reflection_plane_nodeN=self.mundo.attachNewNode(reflection_plane_node)
        #
        reflection_buffer=self.mundo.base.win.makeTextureBuffer('reflection_buffer', 512, 512)
        reflection_buffer.setClearColor(Vec4(0, 0, 0, 1))
        self.camara2=self.mundo.base.makeCamera(reflection_buffer)
        self.camara2.node().getLens().setFov(self.cam.node().getLens().getFov())
        dummy_reflection=NodePath("dummy_reflection")
        dummy_reflection.setTwoSided(False)
        dummy_reflection.setClipPlane(reflection_plane_nodeN)
        self.camara2.node().setInitialState(dummy_reflection.getState())
        self.camara2.reparentTo(self.mundo)
        #
        ts0=TextureStage("tsBuffer_reflection")
        tex0=reflection_buffer.getTexture()
        tex0.setWrapU(Texture.WMClamp)
        tex0.setWrapV(Texture.WMClamp)
        self.plano.setTexture(ts0, tex0)

    def _configurar_refraccion(self):
        # refraccion
        refraction_plane=Plane(Vec3(0.0, 0.0, -1.0), Vec3(0.0, 0.0, self.plano.getZ())) #+0.1
        refraction_plane_node=PlaneNode("refraction_plane_node")
        refraction_plane_node.setPlane(refraction_plane)
        refraction_plane_nodeN=self.mundo.attachNewNode(refraction_plane_node)
        #
        refraction_buffer=self.mundo.base.win.makeTextureBuffer('refraction_buffer', 512, 512)
        refraction_buffer.setClearColor(Vec4(0, 0, 0, 1))
        self.camara3=self.mundo.base.makeCamera(refraction_buffer)
        self.camara3.node().getLens().setFov(self.cam.node().getLens().getFov())
        dummy_refraction=NodePath("dummy_refraction")
        dummy_refraction.setTwoSided(False)
        dummy_refraction.setClipPlane(refraction_plane_nodeN)
        self.camara3.node().setInitialState(dummy_refraction.getState())
        self.camara3.reparentTo(self.mundo)
        #
        ts1=TextureStage("tsBuffer_refraction")
        tex1=refraction_buffer.getTexture()
        tex1.setWrapU(Texture.WMClamp)
        tex1.setWrapV(Texture.WMClamp)
        self.plano.setTexture(ts1, tex1)

    def _configurar_dudv(self):
        ts2=TextureStage("tsBuffer_dudv")
        tex2=self.mundo.base.loader.loadTexture("texturas/agua_dudv.png")
        tex2.setWrapU(Texture.WMRepeat)
        tex2.setWrapV(Texture.WMRepeat)
        self.plano.setTexture(ts2, tex2)
    
    def _configurar_normal(self):
        ts3=TextureStage("tsBuffer_normal")
        tex3=self.mundo.base.loader.loadTexture("texturas/agua_normal.png")
        tex3.setWrapU(Texture.WMRepeat)
        tex3.setWrapV(Texture.WMRepeat)
        self.plano.setTexture(ts3, tex3)

    def update(self, dt):
        #
        dz=self.camara.getZ(self.mundo)-self.plano.getZ(self.mundo)
        cam_p=self.camara.getP(self.mundo)
        self.camara2.setPos(self.camara.getPos(self.mundo))
        self.camara2.setHpr(self.camara.getHpr(self.mundo))
        self.camara2.setZ(self.plano.getZ(self.mundo)-dz)
        self.camara2.setP(-cam_p)
        self.camara3.setPos(self.camara.getPos(self.mundo))
        self.camara3.setHpr(self.camara.getHpr(self.mundo))
        self.mundo.texto1.setText("cam %s\ncam2 %s\ncam3 %s"%(str(self.camara.getPos(self.mundo)), str(self.camara2.getPos(self.mundo)), str(self.camara3.getPos(self.mundo))))
        #
        self.move_factor+=0.03*dt
        self.move_factor%=1
        self.plano.setShaderInput("move_factor", self.move_factor)
        self.plano.setShaderInput("cam_pos", self.camara.getPos(self.mundo))
