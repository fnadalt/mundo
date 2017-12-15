from direct.gui.OnscreenText import OnscreenText
from direct.gui.DirectGui import *
from panda3d.bullet import *
from panda3d.core import *

from dia import Dia
from cielo import Cielo
from sol import Sol
from terreno import Terreno
from agua import Agua
from personaje import *
from camara import ControladorCamara
from input import InputMapper

import voxels

import logging
log=logging.getLogger(__name__)


class Mundo(NodePath):

    PosInicialFoco=Vec3(-937,-323,1) # |(-937,-323,1)
    
    def __init__(self, base):
        NodePath.__init__(self, "mundo")
        self.reparentTo(base.render)
        # referencias:
        self.base=base
        # componentes:
        self.input_mapper=None
        self.controlador_camara=None
        # variables internas:
        self._counter=50 # forzar terreno.update antes de hombre.update
        self._personajes=[]
        self._periodo_dia_actual=0
    
    def iniciar(self):
        self._establecer_shader()
        # fisica:
        self._configurar_fisica()
        # componentes:
        self.input_mapper=InputMapper(self.base)
        self.input_mapper.ligar_eventos()
        self.controlador_camara=ControladorCamara(self.base)
        self.controlador_camara.input_mapper=self.input_mapper
        # mundo:
        self._cargar_material()
        #
        self._cargar_terreno(Mundo.PosInicialFoco)
        self._cargar_hombre()
        #self._cargar_objetos()
        self._cargar_obj_voxel()
        # gui:
        self._cargar_debug_info()
        self._cargar_gui()
        # ShowBase
        self.base.cam.node().setCameraMask(DrawMask(5))
        self.base.render.node().adjustDrawMask(DrawMask(7), DrawMask(0), DrawMask(0))
        #
        self.base.taskMgr.add(self._update, "mundo_update")
    
    def terminar(self):
        pass    

    def _establecer_shader(self):
        self.setShaderOff(0)
        self.base.render.setShaderInput("sun_wpos", Vec3(0, 0, 0), priority=0)
        self.base.render.setShaderInput("water_clipping", Vec4(0, 0, 0, 0), priority=0)
    
    def _cargar_obj_voxel(self):
        return
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
        Negro=Vec4(0.0, 0.0, 0.0, 1.0)
        #Blanco=Vec4(1.0, 1.0, 1.0, 1.0)
        self.texto1=OnscreenText(text="info?", pos=(-1.2, 0.9), scale=0.045, align=TextNode.ALeft, fg=Negro, mayChange=True)

    def _cargar_material(self):
        material=Material("mundo")
        material.setAmbient((0.1, 0.1, 0.1, 1.0))
        material.setDiffuse((1.0, 1.0, 1.0, 1.0))
        material.setSpecular((0.0, 0.0, 0.0, 1.0))
        material.setShininess(0)
        self.setMaterialOff(1)
        self.setMaterial(material, 2)

    def _cargar_gui(self):
        self.lblHora=DirectLabel(text="00:00", text_fg=(0.15, 0.15, 0.9, 1.0), text_bg=(1.0, 1.0, 1.0, 1.0), scale=0.1, pos=(1.2, 0.0, -0.9), color=(1, 1, 1, 1))

    def _cargar_hombre(self):
        #
        self.hombre=Personaje()
        self.hombre.altitud_agua=self.terreno.altitud_agua
        self.hombre.input_mapper=self.input_mapper
        self.hombre.construir(self, self.bullet_world)
        self.hombre.cuerpo.setPos(self.terreno.pos_foco)
        self.hombre.cuerpo.setZ(self.terreno.obtener_altitud(self.terreno.pos_foco)+0.5)
        #
        self._personajes.append(self.hombre)
        #
        self.controlador_camara.seguir(self.hombre.cuerpo)
        self.terreno.foco=self.hombre.cuerpo
    
    def _cargar_objetos(self):
        #
        self.palo=self.base.loader.loadModel("objetos/palof")
        self.palo.reparentTo(self.hombre.handR)
        self.palo.setPos(0.5,0.75,-0.25)
        self.palo.setR(-85.0)
        self.palo.setScale(10.0)
        #
        self.arbusto=self.base.loader.loadModel("objetos/arbustof.01.egg")
        self.arbusto.reparentTo(self)
        self.arbusto.setZ(self.terreno.obtener_altitud(self.arbusto.getPos()))
    
    def _cargar_terreno(self, pos_inicial_foco):
        # dia
        self.dia=Dia(180.0, 0.45) #|(1800.0, 0.50)
        # terreno
        self.terreno=Terreno(self.base, self.bullet_world)
        self.terreno.nodo.reparentTo(self)
        self.terreno.update(pos_inicial_foco)
        # cielo
        self.cielo=Cielo(self.base, self.terreno.altitud_agua+85.0)
        self.cielo.nodo.reparentTo(self)
        self.setLight(self.cielo.luz)
        # sol
        self.sol=Sol(self.base)
        self.sol.pivot.reparentTo(self.cielo.nodo)
        #self.sol.mostrar_camaras()
        self.setLight(self.sol.luz)
        # agua
        self.agua=Agua(self.base, self.terreno.altitud_agua)
        self.agua.superficie.reparentTo(self.base.render)
        self.agua.generar()
        #self.agua.mostrar_camaras()
        #
        self.controlador_camara.altitud_agua=self.terreno.altitud_agua

    def _update(self, task):
        info=""
        info+=self.dia.obtener_info()+"\n"
        info+=self.hombre.obtener_info()+"\n"
        info+=self.agua.obtener_info()+"\n"
        #info+=self.input_mapper.obtener_info()+"\n"
