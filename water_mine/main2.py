from direct.gui.OnscreenText import OnscreenText
from direct.showbase.ShowBase import ShowBase
from panda3d.core import *

class App(ShowBase):

    def __init__(self):
        ShowBase.__init__(self)
        #self.disableMouse()
        #
        self.mundo=self.render.attachNewNode("mundo")
        #
        sun=DirectionalLight("sun")
        sun.setColor((0.5, 0.5, 0.5, 1.0))
        sunN=self.render.attachNewNode(sun)
        sunN.setHpr(-45, -45, 0)
        self.mundo.setLight(sunN)
        #
        self.terreno=self.loader.loadModel("terreno")
        self.terreno.reparentTo(self.mundo)
        #self.terreno.setClipPlane(plane_nodeN)
        #
        point=PointLight("foco")
        point.setColor((0.7, 0.7, 0.7, 1.0))
        pointN=self.mundo.attachNewNode(point)
        pointN.setPos(0.0, 0.0, 0.2)
        self.mundo.setLight(pointN)
        #
        self.horrendo=self.loader.loadModel("horrendo")
        self.horrendo.reparentTo(self.mundo)
        self.horrendo.setPos(0.0, 0.0, 3.0)
        #
        self.hombre=self.loader.loadModel("actor.egg")
        self.hombre.reparentTo(self.mundo)
        self.hombre.setPos(0.0, 3.0, -0.5)
        #
        self.vel_cam=Vec2(0.0, 0.0)
        self.nodo_camaras=self.mundo.attachNewNode("nodo_camaras")
        self.camera.reparentTo(self.nodo_camaras)
        self.camera2=None
        self.camera3=None
        #
        self.agua=Agua(self, self.mundo, sunN, -0.05)
        self.agua.generar()
        #
        self.accept("arrow_left", self.input, ["arrow_left"])
        self.accept("arrow_right", self.input, ["arrow_right"])
        self.accept("arrow_up", self.input, ["arrow_up"])
        self.accept("arrow_down", self.input, ["arrow_down"])
        self.accept("+", self.input, ["+"])
        self.accept("-", self.input, ["-"])
        self.accept("q", self.input, ["+pitch"])
        self.accept("a", self.input, ["-pitch"])
        self.accept("w", self.input, ["+nodo_camaras"])
        self.accept("s", self.input, ["-nodo_camaras"])
        self.accept("arrow_left-up", self.input, ["deactivate"])
        self.accept("arrow_right-up", self.input, ["deactivate"])
        self.accept("arrow_up-up", self.input, ["deactivate"])
        self.accept("arrow_down-up", self.input, ["deactivate"])
        self.accept("+-up", self.input, ["deactivate"])
        self.accept("--up", self.input, ["deactivate"])
        self.accept("a-up", self.input, ["deactivate"])
        self.accept("q-up", self.input, ["deactivate"])
        self.accept("w-up", self.input, ["deactivate"])
        self.accept("s-up", self.input, ["deactivate"])
        # debug info text
        self.texto1=OnscreenText(text="info?", pos=(0.5, 0.5), scale=0.05, mayChange=True)
        #
        self.taskMgr.add(self.update,"update")

    def update(self, task):
        dt=self.taskMgr.globalClock.getDt()
        self.agua.update(dt)
        #
        if self.vel_cam!=Vec2.zero():
            self.nodo_camaras.setPos(self.nodo_camaras, Vec3(self.vel_cam, 0.0)*dt)
        #
        return task.cont

    def input(self, tecla):
        dmove=1.0
        if tecla=="arrow_left":
            self.vel_cam.setX(-dmove)
        elif tecla=="arrow_right":
            self.vel_cam.setX(dmove)
        elif tecla=="arrow_up":
            self.vel_cam.setY(dmove)
        elif tecla=="arrow_down":
            self.vel_cam.setY(-dmove)
        elif tecla=="+":
            self.camera.setZ(self.camera, 1.0)
        elif tecla=="-":
            self.camera.setZ(self.camera, -1.0)
        elif tecla=="+pitch":
            self.camera.setP(self.camera, 1.0)
        elif tecla=="-pitch":
            self.camera.setP(self.camera, -1.0)
        elif tecla=="+nodo_camaras":
            self.nodo_camaras.setZ(self.nodo_camaras, 1.0)
        elif tecla=="-nodo_camaras":
            self.nodo_camaras.setZ(self.nodo_camaras, -1.0)
        elif tecla=="deactivate":
            self.vel_cam=Vec2(0.0, 0.0)
            
