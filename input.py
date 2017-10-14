from camara import ControladorCamara
from personaje import Personaje
from panda3d.core import KeyboardButton

import logging
log=logging.getLogger(__name__)

class InputMapper:
    
    def __init__(self, base):
        #
        self.base=base
        self.personaje=None
        #
        self._isKeyDown=self.base.mouseWatcherNode.isButtonDown
        #
        self.estado=dict() # {Personaje.Estado:bool, ...}
        self.param_estado=Personaje.ParamEstadoNulo
        #
        self._teclas=list() # ["tecla", ...]
        # camara
        self.estado[ControladorCamara.EstadoAcercando]=False
        self.estado[ControladorCamara.EstadoAlejando]=False
        self.estado[ControladorCamara.EstadoMirarAdelante]=False
        # personaje
        self.estado[Personaje.EstadoCaminando]=False
        self.estado[Personaje.EstadoCorriendo]=False
        self.estado[Personaje.EstadoSaltando]=False
        self.estado[Personaje.EstadoAgachado]=False
        self.estado[Personaje.EstadoFlotando]=False
        self.estado[Personaje.EstadoAgarrando]=False

    def chequear_falsear(self, estado):
        flag=self.estado[estado]
        self.estado[estado]=False
        return flag

    def ligar_eventos(self):
        # toggles
        # self._ligar_toggle() reemplazado por polling interface para teclado, self.update()
        #
        # "one shot"
        self._ligar_one_shot("wheel_up", ControladorCamara.EstadoAcercando)
        self._ligar_one_shot("wheel_down", ControladorCamara.EstadoAlejando)
        self._ligar_one_shot("mouse1-up", ControladorCamara.EstadoMirarAdelante)

    def desligar_eventos(self):
        for tecla in self._teclas:
            self.base.ignore(tecla)
    
    def obtener_info(self):
        info="InputMapper:\nestado:%s\nparams:%s"%(str(self.estado), str(self.param_estado))
        return info

    def update(self):
        # estados
        self.estado[Personaje.EstadoCaminando]=self._isKeyDown(KeyboardButton.asciiKey(b"w")) or self._isKeyDown(KeyboardButton.asciiKey(b"s")) or self._isKeyDown(KeyboardButton.asciiKey(b"a")) or self._isKeyDown(KeyboardButton.asciiKey(b"d"))
        self.estado[Personaje.EstadoCorriendo]=self._isKeyDown(KeyboardButton.shift())
        self.estado[Personaje.EstadoSaltando]=self._isKeyDown(KeyboardButton.space())
        # parámetros de estado
        self.param_estado=Personaje.ParamEstadoNulo
        if self._isKeyDown(KeyboardButton.asciiKey(b"w")):
            self.param_estado|=Personaje.ParamEstadoAdelante
        if self._isKeyDown(KeyboardButton.asciiKey(b"s")):
            self.param_estado|=Personaje.ParamEstadoAtras
        if self._isKeyDown(KeyboardButton.asciiKey(b"a")):
            self.param_estado|=Personaje.ParamEstadoIzquierda
        if self._isKeyDown(KeyboardButton.asciiKey(b"d")):
            self.param_estado|=Personaje.ParamEstadoDerecha
        if self._isKeyDown(KeyboardButton.asciiKey(b"q")):
            self.param_estado|=Personaje.ParamEstadoGirando | Personaje.ParamEstadoIzquierda
        if self._isKeyDown(KeyboardButton.asciiKey(b"e")):
            self.param_estado|=Personaje.ParamEstadoGirando | Personaje.ParamEstadoDerecha

    def _establecer_estado(self, flag, estado, param_estado):
        if flag:
            self.estado[estado]=True
            self.param_estado+=param_estado
        else:
            self.param_estado-=param_estado
            if self.param_estado<0:
                self.param_estado=0
            if self.param_estado==0:
                self.estado[estado]=False
    
    def _ligar_toggle(self, tecla, estado, param_estado=Personaje.ParamEstadoNulo):
        #
        self.base.accept(tecla, self._establecer_estado, [True, estado, param_estado])
        self.base.accept(tecla+"-up", self._establecer_estado, [False, estado, param_estado])
        #
        self._teclas.append(tecla)
        self._teclas.append(tecla+"-up")

    def _ligar_one_shot(self, tecla, estado, param_estado=Personaje.ParamEstadoNulo):
        #
        self.base.accept(tecla, self._establecer_estado, [True, estado, param_estado])
        #
        self._teclas.append(tecla)

