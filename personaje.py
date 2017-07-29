from direct.actor.Actor import Actor
from panda3d.bullet import *
from panda3d.core import *
import os, os.path
import math

import logging
log=logging.getLogger(__name__)

#
#
# PERSONAJE
#
#
class Personaje:
    
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
        self.mundo.mundo_fisico.attachRigidBody(_rbody)
        # actor
        _ruta_directorio=os.path.join(os.getcwd(), "personajes", nombre_actor)
        _archivos_egg=[x for x in os.listdir(_ruta_directorio) if x[-4:].lower()==".egg"]
        print str(os.listdir(_ruta_directorio))
        _anims={}
        for _archivo_egg in _archivos_egg:
            _anims[_archivo_egg[:-4]]=os.path.join(_ruta_directorio, _archivo_egg)
        log.debug("%s: animaciones %s"%(self.nombre, str(_anims)))
        self.actor=Actor(os.path.join(_ruta_directorio, "actor"), _anims)
        self.actor.reparentTo(self.cuerpo)
        self.actor.setZ(-0.5)
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
        self.base.taskMgr.add(self._update, "%s_update"%self.nombre)

    def _update(self, task):
        # time
        dt=self.base.taskMgr.globalClock.getDt()
        # camara
        if self.controlador_camara!=None:
            self.controlador_camara.update(dt)
        # animaciones
        self.animar()
        # movimiento
        if not self.quieto:
            self.cuerpo.setPos(self.cuerpo, self.velocidad_lineal*self.factor_movimiento*dt)
            altura=self.cuerpo.getZ()-self.altitud_suelo-0.5
            if self.velocidad_lineal.getZ()==0.0:
                self.cuerpo.setH(self.cuerpo, self.velocidad_angular*self.factor_movimiento*dt)
                self.cuerpo.setZ(self.altitud_suelo+0.5)
            else:
                delta_velocidad_lineal=self.mundo.mundo_fisico.getGravity()*dt
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
        #
        return task.cont

    def animar(self):
        _anim_actual=self.actor.getCurrentAnim()
        if self.quieto and _anim_actual!="quieto":
            #log.debug("quieto")
            self.actor.loop("quieto")
        else:
            if self.velocidad_lineal.getZ()==0.0:
                if self.velocidad_lineal.getY()<0.0 and _anim_actual!="avanzar":
                    log.debug("avanzar")
                    self.actor.setPlayRate(3.5, "avanzar")
                    self.actor.loop("avanzar")
                elif self.velocidad_lineal.getY()>0.0 and _anim_actual!="retroceder":
                    log.debug("retroceder")
                    self.actor.setPlayRate(2.5, "retroceder")
                    self.actor.loop("avanzar")
            else:
                if self.velocidad_lineal.getZ()>0.0 and _anim_actual!="saltar":
                    self.actor.setPlayRate(1.2, "saltar")
                    self.actor.play("saltar", fromFrame=20, toFrame=59)

    def controlar(self, camara, controles):
        if self.controlador_camara!=None:
            return
        self.controlador_camara=ControladorCamara(self.base, camara, self.actor)
        self.controles=controles
        #
        for e, f in self.controles.items():
            log.debug("%s controles %s -> %s"%(self.nombre, e, f))
            if f not in Personaje.controles_trigger:
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
        if self.modo_camara==Personaje.CAM_TERCERA_PERSONA:
            self.foco_camara.setH(0.0)
        elif self.modo_camara==Personaje.CAM_PRIMERA_PERSONA:
            _angulo=self.foco_camara.getH()
            _cuerpo_H=self.cuerpo.getH()
            self.cuerpo.setH(_cuerpo_H+_angulo)
            self.foco_camara.setH(0.0)
        
    def avanzar(self, flag):
        self.velocidad_lineal.setY(-self.max_vel_lineal[0] if flag else 0.0)
        if flag:
            self.quieto=False
    
    def retroceder(self, flag):
        self.velocidad_lineal.setY(self.max_vel_lineal[1] if flag else 0.0)
        if flag:
            self.quieto=False
    
    def desplazar_izquierda(self, flag):
        self.velocidad_lineal.setX(self.max_vel_lineal[2] if flag else 0.0)
        if flag:
            self.quieto=False
    
    def desplazar_derecha(self, flag):
        self.velocidad_lineal.setX(-self.max_vel_lineal[2] if flag else 0.0)
        if flag:
            self.quieto=False
    
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

