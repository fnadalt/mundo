from direct.actor.Actor import Actor
from panda3d.bullet import *
from panda3d.core import *
import os, os.path

from input import InputMapper
from shader import GestorShader

import logging
log=logging.getLogger(__name__)

#
#
# PERSONAJE
#
#
class Personaje:
    
##    ELIMINAR
#    # ambiente
#    AmbienteNulo=0
#    AmbienteAire=1
#    AmbienteAgua=2
    
    # suelo
    SueloNulo=0
    SueloGenerico=1
    SueloEscalera=2
    SueloPendienteSubida=3
    SueloPendienteBajada=4
    
    # estados
    EstadoNulo=0
    # capa 0
    EstadoQuieto=1
    EstadoCaminando=2
    EstadoCorriendo=3
    EstadoSaltando=4
    EstadoFlotando=5
    EstadoCayendo=6
    EstadoConduciendo=7
    # capa 1
    EstadoAgachado=16
    EstadoAgarrando=17
    
    # parametros de estados
    ParamEstadoNulo=0
    ParamEstadoAdelante=1
    ParamEstadoAtras=2
    ParamEstadoIzquierda=4
    ParamEstadoDerecha=8
    ParamEstadoArriba=16
    ParamEstadoAbajo=32
    ParamEstadoGirando=64

    def __init__(self, clase):
        # variables internas
#        self._ambiente=self.AmbienteNulo ELIMINAR
        self._suelo=self.SueloNulo
        self._partes_actor=list() # [] | [nombre_parte, ...]
        self._estado_capa=[self.EstadoNulo, self.EstadoNulo] # [estado,estado,estado]
        self._params_estado=self.ParamEstadoNulo
        self._altura=0.0
        self._velocidad_lineal=LVector3()
        self._velocidad_angular=LVector3() # grados
        self._ajuste_altura=0.0
        # variables externas
        self.altitud_suelo=0.0
        self.altitud_agua=0.0
        # parametros
        self.directorio_recursos="personajes"
        self.clase=clase
        self.prefijo_cuerpo_suelo="cuerpo_suelo_"
        self.rapidez_caminar=1.0 # multiplicador
        self.rapidez_correr=2.0 # multiplicador
        # referencias
        self.input_mapper=None
        self.bullet_world=None
        # componentes
        self.cuerpo=None
        self.actor=None
    
    def iniciar(self, parent_node_path, bullet_world, partes=list()):
        log.info("iniciar")
        # recursos
        ruta_dir=os.path.join(os.getcwd(), self.directorio_recursos, self.clase)
        if not os.path.exists(ruta_dir):
            raise Exception("no existe el directorio '%s'"%(ruta_dir))
        archivos=[archivo for archivo in os.listdir(ruta_dir) if archivo[-4:].lower()==".egg" or archivo[-4:].lower()==".bam"]
        archivo_actor=""
        dict_animaciones=dict()
        for archivo in archivos:
            if archivo[:-4]=="actor":
                archivo_actor=archivo
            else:
                dict_animaciones[archivo[:-4]]=Filename.fromOsSpecific(os.path.join(ruta_dir, archivo))
        if archivo_actor=="":
            raise Exception("no se encontró ningún archivo de actor (actor.[egg|bam]) en '%s'"%ruta_dir)
        # cuerpo
        self.bullet_world=bullet_world
        shp=BulletCapsuleShape(0.25, 0.5, ZUp)
        rb=BulletRigidBodyNode("cuerpo_personaje_%s"%self.clase)
        rb.setMass(70.0)
        rb.addShape(shp)
        rb.setKinematic(True)
        self.bullet_world.attach(rb)
        self.cuerpo=parent_node_path.attachNewNode(rb)
        self.cuerpo.setCollideMask(BitMask32.bit(2))
        self._ajuste_altura=rb.getShapeBounds().getRadius()
        # actor
        self.actor=Actor(Filename.fromOsSpecific(os.path.join(ruta_dir, archivo_actor)), dict_animaciones)
        self.actor.reparentTo(self.cuerpo)
        self.actor.setZ(-self._ajuste_altura)
        # partes
        for parte in partes:
            self.actor.makeSubpart(parte[0], parte[1], parte[2])
        # establecer estado inicial Quieto
        self._estado_capa[0]=Personaje.EstadoQuieto
        self._cambio_estado(0, Personaje.EstadoNulo, Personaje.EstadoQuieto)
        # shader
        GestorShader.aplicar(self.actor, GestorShader.ClasePersonaje, 2)
    
    def terminar(self):
        log.info("terminar")
        self.actor.delete()
        self.bullet_world.remove(self.cuerpo.node())
        self.actor=None
        self.cuerpo=None
        self.input_mapper=None
        self.bullet_world=None
    
    def setPos(self, posicion):
        _posicion=Vec3(posicion[0], posicion[1], posicion[2]+self._ajuste_altura)
        self.cuerpo.setPos(_posicion)

    def chequear_estado(self, estado):
        if estado>15: # capa 1
            return estado==self._estado_capa[1]
        elif estado>0: # capa 0
            return estado==self._estado_capa[0]
    
    def update(self, dt):
        # definir ambiente y suelo
        #self._definir_ambiente() ELIMINAR
        self._definir_suelo()
        # definir estados
        for idx_capa in range(len(self._estado_capa)):
            estado_nuevo=self._definir_estado(idx_capa)
            if self._estado_capa[idx_capa]!=estado_nuevo:
                # procesar cambio de estado
                self._cambio_estado(idx_capa, self._estado_capa[idx_capa], estado_nuevo)
                self._estado_capa[idx_capa]=estado_nuevo
        # verificar cambio de parametros
        param_estado_nuevo=self.input_mapper.parametros
        if self._params_estado!=param_estado_nuevo:
            # procesar cambio en parametros
            self._cambio_params(self._params_estado, param_estado_nuevo)
            self._params_estado=param_estado_nuevo
        # procesar estados
        self._procesar_estados(dt)
        # altura desde el suelo (se encuentra al final para ser evaluada en forma porterior)
        self._altura=self.cuerpo.getZ()-self.altitud_suelo-0.5

    def obtener_info(self):
        info="Personaje:BulletRigidBodyNode vl=%s va=%s\n"%(str(self.cuerpo.node().getLinearVelocity()), str(self.cuerpo.node().getAngularVelocity()))
        info+="velocidad_lineal=%s velocidad_angular=%s\n"%(str(self._velocidad_lineal), str(self._velocidad_angular))
        info+="posicion=%s altitud_suelo=%s altura=%s\n"%(str(self.cuerpo.getPos()), str(self.altitud_suelo), str(self._altura))
        info+="ambiente=%s suelo=%s\n"%(str(self._ambiente), str(self._suelo))
        info+="estado=%s params=%s\n"%(str(self._estado_capa), str(self._params_estado))
        return info

