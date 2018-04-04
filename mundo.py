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
from hombre import *
from nave import *
from camara import ControladorCamara
from input import InputMapperTecladoMouse
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
        self.terreno=None
        self.cielo=None
        self.sol=None
        self.agua=None
        self.objetos=None
        self.hombre=None
        self.nave=None
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
        self.sistema.update(0.0, self.sistema.posicion_cursor)
        sistema.establecer_instancia(self.sistema)
        # fisica:
        self._configurar_fisica()
        # mundo:
        self._establecer_material() # quitarlo, optimizacion? no, al reves!
        self._establecer_shader()
        # componentes:
        self.input_mapper=InputMapperTecladoMouse(self.base)
        self.controlador_camara=ControladorCamara(self.base)
        self.controlador_camara.iniciar()
        #
        self._cargar_terreno()#
        self._cargar_personajes()#
        self._cargar_objetos()#
        #self._cargar_obj_voxel()
        # gui:
        self._cargar_debug_info()
        self._cargar_gui()
        # ShowBase
        self.base.cam.node().setCameraMask(DrawMask(1))
        self.base.render.node().adjustDrawMask(DrawMask(5), DrawMask(0), DrawMask(0))
        #
        self.base.accept("l-up", self._hacer, [0])
        self.base.accept("m-up", self._hacer, [1])
        self.base.accept("v-up", self._hacer, [2])
        #
        self.base.taskMgr.add(self._update, "mundo_update")
        #

    def terminar(self):
        log.info("terminar")
        #
        self.base.ignore("l-up")
        self.base.ignore("m-up")
        self.base.ignore("v-up")
        #
        self.controlador_camara.terminar()
        #
        for _personaje in self._personajes:
            _personaje.terminar()
        if self.objetos:
            self.objetos.terminar()
        if self.agua:
            self.agua.terminar()
        if self.sol:
            self.sol.terminar()
        if self.cielo:
            self.cielo.terminar()
        if self.terreno:
            self.terreno.terminar()
        #
        self.sistema=None
        sistema.remover_instancia()

    def _hacer(self, que):
        if que==0:
            log.debug(self.sistema.obtener_info())
        elif que==1:
            self.nodo.analyze()
        elif que==2:
            self.base.bufferViewer.toggleEnable()
        elif que==3:
            if not self.nave:
                return
            if not self.hombre.conduciendo:
                self.nave.setPos(self.sistema.posicion_cursor)
                self.hombre.cuerpo.reparentTo(self.nave.cuerpo)
                self.hombre.setPos(Vec3(0, 0, -0.5))
                self.hombre.conduciendo=True
                self.controlador_camara.seguir(self.nave.cuerpo)
            else:
                self.hombre.cuerpo.reparentTo(self.nodo)
                self.hombre.setPos(self.sistema.posicion_cursor)
                self.hombre.conduciendo=False
                self.controlador_camara.seguir(self.hombre.cuerpo)

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
        #
        # ¿esto habra solucionado el problema del clipping caprichoso?
        self.nodo.setShaderInput("altitud_agua", sistema.Sistema.TopoAltitudOceano, 0.0, 0.0, 0.0, priority=1)
        #
        #GestorShader.aplicar(self.nodo, GestorShader.ClaseGenerico, 1) # quitarlo, optimizacion?
        #GestorShader.aplicar(self, GestorShader.ClaseDebug, 1000)

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
        self.objN=self.nodo.attachNewNode(model_root)
        self.objN.attachNewNode(self.obj.iniciar_smooth())
        self.objN.setColor(0.4, 0.4, 0.4, 1)
        self.objN.setTwoSided(True, 1)
        self.objN.setShaderAuto()
        self.objN.setScale(1)
        self.objN.setPos(-N/2, -N/2, -9.5)

    def _configurar_fisica(self):
        self.bullet_world=BulletWorld()
        #return
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

    def _cargar_personajes(self):
        # personajes
        self.hombre=Hombre()
        self._personajes.append(self.hombre)
        # nave
        self.nave=Nave()
        self._personajes.append(self.nave)
        #
        for _personaje in self._personajes:
            _personaje.input_mapper=self.input_mapper
            _personaje.altitud_agua=sistema.Sistema.TopoAltitudOceano
            _personaje.iniciar(self.nodo, self.bullet_world)
        # posicionar
        self.hombre.setPos(self.sistema.posicion_cursor)
        pos=self.sistema.posicion_cursor+Vec3(-3, -3, 0)
        self.nave.setPos(Vec3(pos[0], pos[1], self.sistema.obtener_altitud_suelo(pos)))
        #
        self.controlador_camara.seguir(self.hombre.cuerpo)

    def _cargar_objetos(self):
        #
        self.palo=self.base.loader.loadModel("objetos/palof")
        self.palo.reparentTo(self.nodo)
        self.palo.setPos(self.sistema.obtener_posicion_3d(Vec3(12, 12, 0)))
        #
        luz_omni=self.nodo.attachNewNode(PointLight("luz_omni"))
        luz_omni.setPos(Vec3(0, -2, 152.5))
        luz_omni.node().setColor(Vec4(1, 0, 0, 1))
        luz_omni.node().setAttenuation(Vec3(0, 1.1, 0))
        self.nodo.setShaderInput("luz_omni[0]", luz_omni, priority=4)
