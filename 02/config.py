# -*- coding: utf-8 -*-

from direct.showbase.DirectObject import DirectObject
from direct.gui.DirectGuiGlobals import *
from direct.gui.DirectGui import *
from panda3d.core import *

# log
import logging
log = logging.getLogger(__name__)


class EscenaConfig(DirectObject):
    """
    * configuración
    """

    Nombre = "config"

    # tipo entrada (input type)
    EntradaTexto = 0
    EntradaInt = 1
    EntradaFloat = 2
    EntradaDate = 3

    def __init__(self, contexto):
        DirectObject.__init__(self)
        # referencias
        self.contexto = contexto
        # componentes
        self.marco = None  # frame
        self.secciones = None
        self.paneles_config = dict()
        self.lbl_msj = None
        # variables internas (internal variables)
        self._rel_aspecto = 4 / 3  # screen aspect ratio

    def iniciar(self):
        log.info("iniciar")
        # variables
        self._rel_aspecto = self.contexto.base.getAspectRatio()
        # marco
        self.marco = DirectFrame(
            parent=self.contexto.base.aspect2d,
            frameColor=(0, 0.5, 0.5, 1),
            pos=(0, 0, 0)
            )
        # secciones
        self.secciones = DirectFrame(
            parent=self.marco,
            frameSize=(-0.5, 0.5, -1, 1),
            frameColor=(0.35, 0.1, 0, 1))
        # título
        DirectLabel(
            parent=self.secciones,
            text="configuración",
            scale=0.125,
            pos=(0, 0, 0.9),
            frameColor=(0, 0, 0, 0),
            text_fg=(0.9, 0.7, 0.6, 1))
        # botones
        boton = self.__crear_boton_seccion("aplicación")
        boton.setPos(0, 0, 0.7)
        boton = self.__crear_boton_seccion("mundo")
        boton.setPos(0, 0, 0.4)
        boton = self.__crear_boton_seccion("input")
        boton.setPos(0, 0, 0.1)
        boton = self.__crear_boton_seccion("terreno")
        boton.setPos(0, 0, -0.2)
        #
        boton = self.__crear_boton_seccion("guardar")  # save
        boton.setPos(0, 0, -0.6)
        boton["command"] = self._guardar
        boton["extraArgs"] = []
        boton = self.__crear_boton_seccion("cancelar")  # cancel
        boton.setPos(0, 0, -0.825)
        boton["command"] = self._cancelar
        boton["extraArgs"] = []
        # paneles
        self._crear_panel_aplic()
        self._crear_panel_mundo()
        self._crear_panel_input()
        self._crear_panel_terreno()
        # mensaje (message)
        self.lbl_msj = DirectLabel(
            parent=self.marco,
            pos=(0, 0, -0.95),
            text="mensaje mensaje mensaje mensaje mensaje mensaje",
            frameColor=(1, 1, 1, 1),
            scale=0.075,
            text_fg=(0.8, 0.1, 0.1, 1))
        self.lbl_msj.hide()
        # eventos
        self.accept("aspectRatioChanged", self._ajustar_rel_aspecto)
        #
        self._ajustar_rel_aspecto()
        self._mostrar_panel("aplicación")
        #
        return True

    def terminar(self):
        log.info("terminar")
        #
        self.secciones = None
        self.lbl_msj = None
        # paneles
        for nombre, panel in list(self.paneles_config):
            log.info("terminar panel %s" % nombre)
            panel.destroy()
        self.paneles_config = dict()
        # eventos
        self.ignoreAll()
        # marco
        if self.marco:
            self.marco.destroy()
            self.marco = None

    def _ajustar_rel_aspecto(self):
        self._rel_aspecto = self.contexto.base.getAspectRatio()
        log.debug("_ajustar_rel_aspecto -> %.3f" % self._rel_aspecto)
        # marco
        self.marco["frameSize"] = (-self._rel_aspecto, self._rel_aspecto, -1, 1)
        # secciones
        self.secciones.setPos(-self._rel_aspecto + 0.5, 0, 0)
        # paneles
        for nombre, panel in list(self.paneles_config.items()):
            panel["frameSize"] = (
                -0.6 * self._rel_aspecto,
                0.6 * self._rel_aspecto,
                -0.9, 0.9)

    def _guardar(self):
        log.info("_guardar")

    def _cancelar(self):
        log.info("_cancelar")

    def _mostrar_panel(self, nombre):
        log.info("_mostrar_panel %s" % nombre)
        for _nombre, panel in list(self.paneles_config.items()):
            log.debug(_nombre)
            if _nombre == nombre:
                log.info("se encontró panel %s" % _nombre)
                panel.show()
            else:
                panel.hide()

    def _crear_panel_aplic(self):  # create aplication (config) panel
        panel = self.__crear_panel_config("aplicación")
        #
        try:
            cfg = self.contexto.config["aplicacion"]
            escenas_basicas = cfg.get("escenas_basicas")
            escena_primera = cfg.get("escena_primera")
        except ValueError as e:
            log.exception("configuración de aplicación: %s" % str(e))
            return
        # escenas básicas
        self.__crear_label_panel(panel, 0.6, "escenas básicas")
        _input = self.__crear_input_panel(panel, 0.6, escenas_basicas,
            "aplicación.escenas_basicas", EscenaConfig.EntradaTexto)
        _input["width"] = 15
        # escena primera
        self.__crear_label_panel(panel, 0.4, "escena primera")
        self.__crear_input_panel(panel, 0.4, escena_primera,
            "aplicación.escena_primera", EscenaConfig.EntradaTexto)

    def _crear_panel_mundo(self):  # create world (config) panel
        panel = self.__crear_panel_config("mundo")
        #
        try:
            cfg = self.contexto.config["mundo"]
            atmosfera = cfg.getboolean("atmosfera")
            terreno = cfg.getboolean("terreno")
        except ValueError as e:
            log.exception("configuración de mundo: %s" % str(e))
            return
        # terreno
        self.__crear_label_panel(panel, 0.6, "terreno")
        self.__crear_check_panel(panel, 0.6, terreno, "mundo.terreno")
        # atmosfera
        self.__crear_label_panel(panel, 0.4, "atmosfera")
        self.__crear_check_panel(panel, 0.4, atmosfera, "mundo.atmosfera")

    def _crear_panel_input(self):  # create input (config) panel
        panel = self.__crear_panel_config("input")
        #
        try:
            cfg = self.contexto.config["input"]
            periodo_refresco = cfg.getfloat("periodo_refresco")
        except ValueError as e:
            log.exception("configuración de input: %s" % str(e))
            return
        #
        self.__crear_label_panel(panel, 0.6, "periodo refresco")
        self.__crear_input_panel(panel, 0.6, str(periodo_refresco),
            "input.periodo_refresco", EscenaConfig.EntradaFloat)

    def _crear_panel_terreno(self):  # create terrain (config) panel
        panel = self.__crear_panel_config("terreno")
        #
        try:
            cfg = self.contexto.config["terreno"]
            heightmap = cfg.get("heightmap")
            altura = cfg.getfloat("altura")
            factor_estiramiento = cfg.getfloat("factor_estiramiento")
            wireframe = cfg.getboolean("wireframe")
            brute_force = cfg.getboolean("brute_force")
            fisica = cfg.getboolean("fisica")
        except ValueError as e:
            log.exception("configuración de terreno: %s" % str(e))
            return
        # heightmap
        self.__crear_label_panel(panel, 0.6, "heightmap")
        self.__crear_input_panel(panel, 0.6, heightmap,
                "terreno.heightmap", EscenaConfig.EntradaTexto)
        # altura
        self.__crear_label_panel(panel, 0.4, "altura")
        self.__crear_input_panel(panel, 0.4, str(altura),
                "terreno.altura", EscenaConfig.EntradaFloat)
        # factor de estiramiento
        self.__crear_label_panel(panel, 0.2, "factor estiramiento")
        self.__crear_input_panel(panel, 0.2, str(factor_estiramiento),
                "terreno.factor_estiramiento", EscenaConfig.EntradaFloat)
        # wireframe
        self.__crear_label_panel(panel, 0.0, "wireframe")
        self.__crear_check_panel(panel, 0.0, wireframe,
            "terreno.wireframe")
        # brute force en GeoMipTerrain
        self.__crear_label_panel(panel, -0.2, "brute force (GeoMip)")
        self.__crear_check_panel(panel, -0.2, brute_force,
            "terreno.brute_force")
        # fisica
        self.__crear_label_panel(panel, -0.4, "habilitar física")
        self.__crear_check_panel(panel, -0.4, fisica,
            "terreno.fisica")

    def __crear_boton_seccion(self, texto):  # create section button
        boton = DirectButton(parent=self.secciones,
                             frameSize=(-0.35, 0.35, -0.1, 0.1),
                             frameColor=(0.35, 0.35, 0.1, 1),
                             relief="raised",
                             borderWidth=(0.01, 0.01),
                             text=texto,
                             text_scale=0.1,
                             text_fg=(0.9, 0.9, 0.9, 1),
                             command=self._mostrar_panel,
                             extraArgs=[texto]
                            )
        return boton

    def __crear_panel_config(self, titulo):
        # panel
        panel = DirectFrame(
            parent=self.marco,
            pos=(0.5, 0, 0),
            frameColor=(0.9, 0.7, 0.6, 1)
            )
        # título (title)
        DirectLabel(
            parent=panel,
            pos=(0, 0, 0.8),
            text=titulo,
            frameColor=(0, 0, 0, 0),
            scale=0.1)
        #
        self.paneles_config[titulo] = panel
        return panel

    def __crear_label_panel(self, _parent, pos_y, texto):
        _label = DirectLabel(
            parent=_parent,
            pos=(-0.5, 0, pos_y),
            frameSize=(0, 7, -0.5, 0.9),
            frameColor=(0, 0, 0, 0),
            scale=0.1,
            text=texto,
            text_pos=(3.25, 0, 0),
            text_scale=0.5,
            text_align=TextNode.ARight
            )
        return _label

    def __crear_input_panel(self, _parent, pos_y, texto_inicial,
        variable, tipo_entrada):
        _input = DirectEntry(
            parent=_parent,
            pos=(0.2, 0, pos_y),
            frameSize=(-3.5, 3.5, -0.5, 0.5),
            scale=0.1,
            initialText=texto_inicial,
            text_pos=(-3.2, 0, 0),
            text_scale=0.5
            )
        _input["focusOutCommand"] = self.__validar_entrada_texto
        _input["focusOutExtraArgs"] = [_input, tipo_entrada, variable]
        return _input

    def __crear_check_panel(self, _parent, pos_y, valor_inicial, variable):
        _check = DirectCheckButton(
            parent=_parent,
            frameSize=(-0.5, 0.5, -0.5, 0.5),
            pos=(-0.075, 0, pos_y),
            scale=0.1,
            indicatorValue=valor_inicial,
            command=self.__validar_check,
            extraArgs=[variable]
            )
        return _check

    def __validar_entrada_texto(self, entrada, tipo_entrada, variable):
        log.debug("__validar variable=%s, tipo=%i" %
                    (variable, tipo_entrada))

    def __validar_check(self, status, variable):
        log.debug("__validar variable=%s, status=%s" % (variable, str(status)))