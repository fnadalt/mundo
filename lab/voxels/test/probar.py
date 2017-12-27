#!/usr/bin/python3

from direct.showbase.ShowBase import ShowBase
from panda3d.core import *
import voxels

class App(ShowBase):

    def __init__(self):
        ShowBase.__init__(self)
        self.render.setShaderAuto()
        #
        lado=30
        self.objeto=voxels.Objeto("objeto",lado,lado,lado,0)
        self.centro=LVector3f(lado/2,lado/2,lado/2)
        print("centro="+str(self.centro))
        #
        mesh=1 # 0:cubo1x1, 1:esfera
        metodo=1 # 0:cubos, 1:smooth
        #
        if mesh==0:
            self.cubo(self.objeto)
        elif mesh==1:
            self.esfera(self.objeto)
        #
        self._dump_vox_data()
        geom_node=None
        if metodo==0:
            geom_node=self.objeto.construir_cubos()
        elif metodo==1:
            geom_node=self.objeto.construir_smooth()
        self.construir_escena(geom_node)

    def _dump_vox_data(self):
        nx=self.objeto.obtener_dimension_x()
        ny=self.objeto.obtener_dimension_y()
        nz=self.objeto.obtener_dimension_z()
        with open("vox_data.txt", "w") as f:
            for x in range(nx):
                for y in range(ny):
                    for z in range(nz):
                        v=self.objeto.obtener_valor(x, y, z)
                        if v>0:
                            f.write("(%i,%i,%i)->%i\n"%(x, y, z, v))

    def construir_escena(self,geom_node):
        print("Objeto.construir()-> %s"%str(geom_node))
        #
        np=NodePath(geom_node)
        np.setTwoSided(True,1)
        #np.setRenderModeWireframe(True)
        np.reparentTo(self.render)
        #
        lux=NodePath(DirectionalLight("sol"))
        lux.reparentTo(self.render)
        lux.setHpr(40,40,0)
        #
        self.render.setLight(lux)
        #
        self.camera.setPos(np,0,-6,-4)
        self.camera.lookAt(np)
        #
        np.writeBamFile("objeto.bam")

    def cubo(self,o):
        longitud_voxels=15
        for x in range(1,longitud_voxels):
            for y in range(1,longitud_voxels):
                for z in range(1,longitud_voxels):
                    o.establecer_valor(x,y,z,255)

    def esfera(self,o):
        for x in range(1,30):
            for y in range(1,29):
                for z in range(1,29):
                    pos=LVector3f(x,y,z)
                    #print("pos="+str(pos))
                    dist=pos-self.centro
                    if dist.length()<=12:
                        o.establecer_valor(x,y,z,255)
                        #v=o.obtener_valor(x,y,z)
                        #print("(%i,%i,%i)->%i"%(x,y,z,v))

if __name__=="__main__":
	print("Probar voxels")
	app=App()
	app.run()
	print("Prueba de voxels ok")

