from direct.gui.DirectFrame import DirectFrame
from direct.gui.DirectLabel import DirectLabel
from panda3d.core import *

import logging
log=logging.getLogger(__name__)

class Agua:
    
    def __init__(self, mundo, luz, altitud):
        self.base=mundo.base
        self.mundo=mundo
        self.luz=luz
        self.altitud=altitud
        #
        self.camera=base.camera
        self.camera2=None
        self.camera3=None
        self.nodo_camaras=self.camera.getParent()
        #
        self.plano=self.base.loader.loadModel("objetos/plano_agua")
        self.plano.reparentTo(self.mundo)
        self.plano.setScale(128.0)
        self.plano.setP(180.0) # paque ande el agua... maldito 1.10
        #self.plano.setTransparency(TransparencyAttrib.MAlpha)
        self.plano.setZ(self.altitud)

    def generar(self):
        #
        self.configurar_reflejo()
        self.configurar_refraccion()
        self.configurar_dudv()
        self.configurar_normal()
        self.move_factor=0.0
        # self.shader?
        #self.plano.setShaderAuto()
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
        self.reflection_buffer=self.base.win.makeTextureBuffer('reflection_buffer', 512, 512)
        self.reflection_buffer.setClearColor(Vec4(0, 0, 0, 1))
        self.camera2=self.base.makeCamera(self.reflection_buffer)
        self.camera2.reparentTo(self.nodo_camaras)
        self.camera2.node().getLens().setFov(self.camera.find("+Camera").node().getLens().getFov())
        dummy_reflection=NodePath("dummy_reflection")
        dummy_reflection.setTwoSided(False)
        dummy_reflection.setClipPlane(reflection_plane_nodeN)
        self.camera2.node().setInitialState(dummy_reflection.getState())
        #
        ts0=TextureStage("tsBuffer_reflection")
        tex0=self.reflection_buffer.getTexture()
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
        self.refraction_buffer=self.base.win.makeTextureBuffer('refraction_buffer', 512, 512)
        self.refraction_buffer.setClearColor(Vec4(0, 0, 0, 1))
        self.camera3=self.base.makeCamera(self.refraction_buffer)
        self.camera3.reparentTo(self.nodo_camaras)
        self.camera3.node().getLens().setFov(self.camera.find("+Camera").node().getLens().getFov())
        dummy_refraction=NodePath("dummy_refraction")
        dummy_refraction.setTwoSided(False)
        dummy_refraction.setClipPlane(refraction_plane_nodeN)
        self.camera3.node().setInitialState(dummy_refraction.getState())
        #
        ts1=TextureStage("tsBuffer_refraction")
        tex1=self.refraction_buffer.getTexture()
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
        #
        cam_pos=self.camera.getPos(self.plano)
        cam_hpr=self.camera.getHpr(self.plano)
        #
        self.camera2.setPos(self.plano, cam_pos)
        self.camera2.setHpr(self.plano, cam_hpr)
        self.camera2.setZ(self.plano, -cam_pos.getZ())
        self.camera2.setP(self.plano, -cam_hpr.getY())
        self.camera2.setR(self.plano, -cam_hpr.getZ())
        self.camera3.setPos(self.plano, cam_pos)
        self.camera3.setHpr(self.plano, cam_hpr)
        ref=self.plano
        self.mundo.texto1.setText("cam %s\n%s\ncam2 %s\n%s\ncam3 %s\n%s\n"%(str(self.camera.getPos(ref)), str(self.camera.getHpr(ref)), str(self.camera2.getPos(ref)), str(self.camera2.getHpr(ref)), str(self.camera3.getPos(ref)), str(self.camera3.getHpr(ref))))
        #
        self.move_factor+=0.03*dt
        self.move_factor%=1
        self.plano.setShaderInput("move_factor", self.move_factor)
        self.plano.setShaderInput("cam_pos", self.camera.getPos(self.plano))

    def dump_info(self):
        info=""
        info+="plano l:%s|%s w:%s|%s\n"%(str(self.plano.getPos()), str(self.plano.getHpr()), str(self.plano.getPos(self.mundo)), str(self.plano.getHpr(self.mundo)))
        info+="nodo  l:%s|%s w:%s|%s\n"%(str(self.nodo_camaras.getPos()), str(self.nodo_camaras.getHpr()), str(self.nodo_camaras.getPos(self.mundo)), str(self.nodo_camaras.getHpr(self.mundo)))
        info+="cam   l:%s|%s w:%s|%s\n"%(str(self.camera.getPos()), str(self.camera.getHpr()), str(self.camera.getPos(self.mundo)), str(self.camera.getHpr(self.mundo)))
        info+="cam2  l:%s|%s w:%s|%s\n"%(str(self.camera2.getPos()), str(self.camera2.getHpr()), str(self.camera2.getPos(self.mundo)), str(self.camera2.getHpr(self.mundo)))
        print(info)

    def mostrar_camaras(self):
        #
        lbl_refl=DirectLabel(text="reflejo", pos=LVector3f(-0.9, 0.8), scale=0.05)
        lbl_refl.reparentTo(self.base.aspect2d)
        frame_refl=DirectFrame(image=self.reflection_buffer.getTexture(0), scale=0.25, pos=LVector3f(-0.9, 0.5))
        frame_refl.reparentTo(self.base.aspect2d)
        #
        lbl_refr=DirectLabel(text="refraccion", pos=LVector3f(-0.9, 0.0), scale=0.05)
        lbl_refr.reparentTo(self.base.aspect2d)
        frame_refr=DirectFrame(image=self.refraction_buffer.getTexture(0), scale=0.25, pos=LVector3f(-0.9, -0.3))
        frame_refr.reparentTo(self.base.aspect2d)
