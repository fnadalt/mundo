from direct.gui.OnscreenText import OnscreenText
from direct.gui.DirectGui import *
from panda3d.bullet import *
from panda3d.core import *

import sistema
#
from cielo import Cielo
from sol import Sol
from terreno import Terreno
from objetos import Objetos
from agua import Agua
from personaje import *
from camara import ControladorCamara
from input import InputMapper
from shader import GestorShader

#import voxels

import logging
log=logging.getLogger(__name__)


class Mundo:

    def __init__(self, base):
        # referencias:
        self.base=base
        self.sistema=None
        # componentes:
        self.nodo=self.base.render.attachNewNode("mundo")
        self.input_mapper=None
        self.controlador_camara=None
        # variables internas:
        self._counter=50 # forzar terreno.update antes de hombre.update
        self._personajes=[]
        self._periodo_dia_actual=0

    def iniciar(self):
        log.info("iniciar")
        # sistema:
        self.sistema=sistema.Sistema()
        self.sistema.iniciar()
        self.sistema.cargar_parametros_iniciales()
        sistema.establecer_instancia(self.sistema)
        # fisica:
        self._configurar_fisica()
        # mundo:
        self._establecer_material()
        self._establecer_shader()
        # componentes:
        self.input_mapper=InputMapper(self.base)
        self.input_mapper.ligar_eventos()
        self.controlador_camara=ControladorCamara(self.base)
        self.controlador_camara.input_mapper=self.input_mapper
        #
        self._cargar_terreno()
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
        log.info("terminar")
        #
        self.agua.terminar()
        self.sol.terminar()
        self.terreno.terminar()
        #
        self.sistema=None
        sistema.remover_instancia()

    def _establecer_material(self):
        log.info("_establecer_material")
        intensidades=(0.20, 0.35, 0.0) # (a,d,s)
        material=Material("material_mundo")
        material.setAmbient((intensidades[0], intensidades[0], intensidades[0], 1.0))
        material.setDiffuse((intensidades[1], intensidades[1], intensidades[1], 1.0))
        material.setSpecular((intensidades[2], intensidades[2], intensidades[2], 1.0))
        material.setShininess(0)
        self.nodo.setMaterial(material, 1)

    def _establecer_shader(self):
        log.info("_establecer_shader")
        GestorShader.iniciar(self.base, sistema.Sistema.TopoAltitudOceano, Vec4(0, 0, 1, sistema.Sistema.TopoAltitudOceano))
        GestorShader.aplicar(self.nodo, GestorShader.ClaseGenerico, 1)
        #GestorShader.aplicar(self, GestorShader.ClaseDebug, 1000)

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
        self.objN=self.nodo.attachNewNode(model_root)
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
        self.debug_fisicaN=self.nodo.attachNewNode(debug_fisica)
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
        _cuerpoN=self.nodo.attachNewNode(_cuerpo)
        _cuerpoN.setPos(0.0, 0.0, 100.0)
        _cuerpoN.setCollideMask(BitMask32.bit(3))
        self.bullet_world.attachRigidBody(_cuerpo)
        _cuerpoN.reparentTo(self.nodo)
        caja=self.base.loader.loadModel("box.egg")
        caja.reparentTo(_cuerpoN)

    def _cargar_debug_info(self):
        Negro=Vec4(0.0, 0.0, 0.0, 1.0)
        #Blanco=Vec4(1.0, 1.0, 1.0, 1.0)
        self.texto1=OnscreenText(text="mundo", pos=(-1.2, 0.9), scale=0.045, align=TextNode.ALeft, fg=Negro, mayChange=True)

    def _cargar_gui(self):
        self.lblHora=DirectLabel(text="00:00", text_fg=(0.15, 0.15, 0.9, 1.0), text_bg=(1.0, 1.0, 1.0, 1.0), scale=0.1, pos=(1.2, 0.0, -0.8), color=(1, 1, 1, 1))
        self.lblTemperatura=DirectLabel(text="0º", text_fg=(0.15, 0.15, 0.9, 1.0), text_bg=(1.0, 1.0, 1.0, 1.0), scale=0.1, pos=(1.2, 0.0, -0.93), color=(1, 1, 1, 1))

    def _cargar_hombre(self):
        #
        self.hombre=Personaje()
        self.hombre.altitud_agua=sistema.Sistema.TopoAltitudOceano
        self.hombre.input_mapper=self.input_mapper
        self.hombre.construir(self.nodo, self.bullet_world)
        self.hombre.cuerpo.setPos(self.sistema.posicion_cursor)
        self.hombre.cuerpo.setZ(self.sistema.obtener_altitud_suelo_cursor()+0.5)
        #
        self._personajes.append(self.hombre)
        #
        self.controlador_camara.seguir(self.hombre.cuerpo)

    def _cargar_objetos(self):
        #
        self.palo=self.base.loader.loadModel("objetos/palof")
        self.palo.reparentTo(self.hombre.handR)
        self.palo.setPos(0.5,0.75,-0.25)
        self.palo.setR(-85.0)
        self.palo.setScale(10.0)
        #
        luz_omni=self.nodo.attachNewNode(PointLight("luz_omni"))
        luz_omni.setPos(Vec3(0, -2, 152.5))
        luz_omni.node().setColor(Vec4(1, 0, 0, 1))
        luz_omni.node().setAttenuation(Vec3(0, 1, 0))
        self.nodo.setShaderInput("luz_omni[0]", luz_omni, priority=4)
        #
        self.spot_light=self.nodo.attachNewNode(Spotlight("spot_light"))
        self.spot_light.setPos(self.hombre.cuerpo.getPos()+Vec3(0, -5, 6))
        self.spot_light.node().setColor((0, 0, 1, 1))
        self.spot_light.node().setAttenuation(Vec3(1, 0, 0))
        self.spot_light.node().setLens(PerspectiveLens())
        self.spot_light.lookAt(self.hombre.cuerpo)
        #self.nodo.setLight(self.spot_light)
        #
        self.nubes=self.base.loader.loadModel("objetos/plano")
        self.nubes.reparentTo(self.nodo)
        #self.nubes.setTwoSided(True)
        self.nubes.setPos(self.hombre.cuerpo.getPos()+Vec3(0, -16, 2.5))
        self.nubes.setP(-90)
        #noise=StackedPerlinNoise2(1, 1, 8, 2, 0.5, 256, 18)
        ts0=TextureStage("ts_nubes")
        tamano=512
        imagen=PNMImage(tamano, tamano)
        #imagen.perlinNoiseFill(noise)
        for x in range(tamano):
            for y in range(tamano):
                #v=noise(x, y)*0.5+0.5
                imagen.setXelA(x, y, 1, 0, 0, 0.5)
        tex0=self.base.loader.loadTexture("texturas/white_noise.png") #Texture("tex_nubes")