##    ELIMINAR
#    def _definir_ambiente(self):
#        if self._ambiente != Personaje.AmbienteAire:
#            self._ambiente=Personaje.AmbienteAire
        
    def _definir_suelo(self):
        if self._suelo!=Personaje.SueloNulo and self._altura>0.5:
            self._suelo=Personaje.SueloNulo
        elif self._suelo==Personaje.SueloNulo and self._altura<0.05:
            self._suelo=Personaje.SueloGenerico

    def _definir_estado(self, idx_capa):
        #
        estado_actual=self._estado_capa[idx_capa]
        estado_nuevo=estado_actual
        # capa 0
        if idx_capa==0:
            # quieto
            if estado_actual==Personaje.EstadoQuieto:
                #->caminar
                if self.input_mapper.accion==InputMapper.AccionAvanzar:
                    estado_nuevo=Personaje.EstadoCaminando
                    #->correr
                    if self.input_mapper.parametro(InputMapper.ParametroRapido):
                        estado_nuevo=Personaje.EstadoCorriendo
                #->saltar
                elif self.input_mapper.accion==InputMapper.AccionElevar:
                    estado_nuevo=Personaje.EstadoSaltando
            # caminando,corriendo
            elif estado_actual==Personaje.EstadoCaminando or estado_actual==Personaje.EstadoCorriendo:
                #caminar<->correr
                estado_nuevo=Personaje.EstadoCorriendo if self.input_mapper.parametro(InputMapper.ParametroRapido) else Personaje.EstadoCaminando
                #->quieto
                if self.input_mapper.accion!=InputMapper.AccionAvanzar:
                    estado_nuevo=Personaje.EstadoQuieto
                #->saltar
                if self.input_mapper.accion==InputMapper.AccionElevar:
                    estado_nuevo=Personaje.EstadoSaltando
            # cayendo
            elif estado_actual==Personaje.EstadoCayendo:
                if self._suelo!=Personaje.SueloNulo:
                    estado_nuevo=Personaje.EstadoQuieto
            # (cualquier estado)
            else:
                pass
            #
            # sin suelo
            if self._suelo==Personaje.SueloNulo:
                estado_nuevo=Personaje.EstadoCayendo
        # capa 1
        elif idx_capa==1:
            pass
        return estado_nuevo
    
    def _cambio_estado(self, idx_capa, estado_previo, estado_nuevo):
        #log.info("%s: cambio de estado en capa %i, de %s a %s"%(self.clase, idx_capa, str(estado_previo), str(estado_nuevo)))
        # capa 0
        self.actor.stop()
        if estado_nuevo==Personaje.EstadoQuieto:
            self._velocidad_lineal=LVector3(0.0, 0.0, 0.0)
            self._velocidad_angular=LVector3(0.0, 0.0, 0.0)
        # capa 1
        #

    def _cambio_params(self, params_previos, params_nuevos):
        #log.info("%s: cambio de parámetros de estados de %s a %s"%(self.clase, str(bin(params_previos)), str(bin(params_nuevos))))
        # detener giro
        if params_previos & Personaje.ParamEstadoGirando and not params_nuevos & Personaje.ParamEstadoGirando:
            self._velocidad_angular=LVector3(0.0, 0.0, 0.0)

    def _procesar_estados(self, dt):
        # capa 0
        # caminando,corriendo
        if self._estado_capa[0]==Personaje.EstadoCaminando or self._estado_capa[0]==Personaje.EstadoCorriendo:
            param=self._params_estado
            rapidez=self.rapidez_caminar if self._estado_capa[0]==Personaje.EstadoCaminando else self.rapidez_correr
            signo_x=-1.0 if param & Personaje.ParamEstadoDerecha else 1.0
            signo_y=-1.0 if param & Personaje.ParamEstadoAdelante else 1.0
            self._velocidad_lineal=LVector3()
            if param & Personaje.ParamEstadoIzquierda or param & Personaje.ParamEstadoDerecha:
                self._velocidad_lineal.setX(rapidez * signo_x)
            if param & Personaje.ParamEstadoAdelante or param & Personaje.ParamEstadoAtras:
                self._velocidad_lineal.setY(rapidez * signo_y)
            if param & Personaje.ParamEstadoGirando:
                self._velocidad_angular=LVector3(0.0, 0.0, 60.0 * rapidez * signo_x)
            self.cuerpo.setZ(self.altitud_suelo+self._ajuste_altura)
        # saltando
        elif self._estado_capa[0]==Personaje.EstadoSaltando:
            self._velocidad_lineal.setZ(5.0)
            self._velocidad_angular=LVector3(0.0, 0.0, 0.0)
        # cayendo
        elif self._estado_capa[0]==Personaje.EstadoCayendo:
            delta_velocidad_lineal=LVector3(0.0, 0.0, -9.81) * dt
            self._velocidad_lineal+=delta_velocidad_lineal
            prox_delta_h=abs(delta_velocidad_lineal.getZ()*dt)
            if delta_velocidad_lineal.getZ()<0.0 and self._altura<=prox_delta_h: # si cayendo y cerca del suelo
                self.cuerpo.setZ(self.altitud_suelo+self._ajuste_altura)
                self._velocidad_lineal.setZ(0.0)            
        #
        # mover, si no está quieto
        if self._estado_capa[0]!=Personaje.EstadoQuieto:
            self.cuerpo.setPos(self.cuerpo, self._velocidad_lineal * dt)
            self.cuerpo.setH(self.cuerpo, self._velocidad_angular.getZ() * dt)