#
#
# CONTROLADOR DE CAMARA
#
#
class ControladorCamara:
    
    CAM_TERCERA_PERSONA=0
    CAM_PRIMERA_PERSONA=1
    #
    CAM_VECTOR_INICIAL=Vec3(0.0, 1.0, 1.0).normalized()

    def __init__(self, base, camara,  objetivo):
        self.base=base
        self.objetivo=objetivo
        self.modo=ControladorCamara.CAM_TERCERA_PERSONA
        self.distancia=3.0
        self.pitch=ControladorCamara.CAM_VECTOR_INICIAL.normalized().angleDeg(Vec3(0.0, 0.0, 1.0))
        print("pitch: "+str(self.pitch))
        #
        self.foco=objetivo.attachNewNode("foco")
        self.foco.setZ(1.0)
        #
        self.posicion_camara=ControladorCamara.CAM_VECTOR_INICIAL
        self.camara=camara
        self.camara.reparentTo(self.foco)
        self.camara.setPos(self.posicion_camara)
        self.camara.lookAt(self.foco)

    def acercar(self):
        self.distancia-=5.0
        if self.distancia<1.2 and self.modo==ControladorCamara.CAM_TERCERA_PERSONA:
            self.distancia=0.0
            self.modo=ControladorCamara.CAM_PRIMERA_PERSONA
            log.info("camara en primera persona")
        elif self.distancia<0.0:
            self.distancia=0.0
            return
        self.posicion_camara=self.posicion_camara.normalized()*self.distancia
#        log.debug("acercar_camara")
#        log.debug("self.distancia %s"%str(self.distancia))
#        log.debug("self.camara %s"%str(self.camara.getPos()))

    def alejar(self):
        self.distancia+=5.0
        if self.distancia>=1600.0:
            self.distancia=1600.0
            return
        elif self.modo==ControladorCamara.CAM_PRIMERA_PERSONA and self.distancia>1.2:
            self.modo=ControladorCamara.CAM_TERCERA_PERSONA
            log.info("camara en tercera persona")
            self.posicion_camara=ControladorCamara.CAM_VECTOR_INICIAL
        self.posicion_camara=self.posicion_camara.normalized()*self.distancia
#        log.debug("alejar_camara")
#        log.debug("self.distancia %s"%str(self.distancia))
#        log.debug("self.camara %s"%str(self.camara.getPos()))

    def update(self, dt):
        #
        self.camara.setPos(self.posicion_camara)
        #
        if self.base.mouseWatcherNode.hasMouse():
            pos_mouse=self.base.mouseWatcherNode.getMouse()
            if abs(pos_mouse.getX())>0.4:
                foco_cam_H=self.foco.getH()
                foco_cam_H-=90.0*dt*1.0 if pos_mouse[0]>0.0 else -1.0
                if self.modo==ControladorCamara.CAM_PRIMERA_PERSONA:
                    if foco_cam_H<-85.0: foco_cam_H=-85.0
                    if foco_cam_H>85.0: foco_cam_H=85.0
                else:
                    if abs(foco_cam_H)>=360.0:
                        foco_cam_H=0.0
                self.foco.setH(foco_cam_H)
            if abs(pos_mouse.getY())>0.4:
                self.pitch+=15.0*dt*1.0 if pos_mouse[1]<0.0 else -1.0
                print "new pitch "+str(self.pitch)
#                if self.pitch<-25.0: self.pitch=-25.0
#                if self.pitch>25.0: self.pitch=25.0
                self.posicion_camara=Vec3(0.0, math.cos(math.radians(self.pitch)), math.sin(math.radians(self.pitch)))
                self.posicion_camara*=self.distancia
                self.camara.lookAt(self.foco)

#
#
# CONTROLADOR DE ANIMACION
#
#
class ControladorAnimacion:
    
    def __init__(self, actor, animaciones):
        self.actor=actor
        self.animaciones=animaciones
        #
        
