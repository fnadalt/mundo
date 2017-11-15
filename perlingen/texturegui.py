from direct.gui.DirectGui import *
from panda3d.core import *

import os
import re

import gui

import logging
log=logging.getLogger(__name__)

class TextureGui:
    
    def __init__(self):
        # components:
        self.plane=None
        self.frame=None
        self.frame_dlg=None
        self.widgets=dict() # {name:DirectGui, ...}
        # variables:
        self.current_stacked_perlin_name=None
        self.stacked_perlin=None
        self.params=dict()
        self.image=None
        self.trigger_close=False
        # init:
        self.params["sx"]=128
        self.params["sy"]=128
        self.params["num_levels"]=4
        self.params["scale_factor"]=1.5
        self.params["amp_scale"]=0.75
        self.params["table_size"]=256
        self.params["seed"]=123
    
    def build(self):
        log.info("build")
        # frame
        self.frame=self.load_gui_main()
        #
        self.fill_widgets()
        # textured plane
        #self.generate_plane()
        #
        #self.frame?.accept("aspectRatioChanged", self._on_aspect_ratio_changed)
    
    def remove(self):
        log.info("remove")
        #
        if self.stacked_perlin:
            self.stacked_perlin=None
        if self.image:
            self.image=None
        #
        if self.plane:
            self.plane.removeNode()
            self.plane=None
        #
        self.frame.destroy()
        self.frame=None

    def generate_plane(self, perlin_override=None):
        log.info("generate_plane")
        return
        #
        if self.plane:
            self.plane.removeNode()
            self.plane=None
        if self.stacked_perlin:
            self.stacked_perlin=None
        if self.image:
            self.image=None
        #
        _card=CardMaker("plane")
        _card.setFrame(-0.5, 0.5, -0.5, 0.5)
        #_card.setColor(1, 0, 0, 1)
        self.plane=self.base.render.attachNewNode(_card.generate())
        # obtener valores
        self.set_params()
        sx=self.params["sx"]
        sy=self.params["sy"]
        num_levels=self.params["num_levels"]
        scale_factor=self.params["scale_factor"]
        amp_scale=self.params["amp_scale"]
        table_size=self.params["table_size"]
        seed=self.params["seed"]
        # create nuevo objeto stacked perlin
        self.stacked_perlin=StackedPerlinNoise2(float(sx), float(sy), int(float(num_levels)), float(scale_factor), float(amp_scale), int(float(table_size)), int(float(seed)))
        perlin_obj=self.stacked_perlin if perlin_override==None else perlin_override
        # generar image
        self.image=PNMImage(512, 512, 1, 65535)
        min=10.0
        max=0.0
        for x in range(self.image.getXSize()):
            for y in range(self.image.getYSize()):
                height=perlin_obj(x, y)
                height/=float(num_levels)
                height+=1
                height/=2
                if height<min: min=height
                if height>max: max=height
                self.image.setGray(x, y, height)
        log.info("min/max:%.3f/%.3f"%(min, max))
        self.image.write("t.png")
        # set TextureGui
        ts0=TextureStage("texture")
        tex0=Texture()
        tex0.load(self.image)
        tex0.setWrapU(Texture.WMClamp)
        tex0.setWrapV(Texture.WMClamp)
        self.plane.setTexture(ts0, tex0)
    
    def load_gui_main(self):
        log.info("load_gui_main")
        #
        ar=base.getAspectRatio()
        # frame y titulo
        frame=DirectFrame(frameColor=gui.FrameBgColor, frameSize=(0, 1, -1, 1), pos=(-ar, 0, 0))
        DirectLabel(parent=frame, text="TextureGui perlin", text_fg=gui.TextFgColor, frameColor=gui.FrameBgColor, scale=0.1, pos=(0.5, 0, 0.9))
        # stacks
        DirectLabel(parent=frame, text="stacks", text_fg=gui.TextFgColor, frameColor=gui.FrameBgColor, scale=0.08, pos=(0.15, 0, 0.75))
