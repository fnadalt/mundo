from direct.gui.OnscreenText import OnscreenText
from panda3d.bullet import *
from panda3d.core import *
from terreno import Terreno
from cielo import Cielo
from agua import Agua
from hombre import Hombre
from camara import ControladorCamara

import logging
log=logging.getLogger(__name__)

class Mundo(NodePath):
    
    def __init__(self, base):
        NodePath.__init__(self, "mundo")
        self.reparentTo(base.render)
        self.setShaderAuto()
        #
        self.base=base
        #
        self.horrendo=base.loader.loadModel("objetos/horrendo")
        self.horrendo.reparentTo(self)
        self.horrendo.setScale(0.15)
        self.horrendo.setPos(0.0, 0.0, -9.5)
        # variables internas
        self._counter=0
        self._personajes=[]
        #
        self._configurar_fisica()
        #
        self._cargar_debug_info()
        self._cargar_material()
        self._cargar_luces()
        self._cargar_hombre()
        self._cargar_terreno()
        # camara y control
        self.controlador_camara=ControladorCamara(self.base, self.base.camera, self.hombre.cuerpo, self.terreno.obtener_altitud)
        self.hombre.controlar(self.controlador_camara, Hombre.controles)
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
        return
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
        self.texto1=OnscreenText(text="info?", pos=(0.5, 0.5), scale=0.05, mayChange=True)

    def _cargar_material(self):
        #self.setMaterialOff(1000)
        material=self.horrendo.getMaterial()
        if material==None:
            material=Material("mundo")
            material.setAmbient(Vec4(1.0, 1.0, 1.0, 1.0))
            material.setDiffuse((0.8, 0.8, 0.8, 1.0))
            material.setSpecular((0.0, 0.0, 0.0, 1.0))
            material.setShininess(0)
        self.setMaterial(material, 0)

    def _cargar_hombre(self):
        self.hombre=Hombre(self)
        self._personajes.append(self.hombre)
        #
    
    def _cargar_terreno(self):
        #
        self.terreno=Terreno(self, self.hombre.cuerpo)
        self.hombre.altitud_suelo=self.terreno.obtener_altitud(self.hombre.cuerpo.getPos())
        #
        self.cielo=Cielo(self)
        #
        self.agua=Agua(self, self.sol_d, self.terreno.nivel_agua)
        self.agua.generar()

    def _cargar_luces(self):
        luz_a=AmbientLight("sol_a")
        luz_a.setColor(Cielo.color*0.12)
        self.sol_a=self.attachNewNode(luz_a)
        self.setLight(self.sol_a)
        #
        luz_d=DirectionalLight("sol_d")
        luz_d.setColor(Vec4(1.0, 1.0, 0.9, 1.0))
        self.sol_d=self.attachNewNode(luz_d)
        self.sol_d.setPos(0.0, 0.0, 1.0)
        self.sol_d.setHpr(0.0, -65.0, 0.0)
        self.sol_d.node()
        self.setLight(self.sol_d)
        #
        point=PointLight("foco")
        point.setColor((0.7, 0.7, 0.7, 1.0))
        self.pointN=self.attachNewNode(point)
        self.pointN.setPos(0.0, 0.0, 1.0)
        #self.setLight(self.pointN)

    def _update(self, task):
        #
        dt=self.base.taskMgr.globalClock.getDt()
        # fisica
        self.mundo_fisico.doPhysics(dt)
        # terreno
        self._counter+=1
        if self._counter==50:
            self._counter=0
            log.debug("update terreno")
            self.terreno.update()
        # personajes
        #self.texto1.setText("_personaje %s:\npos=%s\nvel=%s\naltura=%f\nparcela=%s"%(self.hombre.nombre, str(self.hombre.cuerpo.getPos()), str(self.hombre.velocidad_lineal), self.hombre.altitud_suelo, str(self.terreno.obtener_indice_parcela_foco())))
        for _personaje in self._personajes:
            if _personaje.quieto:
                continue
            _personaje.altitud_suelo=self.terreno.obtener_altitud(_personaje.cuerpo.getPos()) #nivel_agua
        #
        self.agua.plano.setX(self.hombre.cuerpo.getX())
        self.agua.plano.setY(self.hombre.cuerpo.getY())
        self.agua.update(dt)
        #
        return task.cont
    
    def _toggle_debug_fisica(self):
        if self.debug_fisicaN.isHidden():
            self.debug_fisicaN.show()
        else:
            self.debug_fisicaN.hide()
