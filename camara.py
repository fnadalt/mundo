from panda3d.core import *

import logging
log=logging.getLogger(__name__)

class ControladorCamara:
    
    # estados
    EstadoNulo=100
    EstadoAcercando=101
    EstadoAlejando=102
    EstadoMirarAdelante=103

    # modo
    ModoTerceraPersona=0
    ModoPrimeraPersona=1
    
    # constantes
    DistanciaInicial=3.0

    def __init__(self, base):
        self.base=base
        # variables internas
        self._ajustando_altitud=False
        # variables externas
        self.pos_camara=LVector3()
        self.modo=ControladorCamara.ModoTerceraPersona
        self.altitud_suelo=0
        self.nivel_agua=0
        # componentes
        self.camara=self.base.camera
        self.target_node_path=None
        self.foco=None
    
    def seguir(self, target_node_path):
        #
        if self.foco!=None:
            self.foco.removeNode()
        #
        self.target_node_path=target_node_path
        self.foco=self.target_node_path.attachNewNode("foco")
        self.foco.setZ(0.5)
        #
        self.camara.reparentTo(self.foco)
        self.camara.setY(ControladorCamara.DistanciaInicial)
        self.camara.lookAt(self.foco)
    
    def update(self, dt):
        # input
        if self.input_mapper.chequear_falsear(ControladorCamara.EstadoAcercando):
            self._acercar()
        elif self.input_mapper.chequear_falsear(ControladorCamara.EstadoAlejando):
            self._alejar()
        elif self.input_mapper.chequear_falsear(ControladorCamara.EstadoMirarAdelante):
            self._mirar_adelante()
        # procesar movimiento del mouse
        pos_mouse=None
        if self.base.mouseWatcherNode.hasMouse():
            mouse=self.base.mouseWatcherNode.getMouse()
            pos_mouse=[mouse[0], mouse[1]]
        else:
            pos_mouse=[0, 0]
        #
        self.pos_camara=self.camara.getPos(self.base.render)
        if self.pos_camara.getZ()<self.nivel_agua+1.0:
            altitud_suelo=self.nivel_agua+1.0
        else:
            altitud_suelo=self.altitud_suelo
        altura=self.pos_camara.getZ()-altitud_suelo
        if not self._ajustando_altitud and altura<0.4:
            self._ajustando_altitud=True
        elif self._ajustando_altitud:
            pos_mouse[1]=-0.75
            if altura>1.2: #|0.75
                self._ajustando_altitud=False
        #
        if abs(pos_mouse[0])>0.4:
            foco_cam_H=self.foco.getH()
            foco_cam_H-=90.0*dt*(1.0 if pos_mouse[0]>0.0 else -1.0)
            if self.modo==ControladorCamara.ModoPrimeraPersona:
                if foco_cam_H<-85.0 or foco_cam_H>85.0:
                    return
            else:
                if abs(foco_cam_H)>=360.0:
                    foco_cam_H=0.0
            self.foco.setH(foco_cam_H)
        if abs(pos_mouse[1])>0.4:
            foco_cam_P=self.foco.getP()
            foco_cam_P-=15.0*dt*(1.0 if pos_mouse[1]>0.0 else -1.0)
            if foco_cam_P<-85.0 or foco_cam_P>85.0:
                return
            self.foco.setP(foco_cam_P)

    def _acercar(self):
        distancia_Y=self.camara.getY()
        distancia_Y-=5.0
        if distancia_Y<1.2 and self.modo==ControladorCamara.ModoTerceraPersona:
            distancia_Y=0.0
            self.modo=ControladorCamara.ModoPrimeraPersona
            self.foco.setP(0.0)
            log.info("camara en primera persona")
        elif distancia_Y<0.0:
            distancia_Y=0.0
            return
        self.camara.setY(distancia_Y)

    def _alejar(self):
        distancia_Y=self.camara.getY()
        distancia_Y+=5.0
        if distancia_Y>=1600.0:
            distancia_Y=1600.0
            return
        elif self.modo==ControladorCamara.ModoPrimeraPersona and distancia_Y>1.2:
            self.modo=ControladorCamara.ModoTerceraPersona
            log.info("camara en tercera persona")
            distancia_Y=ControladorCamara.DistanciaInicial
        self.camara.setY(distancia_Y)

    def _mirar_adelante(self):
        if self.modo==ControladorCamara.ModoTerceraPersona:
            self.foco.setH(0.0)
        elif self.modo==ControladorCamara.ModoPrimeraPersona:
            _angulo=self.foco.getH()
            _cuerpo_H=self.target_node_path.getH()
            self.target_node_path.setH(_cuerpo_H+_angulo)
            self.foco.setH(0.0)

