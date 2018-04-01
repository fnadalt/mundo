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
        # personaje
        self.estado[Personaje.EstadoCaminando]=False
        self.estado[Personaje.EstadoCorriendo]=False
        self.estado[Personaje.EstadoSaltando]=False
        self.estado[Personaje.EstadoAgachado]=False
        self.estado[Personaje.EstadoFlotando]=False
        self.estado[Personaje.EstadoAgarrando]=False

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