#        luz_omni.reparentTo(self.palo)
#        luz_omni.setPos(0, 0, 1)
        #
        self.spot_light=self.nodo.attachNewNode(Spotlight("spot_light"))
        self.spot_light.setPos(self.hombre.cuerpo.getPos()+Vec3(0, -5, 6))
        self.spot_light.node().setColor((1, 1, 0.7, 1))
        self.spot_light.node().setAttenuation(Vec3(0.04,0.025,0.01))
        self.spot_light.node().setLens(PerspectiveLens())
        #self.spot_light.node().setShadowCaster(True, 256, 256)
        self.spot_light.lookAt(self.hombre.cuerpo)
        self.nodo.setLight(self.spot_light)
        self.spot_light.reparentTo(self.palo)
        self.spot_light.setPos(0, 0, 1)
        self.spot_light.setHpr(0, 15, 0)
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
            p.clearModelNodes()
            p.reparentTo(nodo_flatten)
            p.setPos(6, 0, 153+x)
            p.setScale(0.2)
        nodo_flatten.flattenStrong()
        #
        cant=3
        prisma=self.base.loader.loadModel("objetos/prisma_tri.egg")
        prisma_geomnode=prisma.find("**/+GeomNode")
        for i_geom in range(prisma_geomnode.node().getNumGeoms()):
            prisma_geom=prisma_geomnode.node().getGeom(i_geom)
            ##
            prisma_vdata=prisma_geom.getVertexData()
            consolidado_prismas_vdata=GeomVertexData("vertex_data", prisma_vdata.getFormat(), Geom.UHStatic)
            consolidado_prismas_vdata.setNumRows(cant * prisma_vdata.getNumRows())
            offset=prisma_vdata.getNumRows()
            ##
            prisma_prims=list()
            consolidado_prismas_prims=list()
            for i_prim in range(prisma_geom.getNumPrimitives()):
                prim=prisma_geom.getPrimitive(i_prim).decompose()
                prisma_prims.append(prim)
                consolidado_prismas_prim=GeomTriangles(Geom.UHStatic)
                consolidado_prismas_prims.append(consolidado_prismas_prim)
            for i_cant in range(cant):
                vdata=GeomVertexData(prisma_vdata)
                vdata.transformVertices(LMatrix4f.translateMat(3*i_cant, 0.0, 0.0))
                for i_row in range(vdata.getNumRows()):
                    consolidado_prismas_vdata.copyRowFrom(i_cant*offset+i_row, vdata, i_row, Thread.getCurrentThread())
                for i_prim in range(len(prisma_prims)):
                    consolidado_prismas_prim=consolidado_prismas_prims[i_prim]
                    prim_verts=prisma_prims[i_prim].getVertexList()
                    for vert in prim_verts:
                        consolidado_prismas_prim.addVertex(vert+i_cant*offset)
            consolidado_prismas_geom=Geom(consolidado_prismas_vdata)
            consolidado_prismas_geom.addPrimitive(consolidado_prismas_prim)
            #
            consolidado_prismas_geomnode=GeomNode("copia_geomnode")
            consolidado_prismas_geomnode.addGeom(consolidado_prismas_geom)
            self.nodo_prismas=self.nodo.attachNewNode("nodo_prismas")
            self.nodo_prismas.setPos(20, 6, 2+self.sistema.obtener_altitud_suelo((20, 6, 0)))
            self.nodo_prismas.attachNewNode(consolidado_prismas_geomnode)
        #


    def _cargar_terreno(self):
        # terreno
        self.terreno=Terreno(self.base, self.bullet_world)
        self.terreno.iniciar()
        self.terreno.nodo.reparentTo(self.nodo)
        self.terreno.update()
        # cielo
        self.cielo=Cielo(self.base, sistema.Sistema.TopoAltitudOceano-20.0)
        self.cielo.nodo.reparentTo(self.nodo)
        # sol
        self.sol=Sol(self.base, sistema.Sistema.TopoAltitudOceano-20.0)
        self.sol.pivot.reparentTo(self.nodo) # self.cielo.nodo
