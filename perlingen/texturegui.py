from direct.gui.DirectGui import *
from panda3d.core import *

import os
import re

import gui
from textureguidialog import TextureGuiDialog

import logging
log=logging.getLogger(__name__)

class TextureGui:

    #
    TableSize=256
    ConstParamNames=["num_levels", "scale_factor"]
    IndexedParamNames=["sx", "sy", "seed", "amp_scale"]

    #
    ImageSideLength=512
    
    def __init__(self, base):
        # references:
        self.base=base
        # components:
        self.plane=None
        self.image=None
        self.frame_stacked_perlins=None
        self.dialog=None
        self.list_stacked_perlins=None
        self.primary_param_widgets=dict() # {name:DirectGui, ...}
        self.secondary_param_widgets=dict() # {name:DirectGui, ...}
        #
        self.params=dict()
        # variables:
        self.close_flag=False
        self.current_stacked_perlin_name=None
        self.manual_mode=0
        self.current_perlin_index=-1
    
    def load(self):
        log.info("load")
        # stacked perlins frame
        self._load_main_frame()
        self._fill_stacked_perlins_list()
        #
        self.frame.accept("aspectRatioChanged", self._on_aspect_ratio_changed)
    
    def unload(self):
        log.info("unload")
        #
        if self.image:
            self.image.clear()
            self.image=None
        #
        if self.plane:
            self.plane.removeNode()
            self.plane=None
        #
        self.frame.ignore("aspectRatioChanged")
        self.frame.destroy()
        self.frame=None

    def update(self):
        if self.dialog:
            if not self.dialog.update():
                self.dialog.unload()
                self.dialog=None
                self.frame.show()
                self._fill_stacked_perlins_list()
                self.current_stacked_perlin_name=None
                self._load_primary_param_widgets()
                self._load_secondary_param_widgets()
        return not self.close_flag

    def _generate_plane(self, perlin_override=None):
        log.info("generate_plane")
        #
        if self.plane:
            self.plane.removeNode()
            self.plane=None
        #
        if self.current_stacked_perlin_name==None:
            return
        #
        self._update_params()
        perlin_obj=None
        if self.manual_mode:
            num_levels=self.params["num_levels"]
            if num_levels==0:
                return
            perlin_obj=StackedPerlinNoise2()
            for i in range(num_levels):
                sx=self.params["sx_%i"%i]
                sy=self.params["sy_%i"%i]
                seed=self.params["seed_%i"%i]
                amp_scale=self.params["amp_scale_%i"%i]
                noise_obj=PerlinNoise2(sx, sy, TextureGui.TableSize, seed)
                perlin_obj.addLevel(noise_obj, amp_scale)
        else:
            num_levels=self.params["num_levels"]
            scale_factor=self.params["scale_factor"]
            sx=self.params["sx_0"]
            sy=self.params["sy_0"]
            seed=self.params["seed_0"]
            amp_scale=self.params["amp_scale_0"]
            perlin_obj=StackedPerlinNoise2(sx, sy, num_levels, scale_factor, amp_scale, TextureGui.TableSize, seed)
        #
        _card=CardMaker("plane")
        _card.setFrame(-0.5, 0.5, -0.5, 0.5)
        #_card.setColor(1, 0, 0, 1)
        self.plane=self.base.render.attachNewNode(_card.generate())
        # generar image
        if self.image:
            self.image.clear()
        self.image=PNMImage(512, 512, 1, 65535)
        min=1000000.0
        max=0.0
        data=list()
        for x in range(self.image.getXSize()):
            for y in range(self.image.getYSize()):
                height=perlin_obj(x, y)
                if height<min: min=height
                if height>max: max=height
                data.append(height)
        elevation=-min
        amplitude=max-min
        log.info("min/max;elevation;amplitude:%.3f/%.3f;%.3f;%.3f"%(min, max, elevation, amplitude))
        #
        min=1000000.0
        max=0.0
        size_y=self.image.getYSize()
        for x in range(self.image.getXSize()):
            for y in range(size_y):
                height=data[(size_y*y)+x]
                height+=elevation
                height/=amplitude
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
    
    def _load_main_frame(self):
        log.info("_load_main_frame")
        #
        ar=self.base.getAspectRatio()
        # frame and tool title
        self.frame=DirectFrame(frameColor=gui.FrameBgColor, frameSize=(0, 1, -1, 1), pos=(-ar, 0, 0))
        DirectLabel(parent=self.frame, text="perlin texture", text_fg=gui.TitleFgColor, frameColor=gui.FrameBgColor, scale=0.1, pos=(0.5, 0, 0.9))
        DirectButton(parent=self.frame, text="x", frameSize=(-0.5, 0.5, -0.5, 0.5), frameColor=gui.WidgetsBgColor, command=self._close, pos=(0.95, 0, 0.95), scale=0.1, text_fg=gui.TextFgColor, text_pos=(-0.05,-0.2), text_scale=0.75)
        # stacked perlins
        DirectLabel(parent=self.frame, text="stacked perlin noise files", text_fg=gui.TextFgColor, text_align=TextNode.ALeft, frameColor=gui.FrameBgColor, scale=0.08, pos=(0, 0, 0.8))
        self.list_stacked_perlins=DirectOptionMenu(parent=self.frame, items=["(select...)"], text_scale=0.5, text_pos=(0.25, 0),  scale=0.1, pos=(0, 0, 0.7), text_fg=gui.TextFgColor, frameColor=gui.WidgetsBgColor, command=self._on_file_selected)
        DirectButton(parent=self.frame, text="+", frameSize=(-0.5, 0.5, -0.5, 0.5), frameColor=gui.WidgetsBgColor, command=self._add_stacked_perlin, pos=(0.05, 0, 0.6), scale=0.1, text_fg=gui.TextFgColor, text_pos=(-0.05,-0.15))
        DirectButton(parent=self.frame, text="-", frameSize=(-0.5, 0.5, -0.5, 0.5), frameColor=gui.WidgetsBgColor, command=self._delete_stacked_perlin, pos=(0.15, 0, 0.6), scale=0.1, text_fg=gui.TextFgColor, text_pos=(-0.05,-0.2))
        DirectButton(parent=self.frame, text="save", frameSize=(-1.0, 1.0, -0.5, 0.5), frameColor=gui.WidgetsBgColor, command=self._save, pos=(0.3, 0, 0.6), scale=0.1, text_fg=gui.TextFgColor, text_pos=(-0.05,-0.2), text_scale=0.75)
        # texture
        DirectLabel(parent=self.frame, text="texture", text_fg=gui.TextFgColor, text_align=TextNode.ALeft, frameColor=gui.FrameBgColor, scale=0.08, pos=(0, 0, 0.4))
        DirectButton(parent=self.frame, text="update", frameSize=(-1.3, 1.3, -0.5, 0.5), frameColor=gui.WidgetsBgColor, command=self._generate_plane, pos=(0.13, 0, 0.3), scale=0.1, text_fg=gui.TextFgColor, text_pos=(-0.05,-0.2), text_scale=0.75)

    def _load_primary_param_widgets(self):
        log.info("_load_primary_param_widgets")
        # destroy previous
        for n, w in self.primary_param_widgets.items():
            w.destroy()
        self.primary_param_widgets=dict()
        #
        self.current_perlin_index=-1
        #
        if self.current_stacked_perlin_name==None:
            return
        # create
        pos_y=0.1
        self.primary_param_widgets["label_parameters"]=DirectLabel(parent=self.frame, text="noise parameters", text_align=TextNode.ARight, text_fg=gui.TextFgColor, frameColor=gui.FrameBgColor, scale=0.08, pos=(0.64, 0, pos_y-0.0))
        if self.manual_mode:
            _items=["(select...)"]+[str(i) for i in range(self.params["num_levels"])]
            self.primary_param_widgets["label_list_noise_objs"]=DirectLabel(parent=self.frame, text="noise objs", text_align=TextNode.ARight, text_fg=gui.TextFgColor, frameColor=gui.FrameBgColor, scale=0.08, pos=(0.45, 0, pos_y-0.15))
            self.primary_param_widgets["list_noise_objs"]=DirectOptionMenu(parent=self.frame, items=_items, text_scale=0.5, text_pos=(0.25, 0),  scale=0.1, pos=(0.5, 0, pos_y-0.15), text_fg=gui.TextFgColor, frameColor=gui.WidgetsBgColor, command=self._on_noise_obj_selected)
            self.primary_param_widgets["btn_add_noise_obj"]=DirectButton(parent=self.frame, text="+", frameSize=(-0.5, 0.5, -0.5, 0.5), frameColor=gui.WidgetsBgColor, command=self._add_noise_obj, pos=(0.55, 0, pos_y-0.25), scale=0.1, text_fg=gui.TextFgColor, text_pos=(-0.05,-0.15))
            self.primary_param_widgets["btn_del_noise_obj"]=DirectButton(parent=self.frame, text="-", frameSize=(-0.5, 0.5, -0.5, 0.5), frameColor=gui.WidgetsBgColor, command=self._del_noise_obj, pos=(0.65, 0, pos_y-0.25), scale=0.1, text_fg=gui.TextFgColor, text_pos=(-0.05,-0.15))
        else:
            self.primary_param_widgets["label_num_levels"]=DirectLabel(parent=self.frame, text="num levels", text_align=TextNode.ARight, text_fg=gui.TextFgColor, frameColor=gui.FrameBgColor, scale=0.08, pos=(0.45, 0, pos_y-0.15))
            self.primary_param_widgets["label_scale_factor"]=DirectLabel(parent=self.frame, text="scale factor", text_align=TextNode.ARight, text_fg=gui.TextFgColor, frameColor=gui.FrameBgColor, scale=0.08, pos=(0.45, 0, pos_y-0.25))
            self.primary_param_widgets["entry_levels"]=self._create_entry(self.frame, (0.5, 0, pos_y-0.15), str(self.params["num_levels"]))
            self.primary_param_widgets["entry_scale_factor"]=self._create_entry(self.frame, (0.5, 0, pos_y-0.25), str(self.params["scale_factor"]))
            self.current_perlin_index=0

    def _load_secondary_param_widgets(self):
        log.info("_load_secondary_param_widgets")
        # destroy previous
        for n, w in self.secondary_param_widgets.items():
            w.destroy()
        self.secondary_param_widgets=dict()
        #
        if self.current_perlin_index==-1:
            return
        # create
        pos_y=-0.3
        self.secondary_param_widgets["label_sx"]=DirectLabel(parent=self.frame, text="scale x", text_align=TextNode.ARight, text_fg=gui.TextFgColor, frameColor=gui.FrameBgColor, scale=0.08, pos=(0.45, 0, pos_y-0.0))
        self.secondary_param_widgets["label_sy"]=DirectLabel(parent=self.frame, text="scale y", text_align=TextNode.ARight, text_fg=gui.TextFgColor, frameColor=gui.FrameBgColor, scale=0.08, pos=(0.45, 0, pos_y-0.1))
        self.secondary_param_widgets["label_amp_scale"]=DirectLabel(parent=self.frame, text="amp scale", text_align=TextNode.ARight, text_fg=gui.TextFgColor, frameColor=gui.FrameBgColor, scale=0.08, pos=(0.45, 0, pos_y-0.2))
        self.secondary_param_widgets["label_seed"]=DirectLabel(parent=self.frame, text="seed", text_align=TextNode.ARight, text_fg=gui.TextFgColor, frameColor=gui.FrameBgColor, scale=0.08, pos=(0.45, 0, pos_y-0.3))
        #
        self.secondary_param_widgets["entry_sx"]=self._create_entry(self.frame, (0.5, 0, pos_y-0.0), str(self.params["sx_%i"%self.current_perlin_index]))
        self.secondary_param_widgets["entry_sy"]=self._create_entry(self.frame, (0.5, 0, pos_y-0.1), str(self.params["sy_%i"%self.current_perlin_index]))
        self.secondary_param_widgets["entry_amp_scale"]=self._create_entry(self.frame, (0.5, 0, pos_y-0.2), str(self.params["amp_scale_%i"%self.current_perlin_index]))
        self.secondary_param_widgets["entry_seed"]=self._create_entry(self.frame, (0.5, 0, pos_y-0.3), str(self.params["seed_%i"%self.current_perlin_index]))
    
    def _create_entry(self, parent, pos, text):
        entry=DirectEntry(parent=parent, initialText=text, text_scale=0.6, text_pos=(0.25, 0), 
                                    pos=pos, text_fg=gui.TextFgColor, frameColor=gui.WidgetsBgColor, 
                                    scale=(0.075, 0.1, 0.1), focusOutCommand=self._update_params)
        return entry

    def _on_aspect_ratio_changed(self):
        log.info("_on_aspect_ratio_changed")
        ar=self.base.getAspectRatio()
        log.info("aspect ratio changed to %.3f"%ar)
        self.frame.setPos(-ar, 0, 0)

    def _on_file_selected(self, arg0):
        log.info("_on_file_selected %s"%arg0)
        if arg0=="(select...)":
            log.info("nothing selected")
            self.current_stacked_perlin_name=None
        else:
            name_file="perlin_%s.txt"%arg0
            self._open_file(name_file)
        #
        self._load_primary_param_widgets()
        self._load_secondary_param_widgets()
        
    def _add_stacked_perlin(self):
        log.info("_add_stacked_perlin")
        #
        self.frame.hide()
        # dialog
        self.dialog=TextureGuiDialog(self.base)
        self.dialog.load()

    def _delete_stacked_perlin(self):
        log.info("_delete_stacked_perlin")
        if self.current_stacked_perlin_name==None:
            return
        #
        log.info("delete stack '%s'..."%self.current_stacked_perlin_name)
        file="perlin_%s.txt"%self.current_stacked_perlin_name
        os.remove(file)
        self._fill_stacked_perlins_list()
        #
        self.current_stacked_perlin_name=None
        self._load_primary_param_widgets()
        self._load_secondary_param_widgets()
    
    def _open_file(self, name_file):
        log.info("_open_file '%s'"%name_file)
        if not os.path.exists(name_file):
            log.info("does not exist")
            return
        # open and read file
        file_params=dict()
        try:
            with open(name_file, "r") as arch:
                linea=arch.readline()
                while(linea):
                    if linea!="":
                        partes=linea.split("=")
                        file_params[partes[0]]=partes[1].strip("\n")
                    linea=arch.readline()
        except:
            log.info("error")
            return
        print(str(file_params))
        # temporary variables
        name=""
        manual_mode=0
        num_levels=0
        scale_factor=1
        validated_params=dict()
        # validate file params
        try:
            if "name" in file_params:
                name=file_params["name"]
            else:
                log.error("'name' key missing")
                return
            if "manual_mode" in file_params:
                manual_mode=int(file_params["manual_mode"])
            else:
                log.error("'manual_mode' key missing")
                return
            if "num_levels" in file_params:
                num_levels=int(file_params["num_levels"])
            else:
                log.error("'num_levels' key missing")
                return
            if "scale_factor" in file_params:
                scale_factor=float(file_params["scale_factor"])
            else:
                log.error("'scale_factor' key missing")
                return
            for i in range(num_levels):
                for k in TextureGui.IndexedParamNames:
                    k_full_name="%s_%i"%(k, i)
                    if k_full_name in file_params:
                        if k==("seed"):
                            validated_params[k_full_name]=int(file_params[k_full_name])
                        else:
                            validated_params[k_full_name]=float(file_params[k_full_name])
                if manual_mode:
                    break
        except ValueError as e:
            log.exception("error %s"%str(e))
            return
        # set params
        validated_params["num_levels"]=num_levels
        validated_params["scale_factor"]=scale_factor
        self.current_stacked_perlin_name=name
        self.manual_mode=manual_mode
        self.params=validated_params
    
    def _save(self):
        log.info("_save")
        #
        if self.current_stacked_perlin_name==None:
            return
        #
        try:
            contenido="name=%s\nmanual_mode=%s\n"%(self.current_stacked_perlin_name, self.manual_mode)
            for k in TextureGui.ConstParamNames:
                contenido+="%s=%s\n"%(k, str(self.params[k]))
            for k in TextureGui.IndexedParamNames:
                for i in range(self.params["num_levels"]):
                    k_full_name="%s_%i"%(k, i)
                    contenido+="%s=%s\n"%(k_full_name, self.params[k_full_name])
                    if not self.manual_mode:
                        break
        except ValueError as e:
            log.exception("error %s"%str(e))
            return
        #
        file_name="perlin_%s.txt"%self.current_stacked_perlin_name
        with open(file_name, "w+") as arch:
            arch.write(contenido)
 
    def _fill_stacked_perlins_list(self):
        log.info("_fill_stacked_perlins_list")
        items=["(select...)"]
        for file in [file for file in os.listdir() if re.fullmatch("perlin\_.*\.txt", file)]:
            name=file[7:-4]
            items.append(name)
        self.list_stacked_perlins["items"]=items

    def _close(self):
        log.info("_close")
        self.close_flag=True

    def _on_noise_obj_selected(self, arg0):
        log.info("_on_noise_obj_selected %s"%arg0)
        self._update_params()
        if arg0=="(select...)":
            log.info("nothing selected")
            self.current_perlin_index=-1
        else:
            self.current_perlin_index=int(arg0)
        self._load_secondary_param_widgets()

    def _add_noise_obj(self):
        log.info("_add_noise_obj")
        self._update_params()
        #
        idx=self.params["num_levels"]
        #
        self.params["num_levels"]+=1
        self.params["sx_%i"%idx]=1
        self.params["sy_%i"%idx]=1
        self.params["seed_%i"%idx]=1
        self.params["amp_scale_%i"%idx]=1
        #
        self._load_primary_param_widgets()
        self._load_secondary_param_widgets()
        
    def _del_noise_obj(self):
        log.info("_del_noise_obj %i"%self.current_perlin_index)
        #
        if self.current_perlin_index==-1:
            return
        #
        num_levels=self.params["num_levels"]
        for i in range(self.current_perlin_index, num_levels-1):
            for k in TextureGui.IndexedParamNames:
                k_full_name="%s_%i"%(k, i)
                k_full_name_next="%s_%i"%(k, i+1)
                self.params[k_full_name]=self.params[k_full_name_next]
        #
        self.params["num_levels"]-=1
        for k in TextureGui.IndexedParamNames:
            k_full_name="%s_%i"%(k, self.params["num_levels"])
            del self.params[k_full_name]
        #
        self._load_primary_param_widgets()
        self._load_secondary_param_widgets()

    def _update_params(self, *args):
        log.info("_update_params")
        #
        if self.current_perlin_index==-1:
            return
        #
        try:
            if not self.manual_mode:
                self.params["num_levels"]=int(self.primary_param_widgets["entry_levels"].get())
                self.params["scale_factor"]=float(self.primary_param_widgets["entry_scale_factor"].get())
            self.params["sx_%i"%self.current_perlin_index]=float(self.secondary_param_widgets["entry_sx"].get())
            self.params["sy_%i"%self.current_perlin_index]=float(self.secondary_param_widgets["entry_sy"].get())
            self.params["seed_%i"%self.current_perlin_index]=int(self.secondary_param_widgets["entry_seed"].get())
            self.params["amp_scale_%i"%self.current_perlin_index]=float(self.secondary_param_widgets["entry_amp_scale"].get())        
        except ValueError as e:
            log.exception("error %s"%str(e))