#        info+=self.cielo.obtener_info()
#        info+=self.sol.obtener_info()+"\n"
        #self.texto1.setText(info)
        # tiempo
        dt=self.base.taskMgr.globalClock.getDt()
        # input
        self.input_mapper.update()
        # fisica
        self.bullet_world.doPhysics(dt)
        # controlador cámara
        self.controlador_camara.altitud_suelo=self.terreno.obtener_altitud(self.controlador_camara.pos_camara.getXy())
        self.controlador_camara.update(dt)
        # ciclo dia/noche, cielo, sol
        self.dia.update(dt)
        offset_periodo=self.dia.calcular_offset(self.dia.periodo.actual, self.dia.periodo.posterior)
        self.cielo.nodo.setX(self.controlador_camara.target_node_path.getPos().getX())
        self.cielo.nodo.setY(self.controlador_camara.target_node_path.getPos().getY())
        self.cielo.update(self.sol.nodo.getPos(self.cielo.nodo), self.dia.hora_normalizada, self.dia.periodo.actual, offset_periodo)
        self.sol.update(self.dia.hora_normalizada, self.dia.periodo.actual, offset_periodo)
        # terreno
        if self._counter==50:
            self._counter=0
            self.terreno.update(self.controlador_camara.target_node_path.getPos())
        # personajes
        for _personaje in self._personajes:
            _altitud_suelo=self.terreno.obtener_altitud(_personaje.cuerpo.getPos())
            _personaje.altitud_suelo=_altitud_suelo
            _personaje.update(dt)
        # agua
        self.agua.superficie.setX(self.controlador_camara.target_node_path.getPos().getX())
        self.agua.superficie.setY(self.controlador_camara.target_node_path.getPos().getY())
        self.agua.update(dt, self.sol.luz.getPos(self), self.sol.luz.node().getColor())
        # gui
        #self.lblHora["text"]=self.dia.obtener_hora()
        #
        self._counter+=1
        return task.cont
    
    def _toggle_debug_fisica(self):
        if self.debug_fisicaN.isHidden():
            self.debug_fisicaN.show()
        else:
            self.debug_fisicaN.hide()