#        tex0.load(imagen)
        self.nubes.setTexture(ts0, tex0)
        #
        pelota=self.base.loader.loadModel("objetos/pelota.egg")
        pelota.reparentTo(self.nodo)
        pelota.setZ(self.sistema.obtener_altitud_suelo(self.sistema.posicion_cursor)+3.0)
        material_pelota=Material("material_pelota")
        intensidades=(0.3, 0.2, 0.2)
        material_pelota.setAmbient((intensidades[0], intensidades[0], intensidades[0], 1.0))
        material_pelota.setDiffuse((intensidades[1], intensidades[1], intensidades[1], 1.0))
        material_pelota.setSpecular((intensidades[2], intensidades[2], intensidades[2], 1.0))
        material_pelota.setShininess(20)
        pelota.setMaterial(material_pelota, priority=2)
        GestorShader.aplicar(pelota, GestorShader.ClaseGenerico, 3)
        #
        plano_vertical=self.base.loader.loadModel("objetos/plano_vertical.egg")
        plano_vertical.reparentTo(self.nodo)
        plano_vertical.setPos(0, -6, self.sistema.obtener_altitud_suelo((0, -6, 0)))
        #plano_vertical.setTwoSided(True)
        plano_vertical.setBillboardAxis()
        GestorShader.aplicar(plano_vertical, GestorShader.ClaseGenerico, 3)
        #
        nodo_flatten=self.nodo.attachNewNode("nodo_flatten")
        for x in range(4):
            p=self.base.loader.loadModel("objetos/pelota.egg")
            p.reparentTo(nodo_flatten)
            p.setPos(6, 0, 153+x)
            p.setScale(0.2)
        #nodo_flatten.flattenStrong()

    def _cargar_terreno(self):
        # terreno
        self.terreno=Terreno(self.base, self.bullet_world)
        self.terreno.iniciar()
        self.terreno.nodo.reparentTo(self.nodo)
        self.terreno.update()
        #
        self.objetos=Objetos(self.base)
        self.objetos.iniciar()
        self.objetos.nodo.reparentTo(self.nodo)
        self.objetos.update()
        # cielo
        self.cielo=Cielo(self.base, sistema.Sistema.TopoAltitudOceano-20.0)
        self.cielo.nodo.reparentTo(self.nodo)
