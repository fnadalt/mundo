from direct.gui.DirectGui import *
from panda3d.core import *

from shader import GestorShader
import config

import logging
log=logging.getLogger(__name__)

class Sol:

    # colores
    ColorNoche=LVector4(0.0, 0.0, 0.0, 1.0)
    ColorAmanecer=LVector4(0.95, 0.75, 0.2, 1.0)
    ColorDia=LVector4(1.0, 1.0, 0.85, 1.0)
    ColorAtardecer=LVector4(0.95, 0.65, 0.3, 1.0)

    def __init__(self, base, altitud_agua):
        # referencias:
        self.base=base
        # componentes:
        self.pivot=None
        self.nodo=None
        self.luz=None
        self.glow_camera=None
        self.glow_buffer=None
        self.blur_x_buffer=None
        self.blur_y_buffer=None
        self.buffer_sombra=None
        # variable internas:
        self._altitud_agua=altitud_agua
        self._periodo_actual=0
        self._color_inicial=Sol.ColorNoche
        self._color_final=Sol.ColorNoche
        self._color_actual=Sol.ColorNoche
        self._colores_post_pico=False
        # componentes:
        # pivot de rotacion
        self.pivot=self.base.render.attachNewNode("pivot_sol")
        self.pivot.setP(10.0) # inclinacion "estacional"
        self.pivot.setZ(self._altitud_agua)
        # esfera solar
        self.nodo=self.base.loader.loadModel("objetos/solf")
        self.nodo.reparentTo(self.pivot)
        #self.nodo.setClipPlaneOff(4)
        self.nodo.setX(300.0) # |400.0
        self.nodo.setScale(20.0)
        self.nodo.setColor((1.0, 1.0, 0.7, 1.0))
        self.nodo.node().adjustDrawMask(DrawMask(6), DrawMask(1), DrawMask(0))
        # luz direccional
        self.luz=self.nodo.attachNewNode(DirectionalLight("luz_solar"))
        self.luz.node().setColor(Vec4(1.0, 1.0, 0.7, 1.0))
        self.luz.node().setCameraMask(DrawMask(8))
        #
        if config.valbool("shader.sombras"):
            tamano=config.valint("shader.sombras_tamano_buffer")
            self.luz.node().setShadowCaster(True, tamano, tamano)
            self.luz.node().getLens().setFov(config.valint("shader.sombras_fov"))
        # init:
        self._establecer_shaders()

    def terminar(self):
        #
        if self.blur_x_buffer:
            self.base.graphicsEngine.removeWindow(self.blur_x_buffer)
        if self.blur_y_buffer:
            self.base.graphicsEngine.removeWindow(self.blur_y_buffer)
        if self.buffer_sombra:
            self.base.graphicsEngine.removeWindow(self.buffer_sombra)
        #
        if self.glow_camera:
            self.glow_camera.removeNode()
            self.glow_camera=None
        
    def obtener_info(self):
            info="Sol pos=%s roll=%.2f p=%i ci=%s cf=%s c=%s"%(str(self.nodo.getPos(self.base.render)), self.pivot.getR(), self._periodo_actual, str(self._color_inicial), str(self._color_final), str(self.luz.node().getColor()))
            return info

    def mostrar_camaras(self):
        #
        if self.glow_buffer:
            DirectLabel(text="glow_map", pos=LVector3f(1.0, 0.8), scale=0.05)
            DirectFrame(image=self.glow_buffer.getTexture(0), scale=0.25, pos=LVector3f(0.85, 0.5))
        #
        if self.blur_x_buffer:
            DirectLabel(text="blur_x_buffer", pos=LVector3f(1.0, 0.2), scale=0.05)
            DirectFrame(image=self.blur_x_buffer.getTexture(0), scale=0.25, pos=LVector3f(0.85, -0.1))
        #
        if self.blur_y_buffer:
            DirectLabel(text="blur_y_buffer", pos=LVector3f(1.0, -0.4), scale=0.05)
            DirectFrame(image=self.blur_y_buffer.getTexture(0), scale=0.25, pos=LVector3f(0.85, -0.7))
        #
        #DirectLabel(text="shadow", pos=LVector3f(0.5, -0.4), scale=0.05)
        #DirectFrame(image=self.buffer_sombra.getTexture(0), scale=0.25, pos=LVector3f(0.30, -0.7))

    def update(self, pos_pivot_camara, hora_normalizada, periodo, offset_periodo):
        # determinar periodo
        if periodo!=self._periodo_actual:
            self._periodo_actual=periodo
            self._establecer_colores(offset_periodo)
        # calcular color de la luz solar
        _offset=offset_periodo
        if (self._periodo_actual==1 or self._periodo_actual==3):
            if _offset>0.5:
                _offset-=0.5
                if not self._colores_post_pico:
                    self._establecer_colores(offset_periodo, self._color_actual)
                    self._colores_post_pico=True
            _offset*=2.0
        else:
            if self._colores_post_pico:
                self._colores_post_pico=False
            #if periodo==2:
            #    if self.shadow_camera.getR()==180.0 and offset_periodo>=0.5:
            #        self.shadow_camera.setR(0.0)
            #    elif self.shadow_camera.getR()==0.0 and offset_periodo>0.0 and offset_periodo<0.5:
            #        self.shadow_camera.setR(180.0)
        self._color_actual=self._color_inicial+((self._color_final-self._color_inicial)*_offset)
        #log.info("update p=%i _o=%.2f c=%s cpp=%s"%(periodo, _offset, str(self._color_actual), str(self._colores_post_pico)))
        self._color_actual[3]=1.0
        # componentes
        self.pivot.setPos(pos_pivot_camara)
        self.pivot.setR(360.0 * hora_normalizada)
        self.luz.lookAt(self.pivot)
        self.luz.node().setColor(self._color_actual*1.5)
        
    def _establecer_colores(self, offset_periodo, color_inicial=None):
        if self._periodo_actual==0:
            self._color_inicial=Sol.ColorNoche if not color_inicial else color_inicial
            self._color_final=Sol.ColorNoche
        elif self._periodo_actual==1:
            if offset_periodo<0.5:
                self._color_inicial=Sol.ColorNoche if not color_inicial else color_inicial
                self._color_final=Sol.ColorAmanecer
            else:
                self._color_inicial=Sol.ColorAmanecer if not color_inicial else color_inicial
                self._color_final=Sol.ColorDia
        elif self._periodo_actual==2:
            self._color_inicial=Sol.ColorDia if not color_inicial else color_inicial
            self._color_final=Sol.ColorDia
        elif self._periodo_actual==3:
            if offset_periodo<0.5:
                self._color_inicial=Sol.ColorDia if not color_inicial else color_inicial
                self._color_final=Sol.ColorAtardecer
            else:
                self._color_inicial=Sol.ColorAtardecer if not color_inicial else color_inicial
                self._color_final=Sol.ColorNoche
        #log.info("_establecer_colores p=%i offset_periodo=%.2f ci=%s cf=%s"%(self._periodo_actual, offset_periodo, str(self._color_inicial), str(self._color_final)))

    def _establecer_shaders(self):
        # glow shader
        GestorShader.aplicar(self.nodo, GestorShader.ClaseSol, 2)
        #
        if config.valbool("shader.sol_blur"):
            # glow buffer
            tamano=config.valint("shader.sol_tamano_buffer")
            self.glow_buffer = base.win.makeTextureBuffer("escena_glow", tamano, tamano)
            self.glow_buffer.setSort(-3)
            self.glow_buffer.setClearColor(LVector4(0, 0, 0, 1))
            # glow camera
            tempnode = self.base.render.attachNewNode(PandaNode("sol_temp_node"))
            tempnode.setShader(self.nodo.getShader(), priority=4)
            #tempnode.setShaderInput("plano_recorte_agua", Vec4(0, 0, 1, self._altitud_agua), priority=4)
            tempnode.setShaderInput("posicion_sol", Vec3(0, 0, 0), priority=4)
            self.glow_camera = self.base.makeCamera(self.glow_buffer, lens=self.base.cam.node().getLens())
            self.glow_camera.node().setCameraMask(DrawMask(4))
            self.glow_camera.node().setInitialState(tempnode.getState())
            # blur shaders
            self.blur_x_buffer=self._generar_buffer_filtro(self.glow_buffer, "blur_x", -2, "blur_x")
            self.blur_y_buffer= self._generar_buffer_filtro(self.blur_x_buffer, "blur_y", -1, "blur_y")
            finalcard = self.blur_y_buffer.getTextureCard()
            finalcard.reparentTo(self.base.render2d)
            finalcard.setAttrib(ColorBlendAttrib.make(ColorBlendAttrib.MAdd))
            #finalcard.hide()

    def _generar_buffer_filtro(self, buffer_base, nombre, orden, nombre_base_arch_shader):
        tamano=config.valint("shader.sol_tamano_buffer")
        blur_buffer = self.base.win.makeTextureBuffer(nombre, tamano, tamano)
        blur_buffer.setSort(orden)
        blur_buffer.setClearColor(LVector4(0, 0, 0, 1))
        blur_camera = self.base.makeCamera2d(blur_buffer)
        blur_camera.reparentTo(self.base.render) # a self.base.render?
        blur_scene = NodePath("escena_filtro_%s"%nombre)
        blur_camera.node().setScene(blur_scene)
        card = buffer_base.getTextureCard()
        card.reparentTo(blur_scene )
        shader = Shader.load(Shader.SL_GLSL, vertex="shaders/blur.v.glsl", fragment="shaders/%s.f.glsl"%nombre_base_arch_shader)
        card.setShader(shader, 1)
        return blur_buffer

    def _generar_buffer_sombra(self): # buen experimento
        #
        shadow_buffer=self.base.win.makeTextureBuffer('shadow_buffer', 512, 512)
        shadow_buffer.setClearColor(Vec4(0, 0, 0, 1))
        self.shadow_camera=self.base.makeCamera(shadow_buffer)
        self.shadow_camera.reparentTo(self.pivot)
        self.shadow_camera.node().getLens().setFov(self.base.camera.find("+Camera").node().getLens().getFov())
        self.shadow_camera.node().getLens().setNearFar(20, 100)
        dummy_sombra=self.base.render.attachNewNode("dummy_sombra")
        GestorShader.aplicar(dummy_sombra, GestorShader.ClaseSombra, 3)
        self.shadow_camera.node().setCameraMask(DrawMask(1))
        self.shadow_camera.node().setInitialState(dummy_sombra.getState())
        distancia=self.nodo.getPos() * 0.20
        self.shadow_camera.setPos(distancia)
        self.shadow_camera.setHpr(90, 0, 180.0)
        #
        return shadow_buffer
