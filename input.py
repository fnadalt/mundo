from panda3d.core import KeyboardButton

import logging
log=logging.getLogger(__name__)

#
#
# InputMapper
#
#
class InputMapper:

    # acciones
    AccionNula=0
    AccionAvanzar=1
    AccionElevar=2
    AccionAgachar=3
    AccionFlotar=5
    AccionAgarrar=6
    AccionSoltar=7
    AccionArrojar=8
    AccionFrenar=9
    AccionUsar=10
    
    # parametros
    ParametroNulo=0
    ParametroAdelante=1
    ParametroAtras=2
    ParametroIzquierda=4
    ParametroDerecha=8
    ParametroArriba=16
    ParametroAbajo=32
    ParametroGirando=64
    ParametroRapido=128
    ParametroLento=256

    def __init__(self, base):
        # referencias
        self.base=base
        self.isButtonDown=self.base.mouseWatcherNode.isButtonDown
        # variables externas
        self.accion=InputMapper.AccionNula
        self.parametros=InputMapper.ParametroNulo

    def parametro(self, param):
        return (param & self.parametros)==param

    def obtener_info(self):
        info="InputMapper:\naccion:%s\nparametros:%s"%(str(self.accion), str(self.parametros))
        return info

    def update(self):
        pass

#
#
# InputMapperTecladoMouse
#
#
class InputMapperTecladoMouse(InputMapper):

    # teclas accion defecto
    TeclasAccionDefecto={KeyboardButton.enter():InputMapper.AccionArrojar, 
                        KeyboardButton.space():InputMapper.AccionElevar, 
                        KeyboardButton.tab():InputMapper.AccionUsar, 
                        KeyboardButton.control():InputMapper.AccionAgachar, 
                        KeyboardButton.alt():InputMapper.AccionAgarrar, 
                        KeyboardButton.asciiKey(b"c"):InputMapper.AccionFlotar, 
                        KeyboardButton.asciiKey(b"x"):InputMapper.AccionSoltar, 
                        KeyboardButton.asciiKey(b"z"):InputMapper.AccionFrenar, 
                        KeyboardButton.asciiKey(b"w"):InputMapper.AccionAvanzar, 
                        KeyboardButton.asciiKey(b"a"):InputMapper.AccionAvanzar, 
                        KeyboardButton.asciiKey(b"s"):InputMapper.AccionAvanzar, 
                        KeyboardButton.asciiKey(b"d"):InputMapper.AccionAvanzar, 
                        }

    # teclas parametro defecto
    TeclasParamDefecto={KeyboardButton.asciiKey(b"w"):InputMapper.ParametroAdelante, 
                        KeyboardButton.asciiKey(b"a"):InputMapper.ParametroIzquierda, 
                        KeyboardButton.asciiKey(b"s"):InputMapper.ParametroAtras, 
                        KeyboardButton.asciiKey(b"d"):InputMapper.ParametroDerecha, 
                        KeyboardButton.asciiKey(b"r"):InputMapper.ParametroArriba, 
                        KeyboardButton.asciiKey(b"f"):InputMapper.ParametroAbajo, 
                        KeyboardButton.asciiKey(b"q"):InputMapper.ParametroGirando|InputMapper.ParametroIzquierda, 
                        KeyboardButton.asciiKey(b"e"):InputMapper.ParametroGirando|InputMapper.ParametroDerecha, 
                        KeyboardButton.shift():InputMapper.ParametroRapido, 
                        KeyboardButton.asciiKey(b"v"):InputMapper.ParametroLento
                        }
    
    def __init__(self, base):
        InputMapper.__init__(self, base)

    def update(self):
        # parametros
        self.parametros=InputMapper.ParametroNulo
        for tecla, parametro in InputMapperTecladoMouse.TeclasParamDefecto.items():
            if self.isButtonDown(tecla):
                self.parametros|=parametro
        # acciones
        self.accion=InputMapper.AccionNula
        for tecla, accion in InputMapperTecladoMouse.TeclasAccionDefecto.items():
            if self.isButtonDown(tecla):
                self.accion=accion
                break

##ELIMINAR
#class InputMapper:
#    
#    def __init__(self, base):
#        #
#        self.base=base
#        self.personaje=None
#        #
#        self._isKeyDown=self.base.mouseWatcherNode.isButtonDown
#        #
#        self.estado=dict() # {Personaje.Estado:bool, ...}
#        self.param_estado=Personaje.ParamEstadoNulo
#        #
#        self._teclas=list() # ["tecla", ...]
#        # personaje
#        self.estado[Personaje.EstadoCaminando]=False
#        self.estado[Personaje.EstadoCorriendo]=False
#        self.estado[Personaje.EstadoSaltando]=False
#        self.estado[Personaje.EstadoAgachado]=False
#        self.estado[Personaje.EstadoFlotando]=False
#        self.estado[Personaje.EstadoAgarrando]=False
#
#    def obtener_info(self):
#        info="InputMapper:\nestado:%s\nparams:%s"%(str(self.estado), str(self.param_estado))
#        return info
#
#    def update(self):
#        # estados
#        self.estado[Personaje.EstadoCaminando]=self._isKeyDown(KeyboardButton.asciiKey(b"w")) or self._isKeyDown(KeyboardButton.asciiKey(b"s")) or self._isKeyDown(KeyboardButton.asciiKey(b"a")) or self._isKeyDown(KeyboardButton.asciiKey(b"d"))
#        self.estado[Personaje.EstadoCorriendo]=self._isKeyDown(KeyboardButton.shift())
#        self.estado[Personaje.EstadoSaltando]=self._isKeyDown(KeyboardButton.space())
#        # parámetros de estado
#        self.param_estado=Personaje.ParamEstadoNulo
#        if self._isKeyDown(KeyboardButton.asciiKey(b"w")):
#            self.param_estado|=Personaje.ParamEstadoAdelante
#        if self._isKeyDown(KeyboardButton.asciiKey(b"s")):
#            self.param_estado|=Personaje.ParamEstadoAtras
#        if self._isKeyDown(KeyboardButton.asciiKey(b"a")):
#            self.param_estado|=Personaje.ParamEstadoIzquierda
#        if self._isKeyDown(KeyboardButton.asciiKey(b"d")):
#            self.param_estado|=Personaje.ParamEstadoDerecha
#        if self._isKeyDown(KeyboardButton.asciiKey(b"q")):
#            self.param_estado|=Personaje.ParamEstadoGirando | Personaje.ParamEstadoIzquierda
#        if self._isKeyDown(KeyboardButton.asciiKey(b"e")):
#            self.param_estado|=Personaje.ParamEstadoGirando | Personaje.ParamEstadoDerecha
#