#        self.nodo.setLight(self.cielo.luz) reemplazado por shader input
        # sol
        self.sol=Sol(self.base, sistema.Sistema.TopoAltitudOceano-20.0)
        self.sol.pivot.reparentTo(self.nodo) # self.cielo.nodo
        #self.sol.mostrar_camaras()
        self.nodo.setLight(self.sol.luz)
        # agua
        self.agua=Agua(self.base, sistema.Sistema.TopoAltitudOceano)
        self.agua.superficie.reparentTo(self.nodo) # estaba self.base.render
        self.agua.generar()
        #self.agua.mostrar_camaras()
        #
        self.controlador_camara.altitud_agua=sistema.Sistema.TopoAltitudOceano

    def _update(self, task):
        info=""
        info+=self.sistema.obtener_info()+"\n"
        #info+=self.terreno.obtener_info()+"\n"
        #info+=self.hombre.obtener_info()+"\n"
        #info+=self.agua.obtener_info()+"\n"
        #info+=self.input_mapper.obtener_info()+"\n"
        #info+=self.cielo.obtener_info()
        #info+=self.sol.obtener_info()+"\n"
        #self.texto1.setText(info)
        # tiempo
        dt=self.base.taskMgr.globalClock.getDt()
        # input
        self.input_mapper.update()
        # fisica
        self.bullet_world.doPhysics(dt)
        # controlador cámara
        self.controlador_camara.altitud_suelo=self.sistema.obtener_altitud_suelo(self.controlador_camara.pos_camara.getXy())
        self.controlador_camara.update(dt)
        pos_pivot_camara=self.controlador_camara.pivot.getPos(self.nodo)
        # sistema
        self.sistema.update(dt, pos_pivot_camara)
        # ciclo dia/noche, cielo, sol
        offset_periodo=self.sistema.calcular_offset_periodo_dia()
        self.cielo.nodo.setX(self.controlador_camara.target_node_path.getPos().getX())
        self.cielo.nodo.setY(self.controlador_camara.target_node_path.getPos().getY())
        self.cielo.update(pos_pivot_camara, self.sistema.hora_normalizada, self.sistema.periodo_dia_actual, offset_periodo)
        self.sol.update(pos_pivot_camara, self.sistema.hora_normalizada, self.sistema.periodo_dia_actual, offset_periodo)
        # personajes
        for _personaje in self._personajes:
            _altitud_suelo=self.sistema.obtener_altitud_suelo(_personaje.cuerpo.getPos())
            _personaje.altitud_suelo=_altitud_suelo
            _personaje.update(dt)
        # agua
        self.agua.superficie.setX(self.controlador_camara.target_node_path.getPos().getX())
        self.agua.superficie.setY(self.controlador_camara.target_node_path.getPos().getY())
        self.agua.update(dt, self.sol.luz.getPos(self.cielo.nodo), self.sol.luz.node().getColor())
        # contador 1/50
        if self._counter==50:
            self._counter=0
            #
            self.terreno.update(pos_pivot_camara)#self.controlador_camara.target_node_path.getPos()) ?
            self.objetos.update(pos_pivot_camara)
            # gui
            self.lblHora["text"]=self.sistema.obtener_hora()
            self.lblTemperatura["text"]="%.0fº"%self.sistema.obtener_temperatura_actual_grados()
        # mundo
        #log.debug("_update posicion_sol %s"%(str(self.sol.nodo.getPos(self.nodo))))
        self.nodo.setShaderInput("color_luz_ambiental", self.cielo.color_luz_ambiental, priority=10)
        self.nodo.setShaderInput("pos_pivot_camara", pos_pivot_camara, priority=10)
        self.nodo.setShaderInput("posicion_sol", self.sol.nodo.getPos(self.nodo), priority=10)
        self.nodo.setShaderInput("offset_periodo_cielo", self.cielo.offset_periodo, priority=10)
        self.nodo.setShaderInput("color_cielo_base_inicial", self.cielo.color_cielo_base_inicial, priority=10)
        self.nodo.setShaderInput("color_cielo_base_final", self.cielo.color_cielo_base_final, priority=10)
        self.nodo.setShaderInput("color_halo_sol_inicial", self.cielo.color_halo_sol_inicial, priority=10)
        self.nodo.setShaderInput("color_halo_sol_final", self.cielo.color_halo_sol_final, priority=10)
        #
        #self.point_light.setPos(self.point_light, Vec3(0.01, 0, 0))
        #
        self._counter+=1
        return task.cont

    def _toggle_debug_fisica(self):
        if self.debug_fisicaN.isHidden():
            self.debug_fisicaN.show()
        else:
            self.debug_fisicaN.hide()