#        opts=DirectOptionMenu(parent=self.frame, items=["(select...)"], text_scale=0.5, text_pos=(0.25, 0),  scale=0.1, pos=(0.3, 0, 0.75), text_fg=gui.TextFgColor, frameColor=gui.WidgetsBgColor, command=self._on_option_selected)
        DirectButton(parent=frame, text="+", frameSize=(-0.5, 0.5, -0.5, 0.5), frameColor=gui.WidgetsBgColor, command=self.add_stacked_perlin, pos=(0.35, 0, 0.62), scale=0.1, text_fg=gui.TextFgColor, text_pos=(-0.05,-0.15))
        DirectButton(parent=frame, text="-", frameSize=(-0.5, 0.5, -0.5, 0.5), frameColor=gui.WidgetsBgColor, command=self.delete_stacked_perlin, pos=(0.5, 0, 0.62), scale=0.1, text_fg=gui.TextFgColor, text_pos=(-0.05,-0.2))
        # perlin
        name=self.current_stacked_perlin_name if self.current_stacked_perlin_name!=None else "?"
        DirectLabel(parent=frame, text="name", text_align=TextNode.ARight, text_fg=gui.TextFgColor, frameColor=gui.FrameBgColor, scale=0.08, pos=(0.45, 0, 0.35))
        DirectLabel(parent=frame, text="scale x", text_align=TextNode.ARight, text_fg=gui.TextFgColor, frameColor=gui.FrameBgColor, scale=0.08, pos=(0.45, 0, 0.25))
        DirectLabel(parent=frame, text="scale y", text_align=TextNode.ARight, text_fg=gui.TextFgColor, frameColor=gui.FrameBgColor, scale=0.08, pos=(0.45, 0, 0.15))
        DirectLabel(parent=frame, text="levels", text_align=TextNode.ARight, text_fg=gui.TextFgColor, frameColor=gui.FrameBgColor, scale=0.08, pos=(0.45, 0, 0.05))
        DirectLabel(parent=frame, text="scale factor", text_align=TextNode.ARight, text_fg=gui.TextFgColor, frameColor=gui.FrameBgColor, scale=0.08, pos=(0.45, 0, -0.05))
        DirectLabel(parent=frame, text="amp scale", text_align=TextNode.ARight, text_fg=gui.TextFgColor, frameColor=gui.FrameBgColor, scale=0.08, pos=(0.45, 0, -0.15))
        DirectLabel(parent=frame, text="table size", text_align=TextNode.ARight, text_fg=gui.TextFgColor, frameColor=gui.FrameBgColor, scale=0.08, pos=(0.45, 0, -0.25))
        DirectLabel(parent=frame, text="seed", text_align=TextNode.ARight, text_fg=gui.TextFgColor, frameColor=gui.FrameBgColor, scale=0.08, pos=(0.45, 0, -0.35))
        self.widgets["label_name"]=DirectLabel(parent=frame, text=name, text_align=TextNode.ALeft, text_fg=gui.TextFgColor, frameColor=gui.FrameBgColor, scale=0.08, pos=(0.5, 0, 0.35))
        self.widgets["entry_sx"]=self._create_entry(frame, (0.5, 0, 0.25), "1")
        self.widgets["entry_sy"]=DirectEntry(parent=frame, initialText="1", text_scale=0.6, text_pos=(0.25, 0), pos=(0.5, 0, 0.15), text_fg=gui.TextFgColor, frameColor=gui.WidgetsBgColor, scale=(0.075, 0.1, 0.1))
        self.widgets["entry_levels"]=DirectEntry(parent=frame, initialText="3", text_scale=0.6, text_pos=(0.25, 0), pos=(0.5, 0, 0.05), text_fg=gui.TextFgColor, frameColor=gui.WidgetsBgColor, scale=(0.075, 0.1, 0.1))
        self.widgets["entry_scale_factor"]=DirectEntry(parent=frame, initialText="1", text_scale=0.6, text_pos=(0.25, 0), pos=(0.5, 0, -0.05), text_fg=gui.TextFgColor, frameColor=gui.WidgetsBgColor, scale=(0.075, 0.1, 0.1))
        self.widgets["entry_amp_scale"]=DirectEntry(parent=frame, initialText="1", text_scale=0.6, text_pos=(0.25, 0), pos=(0.5, 0, -0.15), text_fg=gui.TextFgColor, frameColor=gui.WidgetsBgColor, scale=(0.075, 0.1, 0.1))
        self.widgets["entry_table_size"]=DirectEntry(parent=frame, initialText="256", text_scale=0.6, text_pos=(0.25, 0), pos=(0.5, 0, -0.25), text_fg=gui.TextFgColor, frameColor=gui.WidgetsBgColor, scale=(0.075, 0.1, 0.1))
        self.widgets["entry_seed"]=DirectEntry(parent=frame, initialText="123", text_scale=0.6, text_pos=(0.25, 0), pos=(0.5, 0, -0.35), text_fg=gui.TextFgColor, frameColor=gui.WidgetsBgColor, scale=(0.075, 0.1, 0.1))
        DirectButton(parent=frame, text="update", frameSize=(-1.85, 1.85, -0.5, 0.5), frameColor=gui.WidgetsBgColor, command=self.generate_plane, pos=(0.5, 0, -0.55), scale=0.1, text_fg=gui.TextFgColor, text_pos=(-0.05,-0.2), text_scale=0.75)
        DirectButton(parent=frame, text="save", frameSize=(-1.85, 1.85, -0.5, 0.5), frameColor=gui.WidgetsBgColor, command=self.save, pos=(0.5, 0, -0.675), scale=0.1, text_fg=gui.TextFgColor, text_pos=(-0.05,-0.2), text_scale=0.75)
        DirectButton(parent=frame, text="close", frameSize=(-1.85, 1.85, -0.5, 0.5), frameColor=gui.WidgetsBgColor, command=self.close, pos=(0.5, 0, -0.8), scale=0.1, text_fg=gui.TextFgColor, text_pos=(-0.05,-0.2), text_scale=0.75)
        # stacked_perlins
        items=["(select...)"]
        for file in [file for file in os.listdir() if re.fullmatch("perlin\_.*\.txt", file)]:
            name=file[7:-4]
            items.append(name)
        #opts["items"]=items
        #
        return frame
        
    def _create_entry(self, parent, pos, text):
        entry=DirectEntry(parent=parent, text=text, text_scale=0.6, text_pos=(0.25, 0), 
                                    pos=pos, text_fg=gui.TextFgColor, frameColor=gui.WidgetsBgColor, 
                                    scale=(0.075, 0.1, 0.1))
        return entry

    def _on_aspect_ratio_changed(self):
        log.info("_on_aspect_ratio_changed")
        ar=base.getAspectRatio()
        log.info("aspect ratio changed to %.3f"%ar)
        self.frame.setPos(-ar, 0, 0)

    def _on_option_selected(self, arg):
        log.info("_on_option_selected %s"%arg)
        if arg=="(select...)":
            log.info("nothing selected")
            return
        else:
            name_file="perlin_%s.txt"%arg
            if self.open_file(name_file):
                self.current_stacked_perlin_name=arg
            #
            self.generate_plane()
        
    def add_stacked_perlin(self):
        log.info("add_stacked_perlin")
        #
        self.frame.destroy()
        self.frame=None
        # dialog
        ar=self.getAspectRatio()
        self.frame_dlg=DirectFrame(frameColor=gui.FrameBgColor, frameSize=(0, 1, -1, 1), pos=(-ar, 0, 0))
        DirectLabel(parent=self.frame_dlg, text="add stack", text_fg=gui.TextFgColor, frameColor=gui.FrameBgColor, scale=0.1, pos=(0.5, 0, 0.9))
        DirectLabel(parent=self.frame_dlg, text="name", text_align=TextNode.ARight, text_fg=gui.TextFgColor, frameColor=gui.FrameBgColor, scale=0.08, pos=(0.45, 0, 0.65)).setName("entry_name")
        #
        i=0
        name=""
        while(True):
            name="stack_%i"%i
            file="perlin_%s.txt"%name
            if not os.path.exists(file):
                break
            i+=1
        DirectEntry(parent=self.frame_dlg, initialText=name, text_scale=0.6, text_pos=(0.25, 0), pos=(0.5, 0, 0.65), text_fg=gui.TextFgColor, frameColor=gui.WidgetsBgColor, scale=(0.075, 0.1, 0.1)).setName("entry_name")
        # accept / cancel
        DirectButton(parent=self.frame_dlg, text="accept", frameSize=(-1.3, 1.3, -0.5, 0.5), frameColor=gui.WidgetsBgColor, command=self.create_file_stacked_perlin, pos=(0.55, 0, -0.9), scale=0.1, text_fg=gui.TextFgColor, text_pos=(-0.05,-0.15), text_scale=0.6)
        DirectButton(parent=self.frame_dlg, text="cancel", frameSize=(-1.3, 1.3, -0.5, 0.5), frameColor=gui.WidgetsBgColor, command=self.close_dialog, pos=(0.85, 0, -0.9), scale=0.1, text_fg=gui.TextFgColor, text_pos=(-0.05,-0.15), text_scale=0.6)

    def create_file_stacked_perlin(self):
        log.info("create_file_stacked_perlin")
        #
        name=base.aspect2d.find("**/entry_name").node().getText()
        name_file="perlin_%s.txt"%name
        # validar
        if not re.fullmatch("[a-zA-Z]+[a-zA-Z0-9\_]*", name):
            entry.node().setText("[alphanum|_]")
            entry.node().setFocus(1)
            return
        if os.path.exists(name_file):
            entry.node().setText("(already exists!)")
            entry.node().setFocus(1)
            return
        #
        self.current_stacked_perlin_name=name
        # write file
        self.write_file(name_file)
        #
        self.close_dialog()

    def write_file(self, name_file):
        log.info("write_file '%s'"%name_file)
        # write file
        with open(name_file, "w") as arch:
            contenido="name=%s\n"%self.current_stacked_perlin_name
            contenido+="sx=%s\n"%self.params["sx"]
            contenido+="sy=%s\n"%self.params["sy"]
            contenido+="num_levels=%s\n"%self.params["num_levels"]
            contenido+="scale_factor=%s\n"%self.params["scale_factor"]
            contenido+="amp_scale=%s\n"%self.params["amp_scale"]
            contenido+="table_size=%s\n"%self.params["table_size"]
            contenido+="seed=%s\n"%self.params["seed"]
            arch.write(contenido)

    def delete_stacked_perlin(self):
        log.info("delete_stacked_perlin")
        if self.current_stacked_perlin_name==None:
            return
        #
        log.info("delete stack '%s'..."%self.current_stacked_perlin_name)
        file="perlin_%s."%self.current_stacked_perlin_name
        os.remove(file+"txt")
        os.remove(file+"png")
        self.current_stacked_perlin_name=None
        self.load_gui_main()
    
    def set_params(self):
        log.info("set_params")
        sx=self.widgets["entry_sx"]["text"]
        sy=base.aspect2d.find("**/entry_sy").node().getText()
        num_levels=base.aspect2d.find("**/entry_levels").node().getText()
        scale_factor=base.aspect2d.find("**/entry_scale_factor").node().getText()
        amp_scale=base.aspect2d.find("**/entry_amp_scale").node().getText()
        table_size=base.aspect2d.find("**/entry_table_size").node().getText()
        seed=base.aspect2d.find("**/entry_seed").node().getText()
        self.params["sx"]=sx
        self.params["sy"]=sy
        self.params["num_levels"]=num_levels
        self.params["scale_factor"]=scale_factor
        self.params["amp_scale"]=amp_scale
        self.params["table_size"]=table_size
        self.params["seed"]=seed

    def fill_widgets(self):
        log.info("fill_widgets")
        self.widgets["entry_sx"]["text"]=str(self.params["sx"])
        self.widgets["entry_sy"]["initialText"]=str(self.params["sy"])
        self.widgets["entry_levels"]["initialText"]=str(self.params["num_levels"])
        self.widgets["entry_scale_factor"]["initialText"]=str(self.params["scale_factor"])
        self.widgets["entry_amp_scale"]["initialText"]=str(self.params["amp_scale"])
        self.widgets["entry_table_size"]["initialText"]=str(self.params["table_size"])
        self.widgets["entry_seed"]["initialText"]=str(self.params["seed"])
    
    def open_file(self, name_file):
        log.info("open_file '%s'"%name_file)
        if not os.path.exists(name_file):
            log.info("does not exist")
            return False
        # open file
        params=dict()
        try:
            with open(name_file, "r") as arch:
                linea=arch.readline()
                while(linea):
                    linea=arch.readline()
                    if linea!="":
                        partes=linea.split("=")
                        params[partes[0]]=partes[1].strip("\n")
        except:
            log.info("error")
            return False
        #
        for k in self.params.keys():
            if k not in params:
                log.info("key missing '%s'"%k)
                return False
        self.params=params
        #
        self.fill_widgets()
        return True
    
    def save(self):
        log.info("save")
        # validar
        for entry in base.aspect2d.find_all_matches("**/+PGEntry"):
            if(entry.node().getName()=="entry_name"):
                continue
            if not re.fullmatch("[\+\-]?[0-9]*\.?[0-9]+", entry.node().getText()):
                entry.node().setText("number!")
                entry.node().setFocus(1)
                return
        # params
        self.set_params()
        # file nuevo?
        if self.current_stacked_perlin_name==None:
            self.add_stacked_perlin()
        else:
            self.write_file("perlin_%s.txt"%self.current_stacked_perlin_name)
        
    def close_dialog(self):
        log.info("close_dialog")
        self.frame_dlg.destroy()
        self.frame_dlg=None
        self.load_gui_main()

    def close(self):
        log.info("close")
        self.trigger_close=True

    def update(self):
        if self.trigger_close:
            log.info("trigger_close")
            gui.manager.load_main()
            self.trigger_close=False
            return False
        return True
