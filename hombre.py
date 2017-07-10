from direct.actor.Actor import Actor
from panda3d.bullet import *
from panda3d.core import *

import logging
log=logging.getLogger(__name__)

class Hombre:
    
    # estados 1111XXXX
    E_QUIETO=0 # 0000 XXXX
    E_AIRE=16 # 0001 XXXX
    E_CAMINAR=32 # 0010 XXXX
    
    # sub estados XXXX1111
    # caminar
    SE_GIRANDO=8 # 1000
    SE_ADELANTE=1 # 0001
    SE_ATRAS=2 # 0010
    SE_IZQUIERDA=4 # 0100
    SE_DERECHA=0 # 0000
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
        self.max_vel_lineal=() # (max_adelante, max_atras, max_izq, max_der)
        self.max_vel_angular=0.0
        self.resistencia=0.0
        self.gravedad_z=0.0
        # variables internas
        self._quieto=True
        self._vel_lineal=Vec2() # Vec2(horizontal, vertical)
        self._vel_angular=0.0
        self._en_aire=False
        self._flag_saltar=False
        self._flag_agachar=False
        # estado + sub estado
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
        if _estado_nuevo!=self.estado:
            self._procesar_cambio_estado(self.estado, _estado_nuevo)
        self._procesar_estado_actual()
        #
        return task.cont

    #
    def _definir_estado(self):
        _nuevo_estado=self.estado
        # QUIETO -> CAMINAR
        if self.en_estado(self.E_QUIETO, None):
            if self._vel_lineal!=Vec2.zero() and self._vel_anguar!=0.0:
                _nuevo_estado=self.E_CAMINAR
        # CAMINAR -> QUIETO
        elif self.en_estado(self.E_CAMINAR, None):
            x=self._vel_lineal.getX()
            y=self._vel_lineal.getY()
            a=self._vel_angular
            if x==0.0 and y==0.0 and a==0.0:
                _nuevo_estado=self.E_QUIETO
            else:
                if x<0.0:
                    _nuevo_estado=(self.E_CAMINAR|self.SE_ATRAS)
                elif x>0.0:
                    _nuevo_estado=(self.E_CAMINAR|self.SE_ADELANTE)
                else:
                    _nuevo_estado=self.E_CAMINAR
                if a!=0.0:
                    if a>0.0:
                        _nuevo_estado=(self.E_CAMINAR|self.SE_GIRAR|self.SE_DERECHA)
                    if a<0.0:
                        _nuevo_estado=(self.E_CAMINAR|self.SE_GIRAR|self.SE_DERECHA)
                else:
                    if y>0.0:
                        _nuevo_estado=(self.E_CAMINAR|self.SE_DERECHA)
                    if y<0.0:
                        _nuevo_estado=(self.E_CAMINAR|self.SE_DERECHA)
        return _nuevo_estado
    
    def _procesar_cambio_estado(self, estado_previo, estado_nuevo):
        log.debug("cambio de estado de %s a %s"%(str(estado_previo), str(estado_nuevo)))
    
    def _procesar_estado_actual(self):
        pass
    
    #
    def en_estado(self, estado, sub_estado):
        if sub_estado==None:
            return (self.estado&240)==estado
        elif estado==None:
            return (self.estado&15)==sub_estado
        e_se=estado|sub_estado
        return (self.estado&e_se)==e_se
    
    def detener(self):
        self._vel_lineal=Vec2()
        self._vel_angular=0.0
    
    def caminar(self, sub_estado):
        log.debug("caminar")
        _vel=Vec2()
        if sub_estado==self.SE_ADELANTE:
            _vel.setX(self.max_vel_lineal.getX())
        elif sub_estado==self.SE_ATRAS:
            _vel.setX(self.max_vel_lineal.getY())
        elif sub_estado==self.SE_IZQUIERDA:
            _vel.setY(self.max_vel_lineal.getZ())
        elif sub_estado==self.SE_DERECHA:
            _vel.setY(self.max_vel_lineal.getW())
        self._vel_lineal=_vel
    
    def girar(self, sub_estado):
        _vel=0.0
        if sub_estado==self.SE_IZQUIERDA:
            _vel=self.max_vel_angular.getX()
        elif sub_estado==self.SE_DERECHA:
            _vel=-self.max_vel_angular.getY()
        self._vel_angular=_vel
    
    def saltar(self):
        self._flag_saltar=True

    def agachar(self):
        self._flag_agachar=True
