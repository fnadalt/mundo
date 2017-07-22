from panda3d.core import *

import logging
log=logging.getLogger(__name__)

class Agua:
    
    def __init__(self, mundo, luz, longitud_lado):
        self.mundo=mundo
        self.camara=mundo.base.camera
        self.luz=luz
        #
        self.plano=self.mundo.base.loader.loadModel("objetos/plano_agua")
        self.plano.setScale(100.0)
        #self.plano.setTransparency(TransparencyAttrib.MAlpha)
        return
        #
        shader=Shader.load(Shader.SL_GLSL, vertex="shaders/water.v.glsl", fragment="shaders/water.f.glsl")
        self.plano.setShader(shader)
        self.plano.setShaderInput("light_pos", self.luz.getPos())
        self.plano.setShaderInput("light_color", self.luz.node().getColor())
    
    def _configurar_reflejo(self):
        reflection_plane=Plane(Vec3(0.0, 0.0, 1.0), Vec3(0.0, 0.0, self.plano.getZ()-0.15))
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
        self.plano.setTexture(ts0, tex0)

    def _configurar_refraccion(self):
        pass

    def _configurar_dudv(self):
        pass

    def _configurar_normal(self):
        pass

    def update(self, dt):
        pass
