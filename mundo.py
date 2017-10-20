from direct.gui.OnscreenText import OnscreenText
from panda3d.bullet import *
from panda3d.core import *
from cielo import Cielo
from sol import Sol
from terreno import Terreno
from agua import Agua
from personaje import *
from camara import ControladorCamara
from input import InputMapper
from heightmap import HeightMap

import voxels

import logging
log=logging.getLogger(__name__)

class Mundo(NodePath):
    
    def __init__(self, base):
        NodePath.__init__(self, "mundo")
        self.reparentTo(base.render)
        #
        self.base=base
        #
        self.horrendo=base.loader.loadModel("objetos/horrendof")
        self.horrendo.reparentTo(self)
        self.horrendo.setScale(0.15)
        self.horrendo.setPos(0.0, 0.0, -9.5)
        # input y camara
        self.input_mapper=InputMapper(self.base)
        self.input_mapper.ligar_eventos()
        self.controlador_camara=ControladorCamara(self.base)
        self.controlador_camara.input_mapper=self.input_mapper
        # variables internas
        self._counter=50 # forzar terreno.update antes de hombre.update
        self._personajes=[]
        #
        self._configurar_fisica()
        #
        self._cargar_debug_info()
        self._cargar_material()
        self._cargar_luces()
        self._cargar_terreno()
        self._cargar_hombre()
        #
        #self._cargar_obj_voxel()
        #
        self.base.taskMgr.add(self._update, "mundo_update")
    
    def _cargar_obj_voxel(self):
        hm=HeightMap(id=66)
        N=64
        self.obj=voxels.Objeto("volumen", N, N, N, 0)
        for x in range(N-2):
            for y in range(N-2):
                h=int(hm.getHeight(x, y)*N)
                print("%s,%s->%i"%(str(x), str(y), h))
                for z in range(h):
                    self.obj.establecer_valor(x+1, y+1, z+1, 255)
        model_root=ModelRoot("volumen")
        self.objN=self.attachNewNode(model_root)
        self.objN.attachNewNode(self.obj.construir_smooth())
        self.objN.setColor(0.4, 0.4, 0.4, 1)
        self.objN.setTwoSided(True, 1)
        self.objN.setShaderAuto()
        self.objN.setScale(1)
        self.objN.setPos(-N/2, -N/2, -9.5)
    
    def _configurar_fisica(self):
        self.bullet_world=BulletWorld()
        #
        debug_fisica=BulletDebugNode("debug_fisica")
        debug_fisica.showNormals(True)
        self.debug_fisicaN=self.attachNewNode(debug_fisica)
        self.debug_fisicaN.hide()
        self.base.accept("f3", self._toggle_debug_fisica)
        #
        self.bullet_world.setGravity(Vec3(0.0, 0.0, -9.81))
        self.bullet_world.setDebugNode(debug_fisica)
        return
        #
        _shape=BulletBoxShape(Vec3(0.5, 0.5, 0.5))
        _cuerpo=BulletRigidBodyNode("caja_rigid_body")
        _cuerpo.setMass(1.0)
        _cuerpo.addShape(_shape)
        _cuerpoN=self.attachNewNode(_cuerpo)
        _cuerpoN.setPos(0.0, 0.0, 100.0)
        _cuerpoN.setCollideMask(BitMask32.bit(3))
        self.bullet_world.attachRigidBody(_cuerpo)
        _cuerpoN.reparentTo(self)
        caja=self.base.loader.loadModel("box.egg")
        caja.reparentTo(_cuerpoN)
    
    def _cargar_debug_info(self):
        self.texto1=OnscreenText(text="info?", pos=(0.0, 0.9), scale=0.05, align=TextNode.ACenter, mayChange=True)

    def _cargar_material(self):
        self.setMaterialOff()
        return
        material=self.horrendo.getMaterial()
        if material==None:
            material=Material("mundo")
            material.setAmbient(Vec4(1.0, 1.0, 1.0, 1.0))
            material.setDiffuse((0.8, 0.8, 0.8, 1.0))
            material.setSpecular((0.0, 0.0, 0.0, 1.0))
            material.setShininess(0)
        self.setMaterial(material, 0)

    def _cargar_hombre(self):
        #
        self.hombre=Personaje()
        self.hombre.nivel_agua=self.terreno.nivel_agua
        self.hombre.input_mapper=self.input_mapper
        self.hombre.construir(self, self.bullet_world)
        self.hombre.cuerpo.setPos(0, 0, 10) # |(214, 600, 100)
        #
        self._personajes.append(self.hombre)
        #
        self.controlador_camara.seguir(self.hombre.cuerpo)
        self.terreno.foco=self.hombre.cuerpo
    
    def _cargar_terreno(self):
        # cielo
        self.cielo=Cielo(self.base)
        self.cielo.nodo.reparentTo(self)
        # sol
        self.sol=Sol(self.base)
        self.sol.pivot.reparentTo(self.cielo.nodo)
        self.setLight(self.sol.luz)
        # terreno
        self.terreno=Terreno(self.base, self.bullet_world)
        self.terreno.reparentTo(self)
        # agua
        self.agua=Agua(self, self.sol.luz, self.terreno.nivel_agua)
        self.agua.generar()
        #self.agua.mostrar_camaras()
        #
        self.controlador_camara.nivel_agua=self.terreno.nivel_agua

    def _cargar_luces(self):
        luz_a=AmbientLight("sol_a")
        luz_a.setColor(Cielo.Color*0.12)
        self.sol_a=self.attachNewNode(luz_a)
        self.setLight(self.sol_a)
        #
