from panda3d.core import *

import logging
log=logging.getLogger(__name__)

class Agua:
    
    def __init__(self, mundo, nivel, longitud_lado):
        self.mundo=mundo
        #
        media_logitud_lado=longitud_lado/2.0
        plano_agua=CardMaker("plano_agua")
        plano_agua.setFrame(-media_logitud_lado, media_logitud_lado, -media_logitud_lado, media_logitud_lado)
        self.nodo=NodePath(plano_agua.generate())
        self.nodo.setP(-90.0)
        self.nodo.setZ(nivel)
        self.nodo.setTransparency(TransparencyAttrib.MAlpha)
        #
        shader=self.mundo.base.loader.loadShader('terrain/shaders/water.sha')
        self.nodo.setShaderInput('wateranim', Vec4(0.03, -0.015, 64.0, 0)) # vx, vy, scale, skip
        self.nodo.setShaderInput('waterdistort', Vec4(0.4, 4.0, 0.25, 0.45)) # offset, strength, refraction factor (0=perfect mirror, 1=total refraction), refractivity
        self.nodo.setShaderInput('time', 0)
        #
        #shader=Shader.load(Shader.SL_GLSL, vertex="shaders/agua.vert", fragment="shaders/agua.frag")
        #self.nodo.setShader(shader)
        # Reflection plane
        self.waterPlane = Plane(Vec3(0, 0, nivel + 1), Point3(0, 0, nivel))
        planeNode = PlaneNode('waterPlane')
        planeNode.setPlane(self.waterPlane)
        self.mundo.attachNewNode(planeNode)
        #
        buffer=self.mundo.base.win.makeTextureBuffer('buffer_reflejo', 512, 512)
        buffer.setClearColor(Vec4(0, 0, 0, 1))
        #
        self.watercamNP = self.mundo.base.makeCamera(buffer)
        self.watercamNP.reparentTo(self.mundo.base.render)
        #
        #cfa = CullFaceAttrib.makeReverse()
        #rs = RenderState.make(cfa)
        #
        cam = self.watercamNP.node()
        cam.getLens().setFov(self.mundo.base.camLens.getFov())
        cam.getLens().setNear(1)
        cam.getLens().setFar(5000)
        #cam.setInitialState(rs)
        #cam.setTagStateKey('Clipped')
        #
        tex0 = buffer.getTexture()
        tex0.setWrapU(Texture.WMClamp)
        tex0.setWrapV(Texture.WMClamp)
        ts0 = TextureStage('reflejo')
        self.nodo.setTexture(ts0, tex0)
        # distortion texture
        tex1 = loader.loadTexture('texturas/agua.png')
        ts1 = TextureStage('distorsion')
        self.nodo.setTexture(ts1, tex1)
    
    def update(self):
        dt=self.mundo.base.taskMgr.globalClock.getDt()
        mc=self.mundo.base.camera.getMat()
        mf=self.waterPlane.getReflectionMat()
        #self.nodo.setShaderInput('k_time', dt)
        self.watercamNP.setMat(mc * mf)
