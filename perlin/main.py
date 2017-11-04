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
        self.params=dict()
        self.imagen=None
        # init:
        self.params["sx"]=128
        self.params["sy"]=128
        self.params["num_levels"]=4
        self.params["scale_factor"]=1.5
        self.params["amp_scale"]=0.75
        self.params["table_size"]=256
        self.params["seed"]=123
        #
        self.disableMouse()
        self.camera.setPos(-0.3, -2.5, 0)
        self.cargar_gui_principal()
        self.generar_plano()
        #
        self.accept("aspectRatioChanged", self._on_aspect_ratio_changed)
    
    def generar_plano(self, perlin_override=None):
        print("generar_plano")
        #
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
        self.establecer_params()
        sx=self.params["sx"]
        sy=self.params["sy"]
        num_levels=self.params["num_levels"]
        scale_factor=self.params["scale_factor"]
        amp_scale=self.params["amp_scale"]
        table_size=self.params["table_size"]
        seed=self.params["seed"]
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
        print("cargar_gui_principal")
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
        self.lbl_nombre=DirectLabel(parent=self.frame, text=nombre, text_align=TextNode.ALeft, text_fg=App.ColorTexto, frameColor=App.ColorFondoFrame, scale=0.08, pos=(0.5, 0, 0.35))
        DirectLabel(parent=self.frame, text="scale x", text_align=TextNode.ARight, text_fg=App.ColorTexto, frameColor=App.ColorFondoFrame, scale=0.08, pos=(0.45, 0, 0.25))
        DirectLabel(parent=self.frame, text="scale y", text_align=TextNode.ARight, text_fg=App.ColorTexto, frameColor=App.ColorFondoFrame, scale=0.08, pos=(0.45, 0, 0.15))
        DirectLabel(parent=self.frame, text="levels", text_align=TextNode.ARight, text_fg=App.ColorTexto, frameColor=App.ColorFondoFrame, scale=0.08, pos=(0.45, 0, 0.05))
        DirectLabel(parent=self.frame, text="scale factor", text_align=TextNode.ARight, text_fg=App.ColorTexto, frameColor=App.ColorFondoFrame, scale=0.08, pos=(0.45, 0, -0.05))
        DirectLabel(parent=self.frame, text="amp scale", text_align=TextNode.ARight, text_fg=App.ColorTexto, frameColor=App.ColorFondoFrame, scale=0.08, pos=(0.45, 0, -0.15))
        DirectLabel(parent=self.frame, text="table size", text_align=TextNode.ARight, text_fg=App.ColorTexto, frameColor=App.ColorFondoFrame, scale=0.08, pos=(0.45, 0, -0.25))
        DirectLabel(parent=self.frame, text="seed", text_align=TextNode.ARight, text_fg=App.ColorTexto, frameColor=App.ColorFondoFrame, scale=0.08, pos=(0.45, 0, -0.35))
        DirectEntry(parent=self.frame, initialText="1", text_scale=0.6, text_pos=(0.25, 0), pos=(0.5, 0, 0.25), text_fg=App.ColorTexto, frameColor=App.ColorFondoWidgets, scale=(0.075, 0.1, 0.1)).setName("entry_sx")
        DirectEntry(parent=self.frame, initialText="1", text_scale=0.6, text_pos=(0.25, 0), pos=(0.5, 0, 0.15), text_fg=App.ColorTexto, frameColor=App.ColorFondoWidgets, scale=(0.075, 0.1, 0.1)).setName("entry_sy")
        DirectEntry(parent=self.frame, initialText="3", text_scale=0.6, text_pos=(0.25, 0), pos=(0.5, 0, 0.05), text_fg=App.ColorTexto, frameColor=App.ColorFondoWidgets, scale=(0.075, 0.1, 0.1)).setName("entry_levels")
        DirectEntry(parent=self.frame, initialText="1", text_scale=0.6, text_pos=(0.25, 0), pos=(0.5, 0, -0.05), text_fg=App.ColorTexto, frameColor=App.ColorFondoWidgets, scale=(0.075, 0.1, 0.1)).setName("entry_scale_factor")
        DirectEntry(parent=self.frame, initialText="1", text_scale=0.6, text_pos=(0.25, 0), pos=(0.5, 0, -0.15), text_fg=App.ColorTexto, frameColor=App.ColorFondoWidgets, scale=(0.075, 0.1, 0.1)).setName("entry_amp_scale")
        DirectEntry(parent=self.frame, initialText="256", text_scale=0.6, text_pos=(0.25, 0), pos=(0.5, 0, -0.25), text_fg=App.ColorTexto, frameColor=App.ColorFondoWidgets, scale=(0.075, 0.1, 0.1)).setName("entry_table_size")
        DirectEntry(parent=self.frame, initialText="123", text_scale=0.6, text_pos=(0.25, 0), pos=(0.5, 0, -0.35), text_fg=App.ColorTexto, frameColor=App.ColorFondoWidgets, scale=(0.075, 0.1, 0.1)).setName("entry_seed")
        DirectButton(parent=self.frame, text="actualizar", frameSize=(-1.85, 1.85, -0.5, 0.5), frameColor=App.ColorFondoWidgets, command=self.generar_plano, pos=(0.5, 0, -0.55), scale=0.1, text_fg=App.ColorTexto, text_pos=(-0.05,-0.2), text_scale=0.75)
        DirectButton(parent=self.frame, text="guardar", frameSize=(-1.85, 1.85, -0.5, 0.5), frameColor=App.ColorFondoWidgets, command=self.guardar, pos=(0.5, 0, -0.675), scale=0.1, text_fg=App.ColorTexto, text_pos=(-0.05,-0.2), text_scale=0.75)
        #
        self.llenar_widgets()
        # stacked_perlins
        items=["(seleccioná...)"]
        for archivo in [archivo for archivo in os.listdir() if re.fullmatch("perlin\_.*\.txt", archivo)]:
            nombre=archivo[7:-4]
            items.append(nombre)
        opts["items"]=items

    def _on_aspect_ratio_changed(self):
        print("_on_aspect_ratio_changed")
        ar=self.getAspectRatio()
        print("aspect ratio changed to %.3f"%ar)
        self.frame.setPos(-ar, 0, 0)

    def _on_option_selected(self, arg):
        print("_on_option_selected %s"%arg)
        if arg=="(seleccioná...)":
            print("nada seleccionado")
            return
        else:
            nombre_archivo="perlin_%s.txt"%arg
            if self.abrir_archivo(nombre_archivo):
                self.nombre_stacked_perlin_actual=arg
                self.lbl_nombre["text"]=arg
            #
            self.generar_plano()
        
    def agregar_stacked_perlin(self):
        print("agregar_stacked_perlin")
        #
        if self.frame!=None:
            self.frame.removeNode()
            self.frame=None
        # dialogo
        ar=self.getAspectRatio()
        self.frame_dlg=DirectFrame(frameColor=App.ColorFondoFrame, frameSize=(0, 1, -1, 1), pos=(-ar, 0, 0))
        DirectLabel(parent=self.frame_dlg, text="agregar pila", text_fg=App.ColorTexto, frameColor=App.ColorFondoFrame, scale=0.1, pos=(0.5, 0, 0.9))
        DirectLabel(parent=self.frame_dlg, text="nombre", text_align=TextNode.ARight, text_fg=App.ColorTexto, frameColor=App.ColorFondoFrame, scale=0.08, pos=(0.45, 0, 0.65)).setName("entry_nombre")
        #
        i=0
        nombre=""
        while(True):
            nombre="pila_%i"%i
            archivo="perlin_%s.txt"%nombre
            if not os.path.exists(archivo):
                break
            i+=1
        DirectEntry(parent=self.frame_dlg, initialText=nombre, text_scale=0.6, text_pos=(0.25, 0), pos=(0.5, 0, 0.65), text_fg=App.ColorTexto, frameColor=App.ColorFondoWidgets, scale=(0.075, 0.1, 0.1)).setName("entry_nombre")
        # aceptar / cancelar
        DirectButton(parent=self.frame_dlg, text="aceptar", frameSize=(-1.3, 1.3, -0.5, 0.5), frameColor=App.ColorFondoWidgets, command=self.crear_archivo_stacked_perlin, pos=(0.55, 0, -0.9), scale=0.1, text_fg=App.ColorTexto, text_pos=(-0.05,-0.15), text_scale=0.6)
        DirectButton(parent=self.frame_dlg, text="cancelar", frameSize=(-1.3, 1.3, -0.5, 0.5), frameColor=App.ColorFondoWidgets, command=self.cerrar_dialogo, pos=(0.85, 0, -0.9), scale=0.1, text_fg=App.ColorTexto, text_pos=(-0.05,-0.15), text_scale=0.6)

    def crear_archivo_stacked_perlin(self):
        print("crear_archivo_stacked_perlin")
        #
        nombre=self.aspect2d.find("**/entry_nombre").node().getText()
        nombre_archivo="perlin_%s.txt"%nombre
        # validar
        if not re.fullmatch("[a-zA-Z]+[a-zA-Z0-9\_]*", nombre):
            entry.node().setText("[alphanum|_]")
            entry.node().setFocus(1)
            return
        if os.path.exists(nombre_archivo):
            entry.node().setText("(ya existe!)")
            entry.node().setFocus(1)
            return
        #
        self.nombre_stacked_perlin_actual=nombre
        # escribir archivo
        self.escribir_archivo(nombre_archivo)
        #
        self.cerrar_dialogo()

    def escribir_archivo(self, nombre_archivo):
        print("escribir_archivo '%s'"%nombre_archivo)
        # escribir archivo
        with open(nombre_archivo, "w") as arch:
            contenido="nombre=%s\n"%self.nombre_stacked_perlin_actual
            contenido+="sx=%s\n"%self.params["sx"]
            contenido+="sy=%s\n"%self.params["sy"]
            contenido+="num_levels=%s\n"%self.params["num_levels"]
            contenido+="scale_factor=%s\n"%self.params["scale_factor"]
            contenido+="amp_scale=%s\n"%self.params["amp_scale"]
            contenido+="table_size=%s\n"%self.params["table_size"]
            contenido+="seed=%s\n"%self.params["seed"]
            arch.write(contenido)

    def eliminar_stacked_perlin(self):
        print("eliminar_stacked_perlin")
        if self.nombre_stacked_perlin_actual==None:
            return
        #
        print("eliminar stack '%s'..."%self.nombre_stacked_perlin_actual)
        archivo="perlin_%s."%self.nombre_stacked_perlin_actual
        os.remove(archivo+"txt")
        os.remove(archivo+"png")
        self.nombre_stacked_perlin_actual=None
        self.cargar_gui_principal()
    
    def establecer_params(self):
        print("establecer_params")
        sx=self.aspect2d.find("**/entry_sx").node().getText()
        sy=self.aspect2d.find("**/entry_sy").node().getText()
        num_levels=self.aspect2d.find("**/entry_levels").node().getText()
        scale_factor=self.aspect2d.find("**/entry_scale_factor").node().getText()
        amp_scale=self.aspect2d.find("**/entry_amp_scale").node().getText()
        table_size=self.aspect2d.find("**/entry_table_size").node().getText()
        seed=self.aspect2d.find("**/entry_seed").node().getText()
        self.params["sx"]=sx
        self.params["sy"]=sy
        self.params["num_levels"]=num_levels
        self.params["scale_factor"]=scale_factor
        self.params["amp_scale"]=amp_scale
        self.params["table_size"]=table_size
        self.params["seed"]=seed

    def llenar_widgets(self):
        print("llenar_widgets")
        self.aspect2d.find("**/entry_sx").node().setText(str(self.params["sx"]))
        self.aspect2d.find("**/entry_sy").node().setText(str(self.params["sy"]))
        self.aspect2d.find("**/entry_levels").node().setText(str(self.params["num_levels"]))
        self.aspect2d.find("**/entry_scale_factor").node().setText(str(self.params["scale_factor"]))
        self.aspect2d.find("**/entry_amp_scale").node().setText(str(self.params["amp_scale"]))
        self.aspect2d.find("**/entry_table_size").node().setText(str(self.params["table_size"]))
        self.aspect2d.find("**/entry_seed").node().setText(str(self.params["seed"]))
    
    def abrir_archivo(self, nombre_archivo):
        print("abrir_archivo '%s'"%nombre_archivo)
        if not os.path.exists(nombre_archivo):
            print("el archivo no existe")
            return False
        # abrir archivo
        params=dict()
        try:
            with open(nombre_archivo, "r") as arch:
                linea=arch.readline()
                while(linea):
                    linea=arch.readline()
                    if linea!="":
                        partes=linea.split("=")
                        params[partes[0]]=partes[1].strip("\n")
        except:
            print("ocurrio un error")
            return False
        #
        for k in self.params.keys():
            if k not in params:
                print("falta el valor '%s'"%k)
                return False
        self.params=params
        #
        self.llenar_widgets()
        return True
    
    def guardar(self):
        print("guardar")
        # validar
        for entry in self.aspect2d.find_all_matches("**/+PGEntry"):
            if(entry.node().getName()=="entry_nombre"):
                continue
            if not re.fullmatch("[\+\-]?[0-9]*\.?[0-9]+", entry.node().getText()):
                entry.node().setText("número!")
                entry.node().setFocus(1)
                return
        # params
        self.establecer_params()
        # archivo nuevo?
        if self.nombre_stacked_perlin_actual==None:
            self.agregar_stacked_perlin()
        else:
            self.escribir_archivo("perlin_%s.txt"%self.nombre_stacked_perlin_actual)
        
    def cerrar_dialogo(self):
        print("cerrar_dialogo")
        if self.frame_dlg!=None:
            self.frame_dlg.removeNode()
            self.frame_dlg=None
        if self.frame==None:
            self.cargar_gui_principal()

if __name__=="__main__":
    app=App()
    app.run()
