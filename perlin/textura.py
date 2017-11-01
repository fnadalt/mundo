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
        self.stacked_perlins=list() # [StackedPerlinNoise2, ...]
        self.plano=None
        self.frame=None
        self.frame_dlg=None
        # variables:
        self.nombre_pila_actual=None
        # init:
        self.disableMouse()
        self.camera.setPos(-0.3, -2.5, 0)
        self.generar_plano()
        self.generar_gui()
        #
        self.accept("aspectRatioChanged", self._on_aspect_ratio_changed)
    
    def agregar_stacked_perlin(self, nombre, sx, sy, num_levels, scale_factor, amp_scale, table_size, seed):
        stackedp=StackedPerlinNoise2(float(sx), float(sy), int(float(num_levels)), float(scale_factor), float(amp_scale), int(float(table_size)), int(float(seed)))
        self.stacked_perlins.append(stackedp)
        #
        archivo="perlin_%s.png"%nombre
        if not os.path.exists(archivo):
            print("generando imágen '%s'..."%archivo)
            imagen=PNMImage(512, 512, 1, 65535)
            for x in range(imagen.getXSize()):
                for y in range(imagen.getYSize()):
                    altitud=stackedp(x, y)
                    imagen.setGray(x, y, altitud)
            imagen.write(archivo)
    
    def agregar_ruido(self, indice_stackedp, amp, sx, sy, table_size, seed):
        perlin=PerlinNoise2(sx, sy, table_size, seed)
        self.stacked_perlins[indice_stackedp].addLevel(perlin, amp)
        
    def generar_plano(self, archivo_imagen="fondo.png"):
        if self.plano!=None:
            self.plano.removeNode()
            self.plano=None
        #
        _card=CardMaker("plano")
        _card.setFrame(-0.5, 0.5, -0.5, 0.5)
        #_card.setColor(1, 0, 0, 1)
        self.plano=self.render.attachNewNode(_card.generate())
        #
        ts0=TextureStage("textura")
        tex0=self.loader.loadTexture(archivo_imagen)
        tex0.setWrapU(Texture.WMClamp)
        tex0.setWrapV(Texture.WMClamp)
        self.plano.setTexture(ts0, tex0)
    
    def generar_gui(self):
        # resetear stacked_perlins
        if len(self.stacked_perlins)>0:
            self.stacked_perlins.clear()
        #
        ar=self.getAspectRatio()
        # frame y titulo
        self.frame=DirectFrame(frameColor=App.ColorFondoFrame, frameSize=(0, 1, -1, 1), pos=(-ar, 0, 0))
        DirectLabel(parent=self.frame, text="perlin", text_fg=App.ColorTexto, frameColor=App.ColorFondoFrame, scale=0.1, pos=(0.5, 0, 0.9))
        # stacks
        DirectLabel(parent=self.frame, text="stacks", text_fg=App.ColorTexto, frameColor=App.ColorFondoFrame, scale=0.08, pos=(0.15, 0, 0.75))
        opts=DirectOptionMenu(parent=self.frame, items=["(seleccioná...)"], text_scale=0.5, text_pos=(0.25, 0),  scale=0.1, pos=(0.3, 0, 0.75), text_fg=App.ColorTexto, frameColor=App.ColorFondoWidgets, command=self._on_option_selected)
        DirectButton(parent=self.frame, text="+", frameSize=(-0.5, 0.5, -0.5, 0.5), frameColor=App.ColorFondoWidgets, command=self._on_btn_agregar_stack, pos=(0.35, 0, 0.62), scale=0.1, text_fg=App.ColorTexto, text_pos=(-0.05,-0.15))
        DirectButton(parent=self.frame, text="-", frameSize=(-0.5, 0.5, -0.5, 0.5), frameColor=App.ColorFondoWidgets, command=self._on_btn_eliminar_stack, pos=(0.5, 0, 0.62), scale=0.1, text_fg=App.ColorTexto, text_pos=(-0.05,-0.2))
        # perlin
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
        # stacked_perlins
        items=["(seleccioná...)"]
        for archivo in [archivo for archivo in os.listdir() if re.fullmatch("perlin\_.*\.txt", archivo)]:
            nombre=archivo[7:-4]
            items.append(nombre)
            with open(archivo, "r") as arch:
                linea=arch.readline()
                params=dict()
                while(linea):
                    linea=arch.readline()
                    if linea!="":
                        partes=linea.split("=")
                        params[partes[0]]=partes[1].strip("\n")
            self.agregar_stacked_perlin(nombre, params["scale_x"], params["scale_y"], params["levels"], params["scale_factor"], params["amp_scale"], params["table_size"], params["seed"])
        opts["items"]=items

    def _on_aspect_ratio_changed(self):
        ar=self.getAspectRatio()
        print("aspect ratio changed to %.3f"%ar)
        self.frame.setPos(-ar, 0, 0)

    def _on_option_selected(self, arg):
        print("option selected %s"%arg)
        if arg=="(seleccioná...)":
            self.nombre_pila_actual=None
            self.generar_plano()
        else:
            self.nombre_pila_actual=arg
            self.generar_plano("perlin_%s.png"%arg)

    def _on_btn_agregar_stack(self):
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
        DirectEntry(parent=self.frame_dlg, initialText="pila_%i"%len(self.stacked_perlins), text_scale=0.6, text_pos=(0.25, 0), pos=(0.5, 0, 0.65), text_fg=App.ColorTexto, frameColor=App.ColorFondoWidgets, scale=(0.075, 0.1, 0.1)).setName("entry_nombre")
        # aceptar / cancelar
        DirectButton(parent=self.frame_dlg, text="aceptar", frameSize=(-1.3, 1.3, -0.5, 0.5), frameColor=App.ColorFondoWidgets, command=self._on_nombre_pila_ok, pos=(0.55, 0, -0.9), scale=0.1, text_fg=App.ColorTexto, text_pos=(-0.05,-0.15), text_scale=0.6)
        DirectButton(parent=self.frame_dlg, text="cancelar", frameSize=(-1.3, 1.3, -0.5, 0.5), frameColor=App.ColorFondoWidgets, command=self._cerrar_dialogo, pos=(0.85, 0, -0.9), scale=0.1, text_fg=App.ColorTexto, text_pos=(-0.05,-0.15), text_scale=0.6)

    def _on_btn_eliminar_stack(self):
        if self.nombre_pila_actual==None:
            return
        archivo="perlin_%s."%self.nombre_pila_actual
        print("eliminar stack '%s'..."%archivo)
        os.remove(archivo+"txt")
        os.remove(archivo+"png")
        self.generar_gui()
    
    def _on_nombre_pila_ok(self):
        #
        nombre=""
        # validar
        for entry in self.aspect2d.find_all_matches("**/+PGEntry"):
            if(entry.node().getName()=="entry_nombre"):
                if not re.fullmatch("[a-zA-Z]+[a-zA-Z0-9\_]*", entry.node().getText()):
                    entry.node().setText("(alphanum,_)")
                    entry.node().setFocus(1)
                    return
                else:
                    nombre=entry.node().getText()
            else:
                if not re.fullmatch("[\+\-]?[0-9]*\.?[0-9]+", entry.node().getText()):
                    entry.node().setText("número!")
                    entry.node().setFocus(1)
                    return
        # obtener valores
        scale_x=self.aspect2d.find("**/entry_scale_x").node().getText()
        scale_y=self.aspect2d.find("**/entry_scale_y").node().getText()
        levels=self.aspect2d.find("**/entry_levels").node().getText()
        scale_f=self.aspect2d.find("**/entry_scale_factor").node().getText()
        amp_scale=self.aspect2d.find("**/entry_amp_scale").node().getText()
        table_size=self.aspect2d.find("**/entry_table_size").node().getText()
        seed=self.aspect2d.find("**/entry_seed").node().getText()
        #
        with open("perlin_%s.txt"%nombre, "w") as arch:
            contenido="nombre=%s\n"%nombre
            contenido+="scale_x=%s\n"%scale_x
            contenido+="scale_y=%s\n"%scale_y
            contenido+="levels=%s\n"%levels
            contenido+="scale_factor=%s\n"%scale_f
            contenido+="amp_scale=%s\n"%amp_scale
            contenido+="table_size=%s\n"%table_size
            contenido+="seed=%s\n"%seed
            arch.write(contenido)
        #
        self._cerrar_dialogo()        
        
    def _cerrar_dialogo(self):
        print("cerrar dialogo")
        if self.frame_dlg!=None:
            self.frame_dlg.removeNode()
            self.frame_dlg=None
        if self.frame==None:
            self.generar_gui()

if __name__=="__main__":
    app=App()
    app.run()
