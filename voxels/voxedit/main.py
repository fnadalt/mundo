#!/usr/bin/python
from direct.gui.OnscreenText import OnscreenText
from direct.gui.DirectButton import DirectButton
from direct.gui.DirectCheckButton import DirectCheckButton
from direct.showbase.ShowBase import ShowBase
from panda3d.core import *
from panda3d.bullet import *
import voxels

class App(ShowBase):

    def __init__(self):
        ShowBase.__init__(self)
        self.disableMouse()
        #
        self.altura_voxels=15
        # variables
        self.dimensiones_plano_base=Point2()
        self.dimensiones_cursor_3d=Point3()
        self.punto_plano_base=Point2() # proyección desde el lente de la cámara hacia el plano
        self.posicion_cursor_3d=Point3() # posición del cursor
        self.posicion_ancla_1=Point3()
        self.posicion_ancla_2=Point3()
        self.dif_anclas=Point3()
        self.altura_cursor_3d=0
        self.arrantrando=False
        self.moviendo_camara=False
        self.objeto_voxels=None
        self.eliminar_voxel=False
        self.cubos_voxel=dict() # {"x:y:z":cubo_voxel,...}
        self.baked=None
        self.smooth=False
        # nodo base
        self.mundo=self.render.attachNewNode("mundo")
        # modelos
        self._cargar_plano_base()
        self._cargar_cursor_3d()
        self._cargar_cubo_voxel()
        # luces y camara
        self._configurar_luces()
        self._configurar_camara()
        # grilla
        self._construir_grilla()
        self._construir_hud()
        # voxels
        self._construir_objeto_voxels()
        # debug info text
        self.texto1=OnscreenText(text="info?", pos=(-1.2, 0.9), scale=0.05, align=TextNode.ALeft, mayChange=True)
        # input
        self._configurar_input()
        # update task
        self.taskMgr.add(self.update,"update")

    def update(self, task):
        #
        if self.mouseWatcherNode.hasMouse():
            #
            mouse_pos=self.mouseWatcherNode.getMouse()
            if self.moviendo_camara:
                dt=self.taskMgr.globalClock.getDt()
                self.texto1.setText("mouse=%s"%(str(mouse_pos)))
                if abs(mouse_pos[0])>0.25:
                    pivot_h=self.pivot_camara.getH()+90*mouse_pos[0]*dt
                    if pivot_h>360: pivot_h=0
                    self.pivot_camara.setH(pivot_h)
                if abs(mouse_pos[1])>0.25:
                    pivot_p=self.pivot_camara.getP()+90*mouse_pos[1]*dt
                    if pivot_p>10 and pivot_p<85:
                        self.pivot_camara.setP(pivot_p)
            else:
                self.punto_plano_base=self._obtener_punto_plano_base_en_plano_base(mouse_pos)
                self.posicion_cursor_3d=self._calcular_posicion_cursor_3d(self.punto_plano_base)
                if self.arrantrando and self.posicion_cursor_3d:
                    self.posicion_ancla_2=self.posicion_cursor_3d
                    self.dif_anclas=self.posicion_ancla_2-self.posicion_ancla_1
                self.dibujar_cursor_3d()
                #
                if self.posicion_cursor_3d:
                    pos_voxel=self._calcular_posicion_grilla_voxel(self.posicion_cursor_3d)
                    self.texto1.setText("cursor (plano)=%s\ncursor (pos)=%s\ncursor (grilla)=%s\narrastrando=%s,(%s)"%(str(self.punto_plano_base), str(self.posicion_cursor_3d), str(pos_voxel), str(self.arrantrando), str(self.dif_anclas)))
        return task.cont

    def _configurar_luces(self):
        #
        sun=DirectionalLight("sun")
        sun.setColor((0.5, 0.5, 0.5, 1.0))
        sunN=self.render.attachNewNode(sun)
        sunN.setHpr(-45, -45, 0)
        self.mundo.setLight(sunN)
        #
        point=PointLight("foco")
        point.setColor((0.7, 0.7, 0.7, 1.0))
        pointN=self.mundo.attachNewNode(point)
        pointN.setPos(0.0, 0.0, 0.2)
        self.mundo.setLight(pointN)

    def _configurar_camara(self):
        #
        self.pivot_camara=self.mundo.attachNewNode("pivot_camara")
        self.pivot_camara.setPos(0, 0, 0)
        #
        self.camera.reparentTo(self.pivot_camara)
        self.camera.setPos(0, 42, 0)
        self.camera.lookAt(self.pivot_camara)
        self.pivot_camara.setHpr(45, 30, 0)

    def _cargar_plano_base(self):
        #
        self.plano_base=self.loader.loadModel("plano_base")
        self.phys_world=BulletWorld()
        tri_mesh=BulletTriangleMesh()
        tri_mesh.addGeom(self.plano_base.find("+GeomNode").node().getGeom(0))
        tri_mesh_shape=BulletTriangleMeshShape(tri_mesh, dynamic=False)
        rig_body=BulletRigidBodyNode("rig_body_plano_base")
        rig_body.addShape(tri_mesh_shape)
        self.rig_body_node=self.mundo.attachNewNode(rig_body)
        self.phys_world.attachRigidBody(rig_body)
        #
        self.plano_base.reparentTo(self.rig_body_node)
        self.plano_base.setR(180)
        #
        bnds_plano_base=self.plano_base.getTightBounds()
        self.dimensiones_plano_base=Point2(bnds_plano_base[1][0]-bnds_plano_base[0][0], bnds_plano_base[1][1]-bnds_plano_base[0][1])

    def _cargar_cursor_3d(self):
        #
        self.cursor_3d=self.loader.loadModel("cursor_3d")
        self.cursor_3d.reparentTo(self.mundo)
        self.cursor_3d.setMaterialOff(2)
        self.cursor_3d.setColor(LVector4f(0, 1, 0, 1))
        self.cursor_3d.setRenderModeWireframe(True)
        #
        self.cursor_3d_2=self.loader.loadModel("cursor_3d")
        self.cursor_3d_2.reparentTo(self.mundo)
        self.cursor_3d_2.setSz(0.01)
        #
        bnds_cursor_3d=self.cursor_3d.getTightBounds()
        self.dimensiones_cursor_3d=Point3(bnds_cursor_3d[1][0]-bnds_cursor_3d[0][0], bnds_cursor_3d[1][1]-bnds_cursor_3d[0][1], bnds_cursor_3d[1][2]-bnds_cursor_3d[0][2])

    def _cargar_cubo_voxel(self):
        self.cubo_voxel=self.loader.loadModel("cubo_voxel")
        self.cubo_voxel.reparentTo(self.mundo)
        self.cubo_voxel.setZ(-1)
        self.cubo_voxel.setShaderAuto(True, 1)

    def _construir_hud(self):
        # boton crear mesh
        btn_crear_mesh=DirectButton(text="crear mesh", scale=0.075, pos=Vec3(0.95, 0.9), command=self._crear_mesh)
        btn_crear_mesh.reparentTo(self.aspect2d)
        # check smooth
        chk_smooth=DirectCheckButton(text="smooth", scale=0.075, pos=Vec3(0.95, 0.8), command=self._establecer_smooth)
        chk_smooth.reparentTo(self.aspect2d)
        # boton eliminar mesh
        btn_eliminar_mesh=DirectButton(text="eliminar mesh", scale=0.075, pos=Vec3(0.95, 0.7), command=self._eliminar_mesh)
        btn_eliminar_mesh.reparentTo(self.aspect2d)

    def _establecer_smooth(self, bool):
        self.smooth=bool

    def _eliminar_mesh(self):
        #
        if self.baked!=None:
            self.baked.removeNode()
            self.baked=None

    def _dump_vox_data(self):
        nx=self.objeto_voxels.obtener_dimension_x()
        ny=self.objeto_voxels.obtener_dimension_y()
        nz=self.objeto_voxels.obtener_dimension_z()
        with open("vox_data.txt", "w") as f:
            for x in range(nx):
                for y in range(ny):
                    for z in range(nz):
                        v=self.objeto_voxels.obtener_valor(x, y, z)
                        if v>0:
                            f.write("(%i,%i,%i)->%i\n"%(x, y, z, v))

    def _crear_mesh(self):
        print("crear mesh")
        print("- eliminando cubos voxel...")
        for k, v in self.cubos_voxel.items():
            self.cubos_voxel[k]=None
            v.removeNode()
        self.cubos_voxel.clear()
        print("- eliminando mesh anterior...")
        self._eliminar_mesh()
        print("- extrayendo superficie a partir de los voxels...")
        geom_node=None
        if self.smooth:
            geom_node=self.objeto_voxels.construir_smooth()
        else:
            geom_node=self.objeto_voxels.construir_cubos()
        self.objeto_voxels.establecer_valores(0)
        self.baked=self.mundo.attachNewNode(geom_node)
        self.baked.setTwoSided(True)
        self.baked.setX(-self.dimensiones_plano_base[0]/2+0.5)
        self.baked.setY(-self.dimensiones_plano_base[1]/2+0.5)
        self.baked.setZ(-1.5)

    def _construir_grilla(self):
        lines=LineSegs("grilla")
        lines.setColor(LVector4f(0, 1, 0, 1))
        dim_x=int(self.dimensiones_plano_base[0])
        dim_y=int(self.dimensiones_plano_base[1])
        for x in range(-int(dim_x/2), int(dim_x/2)+1):
            lines.moveTo(x, self.dimensiones_plano_base[1]/2, 0.01)
            lines.drawTo(x, -self.dimensiones_plano_base[1]/2, 0.01)
        for y in range(-int(dim_y/2), int(dim_y/2)+1):
            lines.moveTo(self.dimensiones_plano_base[0]/2, y, 0.01)
            lines.drawTo(-self.dimensiones_plano_base[0]/2, y, 0.01)
        geom_n=lines.create()
        self.mundo.attachNewNode(geom_n)
        
    def _construir_objeto_voxels(self):
        #
        lado_x=self.dimensiones_plano_base[0]+2 # "+2" -> margen de un voxel a cada lado
        lado_y=self.dimensiones_plano_base[1]+2
        lado_altura=self.altura_voxels+2
        self.objeto_voxels=voxels.Objeto("objeto_voxels", int(lado_x), int(lado_y), lado_altura, 0)

    def _obtener_punto_plano_base_en_plano_base(self, mouse_pos):
        hit_pos=None
        #
        v_from=Point3()
        v_to=Point3()
        self.camLens.extrude(mouse_pos, v_from, v_to)
        v_from=self.render.getRelativePoint(self.cam, v_from)
        v_to=self.render.getRelativePoint(self.cam, v_to)
        #
        ray_result=self.phys_world.rayTestClosest(v_from, v_to)
        hit_node=ray_result.getNode()
        if hit_node:
            hit_pos=ray_result.getHitPos()
        #
        return hit_pos

    def _calcular_posicion_cursor_3d(self, punto_plano_base):
        punto=None
        if punto_plano_base:
            pos_x=int(punto_plano_base[0]+0.5)
            pos_y=int(punto_plano_base[1]+0.5)-1
            pos_z=1+self.altura_cursor_3d*self.dimensiones_cursor_3d[2]+0.02
            punto=Point3(pos_x, pos_y, pos_z)
        return punto

    def _calcular_posicion_grilla_voxel(self, posicion_cursor_3d):
        posicion=None
        if posicion_cursor_3d:
            pos_x=posicion_cursor_3d[0]+(self.dimensiones_plano_base[0]/2)-1
            pos_y=posicion_cursor_3d[1]+(self.dimensiones_plano_base[1]/2)
            pos_z=posicion_cursor_3d[2]
            posicion=Point3(pos_x, pos_y, pos_z)
        return posicion

    def _configurar_input(self):
        self.accept("escape", self.cancelar_arrastre)
        self.accept("control", self._eliminar_voxel, [True])
        self.accept("control-up", self._eliminar_voxel, [False])
        self.accept("mouse1", self.colocar_cubos)
        self.accept("control-mouse1", self.colocar_cubos)
        self.accept("mouse2", self._mover_camara, [True])
        self.accept("mouse2-up", self._mover_camara, [False])
        self.accept("mouse3", self.iniciar_arrastre)
        self.accept("wheel_up", self.mouse_wheel, [1])
        self.accept("wheel_down", self.mouse_wheel, [-1])

    def _eliminar_voxel(self, bool):
        print("_eliminar_voxel %s"%(str(bool)))
        self.eliminar_voxel=bool
        self.cursor_3d.setColorOff(1)
        if bool:
            self.cursor_3d.setColor(LVector4f(1, 0, 0, 1))
        else:
            self.cursor_3d.setColor(LVector4f(0, 1, 0, 1))

    def _mover_camara(self, bool):
        self.moviendo_camara=bool

    def iniciar_arrastre(self):
        if not self.arrantrando and self.posicion_cursor_3d:
            self.arrantrando=True
            self.posicion_ancla_1=self.posicion_cursor_3d
            self.posicion_ancla_2=self.posicion_ancla_1

    def cancelar_arrastre(self):
        self.arrantrando=False
        self.cursor_3d.setScale(1)
        self.dif_anclas=Point3()

    def _calcular_pos_desde_anclas(self):
        pos_x=self.posicion_ancla_1[0]+self.dif_anclas[0] if self.dif_anclas[0]>0 else self.posicion_ancla_1[0]
        pos_y=self.posicion_ancla_1[1]+self.dif_anclas[1] if self.dif_anclas[1]<0 else self.posicion_ancla_1[1]
        pos_z=self.posicion_ancla_1[2]+self.dif_anclas[2] if self.dif_anclas[2]>0 else self.posicion_ancla_1[2]
        return Point3(pos_x, pos_y, pos_z)

    def dibujar_cursor_3d(self):
        if self.arrantrando:
            pos=self._calcular_pos_desde_anclas()
            self.cursor_3d.setPos(pos)
            self.cursor_3d.setSx(1+abs(self.dif_anclas[0]))
            self.cursor_3d.setSy(1+abs(self.dif_anclas[1]))
            self.cursor_3d.setSz(1+abs(self.dif_anclas[2]))
        elif not self.arrantrando and self.posicion_cursor_3d:
            self.cursor_3d.setPos(self.posicion_cursor_3d)
        pos_2=self.cursor_3d.getPos()
        pos_2[2]=0.01
        self.cursor_3d_2.setPos(pos_2)

    def colocar_cubos(self):
        print("colocar cubos")
        if self.arrantrando:
            pos0=self._calcular_pos_desde_anclas()
            print("colocar cubos, posicion inicial %s"%pos0)
            for x in range(abs(int(self.dif_anclas[0]))+1):
                for y in range(abs(int(self.dif_anclas[1]))+1):
                    for z in range(abs(int(self.dif_anclas[2]))+1):
                        pos_x=pos0[0]-x*self.dimensiones_cursor_3d[0]
                        pos_y=pos0[1]+y*self.dimensiones_cursor_3d[1]
                        pos_z=pos0[2]-z*self.dimensiones_cursor_3d[2]+1
                        pos=Point3(pos_x, pos_y, pos_z)
                        self.colocar_cubo(pos)
            self.cancelar_arrastre()
        elif not self.arrantrando and self.posicion_cursor_3d:
            self.colocar_cubo(self.posicion_cursor_3d+Point3(0, 0, 1))

    def colocar_cubo(self, posicion):
        #
        pos_grilla_voxel=self._calcular_posicion_grilla_voxel(posicion)
        str_idx_pos="%s:%s:%s"%(str(int(pos_grilla_voxel[0])), str(int(pos_grilla_voxel[1])), str(int(pos_grilla_voxel[2])))
        if not self.eliminar_voxel:
            print("colocar voxel %s"%(str_idx_pos))
            self.objeto_voxels.establecer_valor(pos_grilla_voxel, 255)
            if not str_idx_pos in self.cubos_voxel:
                print("generando cubo_voxel...")
                cubo=self.mundo.attachNewNode("cubo_%s"%str(posicion))
                self.cubo_voxel.instanceTo(cubo)
                cubo.setPos(posicion)
                self.cubos_voxel[str_idx_pos]=cubo
            else:
                print("el cubo_voxel ya existe")
        else:
            print("eliminar voxel %s"%(str_idx_pos))
            self.objeto_voxels.establecer_valor(pos_grilla_voxel, 0)
            if str_idx_pos in self.cubos_voxel:
                cubo=self.cubos_voxel[str_idx_pos]
                del self.cubos_voxel[str_idx_pos]
                cubo.removeNode()

    def mouse_wheel(self, delta):
        self.altura_cursor_3d+=delta
        if self.altura_cursor_3d<0:
            self.altura_cursor_3d=0
        elif self.altura_cursor_3d>15:
            self.altura_cursor_3d=15

app=App()
app.run()
