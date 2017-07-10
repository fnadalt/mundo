from direct.actor.Actor import Actor
from panda3d.bullet import *
from panda3d.core import *

import logging
log=logging.getLogger(__name__)

class Hombre:
    
    # estados 1111XXXX
    E_QUIETO=0 # 0000 XXXX
    E_AIRE=16 # 00001 XXXX
    E_CAMINAR=32 # 0010 XXXX
    
    # sub estados XXXX1111
    # caminar
    SE_GIRANDO=8 # 1000
    SE_ADELANTE=0 # 0000
    SE_ATRAS=1 # 0001
    SE_IZQUIERDA=2 # 0010
    SE_DERECHA=4 # 0100
    # aire
    SE_HACIA_ARRIBA=0 # 0000
    SE_HACIA_ABAJO=1 # 0001
    
    def __init__(self, mundo):
        #
        self.mundo=mundo
        self.base=mundo.base
        # fisica
        _shape=BulletCapsuleShape(0.25, 0.5, ZUp)
        _rbody=BulletCharacterControllerNode(_shape, 0.5, "hombre_rigid_body")
        self.cuerpo=self.mundo.attachNewNode(_rbody)
        self.mundo.mundo_fisico.attachCharacter(_rbody)
        # actor
        self.actor=Actor("player")
        self.actor.reparentTo(self.cuerpo)
        self.actor.setZ(-0.5)
        # foco de la camara
        self.foco_camara=self.actor.attachNewNode("foco_camara")
        self.foco_camara.setZ(1.0)
        # parametros
        self.max_vel_lineal=Vec4() # Vec4(max_adelante, max_atras, max_izq, max_der)
        self.max_vel_angular=Vec2() # Vec2(max_izq, max_der)
        # variables internas
        self._vel_lineal=Vec2() # Vec2(horizontal, vertical)
        self._vel_angular=0.0
        self._flag_saltar=False
        # estado
        self.estado=0
        #
        self.base.taskMgr.add(self._update, "hombre_update")

    def _update(self, task):
        # time
        dt=self.base.taskMgr.globalClock.getDt()
        # camara
        if self.base.mouseWatcherNode.hasMouse():
            pos_mouse=self.base.mouseWatcherNode.getMouse()
            if abs(pos_mouse.getX())>0.2:
                foco_cam_H=self.foco_camara.getH()
                foco_cam_H-=360.0*pos_mouse.getX()*dt
                self.foco_camara.setH(foco_cam_H)
            if abs(pos_mouse.getY())>0.2:
                foco_cam_P=self.foco_camara.getP()
                foco_cam_P-=180.0*pos_mouse.getY()*dt
                if foco_cam_P<-45.0: foco_cam_P=-45.0
                if foco_cam_P>90.0: foco_cam_P=90.0
                self.foco_camara.setP(foco_cam_P)
        # estado
        _estado_nuevo=self._definir_estado()
        if estado_nuevo!=self.estado:
            self._procesar_cambio_estado(self.estado, _estado_nuevo)
        self._procesar_estado_actual()
        #
        return task.cont

    #
    def _definir_estado(self):
        pass
    
    def _procesar_cambio_estado(self, estado_previo, estado_nuevo):
        pass
    
    def _procesar_estado_actual(self):
        pass
    
    #
    def en_estado(self, estado, sub_estado):
        estado_parcial=estado | sub_estado
        return (self.estado & estado_parcial)==estado_parcial
    
    def caminar(self, sub_estado):
        _vel=Vec2()
        if self.en_estado(0, self.SE_ADELANTE):
            _vel.setX(self.max_vel_lineal.getX())
        elif self.en_estado(0, self.SE_ATRAS):
            _vel.setX(self.max_vel_lineal.getY())
        elif self.en_estado(0, self.SE_IZQUIERDA):
            _vel.setY(self.max_vel_lineal.getZ())
        elif self.en_estado(0, self.SE_DERECHA):
            _vel.setY(self.max_vel_lineal.getW())
        self._vel_lineal=_vel
    
    def girar(self, sub_estado):
        _vel=0.0
        if self.en_estado(0, self.SE_GIRANDO|self.SE_IZQUIERDA):
            _vel=self.max_vel_angular.getX()
        elif self.en_estado(0, self.SE_GIRANDO|self.SE_DERECHA):
            _vel=-self.max_vel_angular.getY()
        self._vel_angular=_vel
    
    def saltar(self):
        self._flag_saltar=True

    def agachar(self):
        self._flag_agachar=True
