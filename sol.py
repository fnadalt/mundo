from direct.gui.DirectGui import *
from panda3d.core import *

from shader import *

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
        # esfera solar
        self.nodo=self.base.loader.loadModel("objetos/solf")
        self.nodo.reparentTo(self.pivot)
        self.nodo.setClipPlaneOff(4)
        self.nodo.setX(300.0) # |400.0
        self.nodo.setScale(20.0)
        self.nodo.setColor((1.0, 1.0, 0.7, 1.0))
        self.nodo.node().adjustDrawMask(DrawMask(7), DrawMask(0), DrawMask(0))
        # luz direccional
        self.luz=self.nodo.attachNewNode(DirectionalLight("luz_solar"))
        self.luz.node().setColor(Vec4(1.0, 1.0, 0.7, 1.0))
        # init:
        self._establecer_shaders()
    
    def obtener_info(self):
            info="Sol roll=%.2f p=%i ci=%s cf=%s c=%s"%(self.pivot.getR(), self._periodo_actual, str(self._color_inicial), str(self._color_final), str(self.luz.node().getColor()))
            return info

    def mostrar_camaras(self):
        #
        DirectLabel(text="glow_map", pos=LVector3f(1.0, 0.8), scale=0.05)
        DirectFrame(image=self.glow_buffer.getTexture(0), scale=0.25, pos=LVector3f(0.85, 0.5))
        #
        DirectLabel(text="blur_x_buffer", pos=LVector3f(1.0, 0.2), scale=0.05)
        DirectFrame(image=self.blur_x_buffer.getTexture(0), scale=0.25, pos=LVector3f(0.85, -0.1))
        #
        DirectLabel(text="blur_y_buffer", pos=LVector3f(1.0, -0.4), scale=0.05)
        DirectFrame(image=self.blur_y_buffer.getTexture(0), scale=0.25, pos=LVector3f(0.85, -0.7))

    def update(self, hora_normalizada, periodo, offset_periodo):
        #
        # suprimido para dar lugar a GeneradorShader
        #self.nodo.setShaderInput("posicion_sol", self.nodo.getPos(self.base.render), 2)
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
        self._color_actual=self._color_inicial+((self._color_final-self._color_inicial)*_offset)
        #log.info("update p=%i _o=%.2f c=%s cpp=%s"%(periodo, _offset, str(self._color_actual), str(self._colores_post_pico)))
        self._color_actual[3]=1.0
        # componentes
        self.pivot.setR(360.0 * hora_normalizada)
        self.luz.lookAt(self.pivot)
        self.luz.node().setColor(self._color_actual)
        
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
        # suprimido para dar lugar a GeneradorShader
#        glow_shader=Shader.load(Shader.SL_GLSL, vertex="shaders/sol.v.glsl", fragment="shaders/sol.f.glsl")
#        self.nodo.setShaderInput("sun_wpos", self.nodo.getPos(self.base.render), 1)
#        self.nodo.setShader(glow_shader, 2)
        shader=GeneradorShader(GeneradorShader.ClaseSol, self.nodo)
        shader.cantidad_texturas=1
        #shader.activar_recorte_agua(Vec3(0, 0, 1), self._altitud_agua)
        shader.generar_aplicar()
        # glow buffer
        self.glow_buffer = base.win.makeTextureBuffer("escena_glow", 512, 512)
        self.glow_buffer.setSort(-3)
        self.glow_buffer.setClearColor(LVector4(0, 0, 0, 1))
        # glow camera
        tempnode = NodePath(PandaNode("temp_node"))
        tempnode.setShader(shader.shader, 3)
        tempnode.setShaderInput("plano_recorte_agua", Vec4(0, 0, 0, 0))
        tempnode.setShaderInput("posicion_sol", Vec3(0, 0, 0))
        glow_camera = self.base.makeCamera(self.glow_buffer, lens=self.base.cam.node().getLens())
        glow_camera.node().setInitialState(tempnode.getState())
        # blur shaders
        self.blur_x_buffer = self._generar_buffer_filtro(self.glow_buffer,  "blur_x", -2, "blur_x")
        self.blur_y_buffer= self._generar_buffer_filtro(self.blur_x_buffer,  "blur_y", -1, "blur_y")
        finalcard = self.blur_y_buffer.getTextureCard()
        finalcard.reparentTo(self.base.render2d)
        finalcard.setAttrib(ColorBlendAttrib.make(ColorBlendAttrib.MAdd))
        #finalcard.hide()

    def _generar_buffer_filtro(self, buffer_base, nombre, orden, nombre_base_arch_shader):
        blur_buffer = self.base.win.makeTextureBuffer(nombre, 512, 512)
        blur_buffer.setSort(orden)
        blur_buffer.setClearColor(LVector4(0, 0, 0, 1))
        blur_camera = self.base.makeCamera2d(blur_buffer)
        blur_scene = NodePath("escena_filtro_%s"%nombre)
        blur_camera.node().setScene(blur_scene )
        card = buffer_base.getTextureCard()
        card.reparentTo(blur_scene )
        shader = Shader.load(Shader.SL_GLSL, vertex="shaders/blur.v.glsl", fragment="shaders/%s.f.glsl"%nombre_base_arch_shader)
        card.setShader(shader, 1)
        return blur_buffer
