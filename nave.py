from panda3d.core import *
from panda3d.bullet import *
from personaje import Personaje

from input import InputMapper

import logging
log=logging.getLogger(__name__)

class Nave(Personaje):
    
    # estados
    # capa 0
    EstadoReposo=Personaje.EstadoClaseDerivadaBase+1
    
    def __init__(self):
        Personaje.__init__(self, "nave")

    def iniciar(self, parent_node_path, bullet_world):
        Personaje.iniciar(self, parent_node_path, bullet_world)
        #
        shp=self.cuerpo.node().getShape(0)
        self.cuerpo.node().removeShape(shp)
        self.cuerpo.node().addShape(BulletBoxShape(Vec3(0.2,0.75,0.60)))
        self.cuerpo.node().setStatic(True)
        self.actor.setY(0.15)
        #
        self._estado_capa[0]=Nave.EstadoReposo
    
    def _definir_estado(self, idx_capa):
        # capa 0
        if idx_capa==0:
            #
            estado_actual=self._estado_capa[idx_capa]
            estado_nuevo=estado_actual
            # quieto
            if estado_actual==Personaje.EstadoQuieto:
                #->reposo
                if not self.chequear_estado(Personaje.EstadoAgarrando, 1): # ojo, podria estar agarrando otra cosa?
                    estado_nuevo=Nave.EstadoReposo
                #->elevar
                elif self.chequear_estado(Personaje.EstadoUsando, 1):
                    estado_nuevo=Personaje.EstadoSaltando
            # saltando (elevando)
            elif estado_actual==Personaje.EstadoSaltando:
                if self._altura>=5.0: # parametrizar?
                    estado_nuevo=Personaje.EstadoFlotando
            # flotando
            elif estado_actual==Personaje.EstadoFlotando:
                if self.input_mapper.accion==InputMapper.AccionAvanzar:
                       estado_nuevo=Personaje.EstadoCaminando
            # reposo
            elif estado_actual==Nave.EstadoReposo:
                #->quieto
                if self.chequear_estado(Personaje.EstadoAgarrando, 1): # ojo, podria estar agarrando otra cosa?
                    estado_nuevo=Personaje.EstadoQuieto
        # capa 1
        elif idx_capa==1:
            #
            estado_actual=Personaje._definir_estado(self, 1)
            estado_nuevo=estado_actual
            # usar
            if self.input_mapper.accion==InputMapper.AccionUsar:
                if self.chequear_estado(Personaje.EstadoQuieto, 0):
                    estado_nuevo|=Personaje.EstadoUsando
        return estado_nuevo

    def _procesar_estados(self, dt):
        # capa 0
        # saltando (elevando)
        if self._estado_capa[0]==Personaje.EstadoSaltando:
            self._velocidad_lineal=Vec3(0, 0, 0.5)
        # flotando
        elif self._estado_capa[0]==Personaje.EstadoFlotando:
            if self._velocidad_lineal.getZ()>0.0:
                self._velocidad_lineal-=Vec3(0, 0, 0.0025)
            elif self._velocidad_lineal.getZ()<0.0:
                self._velocidad_lineal.setZ(0.0)
        # caminando (avanzando)
        elif self._estado_capa[0]==Personaje.EstadoCaminando:
            param=self._params_estado
            signo_x=-1.0 if param & Personaje.ParamEstadoDerecha else 1.0
            signo_y=-1.0 if param & Personaje.ParamEstadoAdelante else 1.0
            signo_z=-1.0 if param & Personaje.ParamEstadoAbajo else 1.0
            self._velocidad_lineal=LVector3()
            if param & Personaje.ParamEstadoAdelante or param & Personaje.ParamEstadoAtras:
                self._velocidad_lineal.setY(self.rapidez_caminar * signo_y)
            if param & Personaje.ParamEstadoAbajo or param & Personaje.ParamEstadoArriba:
                self._velocidad_lineal.setZ(self.rapidez_caminar * signo_z)
            if param & Personaje.ParamEstadoGirando:
                self._velocidad_angular=LVector3(0.0, 0.0, 45.0 * self.rapidez_caminar * signo_x)
        #
        # mover, si no está quieto
        if self._estado_capa[0]!=Personaje.EstadoQuieto:
            self.cuerpo.setPos(self.cuerpo, self._velocidad_lineal * dt)
            self.cuerpo.setH(self.cuerpo, self._velocidad_angular.getZ() * dt)
        #
        # capa 1

    def _agarrar(self):
        if self.contactos:
            if not self.chequear_estado(Personaje.EstadoAgarrando, 1):
                nodo_objeto=NodePath(self.contactos[0].getNode1())
                if nodo_objeto.getName().startswith(self.prefijo_cuerpo_personaje):
                    log.debug("_agarrar %s"%(nodo_objeto.getName()))
                    self.objetos_estados[Personaje.EstadoAgarrando]=nodo_objeto
                    self.cuerpo.node().setStatic(False)
                    nodo_objeto.reparentTo(self.cuerpo)
                    nodo_objeto.setPos(0, 0.1, 0.1)
                    nodo_objeto.setHpr(0, 0, 0)
                    return True
        return False
    
    def _soltar(self):
        if Personaje.EstadoAgarrando in self.objetos_estados:
            nodo_objeto=self.objetos_estados[Personaje.EstadoAgarrando]
            if not self.cuerpo.find(nodo_objeto.getName()):
                log.debug("_soltar %s"%(nodo_objeto.getName()))
                self.cuerpo.node().setStatic(True)
                del self.objetos_estados[Personaje.EstadoAgarrando]
                return True
        return False
