from panda3d.core import *

import logging
log=logging.getLogger(__name__)

class Agua2:
    
    def __init__(self, mundo, luz, altitud):
        self.mundo=mundo
        self.camara=mundo.base.camera
        self.cam=self.camara.find("+Camera")
        self.luz=luz
        self.altitud=altitud
        #
        self.plano=self.mundo.base.loader.loadModel("objetos/plano_agua")
        self.agua.plano.reparentTo(self)
        self.plano.setScale(1.0)
        self.agua.plano.setZ(self.altitud)
        #self.plano.setTransparency(TransparencyAttrib.MAlpha)
        #
        self.move_factor=0.0

    def generar(self):
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
        reflection_plane=Plane(Vec3(0.0, 0.0, 1.0), Vec3(0.0, 0.0, 0.0)) #-0.15
        reflection_plane_node=PlaneNode("reflection_plane_node")
        reflection_plane_node.setPlane(reflection_plane)
        reflection_plane_nodeN=self.mundo.attachNewNode(reflection_plane_node)
        #reflection_plane_nodeN.setZ(self.plano.getZ())
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

class Agua:
    
    def __init__(self, mundo, luz, altitud):
        self.base=mundo.base
        self.camera=self.base.camera
        self.nodo_camaras=self.camera.getParent()
        self.mundo=mundo
        self.luz=luz
        self.altitud=altitud
        #
        self.camera=base.camera
        self.camera2=None
        self.camera3=None
        #
        self.plano=self.base.loader.loadModel("objetos/plano_agua")
        self.plano.reparentTo(self.mundo)
        self.plano.setScale(1.0)
        self.plano.setTransparency(TransparencyAttrib.MAlpha)
        self.plano.setZ(self.altitud)

    def generar(self):
        #
        self.configurar_reflejo()
        self.configurar_refraccion()
        self.configurar_dudv()
        self.configurar_normal()
        self.move_factor=0.0
        # self.shader?
        shader=Shader.load(Shader.SL_GLSL, vertex="shaders/agua.v.glsl", fragment="shaders/agua.f.glsl")
        self.plano.setShader(shader)
        self.plano.setShaderInput("light_pos", self.luz.getPos())
        self.plano.setShaderInput("light_color", self.luz.node().getColor())

    def configurar_reflejo(self):
        # reflejo
        reflection_plane=Plane(Vec3(0.0, 0.0, 1.0), Vec3(0.0, 0.0, self.altitud-0.15))
        reflection_plane_node=PlaneNode("reflection_plane_node")
        reflection_plane_node.setPlane(reflection_plane)
        reflection_plane_nodeN=self.mundo.attachNewNode(reflection_plane_node)
        #
        reflection_buffer=self.base.win.makeTextureBuffer('reflection_buffer', 512, 512)
        reflection_buffer.setClearColor(Vec4(0, 0, 0, 1))
        self.camera2=self.base.makeCamera(reflection_buffer)
        self.camera2.reparentTo(self.nodo_camaras)
        self.camera2.node().getLens().setFov(self.camera.find("+Camera").node().getLens().getFov())
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
        
    def configurar_refraccion(self):
        # refraccion
        refraction_plane=Plane(Vec3(0.0, 0.0, -1.0), Vec3(0.0, 0.0, self.altitud+0.1))
        refraction_plane_node=PlaneNode("refraction_plane_node")
        refraction_plane_node.setPlane(refraction_plane)
        refraction_plane_nodeN=self.mundo.attachNewNode(refraction_plane_node)
        #
        refraction_buffer=self.base.win.makeTextureBuffer('refraction_buffer', 512, 512)
        refraction_buffer.setClearColor(Vec4(0, 0, 0, 1))
        self.camera3=self.base.makeCamera(refraction_buffer)
        self.camera3.reparentTo(self.nodo_camaras)
        self.camera3.node().getLens().setFov(self.camera.find("+Camera").node().getLens().getFov())
        dummy_refraction=NodePath("dummy_refraction")
        dummy_refraction.setTwoSided(False)
        dummy_refraction.setClipPlane(refraction_plane_nodeN)
        self.camera3.node().setInitialState(dummy_refraction.getState())
        #
        ts1=TextureStage("tsBuffer_refraction")
        tex1=refraction_buffer.getTexture()
        tex1.setWrapU(Texture.WMClamp)
        tex1.setWrapV(Texture.WMClamp)
        self.plano.setTexture(ts1, tex1)
    
    def configurar_dudv(self):
        ts2=TextureStage("tsBuffer_dudv")
        tex2=self.base.loader.loadTexture("texturas/agua_dudv.png")
        tex2.setWrapU(Texture.WMRepeat)
        tex2.setWrapV(Texture.WMRepeat)
        self.plano.setTexture(ts2, tex2)
    
    def configurar_normal(self):
        ts3=TextureStage("tsBuffer_normal")
        tex3=self.base.loader.loadTexture("texturas/agua_normal.png")
        tex3.setWrapU(Texture.WMRepeat)
        tex3.setWrapV(Texture.WMRepeat)
        self.plano.setTexture(ts3, tex3)
    
    def update(self, dt):
        self.camera2.setPos(self.camera.getPos())
        self.camera2.setHpr(self.camera.getHpr())
        self.camera2.setZ(-self.camera.getZ()-2.0*self.nodo_camaras.getZ())
        self.camera2.setP(-self.camera.getP())
        self.camera2.setR(-self.camera.getR())
        self.camera3.setPos(self.camera.getPos())
        self.camera3.setHpr(self.camera.getHpr())
        self.camera3.setP(self.camera.getP())
        ref=self.mundo
        self.mundo.texto1.setText("cam %s %s\ncam2 %s %s\ncam3 %s %s"%(str(self.camera.getPos(ref)), str(self.camera.getHpr(ref)), str(self.camera2.getPos(ref)), str(self.camera2.getHpr(ref)), str(self.camera3.getPos(ref)), str(self.camera3.getHpr(ref))))
        #
        self.move_factor+=0.03*dt
        self.move_factor%=1
        self.plano.setShaderInput("move_factor", self.move_factor)
        self.plano.setShaderInput("cam_pos", self.camera.getPos(self.mundo))

    def dump_info(self):
        info=""
        info+="plano l:%s|%s w:%s|%s\n"%(str(self.plano.getPos()), str(self.plano.getHpr()), str(self.plano.getPos(self.mundo)), str(self.plano.getHpr(self.mundo)))
        info+="nodo  l:%s|%s w:%s|%s\n"%(str(self.nodo_camaras.getPos()), str(self.nodo_camaras.getHpr()), str(self.nodo_camaras.getPos(self.mundo)), str(self.nodo_camaras.getHpr(self.mundo)))
        info+="cam   l:%s|%s w:%s|%s\n"%(str(self.camera.getPos()), str(self.camera.getHpr()), str(self.camera.getPos(self.mundo)), str(self.camera.getHpr(self.mundo)))
        info+="cam2  l:%s|%s w:%s|%s\n"%(str(self.camera2.getPos()), str(self.camera2.getHpr()), str(self.camera2.getPos(self.mundo)), str(self.camera2.getHpr(self.mundo)))
        print info
