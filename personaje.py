from direct.actor.Actor import Actor
from panda3d.bullet import *
from panda3d.core import *
import os, os.path

import logging
log=logging.getLogger(__name__)

#
#
# PERSONAJE
#
#
class Personaje:
    
    # ambiente
    AmbienteNulo=0
    AmbienteAire=1
    AmbienteAgua=2
    
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

    def __init__(self):
        # variables internas
        self._ambiente=self.AmbienteNulo
        self._suelo=self.SueloNulo
        self._partes_actor=list() # [] | [nombre_parte, ...]
        self._estado_capa=[self.EstadoNulo, self.EstadoNulo] # [estado,estado,estado]
        self._params_estado=self.ParamEstadoNulo
        self._altura=0.0
        self._velocidad_lineal=LVector3()
        self._velocidad_angular=LVector3() # grados
        # variables externas
        self.altitud_suelo=0.0
        self.altitud_agua=0.0
        # parametros
        self.directorio_recursos="personajes"
        self.clase="male"
        self.prefijo_cuerpo_suelo="cuerpo_suelo_"
        self.rapidez_caminar=1.0 # multiplicador
        self.rapidez_correr=2.0 # multiplicador
        # referencias
        self.input_mapper=None
        # componentes
        self.cuerpo=None
        self.actor=None
    
    def construir(self, parent_node_path, bullet_world):
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
                dict_animaciones[archivo[:-4]]=os.path.join(ruta_dir, archivo)
        if archivo_actor=="":
            raise Exception("no se encontró ningún archivo de actor (actor.[egg|bam]) en '%s'"%ruta_dir)
        # cuerpo
        shp=BulletCapsuleShape(0.25, 0.5, ZUp)
        rb=BulletRigidBodyNode("cuerpo_personaje_%s"%self.clase)
        rb.setMass(70.0)
        rb.addShape(shp)
        rb.setKinematic(True)
        bullet_world.attachRigidBody(rb)
        self.cuerpo=parent_node_path.attachNewNode(rb)
        self.cuerpo.setCollideMask(BitMask32.bit(2))
        # actor
        self.actor=Actor(os.path.join(ruta_dir, archivo_actor), dict_animaciones)
        self.actor.reparentTo(self.cuerpo)
        self.actor.setScale(0.06)
        self.actor.setZ(-0.5)
        # partes
        self.actor.makeSubpart("torso", ["hips"], ["thigh.L", "thigh.R"])
        self.actor.makeSubpart("pelvis", ["thigh.L", "thigh.R"])
        # joints
        self.handR=self.actor.exposeJoint(None,"modelRoot", "hand.R")        
        # establecer estado inicial
        self._estado_capa[0]=Personaje.EstadoQuieto
        self._cambio_estado(0, Personaje.EstadoNulo, Personaje.EstadoQuieto)

    def chequear_estado(self, estado):
        if estado>15: # capa 1
            return estado==self._estado_capa[1]
        elif estado>0: # capa 0
            return estado==self._estado_capa[0]
        
    def update(self, dt):
        # definir ambiente y suelo
        self._definir_ambiente()
        self._definir_suelo()
        # definir estados
        for idx_capa in range(len(self._estado_capa)):
            estado_nuevo=self._definir_estado(idx_capa)
            if self._estado_capa[idx_capa]!=estado_nuevo:
                # procesar cambio de estado
                self._cambio_estado(idx_capa, self._estado_capa[idx_capa], estado_nuevo)
                self._estado_capa[idx_capa]=estado_nuevo
        # verificar cambio de parametros
        param_estado_nuevo=self.input_mapper.param_estado
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
        info+="posición=%s altitud_suelo=%s altura=%s\n"%(str(self.cuerpo.getPos()), str(self.altitud_suelo), str(self._altura))
        info+="ambiente=%s suelo=%s\n"%(str(self._ambiente), str(self._suelo))
        info+="estado=%s params=%s\n"%(str(self._estado_capa), str(self._params_estado))
        return info

    def _definir_ambiente(self):
        if self._ambiente != Personaje.AmbienteAire:
            self._ambiente=Personaje.AmbienteAire
        
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
                if self.input_mapper.estado[Personaje.EstadoCaminando]:
                    estado_nuevo=Personaje.EstadoCaminando
                #->correr
                if self.input_mapper.estado[Personaje.EstadoCorriendo]:
                    estado_nuevo=Personaje.EstadoCorriendo
                #->saltar
                elif self.input_mapper.estado[Personaje.EstadoSaltando]:
                    estado_nuevo=Personaje.EstadoSaltando
            # caminando,corriendo
            elif estado_actual==Personaje.EstadoCaminando or estado_actual==Personaje.EstadoCorriendo:
                #caminar<->correr
                estado_nuevo=Personaje.EstadoCorriendo if self.input_mapper.estado[Personaje.EstadoCorriendo] else Personaje.EstadoCaminando
                #->quieto
                if not self.input_mapper.estado[Personaje.EstadoCaminando] and not self.input_mapper.estado[Personaje.EstadoCorriendo]:
                    estado_nuevo=Personaje.EstadoQuieto
                #->saltar
                elif self.input_mapper.estado[Personaje.EstadoSaltando]:
                    estado_nuevo=Personaje.EstadoSaltando
            # cayendo
            elif estado_actual==Personaje.EstadoCayendo:
                if self._suelo!=Personaje.SueloNulo:
                    estado_nuevo=Personaje.EstadoQuieto
            #
            # sin suelo
            if self._suelo==Personaje.SueloNulo:
                estado_nuevo=Personaje.EstadoCayendo
            pass
        # capa 1
        elif idx_capa==1:
            pass
        return estado_nuevo
    
    def _cambio_estado(self, idx_capa, estado_previo, estado_nuevo):
        #log.info("%s: cambio de estado en capa %i, de %s a %s"%(self.clase, idx_capa, str(estado_previo), str(estado_nuevo)))
        # capa 0
        if estado_nuevo==Personaje.EstadoQuieto:
            self._velocidad_lineal=LVector3(0.0, 0.0, 0.0)
            self._velocidad_angular=LVector3(0.0, 0.0, 0.0)
            self.actor.loop("quieto")
        elif estado_nuevo==Personaje.EstadoCaminando:
            #self.actor.setPlayRate(1.0, "caminar") # |4.0
            self.actor.loop("caminar")
        elif estado_nuevo==Personaje.EstadoCorriendo:
            self.actor.setPlayRate(1.5, "correr")
            self.actor.loop("correr")
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
            self.cuerpo.setZ(self.altitud_suelo+0.5)
        elif self._estado_capa[0]==Personaje.EstadoSaltando:
            self._velocidad_lineal.setZ(5.0)
            self._velocidad_angular=LVector3(0.0, 0.0, 0.0)
        elif self._estado_capa[0]==Personaje.EstadoCayendo:
            delta_velocidad_lineal=LVector3(0.0, 0.0, -9.81) * dt
            self._velocidad_lineal+=delta_velocidad_lineal
            prox_delta_h=abs(delta_velocidad_lineal.getZ()*dt)
            if delta_velocidad_lineal.getZ()<0.0 and self._altura<=prox_delta_h: # si cayendo y cerca del suelo
                self.cuerpo.setZ(self.altitud_suelo+0.5)
                self._velocidad_lineal.setZ(0.0)            
        #
        # mover, si no está quieto
        if self._estado_capa[0]!=Personaje.EstadoQuieto:
            self.cuerpo.setPos(self.cuerpo, self._velocidad_lineal * dt)
            self.cuerpo.setH(self.cuerpo, self._velocidad_angular.getZ() * dt)
        