#        self.sol.mostrar_camaras()
        self.nodo.setLight(self.sol.luz)
        # objetos
        self.objetos=Objetos(self.base)
        self.objetos.iniciar()
        self.objetos.nodo.reparentTo(self.nodo)
        self.objetos.update()
        # agua
        self.agua=Agua(self.base, sistema.Sistema.TopoAltitudOceano)
        self.agua.nodo.reparentTo(self.nodo) # estaba self.base.render
        self.agua.generar()
#        self.agua.mostrar_camaras()
        #
        #self.cielo.nodo.setBin("background", 0)
        #self.sol.nodo.setBin("background", 1)
        #self.agua.nodo.setBin("background", 2)
        #self.terreno.nodo.setBin("opaque", 0)
        #self.objetos.nodo.setBin("transparent", 0)
        #
        self.controlador_camara.altitud_agua=sistema.Sistema.TopoAltitudOceano
        #

    def _update(self, task):
        if self._counter==50:
            info=""
            info+=self.sistema.obtener_info()+"\n"
            #info+=self.terreno.obtener_info()+"\n"
            #info+=self.hombre.obtener_info()+"\n"
            #info+=self.agua.obtener_info()+"\n"
            info+=self.objetos.obtener_info()+"\n"
            #info+=self.input_mapper.obtener_info()+"\n"
            #info+=self.cielo.obtener_info()
            #info+=self.sol.obtener_info()+"\n"
            self.texto1.setText(info)
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
        self.nodo.setShaderInput("pos_pivot_camara", pos_pivot_camara, priority=10)
        # sistema
        self.sistema.update(dt, pos_pivot_camara)
        # cielo
        if self.cielo:
            offset_periodo=self.sistema.calcular_offset_periodo_dia()
            self.cielo.nodo.setX(self.controlador_camara.target_node_path.getPos().getX())
            self.cielo.nodo.setY(self.controlador_camara.target_node_path.getPos().getY())
            self.cielo.update(pos_pivot_camara, self.sistema.hora_normalizada, self.sistema.periodo_dia_actual, offset_periodo)
            self.nodo.setShaderInput("color_luz_ambiental", self.cielo.color_luz_ambiental, priority=10)
            self.nodo.setShaderInput("offset_periodo_cielo", self.cielo.offset_periodo, priority=10)
            self.nodo.setShaderInput("color_cielo_base_inicial", self.cielo.color_cielo_base_inicial, priority=10)
            self.nodo.setShaderInput("color_cielo_base_final", self.cielo.color_cielo_base_final, priority=10)
            self.nodo.setShaderInput("color_halo_sol_inicial", self.cielo.color_halo_sol_inicial, priority=10)
            self.nodo.setShaderInput("color_halo_sol_final", self.cielo.color_halo_sol_final, priority=10)
        # sol
        if self.sol:
            self.sol.update(pos_pivot_camara, self.sistema.hora_normalizada, self.sistema.periodo_dia_actual, offset_periodo)
            self.nodo.setShaderInput("posicion_sol", self.sol.nodo.getPos(self.nodo), priority=10)
        # personajes
        for _personaje in self._personajes:
            _altitud_suelo=self.sistema.obtener_altitud_suelo(_personaje.cuerpo.getPos())
            _personaje.altitud_suelo=_altitud_suelo
            _personaje.update(dt)
        # contador 1/50
        if self._counter==50:
            self._counter=0
            #
            if self.terreno:
                self.terreno.update()#pos_pivot_camara)#self.controlador_camara.target_node_path.getPos()) ?
            if self.objetos:
                self.objetos.update()#pos_pivot_camara)
            # gui
            self.lblHora["text"]=self.sistema.obtener_hora()
            self.lblTemperatura["text"]="%.0fº"%self.sistema.obtener_temperatura_actual_grados()
        # agua
        if self.agua:
            self.agua.nodo.setX(self.controlador_camara.target_node_path.getPos().getX())
            self.agua.nodo.setY(self.controlador_camara.target_node_path.getPos().getY())
            self.agua.update(dt, self.sol.luz.getPos(self.cielo.nodo), self.sol.luz.node().getColor())
        #
        self._counter+=1
        return task.cont

    def _toggle_debug_fisica(self):
        if self.debug_fisicaN.isHidden():
            self.debug_fisicaN.show()
        else:
            self.debug_fisicaN.hide()
