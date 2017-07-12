from panda3d.bullet import *
from panda3d.core import *

import logging
log=logging.getLogger(__name__)

class Personaje:
    
    CAM_TERCERA_PERSONA=0
    CAM_PRIMERA_PERSONA=1
    #
    controles_trigger=["saltar", "acercar_camara", "alejar_camara", "mirar_adelante"]
    
    def __init__(self, mundo, actor):
        #
        self.mundo=mundo
        self.base=mundo.base
        self.nombre=actor.getName()
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
        self.actor=actor
        self.actor.reparentTo(self.cuerpo)
        self.actor.setZ(-0.5)
        # control
        self.foco_camara=self.actor.attachNewNode("%s_foco_camara"%self.nombre)
        self.foco_camara.setZ(1.0)
        self.nodo_camara=None
        self.controles={} # {"evento":"funcion"}
        # parametros
        self.max_vel_lineal=(1.0, 0.4, 0.7) # (max_adelante, max_atras, max_lateral)
        self.max_vel_angular=90.0
        self.factor_movimiento=1.0
        self.altitud_suelo=0.0
        # variables externas
        self.quieto=False
        self.modo_camara=Personaje.CAM_TERCERA_PERSONA
        self.velocidad_lineal=LVector3()
        self.velocidad_angular=0.0
        #
        self.base.taskMgr.add(self._update, "%s_update"%self.nombre)

    def _update(self, task):
        # time
        dt=self.base.taskMgr.globalClock.getDt()
        # camara
        if self.nodo_camara!=None:
            if self.base.mouseWatcherNode.hasMouse():
                pos_mouse=self.base.mouseWatcherNode.getMouse()
                if abs(pos_mouse.getX())>0.4:
                    foco_cam_H=self.foco_camara.getH()
                    foco_cam_H-=90.0*dt*1.0 if pos_mouse[0]>0.0 else -1.0
                    if self.modo_camara==Personaje.CAM_PRIMERA_PERSONA:
                        if foco_cam_H<-85.0: foco_cam_H=-85.0
                        if foco_cam_H>85.0: foco_cam_H=85.0
                    else:
                        if abs(foco_cam_H)>=360.0:
                            foco_cam_H=0.0
                    self.foco_camara.setH(foco_cam_H)
                if abs(pos_mouse.getY())>0.4:
                    foco_cam_P=self.foco_camara.getP()
                    foco_cam_P+=15.0*dt*1.0 if pos_mouse[1]<0.0 else -1.0
                    if foco_cam_P<-25.0: foco_cam_P=-25.0
                    if foco_cam_P>25.0: foco_cam_P=25.0
                    self.foco_camara.setP(foco_cam_P)
        # movimiento
        if not self.quieto:
            altura=self.cuerpo.getZ()-self.altitud_suelo
            if self.velocidad_lineal.getZ()==0.0:
                self.cuerpo.setPos(self.cuerpo, self.velocidad_lineal*self.factor_movimiento*dt)
                self.cuerpo.setH(self.cuerpo, self.velocidad_angular*self.factor_movimiento*dt)
                if altura<0.1:
                    self.velocidad_lineal+=self.mundo.mundo_fisico.getGravity()*dt
                else:
                    self.cuerpo.setZ(self.altitud_suelo+0.5)
            else:
                self.cuerpo.setPos(self.cuerpo, self.velocidad_lineal*self.factor_movimiento*dt)
                delta_velocidad_lineal=self.mundo.mundo_fisico.getGravity()*dt
                self.velocidad_lineal+=delta_velocidad_lineal
                #
                if delta_velocidad_lineal.getZ()<0.0 and altura<=abs(delta_velocidad_lineal.getZ()): # si cayendo y cerca del suelo
                    self.cuerpo.setZ(self.altitud_suelo+0.5)
                    self.velocidad_lineal.setZ(0.0)
            #
            if self.velocidad_lineal==LVector3.zero() and self.velocidad_angular==0.0:
                self.quieto=True
            #
        #
        return task.cont

    def controlar(self, nodo_camara, controles):
        if self.nodo_camara!=None:
            return
        self.nodo_camara=nodo_camara
        self.nodo_camara.reparentTo(self.foco_camara)
        self.nodo_camara.setY(3.0)
        self.nodo_camara.lookAt(self.foco_camara)
        self.controles=controles
        for e, f in self.controles.items():
            log.debug("%s controles %s -> %s"%(self.nombre, e, f))
            if f not in Personaje.controles_trigger:
                self.base.accept(e, getattr(self, f), [True])
                self.mundo.base.accept("%s-up"%e, getattr(self, f), [False])
            else:
                self.base.accept(e, getattr(self, f))

    def liberar_control(self):
        if self.nodo_camara==None:
            return
        self.nodo_camara.reparentTo(self.base)
        self.nodo_camara=None
        for e, f in self.controles.items():
            self.mundo.base.ignore(e)
            if f not in Personaje.controles_trigger:
                self.mundo.base.ignore("%s-up")

    def acercar_camara(self):
        cam_Y=self.base.cam.getY()
        cam_Y-=5.0
        if cam_Y<1.2:
            cam_Y=0.0
            self.modo_camara=Personaje.CAM_PRIMERA_PERSONA
        self.base.cam.setY(cam_Y)    

    def alejar_camara(self):
        cam_Y=self.base.cam.getY()
        cam_Y+=5.0
        if cam_Y<1.2:
            cam_Y=1.2
            self.modo_camara=Personaje.CAM_TERCERA_PERSONA
        elif cam_Y>1600.0:
            return
        self.base.cam.setY(cam_Y)
    
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
