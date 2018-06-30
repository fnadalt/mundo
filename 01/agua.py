from direct.gui.DirectFrame import DirectFrame
from direct.gui.DirectLabel import DirectLabel
from panda3d.core import *

from shader import GestorShader
import config

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
        self.reflection_buffer=None
        self.refraction_buffer=None
        #
        self.nodo=self.base.loader.loadModel("objetos/plano_agua")
        self.nodo.setZ(self.altitud)
        self.nodo.node().adjustDrawMask(DrawMask(1), DrawMask(2), DrawMask(0))

    def terminar(self):
        if self.reflection_buffer:
            self.base.graphicsEngine.removeWindow(self.reflection_buffer)
        if self.refraction_buffer:
            self.base.graphicsEngine.removeWindow(self.refraction_buffer)
 
    def generar(self):
        #
        self.configurar_dudv()
        self.configurar_normal()
        if config.valbool("shader.agua_reflejo_refraccion"):
            self.configurar_reflejo()
            self.configurar_refraccion()
        self.factor_movimiento_agua=0.0
        self.shader=GestorShader.aplicar(self.nodo, GestorShader.ClaseAgua, 2)

    def configurar_reflejo(self):
        #
        tamano=config.valint("shader.agua_tamano_buffer")
        self.reflection_buffer=self.base.win.makeTextureBuffer('reflection_buffer', tamano, tamano)
        self.reflection_buffer.setClearColor(Vec4(0, 0, 0, 1)) # quitar?
        self.camera2=self.base.makeCamera(self.reflection_buffer, camName="cam_reflejo")
        self.camera2.reparentTo(self.nodo)
        self.camera2.node().getLens().setFov(self.camera.find("+Camera").node().getLens().getFov())
        dummy_reflection=NodePath("dummy_reflection") # antes, base.render.attachNewNode
        #dummy_reflection.setShaderInput("plano_recorte_agua", Vec4(0, 0, 1, self.altitud), priority=3)
        #dummy_reflection.setShaderInput("altitud_agua", 150.0, 0.0, 0.0, 0.0, priority=2)
        self.camera2.node().setCameraMask(DrawMask(2))
        self.camera2.node().setInitialState(dummy_reflection.getState())
        #
        ts2=TextureStage("tsBuffer_reflection")
        tex2=self.reflection_buffer.getTexture(0)
        tex2.setWrapU(Texture.WMClamp)
        tex2.setWrapV(Texture.WMClamp)
        self.nodo.setTexture(ts2, tex2)
        
    def configurar_refraccion(self):
        #
        tamano=config.valint("shader.agua_tamano_buffer")
        self.refraction_buffer=self.base.win.makeTextureBuffer('refraction_buffer', tamano, tamano)
        self.refraction_buffer.setClearColor(Vec4(0, 0, 0, 1))
        self.camera3=self.base.makeCamera(self.refraction_buffer, camName="cam_refraccion")
        self.camera3.reparentTo(self.nodo)
        self.camera3.node().getLens().setFov(self.camera.find("+Camera").node().getLens().getFov())
        dummy_refraction=NodePath("dummy_refraction")
        #dummy_refraction.setShaderInput("plano_recorte_agua", Vec4(0, 0, -1, -self.altitud), priority=4)
        dummy_refraction.setShaderInput("altitud_agua", -self.altitud, 0.0, 0.0, 0.0, priority=5)
        self.camera3.node().setCameraMask(DrawMask(2))
        self.camera3.node().setInitialState(dummy_refraction.getState())
        #
        ts3=TextureStage("tsBuffer_refraction")
        tex3=self.refraction_buffer.getTexture(0)
        tex3.setWrapU(Texture.WMClamp)
        tex3.setWrapV(Texture.WMClamp)
        self.nodo.setTexture(ts3, tex3)
    
    def configurar_dudv(self):
        ts0=TextureStage("tsBuffer_dudv")
        tex0=self.base.loader.loadTexture("texturas/agua_dudv2.png")
        tex0.setWrapU(Texture.WMRepeat)
        tex0.setWrapV(Texture.WMRepeat)
        self.nodo.setTexture(ts0, tex0)
    
    def configurar_normal(self):
        ts1=TextureStage("tsBuffer_normal")
        tex1=self.base.loader.loadTexture("texturas/agua_normal2.png")
        tex1.setWrapU(Texture.WMRepeat)
        tex1.setWrapV(Texture.WMRepeat)
        self.nodo.setTexture(ts1, tex1)
    
    def update(self, dt, pos_luz, color_luz):
        #self._posicionar_camaras()
        self._posicionar_camaras_2()
        #
        self.factor_movimiento_agua+=0.02*dt
        self.factor_movimiento_agua%=1
        ref=self.nodo # self.nodo|self.base.render
        self.nodo.setShaderInput("factor_movimiento_agua", self.factor_movimiento_agua, priority=2)
        self.nodo.setShaderInput("posicion_camara", self.camera.getPos(ref), priority=2)

    def obtener_info(self):
        _dot=self.nodo.getPos(self.base.render)-self.camera.getPos(self.base.render)
        _dot=_dot.dot(Vec3(0, 1, 0))
        info="Agua:\n"
        info+="plano l:%s|%s\n"%(str(self.nodo.getPos()), str(self.nodo.getHpr()))
        info+="      r:%s|%s\n"%(str(self.nodo.getPos(self.base.render)), str(self.nodo.getHpr(self.base.render)))
        info+="cam l:%s|%s\n"%(str(self.camera.getPos()), str(self.camera.getHpr()))
        info+="    r:%s|%s\n"%(str(self.camera.getPos(self.base.render)), str(self.camera.getHpr(self.base.render)))
        info+="    s:%s|%s\n"%(str(self.camera.getPos(self.nodo)), str(self.camera.getHpr(self.nodo)))
        info+="    dot: %s\n"%(str(_dot))
        if self.camera2:
            info+="cam2 l:%s|%s\n"%(str(self.camera2.getPos()), str(self.camera2.getHpr()))
            info+="     r:%s|%s\n"%(str(self.camera2.getPos(self.base.render)), str(self.camera2.getHpr(self.base.render)))
        if self.camera3:
            info+="cam3 l:%s|%s\n"%(str(self.camera3.getPos()), str(self.camera3.getHpr()))
            info+="     r:%s|%s\n"%(str(self.camera3.getPos(self.base.render)), str(self.camera3.getHpr(self.base.render)))
        return info

    def mostrar_camaras(self):
        #
        if self.reflection_buffer:
            lbl_refl=DirectLabel(text="reflejo", pos=LVector3f(-1.05, -0.4), scale=0.05)
            lbl_refl.reparentTo(self.base.aspect2d)
            frame_refl=DirectFrame(image=self.reflection_buffer.getTexture(0), scale=0.25, pos=LVector3f(-1.05, -0.7))
            frame_refl.reparentTo(self.base.aspect2d)
        #
        if self.refraction_buffer:
            lbl_refr=DirectLabel(text="refraccion", pos=LVector3f(-0.5, -0.4), scale=0.05)
            lbl_refr.reparentTo(self.base.aspect2d)
            frame_refr=DirectFrame(image=self.refraction_buffer.getTexture(0), scale=0.25, pos=LVector3f(-0.5, -0.7))
            frame_refr.reparentTo(self.base.aspect2d)

    def _posicionar_camaras(self):
        #
        cam_pos=self.camera.getPos(self.nodo)
        cam_hpr=self.camera.getHpr(self.nodo)
        #
        if self.camera2:
            self.camera2.setPos(self.nodo, cam_pos)
            self.camera2.setZ(self.nodo, -cam_pos.getZ())
            self.camera2.setH(self.nodo, cam_hpr.getX())
            self.camera2.setP(self.nodo, -cam_hpr.getY())
            self.camera2.setR(self.nodo, -cam_hpr.getZ())
        #
        if self.camera3:
            self.camera3.setPos(self.nodo, cam_pos)
            self.camera3.setHpr(self.nodo, cam_hpr)

    def _posicionar_camaras_2(self):
        #
        cam_pos=self.camera.getPos(self.base.render)
        cam_hpr=self.camera.getHpr(self.base.render)
        sup_pos=self.nodo.getPos(self.base.render)
        #
        if self.camera2:
            self.camera2.setPos(self.base.render, cam_pos)
            self.camera2.setZ(self.base.render, sup_pos.getZ()-(cam_pos.getZ()-sup_pos.getZ()))
            self.camera2.setH(self.base.render, cam_hpr.getX())
            self.camera2.setP(self.base.render, -cam_hpr.getY())
            self.camera2.setR(self.base.render, -cam_hpr.getZ())
        #
        if self.camera3:
            self.camera3.setPos(self.base.render, cam_pos)
            self.camera3.setHpr(self.base.render, cam_hpr)
