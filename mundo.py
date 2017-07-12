from direct.gui.OnscreenText import OnscreenText
from panda3d.bullet import *
from panda3d.core import *
from terreno import Terreno
from hombre import Hombre

import logging
log=logging.getLogger(__name__)

class Mundo(NodePath):
    
    def __init__(self, base):
        NodePath.__init__(self, "mundo")
        self.reparentTo(base.render)
        #
        self.base=base
        # variables internas
        self._personajes=[]
        #
        self._configurar_fisica()
        #
        self._cargar_debug_info()
        self._cargar_hombre()
        self._cargar_terreno()
        self._cargar_luces()
        #
        self.base.taskMgr.add(self._update, "world_update")
    
    def _configurar_fisica(self):
        self.mundo_fisico=BulletWorld()
        #
        debug_fisica=BulletDebugNode("debug_fisica")
        debug_fisica.showNormals(True)
        self.debug_fisicaN=self.attachNewNode(debug_fisica)
        self.debug_fisicaN.hide()
        self.base.accept("f3", self._toggle_debug_fisica)
        #
        self.mundo_fisico.setGravity(Vec3(0.0, 0.0, -9.81))
        self.mundo_fisico.setDebugNode(debug_fisica)
        #
        _shape=BulletBoxShape(Vec3(0.5, 0.5, 0.5))
        _cuerpo=BulletRigidBodyNode("caja_rigid_body")
        _cuerpo.setMass(1.0)
        _cuerpo.addShape(_shape)
        _cuerpoN=self.attachNewNode(_cuerpo)
        _cuerpoN.setPos(0.0, 0.0, 100.0)
        _cuerpoN.setCollideMask(BitMask32.bit(3))
        self.mundo_fisico.attachRigidBody(_cuerpo)
        _cuerpoN.reparentTo(self)
        caja=self.base.loader.loadModel("box.egg")
        caja.reparentTo(_cuerpoN)
    
    def _cargar_debug_info(self):
        self.texto1=OnscreenText(text="info?", pos=(0.9, 0.9), scale=0.05, mayChange=True)
    
    def _cargar_hombre(self):
        self.hombre=Hombre(self)
        self._personajes.append(self.hombre)
        #
        controles={
                        "w":"avanzar", "s":"retroceder", "a":"desplazar_izquierda", "d":"desplazar_derecha", 
                        "q":"girar_izquierda", "e":"girar_derecha", "wheel_up":"acercar_camara", "wheel_down":"alejar_camara", 
                        "mouse1-up":"mirar_adelante", "space":"saltar"
                        }
        self.hombre.controlar(self.base.cam, controles)
    
    def _cargar_terreno(self):
        self.terreno=Terreno(self, self.hombre.cuerpo)
        altitud=self.terreno.obtener_altitud(self.hombre.cuerpo.getPos())
        self.hombre.establecer_altitud(altitud)
        log.debug("hombre at "+str(self.hombre.cuerpo.getPos()))
        test=self.mundo_fisico.rayTestAll(LPoint3(0.0, 0.0, 1000.0), LPoint3(0.0, 0.0, -1000.0))
        for hit in test.getHits():
            log.debug("ray test hit %s at %s"%(str(hit.getNode()), str(hit.getHitPos())))

    def _cargar_luces(self):
        luz_d=DirectionalLight("sol0")
        luz_d.setColor(Vec4(0.55, 0.55, 0.55, 1.0))
        self.sol0=self.base.render.attachNewNode(luz_d)
        self.sol0.setHpr(45.0, -75.0, 0.0)
        self.setLight(self.sol0)
    
    def _update(self, task):
        #
        dt=self.base.taskMgr.globalClock.getDt()
        # fisica
        self.mundo_fisico.doPhysics(dt)
        # personajes
        for _personaje in self._personajes:
            if _personaje.quieto:
                continue
            pos=_personaje.cuerpo.getPos()
            altitud=self.terreno.obtener_altitud(pos)
            altura=pos.getZ()-altitud
            if _personaje.esta_cayendo():
                if altura<=_personaje.velocidad_lineal.getZ():
                    _personaje.detener_caida()
                    _personaje.establecer_altitud(altitud)
            elif not _personaje.esta_elevandose():
                if altura>0.1:
                    _personaje.iniciar_caida()
                else:
                    _personaje.establecer_altitud(altitud)
            self.texto1.setText("_personaje %s:\npos=%s\nvel=%s\naltura=%f"%(_personaje.nombre, str(pos), str(_personaje.velocidad_lineal), altura))
        #
        return task.cont
    
    def _toggle_debug_fisica(self):
        if self.debug_fisicaN.isHidden():
            self.debug_fisicaN.show()
        else:
            self.debug_fisicaN.hide()