class Agua:
    
    def __init__(self, app, mundo, luz, altitud):
        self.base=app
        self.camera=app.camera
        self.nodo_camaras=app.nodo_camaras
        self.mundo=mundo
        self.luz=luz
        self.altitud=altitud
        #
        self.camera=self.base.camera
        self.camera2=None
        self.camera3=None
        self.camara_manual=False
        #
        self.plano=self.base.loader.loadModel("plano")
        self.plano.reparentTo(self.mundo)
        self.plano.setScale(1.0)
        self.plano.setTransparency(TransparencyAttrib.MAlpha)
        self.plano.setZ(self.altitud)

    def generar(self):
        #
        self.configurar_reflejo()
        self.configurar_refraccion()
        self.configurar_dudv()
        self.configurar_normal()
        self.move_factor=0.0
        #
        shader=Shader.load(Shader.SL_GLSL, vertex="water.v.glsl", fragment="water.f.glsl")
        self.plano.setShader(shader)
        self.plano.setShaderInput("light_pos", self.luz.getPos())
        self.plano.setShaderInput("light_color", self.luz.node().getColor())

    def configurar_reflejo(self):
        # reflejo
        reflection_plane=Plane(Vec3(0.0, 0.0, 1.0), Vec3(0.0, 0.0, -0.15))
        reflection_plane_node=PlaneNode("reflection_plane_node")
        reflection_plane_node.setPlane(reflection_plane)
        reflection_plane_nodeN=self.mundo.attachNewNode(reflection_plane_node)
        #
        reflection_buffer=self.base.win.makeTextureBuffer('reflection_buffer', 512, 512)
        reflection_buffer.setClearColor(Vec4(0, 0, 0, 1))
        self.camera2=self.base.makeCamera(reflection_buffer)
        self.camera2.reparentTo(self.nodo_camaras)
        self.camera2.node().getLens().setFov(self.camera.find("+Camera").node().getLens().getFov())
        dummy_reflection=NodePath("dummy_reflection")
        dummy_reflection.setTwoSided(False)
        dummy_reflection.setClipPlane(reflection_plane_nodeN)
        self.camera2.node().setInitialState(dummy_reflection.getState())
        #
        ts0=TextureStage("tsBuffer_reflection")
        tex0=reflection_buffer.getTexture()
        tex0.setWrapU(Texture.WMClamp)
        tex0.setWrapV(Texture.WMClamp)
        self.plano.setTexture(ts0, tex0)
        
    def configurar_refraccion(self):
        # refraccion
        refraction_plane=Plane(Vec3(0.0, 0.0, -1.0), Vec3(0.0, 0.0, 0.1))
        refraction_plane_node=PlaneNode("refraction_plane_node")
        refraction_plane_node.setPlane(refraction_plane)
        refraction_plane_nodeN=self.mundo.attachNewNode(refraction_plane_node)
        #
        refraction_buffer=self.base.win.makeTextureBuffer('refraction_buffer', 512, 512)
        refraction_buffer.setClearColor(Vec4(0, 0, 0, 1))
        self.camera3=self.base.makeCamera(refraction_buffer)
        self.camera3.reparentTo(self.nodo_camaras)
        self.camera3.node().getLens().setFov(self.camera.find("+Camera").node().getLens().getFov())
        dummy_refraction=NodePath("dummy_refraction")
        dummy_refraction.setTwoSided(False)
        dummy_refraction.setClipPlane(refraction_plane_nodeN)
        self.camera3.node().setInitialState(dummy_refraction.getState())
        #
        ts1=TextureStage("tsBuffer_refraction")
        tex1=refraction_buffer.getTexture()
        tex1.setWrapU(Texture.WMClamp)
        tex1.setWrapV(Texture.WMClamp)
        self.plano.setTexture(ts1, tex1)
    
    def configurar_dudv(self):
        ts2=TextureStage("tsBuffer_dudv")
        tex2=self.base.loader.loadTexture("agua_dudv.png")
        tex2.setWrapU(Texture.WMRepeat)
        tex2.setWrapV(Texture.WMRepeat)
        self.plano.setTexture(ts2, tex2)
    
    def configurar_normal(self):
        ts3=TextureStage("tsBuffer_normal")
        tex3=self.base.loader.loadTexture("agua_normal.png")
        tex3.setWrapU(Texture.WMRepeat)
        tex3.setWrapV(Texture.WMRepeat)
        self.plano.setTexture(ts3, tex3)
    
    def update(self, dt):
        if not self.camara_manual:
            self.camera2.setPos(self.camera.getPos())
            self.camera2.setHpr(self.camera.getHpr())
            self.camera2.setZ(-self.camera.getZ()-2.0*self.nodo_camaras.getZ())
            self.camera2.setP(-self.camera.getP())
            self.camera2.setR(-self.camera.getR())
            self.camera3.setPos(self.camera.getPos())
            self.camera3.setHpr(self.camera.getHpr())
            self.camera3.setP(self.camera.getP())
        self.base.texto1.setText("cam %s %s\ncam2 %s %s\ncam3 %s %s"%(str(self.camera.getPos(self.mundo)), str(self.camera.getHpr(self.mundo)), str(self.camera2.getPos(self.mundo)), str(self.camera2.getHpr(self.mundo)), str(self.camera3.getPos(self.mundo)), str(self.camera3.getHpr(self.mundo))))
        #
        self.move_factor+=0.03*dt
        self.move_factor%=1
        self.plano.setShaderInput("move_factor", self.move_factor)
        self.plano.setShaderInput("cam_pos", self.camera.getPos(self.mundo))
    
    def dump_info(self):
        info=""
        info+="plano l:%s|%s w:%s|%s\n"%(str(self.plano.getPos()), str(self.plano.getHpr()), str(self.plano.getPos(self.mundo)), str(self.plano.getHpr(self.mundo)))
        info+="nodo  l:%s|%s w:%s|%s\n"%(str(self.nodo_camaras.getPos()), str(self.nodo_camaras.getHpr()), str(self.nodo_camaras.getPos(self.mundo)), str(self.nodo_camaras.getHpr(self.mundo)))
        info+="cam   l:%s|%s w:%s|%s\n"%(str(self.camera.getPos()), str(self.camera.getHpr()), str(self.camera.getPos(self.mundo)), str(self.camera.getHpr(self.mundo)))
        info+="cam2  l:%s|%s w:%s|%s\n"%(str(self.camera2.getPos()), str(self.camera2.getHpr()), str(self.camera2.getPos(self.mundo)), str(self.camera2.getHpr(self.mundo)))
        print(info)
    
app=App()
app.run()