#
#
# PERSONAJE VIEJO
#
#
class PersonajeViejo:
    
    #
    controles_trigger=["saltar", "acercar_camara", "alejar_camara", "mirar_adelante"]
    
    def __init__(self, mundo, nombre_actor):
        #
        self.mundo=mundo
        self.base=mundo.base
        self.nombre=nombre_actor
        # fisica
        _shape=BulletCapsuleShape(0.25, 0.5, ZUp)
        _rbody=BulletRigidBodyNode("%s_rigid_body"%self.nombre)
        _rbody.setMass(1.0)
        _rbody.addShape(_shape)
        _rbody.setKinematic(True)
        self.cuerpo=self.mundo.attachNewNode(_rbody)
        self.cuerpo.setCollideMask(BitMask32.bit(2))
        self.mundo.bullet_world.attachRigidBody(_rbody)
        # actor
        _ruta_directorio=os.path.join(os.getcwd(), "personajes", nombre_actor)
        _archivos_egg=[x for x in os.listdir(_ruta_directorio) if x[-4:].lower()==".egg"]
        print(str(os.listdir(_ruta_directorio)))
        _anims={}
        for _archivo_egg in _archivos_egg:
            _anims[_archivo_egg[:-4]]=os.path.join(_ruta_directorio, _archivo_egg)
        log.debug("%s: animaciones %s"%(self.nombre, str(_anims)))
        self.actor=Actor(os.path.join(_ruta_directorio, "actor"), _anims)
        self.actor.reparentTo(self.cuerpo)
        self.actor.setZ(-0.5)
        #self.actor.setShaderOff() # paque se refleje en el agua?
        #
        self.controlador_animacion=None
        # control
        self.controlador_camara=None
        self.controles={} # {"evento":"funcion"}
        # parametros
        self.max_vel_lineal=(1.0, 0.4, 0.7) # (max_adelante, max_atras, max_lateral)
        self.max_vel_angular=90.0
        self.factor_movimiento=1.0
        self.altitud_suelo=0.0
        # variables externas
        self.quieto=False
        self.velocidad_lineal=LVector3()
        self.velocidad_angular=0.0
        #
        #self.base.taskMgr.add(self.update, "%s_update"%self.nombre) # se hace en mundo

    def update(self, dt):
        # camara
        if self.controlador_camara!=None:
            self.controlador_camara.update(dt)
        # animaciones
        #if self.quieto and self.controlador_animacion.obtener_nombre_estado_actual(0)!="quieto":
        #    log.debug("nombre_estado_actual(0)->%s"%str(self.controlador_animacion.obtener_nombre_estado_actual(0)))
        #    self.controlador_animacion.pasar_a(0,"quieto")
        #self.controlador_animacion.update(dt)
        # movimiento
        if not self.quieto:
            self.cuerpo.setPos(self.cuerpo, self.velocidad_lineal*self.factor_movimiento*dt)
            altura=self.cuerpo.getZ()-self.altitud_suelo-0.5
            if self.velocidad_lineal.getZ()==0.0:
                self.cuerpo.setH(self.cuerpo, self.velocidad_angular*self.factor_movimiento*dt)
                self.cuerpo.setZ(self.altitud_suelo+0.5)
            else:
                delta_velocidad_lineal=self.mundo.bullet_world.getGravity()*dt
                self.velocidad_lineal+=delta_velocidad_lineal
                #
                prox_delta_h=abs(delta_velocidad_lineal.getZ()*dt)
                #log.debug("%s: dvZ=%s prox_dh=%f h=%f"%(self.nombre, str(delta_velocidad_lineal.getZ()), prox_delta_h, altura))
                if delta_velocidad_lineal.getZ()<0.0 and altura<=prox_delta_h: # si cayendo y cerca del suelo
                    #log.debug("prevenir penetracion del suelo")
                    self.cuerpo.setZ(self.altitud_suelo+0.5)
                    self.velocidad_lineal.setZ(0.0)
            #
            if self.velocidad_lineal==LVector3.zero() and self.velocidad_angular==0.0:
                self.quieto=True
            #
            #log.debug("%s: pos=%s vel=%s h=%f altitud=%f"%(self.nombre, str(self.cuerpo.getPos()), str(self.velocidad_lineal), altura, self.altitud_suelo))

    def controlar(self, controlador_camara, controles):
        if self.controlador_camara!=None:
            return
        self.controlador_camara=controlador_camara
        self.controles=controles
        #
        for e, f in self.controles.items():
            log.debug("%s controles %s -> %s"%(self.nombre, e, f))
            if f not in PersonajeViejo.controles_trigger:
                self.base.accept(e, getattr(self, f), [True])
                self.mundo.base.accept("%s-up"%e, getattr(self, f), [False])
            else:
                self.base.accept(e, getattr(self, f))

    def liberar_control(self):
        if self.controlador_camara==None:
            return
        self.controlador_camara.camara.wrtReparentTo(self.base.render)
        self.controlador_camara=None
        for e, f in self.controles.items():
            self.mundo.base.ignore(e)
            if f not in Personaje.controles_trigger:
                self.mundo.base.ignore("%s-up")

    def acercar_camara(self):
        if self.controlador_camara!=None:
            self.controlador_camara.acercar()

    def alejar_camara(self):
        if self.controlador_camara!=None:
            self.controlador_camara.alejar()
    
    def mirar_adelante(self):
        if self.controlador_camara!=None:
            self.controlador_camara.mirar_adelante()
    
    def caminar(self, flag):
        self.velocidad_lineal.setY(-self.max_vel_lineal[0] if flag else 0.0)
        if flag:
            self.quieto=False
            #self.controlador_animacion.pasar_a(0,"caminar")
    
    def retroceder(self, flag):
        self.velocidad_lineal.setY(self.max_vel_lineal[1] if flag else 0.0)
        if flag:
            self.quieto=False
            #self.controlador_animacion.pasar_a("retroceder")
    
    def desplazar_izquierda(self, flag):
        self.velocidad_lineal.setX(self.max_vel_lineal[2] if flag else 0.0)
        if flag:
            self.quieto=False
            #self.controlador_animacion.pasar_a("desplazar_izquierda")
    
    def desplazar_derecha(self, flag):
        self.velocidad_lineal.setX(-self.max_vel_lineal[2] if flag else 0.0)
        if flag:
            self.quieto=False
            #self.controlador_animacion.pasar_a("desplazar_derecha")
    
    def girar_izquierda(self, flag):
        self.velocidad_angular=self.max_vel_angular if flag else 0.0
        if flag:
            self.quieto=False
    
    def girar_derecha(self, flag):
        self.velocidad_angular=-self.max_vel_angular if flag else 0.0
        if flag:
            self.quieto=False
    
    def saltar(self):
        self.velocidad_lineal.setZ(4.0)
        self.velocidad_angular=0.0
        self.quieto=False
    
    def agachar(self, flag):
        pass

    def colgarse(self, flag):
        pass
