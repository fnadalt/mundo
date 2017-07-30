#from panda3d.core import *

import logging
log=logging.getLogger(__name__)

class ControladorCamara:

    CAM_TERCERA_PERSONA=0
    CAM_PRIMERA_PERSONA=1
    #
    CAM_DIST_Y_INICIAL=3.0

    def __init__(self, base, camara,  objetivo):
        self.base=base
        self.objetivo=objetivo
        self.modo=ControladorCamara.CAM_TERCERA_PERSONA
        #
        self.foco=objetivo.attachNewNode("foco")
        self.foco.setZ(0.5)
        #
        self.camara=camara
        self.camara.reparentTo(self.foco)
        self.camara.setY(ControladorCamara.CAM_DIST_Y_INICIAL)
        self.camara.lookAt(self.foco)

    def acercar(self):
        distancia_Y=self.camara.getY()
        distancia_Y-=5.0
        if distancia_Y<1.2 and self.modo==ControladorCamara.CAM_TERCERA_PERSONA:
            distancia_Y=0.0
            self.modo=ControladorCamara.CAM_PRIMERA_PERSONA
            self.foco.setP(0.0)
            log.info("camara en primera persona")
        elif distancia_Y<0.0:
            distancia_Y=0.0
            return
        self.camara.setY(distancia_Y)
#        log.debug("acercar_camara")
#        log.debug("self.distancia %s"%str(self.distancia))
#        log.debug("self.camara %s"%str(self.camara.getPos()))

    def alejar(self):
        distancia_Y=self.camara.getY()
        distancia_Y+=5.0
        if distancia_Y>=1600.0:
            distancia_Y=1600.0
            return
        elif self.modo==ControladorCamara.CAM_PRIMERA_PERSONA and distancia_Y>1.2:
            self.modo=ControladorCamara.CAM_TERCERA_PERSONA
            log.info("camara en tercera persona")
            distancia_Y=ControladorCamara.CAM_DIST_Y_INICIAL
        self.camara.setY(distancia_Y)
#        log.debug("alejar_camara")
#        log.debug("self.distancia %s"%str(self.distancia))
#        log.debug("self.camara %s"%str(self.camara.getPos()))

    def mirar_adelante(self):
        if self.modo==ControladorCamara.CAM_TERCERA_PERSONA:
            self.foco.setH(0.0)
        elif self.modo==ControladorCamara.CAM_PRIMERA_PERSONA:
            _angulo=self.foco.getH()
            _cuerpo_H=self.objetivo.getH()
            self.objetivo.setH(_cuerpo_H+_angulo)
            self.foco.setH(0.0)

    def update(self, dt):
        #
        if self.base.mouseWatcherNode.hasMouse():
            pos_mouse=self.base.mouseWatcherNode.getMouse()
            if abs(pos_mouse.getX())>0.4:
                foco_cam_H=self.foco.getH()
                foco_cam_H-=90.0*dt*(1.0 if pos_mouse[0]>0.0 else -1.0)
                if self.modo==ControladorCamara.CAM_PRIMERA_PERSONA:
                    if foco_cam_H<-85.0 or foco_cam_H>85.0:
                        return
                else:
                    if abs(foco_cam_H)>=360.0:
                        foco_cam_H=0.0
                self.foco.setH(foco_cam_H)
            if abs(pos_mouse.getY())>0.4:
                foco_cam_P=self.foco.getP()
                foco_cam_P-=15.0*dt*(1.0 if pos_mouse[1]>0.0 else -1.0)
                if foco_cam_P<-25.0 or foco_cam_P>25.0:
                    return
                self.foco.setP(foco_cam_P)
