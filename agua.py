from direct.gui.DirectFrame import DirectFrame
from direct.gui.DirectLabel import DirectLabel
from panda3d.core import *

import logging
log=logging.getLogger(__name__)

class Agua:
    
    def __init__(self, base, altitud):
        self.base=base
        self.altitud=altitud
        #
        self.camera=self.base.camera
        self.camera2=None
        self.camera3=None
        #
        self.superficie=self.base.loader.loadModel("objetos/plano_aguaf")
        self.superficie.setZ(self.altitud)
        self.superficie.hide()#
        #self.superficie.node().adjustDrawMask(DrawMask(5), DrawMask(0), DrawMask(0))

    def generar(self):
        #
        self.configurar_reflejo()
        self.configurar_refraccion()
        self.configurar_dudv()
        self.configurar_normal()
        self.move_factor=0.0
        # self.shader?
        shader=Shader.load(Shader.SL_GLSL, vertex="shaders/agua.v.glsl", fragment="shaders/agua.f.glsl")
        self.superficie.setShader(shader, 1)
        self.superficie.setShaderInput("altitud_agua", self.altitud)

    def configurar_reflejo(self):
        # reflejo
        reflection_plane=Plane(Vec3(0.0, 0.0, -1.0), Vec3(0.0, 0.0, 0.0)) # self.altitud-0.15
        reflection_plane_node=PlaneNode("reflection_plane_node")
        reflection_plane_node.setPlane(reflection_plane)
        self.reflection_plane_nodeN=self.base.render.attachNewNode(reflection_plane_node)
        self.reflection_plane_nodeN.setPos(-937, -323, 150)
        #self.reflection_plane_nodeN.show()
        #
        self.reflection_buffer=self.base.win.makeTextureBuffer('reflection_buffer', 512, 512)
        self.reflection_buffer.setClearColor(Vec4(0, 0, 0, 1))
        self.camera2=self.base.makeCamera(self.reflection_buffer)
        self.camera2.reparentTo(self.base.render)
        self.camera2.node().getLens().setFov(self.camera.find("+Camera").node().getLens().getFov())
        dummy_reflection=NodePath("dummy_reflection")
        dummy_shader=Shader.load(Shader.SL_GLSL, vertex="shaders/debug.v.glsl",  fragment="shaders/debug.f.glsl")
        #dummy_reflection.setShader(dummy_shader, 20)
        dummy_reflection.setShaderInput("clipo_dir", 1.0)
        #dummy_reflection.setTwoSided(False)
        #dummy_reflection.setClipPlane(self.reflection_plane_nodeN)
        #self.camera2.node().setCameraMask(DrawMask(5))
        self.camera2.node().setInitialState(dummy_reflection.getState())
        #
        ts0=TextureStage("tsBuffer_reflection")
        tex0=self.reflection_buffer.getTexture()
        tex0.setWrapU(Texture.WMClamp)
        tex0.setWrapV(Texture.WMClamp)
        self.superficie.setTexture(ts0, tex0)
        
    def configurar_refraccion(self):
        # refraccion
        refraction_plane=Plane(Vec3(0.0, 0.0, -1.0), Vec3(0.0, 0.0, self.altitud+0.1)) # self.altitud+0.1
        refraction_plane_node=PlaneNode("refraction_plane_node")
        refraction_plane_node.setPlane(refraction_plane)
        #self.refraction_plane_nodeN=self.base.render.attachNewNode(refraction_plane_node)
        #
        self.refraction_buffer=self.base.win.makeTextureBuffer('refraction_buffer', 512, 512)
        self.refraction_buffer.setClearColor(Vec4(0, 0, 0, 1))
        self.camera3=self.base.makeCamera(self.refraction_buffer)
        self.camera3.reparentTo(self.base.render)
        self.camera3.node().getLens().setFov(self.camera.find("+Camera").node().getLens().getFov())
        dummy_refraction=NodePath("dummy_refraction")
        dummy_shader=Shader.load(Shader.SL_GLSL, vertex="shaders/debug.v.glsl",  fragment="shaders/debug.f.glsl")
        dummy_refraction.setShader(dummy_shader, 21)
        dummy_refraction.setShaderInput("clipo_dir", -1.0)
        #dummy_refraction.setTwoSided(False)
        #dummy_refraction.setClipPlane(self.refraction_plane_nodeN)
        #self.camera3.node().setCameraMask(DrawMask(5))
        self.camera3.node().setInitialState(dummy_refraction.getState())
        #
        ts1=TextureStage("tsBuffer_refraction")
        tex1=self.refraction_buffer.getTexture()
        tex1.setWrapU(Texture.WMClamp)
        tex1.setWrapV(Texture.WMClamp)
        self.superficie.setTexture(ts1, tex1)
    
    def configurar_dudv(self):
        ts2=TextureStage("tsBuffer_dudv")
        tex2=self.base.loader.loadTexture("texturas/agua_dudv.png")
        tex2.setWrapU(Texture.WMRepeat)
        tex2.setWrapV(Texture.WMRepeat)
        self.superficie.setTexture(ts2, tex2)
    
    def configurar_normal(self):
        ts3=TextureStage("tsBuffer_normal")
        tex3=self.base.loader.loadTexture("texturas/agua_normal.png")
        tex3.setWrapU(Texture.WMRepeat)
        tex3.setWrapV(Texture.WMRepeat)
        self.superficie.setTexture(ts3, tex3)
    
    def update(self, dt, pos_luz, color_luz):
        #self._posicionar_camaras()
        self._posicionar_camaras_2()
        #
        ref=self.base.render
        #
        self.move_factor+=0.03*dt
        self.move_factor%=1
        self.superficie.setShaderInput("move_factor", self.move_factor)
        self.superficie.setShaderInput("cam_pos", self.camera.getPos(ref)) # self.superficie|self.base.render
        #pos_luz=Vec4(0, 0, 10, 1) # fijar, para debug
        self.superficie.setShaderInput("light_pos", pos_luz)
        self.superficie.setShaderInput("light_color", color_luz)

    def obtener_info(self):
        _dot=self.superficie.getPos(self.base.render)-self.camera.getPos(self.base.render)
        _dot=_dot.dot(Vec3(0, 1, 0))
        info="Agua:\n"
        info+="plano l:%s|%s\n"%(str(self.superficie.getPos()), str(self.superficie.getHpr()))
        info+="      r:%s|%s\n"%(str(self.superficie.getPos(self.base.render)), str(self.superficie.getHpr(self.base.render)))
        info+="cam l:%s|%s\n"%(str(self.camera.getPos()), str(self.camera.getHpr()))
        info+="    r:%s|%s\n"%(str(self.camera.getPos(self.base.render)), str(self.camera.getHpr(self.base.render)))
        info+="    s:%s|%s\n"%(str(self.camera.getPos(self.superficie)), str(self.camera.getHpr(self.superficie)))
        info+="    dot: %s\n"%(str(_dot))
        info+="cam2 l:%s|%s\n"%(str(self.camera2.getPos()), str(self.camera2.getHpr()))
        info+="     r:%s|%s\n"%(str(self.camera2.getPos(self.base.render)), str(self.camera2.getHpr(self.base.render)))
        info+="cam3 l:%s|%s\n"%(str(self.camera3.getPos()), str(self.camera3.getHpr()))
        info+="     r:%s|%s\n"%(str(self.camera3.getPos(self.base.render)), str(self.camera3.getHpr(self.base.render)))
        return info

    def mostrar_camaras(self):
        #
        lbl_refl=DirectLabel(text="reflejo", pos=LVector3f(-1.05, -0.4), scale=0.05)
        lbl_refl.reparentTo(self.base.aspect2d)
        frame_refl=DirectFrame(image=self.reflection_buffer.getTexture(0), scale=0.25, pos=LVector3f(-1.05, -0.7))
        frame_refl.reparentTo(self.base.aspect2d)
        #
        lbl_refr=DirectLabel(text="refraccion", pos=LVector3f(-0.5, -0.4), scale=0.05)
        lbl_refr.reparentTo(self.base.aspect2d)
        frame_refr=DirectFrame(image=self.refraction_buffer.getTexture(0), scale=0.25, pos=LVector3f(-0.5, -0.7))
        frame_refr.reparentTo(self.base.aspect2d)

    def _posicionar_camaras(self):
        #
        cam_pos=self.camera.getPos(self.superficie)
        cam_hpr=self.camera.getHpr(self.superficie)
        #
        self.camera2.setPos(self.superficie, cam_pos)
        self.camera2.setZ(self.superficie, -cam_pos.getZ())
        self.camera2.setH(self.superficie, cam_hpr.getX())
        self.camera2.setP(self.superficie, -cam_hpr.getY())
        self.camera2.setR(self.superficie, -cam_hpr.getZ())
        #
        self.camera3.setPos(self.superficie, cam_pos)
        self.camera3.setHpr(self.superficie, cam_hpr)

    def _posicionar_camaras_2(self):
        #
        cam_pos=self.camera.getPos(self.base.render)
        cam_hpr=self.camera.getHpr(self.base.render)
        sup_pos=self.superficie.getPos(self.base.render)
        #
        self.camera2.setPos(self.base.render, cam_pos)
        self.camera2.setZ(self.base.render, sup_pos.getZ()-(cam_pos.getZ()-sup_pos.getZ()))
        self.camera2.setH(self.base.render, cam_hpr.getX())
        self.camera2.setP(self.base.render, -cam_hpr.getY())
        self.camera2.setR(self.base.render, -cam_hpr.getZ())
        #
        self.camera3.setPos(self.base.render, cam_pos)
        self.camera3.setHpr(self.base.render, cam_hpr)