#        luz_d=DirectionalLight("sol_d")
#        luz_d.setColor(Vec4(1.0, 1.0, 0.9, 1.0))
#        self.sol_d=self.attachNewNode(luz_d)
#        self.sol_d.setPos(0.0, 0.0, 1.0)
#        self.sol_d.setHpr(0.0, -65.0, 0.0)
#        self.sol_d.node()
#        self.setLight(self.sol_d)
        #
        point=PointLight("foco")
        point.setColor((0.7, 0.7, 0.7, 1.0))
        self.pointN=self.attachNewNode(point)
        self.pointN.setPos(0.0, 0.0, 1.0)
        #self.setLight(self.pointN)

    def _update(self, task):
        info=""
        #info+=self.hombre.obtener_info()+"\n"
        #info+=self.input_mapper.obtener_info()+"\n"
<<<<<<< HEAD
        info+=self.sol.obtener_info()+"\n"
        info+=self.cielo.obtener_info()
=======
        info+=self.sol.obtener_info()
>>>>>>> 82bf037d9b4b416c9e8d8df28b6db9e691ac8e07
        self.texto1.setText(info)
        # tiempo
        dt=self.base.taskMgr.globalClock.getDt()
        # input
        self.input_mapper.update()
        # fisica
        self.bullet_world.doPhysics(dt)
<<<<<<< HEAD
        # sol y cielo
        self.sol.update(dt)
        self.cielo.update(self.sol.hora)
=======
        # sol
        self.sol.update(dt)
>>>>>>> 82bf037d9b4b416c9e8d8df28b6db9e691ac8e07
        # terreno
        if self._counter==50:
            self._counter=0
            self.terreno.update()
        self._counter+=1
        # agua
        self.agua.plano.setX(self.hombre.cuerpo.getX())
        self.agua.plano.setY(self.hombre.cuerpo.getY())
        self.agua.update(dt)
        # personajes
        for _personaje in self._personajes:
            _altitud_suelo=self.terreno.obtener_altitud(_personaje.cuerpo.getPos())
            _personaje.altitud_suelo=_altitud_suelo
            _personaje.update(dt)
        # controlador cámara
        self.controlador_camara.altitud_suelo=self.terreno.obtener_altitud(self.controlador_camara.pos_camara.getXy())
        self.controlador_camara.update(dt)
        #
        return task.cont
    
    def _toggle_debug_fisica(self):
        if self.debug_fisicaN.isHidden():
            self.debug_fisicaN.show()
        else:
            self.debug_fisicaN.hide()
