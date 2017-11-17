from direct.gui.DirectGui import *
from panda3d.core import *

import os
import re

import gui

import logging
log=logging.getLogger(__name__)

class TextureGui:
    
    def __init__(self, base):
        # references:
        self.base=base
        # components:
        self.plane=None
        self.image=None
        self.frame_stacked_perlins=None
        self.frame_perlin=None
        self.frame_dlg=None
        self.list_stacked_perlins=None
        #
        self.current_stacked_perlin=None
        self.perlins=list()
        self.widgets_perlin=dict() # {name:DirectGui, ...}
        self.params=dict()
        # variables:
        self.current_stacked_perlin_name=None
        self.current_perlin_index=-1
    
    def load(self):
        log.info("load")
        # params
        self.params["sx"]=128
        self.params["sy"]=128
        self.params["num_levels"]=4
        self.params["scale_factor"]=1.5
        self.params["amp_scale"]=0.75
        self.params["table_size"]=256
        self.params["seed"]=123
        # stacked perlins frame
        self._load_stacked_perlins_widgets()
        self._load_perlin_widgets(0)
        #
        #self.fill_widgets()
        # textured plane
        #self.generate_plane()
        #
        #self.frame?.accept("aspectRatioChanged", self._on_aspect_ratio_changed)
    
    def unload(self):
        log.info("unload")
        #
        if self.plane:
            self.plane.removeNode()
            self.plane=None
        #
        self.frame.destroy()
        self.frame=None

    def close_dialog(self):
        return False

    def _generate_plane(self, perlin_override=None):
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
    
    def _load_stacked_perlins_widgets(self):
        log.info("_load_stacked_perlins_widgets")
        #
        ar=base.getAspectRatio()
        # frame and tool title
        self.frame=DirectFrame(frameColor=gui.FrameBgColor, frameSize=(0, 1, -1, 1), pos=(-ar, 0, 0))
        DirectLabel(parent=self.frame, text="perlin texture", text_fg=gui.TextFgColor, frameColor=gui.FrameBgColor, scale=0.1, pos=(0.5, 0, 0.9))
        # stacked perlinss
        DirectLabel(parent=self.frame, text="stacks", text_fg=gui.TextFgColor, frameColor=gui.FrameBgColor, scale=0.08, pos=(0.15, 0, 0.75))
        self.list_stacked_perlins=DirectOptionMenu(parent=self.frame, items=["(select...)"], text_scale=0.5, text_pos=(0.25, 0),  scale=0.1, pos=(0.3, 0, 0.75), text_fg=gui.TextFgColor, frameColor=gui.WidgetsBgColor, command=self._on_option_selected)
        DirectButton(parent=self.frame, text="+", frameSize=(-0.5, 0.5, -0.5, 0.5), frameColor=gui.WidgetsBgColor, command=self._add_stacked_perlin, pos=(0.35, 0, 0.62), scale=0.1, text_fg=gui.TextFgColor, text_pos=(-0.05,-0.15))
        DirectButton(parent=self.frame, text="-", frameSize=(-0.5, 0.5, -0.5, 0.5), frameColor=gui.WidgetsBgColor, command=self._delete_stacked_perlin, pos=(0.5, 0, 0.62), scale=0.1, text_fg=gui.TextFgColor, text_pos=(-0.05,-0.2))
        #
        DirectButton(parent=self.frame, text="update", frameSize=(-1.85, 1.85, -0.5, 0.5), frameColor=gui.WidgetsBgColor, command=self._generate_plane, pos=(0.5, 0, -0.55), scale=0.1, text_fg=gui.TextFgColor, text_pos=(-0.05,-0.2), text_scale=0.75)
        DirectButton(parent=self.frame, text="save", frameSize=(-1.85, 1.85, -0.5, 0.5), frameColor=gui.WidgetsBgColor, command=self._save, pos=(0.5, 0, -0.675), scale=0.1, text_fg=gui.TextFgColor, text_pos=(-0.05,-0.2), text_scale=0.75)
        DirectButton(parent=self.frame, text="close", frameSize=(-1.85, 1.85, -0.5, 0.5), frameColor=gui.WidgetsBgColor, command=self._close, pos=(0.5, 0, -0.8), scale=0.1, text_fg=gui.TextFgColor, text_pos=(-0.05,-0.2), text_scale=0.75)

    def _load_perlin_widgets(self, pos_y):
        log.info("_load_perlin_widgets")
        #
        for n, w in self.widgets_perlin.items():
            w.destroy()
        #
        name=self.current_stacked_perlin_name if self.current_stacked_perlin_name!=None else "?"
        #
        self.widgets_perlin["label_name"]=DirectLabel(parent=self.frame, text="name", text_align=TextNode.ARight, text_fg=gui.TextFgColor, frameColor=gui.FrameBgColor, scale=0.08, pos=(0.45, 0, pos_y-0.0))
        self.widgets_perlin["label_sx"]=DirectLabel(parent=self.frame, text="scale x", text_align=TextNode.ARight, text_fg=gui.TextFgColor, frameColor=gui.FrameBgColor, scale=0.08, pos=(0.45, 0, pos_y-0.1))
        self.widgets_perlin["label_sy"]=DirectLabel(parent=self.frame, text="scale y", text_align=TextNode.ARight, text_fg=gui.TextFgColor, frameColor=gui.FrameBgColor, scale=0.08, pos=(0.45, 0, pos_y-0.2))
        self.widgets_perlin["label_num_levels"]=DirectLabel(parent=self.frame, text="levels", text_align=TextNode.ARight, text_fg=gui.TextFgColor, frameColor=gui.FrameBgColor, scale=0.08, pos=(0.45, 0, pos_y-0.3))
        self.widgets_perlin["label_scale_factor"]=DirectLabel(parent=self.frame, text="scale factor", text_align=TextNode.ARight, text_fg=gui.TextFgColor, frameColor=gui.FrameBgColor, scale=0.08, pos=(0.45, 0, pos_y-0.4))
        self.widgets_perlin["label_amp_scale"]=DirectLabel(parent=self.frame, text="amp scale", text_align=TextNode.ARight, text_fg=gui.TextFgColor, frameColor=gui.FrameBgColor, scale=0.08, pos=(0.45, 0, pos_y-0.5))
        self.widgets_perlin["label_table_size"]=DirectLabel(parent=self.frame, text="table size", text_align=TextNode.ARight, text_fg=gui.TextFgColor, frameColor=gui.FrameBgColor, scale=0.08, pos=(0.45, 0, pos_y-0.6))
        self.widgets_perlin["label_seed"]=DirectLabel(parent=self.frame, text="seed", text_align=TextNode.ARight, text_fg=gui.TextFgColor, frameColor=gui.FrameBgColor, scale=0.08, pos=(0.45, 0, pos_y-0.7))
        #
        self.widgets_perlin["label_name_value"]=DirectLabel(parent=self.frame, text=name, text_align=TextNode.ALeft, text_fg=gui.TextFgColor, frameColor=gui.FrameBgColor, scale=0.08, pos=(0.5, 0, pos_y-0.0))
        self.widgets_perlin["entry_sx"]=self._create_entry(self.frame, (0.5, 0, pos_y-0.1), str(self.params["sx"]))
        self.widgets_perlin["entry_sy"]=self._create_entry(self.frame, (0.5, 0, pos_y-0.2), str(self.params["sy"]))
        self.widgets_perlin["entry_levels"]=self._create_entry(self.frame, (0.5, 0, pos_y-0.3), str(self.params["num_levels"]))
        self.widgets_perlin["entry_scale_factor"]=self._create_entry(self.frame, (0.5, 0, pos_y-0.4), str(self.params["scale_factor"]))
        self.widgets_perlin["entry_amp_scale"]=self._create_entry(self.frame, (0.5, 0, pos_y-0.5), str(self.params["amp_scale"]))
        self.widgets_perlin["entry_table_size"]=self._create_entry(self.frame, (0.5, 0, pos_y-0.6), str(self.params["table_size"]))
        self.widgets_perlin["entry_seed"]=self._create_entry(self.frame, (0.5, 0, pos_y-0.7), str(self.params["seed"]))
    
    def _create_entry(self, parent, pos, text):
        entry=DirectEntry(parent=parent, initialText=text, text_scale=0.6, text_pos=(0.25, 0), 
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
        
    def _add_stacked_perlin(self):
        log.info("_add_stacked_perlin")
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

    def _create_file_stacked_perlin(self):
        log.info("_create_file_stacked_perlin")
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

    def _write_file(self, name_file):
        log.info("_write_file '%s'"%name_file)
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

    def _delete_stacked_perlin(self):
        log.info("_delete_stacked_perlin")
        if self.current_stacked_perlin_name==None:
            return
        #
        log.info("delete stack '%s'..."%self.current_stacked_perlin_name)
        file="perlin_%s."%self.current_stacked_perlin_name
        os.remove(file+"txt")
        os.remove(file+"png")
        self.current_stacked_perlin_name=None
        self._fill_stacked_perlins_list()
    
    def _open_file(self, name_file):
        log.info("_open_file '%s'"%name_file)
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
    
    def _save(self):
        log.info("_save")
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
        
    def _close_dialog(self):
        log.info("_close_dialog")

    def _fill_stacked_perlins_list(self):
        log.info("_fill_stacked_perlins_list")
        items=["(select...)"]
        for file in [file for file in os.listdir() if re.fullmatch("perlin\_.*\.txt", file)]:
            name=file[7:-4]
            items.append(name)
        self.list_stacked_perlins=items

    def _close(self):
        log.info("_close")
        gui.close_current_flag=True

