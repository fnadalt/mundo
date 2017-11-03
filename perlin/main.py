#!/usr/bin/python

from direct.showbase.ShowBase import ShowBase
from direct.gui.DirectGui import *
from panda3d.core import *
import os
import re

class App(ShowBase):
    
    ColorFondoFrame=(0, 0.7, 0.7, 1)
    ColorFondoWidgets=(0.1, 0.78, 0.78,  1)
    ColorTexto=(0.9, 0.9, 0.5, 1)

    def __init__(self):
        super(App, self).__init__()
        # componentes:
        self.plano=None
        self.frame=None
        self.frame_dlg=None
        # variables:
        self.nombre_stacked_perlin_actual=None
        self.stacked_perlin=None
        self.imagen=None
        # init:
        self.disableMouse()
        self.camera.setPos(-0.3, -2.5, 0)
        self.cargar_gui_principal()
        #
        self.accept("aspectRatioChanged", self._on_aspect_ratio_changed)
    
    def generar_plano(self, perlin_override=None):
        if self.plano!=None:
            self.plano.removeNode()
            self.plano=None
        if self.stacked_perlin:
            self.stacked_perlin=None
        if self.imagen:
            self.imagen=None
        #
        _card=CardMaker("plano")
        _card.setFrame(-0.5, 0.5, -0.5, 0.5)
        #_card.setColor(1, 0, 0, 1)
        self.plano=self.render.attachNewNode(_card.generate())
        # obtener valores
        sx=self.aspect2d.find("**/entry_scale_x").node().getText()
        sy=self.aspect2d.find("**/entry_scale_y").node().getText()
        num_levels=self.aspect2d.find("**/entry_levels").node().getText()
        scale_factor=self.aspect2d.find("**/entry_scale_factor").node().getText()
        amp_scale=self.aspect2d.find("**/entry_amp_scale").node().getText()
        table_size=self.aspect2d.find("**/entry_table_size").node().getText()
        seed=self.aspect2d.find("**/entry_seed").node().getText()
        # crear nuevo objeto stacked perlin
        self.stacked_perlin=StackedPerlinNoise2(float(sx), float(sy), int(float(num_levels)), float(scale_factor), float(amp_scale), int(float(table_size)), int(float(seed)))
        perlin_obj=self.stacked_perlin if perlin_override==None else perlin_override
        # generar imagen
        self.imagen=PNMImage(512, 512, 1, 65535)
        min=10.0
        max=0.0
        for x in range(self.imagen.getXSize()):
            for y in range(self.imagen.getYSize()):
                altitud=perlin_obj(x, y)
                altitud/=float(num_levels)
                altitud+=1
                altitud/=2
                if altitud<min: min=altitud
                if altitud>max: max=altitud
                self.imagen.setGray(x, y, altitud)
        print("min/max:%.3f/%.3f"%(min, max))
        self.imagen.write("t.png")
        # establecer textura
        ts0=TextureStage("textura")
        tex0=Texture()
        tex0.load(self.imagen)
        tex0.setWrapU(Texture.WMClamp)
        tex0.setWrapV(Texture.WMClamp)
        self.plano.setTexture(ts0, tex0)
    
    def cargar_gui_principal(self):
        #
        ar=self.getAspectRatio()
        # frame y titulo
        self.frame=DirectFrame(frameColor=App.ColorFondoFrame, frameSize=(0, 1, -1, 1), pos=(-ar, 0, 0))
        DirectLabel(parent=self.frame, text="perlin", text_fg=App.ColorTexto, frameColor=App.ColorFondoFrame, scale=0.1, pos=(0.5, 0, 0.9))
        # stacks
        DirectLabel(parent=self.frame, text="stacks", text_fg=App.ColorTexto, frameColor=App.ColorFondoFrame, scale=0.08, pos=(0.15, 0, 0.75))
        opts=DirectOptionMenu(parent=self.frame, items=["(seleccioná...)"], text_scale=0.5, text_pos=(0.25, 0),  scale=0.1, pos=(0.3, 0, 0.75), text_fg=App.ColorTexto, frameColor=App.ColorFondoWidgets, command=self._on_option_selected)
        DirectButton(parent=self.frame, text="+", frameSize=(-0.5, 0.5, -0.5, 0.5), frameColor=App.ColorFondoWidgets, command=self.agregar_stacked_perlin, pos=(0.35, 0, 0.62), scale=0.1, text_fg=App.ColorTexto, text_pos=(-0.05,-0.15))
        DirectButton(parent=self.frame, text="-", frameSize=(-0.5, 0.5, -0.5, 0.5), frameColor=App.ColorFondoWidgets, command=self.eliminar_stacked_perlin, pos=(0.5, 0, 0.62), scale=0.1, text_fg=App.ColorTexto, text_pos=(-0.05,-0.2))
        # perlin
        nombre=self.nombre_stacked_perlin_actual if self.nombre_stacked_perlin_actual!=None else "?"
        DirectLabel(parent=self.frame, text="nombre", text_align=TextNode.ARight, text_fg=App.ColorTexto, frameColor=App.ColorFondoFrame, scale=0.08, pos=(0.45, 0, 0.35))
        DirectLabel(parent=self.frame, text=nombre, text_align=TextNode.ALeft, text_fg=App.ColorTexto, frameColor=App.ColorFondoFrame, scale=0.08, pos=(0.5, 0, 0.35))
        DirectLabel(parent=self.frame, text="scale x", text_align=TextNode.ARight, text_fg=App.ColorTexto, frameColor=App.ColorFondoFrame, scale=0.08, pos=(0.45, 0, 0.25))
        DirectLabel(parent=self.frame, text="scale y", text_align=TextNode.ARight, text_fg=App.ColorTexto, frameColor=App.ColorFondoFrame, scale=0.08, pos=(0.45, 0, 0.15))
        DirectLabel(parent=self.frame, text="levels", text_align=TextNode.ARight, text_fg=App.ColorTexto, frameColor=App.ColorFondoFrame, scale=0.08, pos=(0.45, 0, 0.05))
        DirectLabel(parent=self.frame, text="scale factor", text_align=TextNode.ARight, text_fg=App.ColorTexto, frameColor=App.ColorFondoFrame, scale=0.08, pos=(0.45, 0, -0.05))
        DirectLabel(parent=self.frame, text="amp scale", text_align=TextNode.ARight, text_fg=App.ColorTexto, frameColor=App.ColorFondoFrame, scale=0.08, pos=(0.45, 0, -0.15))
        DirectLabel(parent=self.frame, text="table size", text_align=TextNode.ARight, text_fg=App.ColorTexto, frameColor=App.ColorFondoFrame, scale=0.08, pos=(0.45, 0, -0.25))
        DirectLabel(parent=self.frame, text="seed", text_align=TextNode.ARight, text_fg=App.ColorTexto, frameColor=App.ColorFondoFrame, scale=0.08, pos=(0.45, 0, -0.35))
        DirectEntry(parent=self.frame, initialText="1", text_scale=0.6, text_pos=(0.25, 0), pos=(0.5, 0, 0.25), text_fg=App.ColorTexto, frameColor=App.ColorFondoWidgets, scale=(0.075, 0.1, 0.1)).setName("entry_scale_x")
        DirectEntry(parent=self.frame, initialText="1", text_scale=0.6, text_pos=(0.25, 0), pos=(0.5, 0, 0.15), text_fg=App.ColorTexto, frameColor=App.ColorFondoWidgets, scale=(0.075, 0.1, 0.1)).setName("entry_scale_y")
        DirectEntry(parent=self.frame, initialText="3", text_scale=0.6, text_pos=(0.25, 0), pos=(0.5, 0, 0.05), text_fg=App.ColorTexto, frameColor=App.ColorFondoWidgets, scale=(0.075, 0.1, 0.1)).setName("entry_levels")
        DirectEntry(parent=self.frame, initialText="1", text_scale=0.6, text_pos=(0.25, 0), pos=(0.5, 0, -0.05), text_fg=App.ColorTexto, frameColor=App.ColorFondoWidgets, scale=(0.075, 0.1, 0.1)).setName("entry_scale_factor")
        DirectEntry(parent=self.frame, initialText="1", text_scale=0.6, text_pos=(0.25, 0), pos=(0.5, 0, -0.15), text_fg=App.ColorTexto, frameColor=App.ColorFondoWidgets, scale=(0.075, 0.1, 0.1)).setName("entry_amp_scale")
        DirectEntry(parent=self.frame, initialText="256", text_scale=0.6, text_pos=(0.25, 0), pos=(0.5, 0, -0.25), text_fg=App.ColorTexto, frameColor=App.ColorFondoWidgets, scale=(0.075, 0.1, 0.1)).setName("entry_table_size")
        DirectEntry(parent=self.frame, initialText="123", text_scale=0.6, text_pos=(0.25, 0), pos=(0.5, 0, -0.35), text_fg=App.ColorTexto, frameColor=App.ColorFondoWidgets, scale=(0.075, 0.1, 0.1)).setName("entry_seed")
        DirectButton(parent=self.frame, text="actualizar", frameSize=(-1.85, 1.85, -0.5, 0.5), frameColor=App.ColorFondoWidgets, command=self.generar_plano, pos=(0.5, 0, -0.55), scale=0.1, text_fg=App.ColorTexto, text_pos=(-0.05,-0.2), text_scale=0.75)
        DirectButton(parent=self.frame, text="guardar", frameSize=(-1.85, 1.85, -0.5, 0.5), frameColor=App.ColorFondoWidgets, command=self.guardar, pos=(0.5, 0, -0.675), scale=0.1, text_fg=App.ColorTexto, text_pos=(-0.05,-0.2), text_scale=0.75)
        # stacked_perlins
        items=["(seleccioná...)"]
        for archivo in [archivo for archivo in os.listdir() if re.fullmatch("perlin\_.*\.txt", archivo)]:
            nombre=archivo[7:-4]
            items.append(nombre)
        opts["items"]=items

    def _on_aspect_ratio_changed(self):
        ar=self.getAspectRatio()
        print("aspect ratio changed to %.3f"%ar)
        self.frame.setPos(-ar, 0, 0)

    def _on_option_selected(self, arg):
        print("option selected %s"%arg)
        if arg=="(seleccioná...)":
            self.nombre_stacked_perlin_actual=None
            self.generar_plano()
        else:
            self.nombre_stacked_perlin_actual=arg
            #
            archivo="perlin_%s.png"%self.nombre_stacked_perlin_actual
            params=dict()
            if os.path.exists(archivo):
                with open(archivo, "r") as arch:
                    linea=arch.readline()
                    while(linea):
                        linea=arch.readline()
                        if linea!="":
                            partes=linea.split("=")
                            params[partes[0]]=partes[1].strip("\n")
            # obtener valores
            self.aspect2d.find("**/entry_scale_x").node().setText(params["scale_x"])
            self.aspect2d.find("**/entry_scale_y").node().setText(params["scale_y"])
            self.aspect2d.find("**/entry_levels").node().setText(params["num_levels"])
            self.aspect2d.find("**/entry_scale_factor").node().setText(params["scale_factor"])
            self.aspect2d.find("**/entry_amp_scale").node().setText(params["amp_scale"])
            self.aspect2d.find("**/entry_table_size").node().setText(params["table_size"])
            self.aspect2d.find("**/entry_seed").node().setText(params["seed"])
            #
            self.generar_plano()
        
    def agregar_stacked_perlin(self):
        print("agregar stack")
        #
        if self.frame!=None:
            self.frame.removeNode()
            self.frame=None
        # dialogo
        ar=self.getAspectRatio()
        self.frame_dlg=DirectFrame(frameColor=App.ColorFondoFrame, frameSize=(0, 1, -1, 1), pos=(-ar, 0, 0))
        DirectLabel(parent=self.frame_dlg, text="agregar pila", text_fg=App.ColorTexto, frameColor=App.ColorFondoFrame, scale=0.1, pos=(0.5, 0, 0.9))
        #
        DirectLabel(parent=self.frame_dlg, text="nombre", text_align=TextNode.ARight, text_fg=App.ColorTexto, frameColor=App.ColorFondoFrame, scale=0.08, pos=(0.45, 0, 0.65)).setName("entry_nombre")
        #
        i=0
        nombre=""
        while(True):
            nombre="pila_%i"%i
            archivo="perlin_%s.png"%nombre
            if not os.path.exists(archivo):
                break
            i+=1
        DirectEntry(parent=self.frame_dlg, initialText=nombre, text_scale=0.6, text_pos=(0.25, 0), pos=(0.5, 0, 0.65), text_fg=App.ColorTexto, frameColor=App.ColorFondoWidgets, scale=(0.075, 0.1, 0.1)).setName("entry_nombre")
        # aceptar / cancelar
        DirectButton(parent=self.frame_dlg, text="aceptar", frameSize=(-1.3, 1.3, -0.5, 0.5), frameColor=App.ColorFondoWidgets, command=self.crear_archivo_stacked_perlin, pos=(0.55, 0, -0.9), scale=0.1, text_fg=App.ColorTexto, text_pos=(-0.05,-0.15), text_scale=0.6)
        DirectButton(parent=self.frame_dlg, text="cancelar", frameSize=(-1.3, 1.3, -0.5, 0.5), frameColor=App.ColorFondoWidgets, command=self.cerrar_dialogo, pos=(0.85, 0, -0.9), scale=0.1, text_fg=App.ColorTexto, text_pos=(-0.05,-0.15), text_scale=0.6)

    def crear_archivo_stacked_perlin(self):
        #
        nombre=self.aspect2d.find("**/entry_nombre").node().getText()
        archivo="perlin_%s.txt"%nombre
        # validar
        if not re.fullmatch("[a-zA-Z]+[a-zA-Z0-9\_]*", nombre):
            entry.node().setText("[alphanum|_]")
            entry.node().setFocus(1)
            return
        if os.path.exists(archivo):
            entry.node().setText("(ya existe!)")
            entry.node().setFocus(1)
            return
        # escribir archivo
        with open(archivo, "w") as arch:
            contenido="nombre=%s\n"%nombre
            contenido+="scale_x=1\n"
            contenido+="scale_y=1\n"
            contenido+="num_levels=1\n"
            contenido+="scale_factor=1\n"
            contenido+="amp_scale=1\n"
            contenido+="table_size=1\n"
            contenido+="seed=1\n"
            arch.write(contenido)
        #
        self.nombre_stacked_perlin_actual=nombre
        #
        self.cerrar_dialogo()

    def eliminar_stacked_perlin(self):
        if self.nombre_stacked_perlin_actual==None:
            return
        #
        print("eliminar stack '%s'..."%self.nombre_stacked_perlin_actual)
        archivo="perlin_%s."%self.nombre_stacked_perlin_actual
        os.remove(archivo+"txt")
        os.remove(archivo+"png")
        self.cargar_gui_principal()
    
    def guardar(self):
        # validar
        for entry in self.aspect2d.find_all_matches("**/+PGEntry"):
            if(entry.node().getName()=="entry_nombre"):
                continue
            if not re.fullmatch("[\+\-]?[0-9]*\.?[0-9]+", entry.node().getText()):
                entry.node().setText("número!")
                entry.node().setFocus(1)
                return
        # archivo nuevo?
        if self.nombre_stacked_perlin_actual==None:
            self.agregar_stacked_perlin()
        if self.nombre_stacked_perlin_actual==None:
            return
        # obtener valores
        sx=self.aspect2d.find("**/entry_scale_x").node().getText()
        sy=self.aspect2d.find("**/entry_scale_y").node().getText()
        num_levels=self.aspect2d.find("**/entry_levels").node().getText()
        scale_factor=self.aspect2d.find("**/entry_scale_factor").node().getText()
        amp_scale=self.aspect2d.find("**/entry_amp_scale").node().getText()
        table_size=self.aspect2d.find("**/entry_table_size").node().getText()
        seed=self.aspect2d.find("**/entry_seed").node().getText()
        # escribir archivo
        with open("perlin_%s.txt"%self.nombre_stacked_perlin_actual, "w") as arch:
            contenido="nombre=%s\n"%self.nombre_stacked_perlin_actual
            contenido+="scale_x=%s\n"%str(sx)
            contenido+="scale_y=%s\n"%str(sy)
            contenido+="num_levels=%s\n"%str(num_levels)
            contenido+="scale_factor=%s\n"%str(scale_factor)
            contenido+="amp_scale=%s\n"%str(amp_scale)
            contenido+="table_size=%s\n"%str(table_size)
            contenido+="seed=%s\n"%str(seed)
            arch.write(contenido)
        #
        self.cerrar_dialogo()        
        
    def cerrar_dialogo(self):
        print("cerrar dialogo")
        if self.frame_dlg!=None:
            self.frame_dlg.removeNode()
            self.frame_dlg=None
        if self.frame==None:
            self.cargar_gui_principal()

if __name__=="__main__":
    app=App()
    app.run()
