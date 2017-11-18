from direct.gui.DirectGui import *
from panda3d.core import *

import os

import gui

import logging
log=logging.getLogger(__name__)

class TextureGuiDialog:
    
    def __init__(self, base):
        # references:
        self.base=base
        # components:
        self.frame=None
        self.entry_name=None
        self.chkbox=None
        self.dialog=None
        # variables:
        self.close_flag=False
        self.close_dialog_flag=False
        self.manual_mode=0
    
    def load(self):
        log.info("load")
        ar=self.base.getAspectRatio()
        self.frame=DirectFrame(frameColor=gui.FrameBgColor, frameSize=(0, 1, -1, 1), pos=(-ar, 0, 0))
        DirectLabel(parent=self.frame, text="add stacked perlin", text_fg=gui.TitleFgColor, frameColor=gui.FrameBgColor, scale=0.1, pos=(0.5, 0, 0.9))
        DirectLabel(parent=self.frame, text="name", text_align=TextNode.ARight, text_fg=gui.TextFgColor, frameColor=gui.FrameBgColor, scale=0.08, pos=(0.2, 0, 0.7))
        #
        i=0
        name=""
        while(True):
            name="stack_%i"%i
            file="perlin_%s.txt"%name
            if not os.path.exists(file):
                break
            i+=1
        self.entry_name=DirectEntry(parent=self.frame, initialText=name, text_scale=0.6, text_pos=(0.25, 0), pos=(0.2, 0, 0.7), text_fg=gui.TextFgColor, frameColor=gui.WidgetsBgColor, scale=(0.075, 0.1, 0.1))
        # manual mode
        self.chkbox=DirectCheckButton(parent=self.frame, text="manual mode", pos=(0.4, 0, 0.55), scale=0.1, frameColor=gui.WidgetsBgColor, text_fg=gui.TextFgColor, text_scale=0.6, command=self._check_manual_mode)
        # accept / cancel
        DirectButton(parent=self.frame, text="accept", frameSize=(-1.3, 1.3, -0.5, 0.5), frameColor=gui.WidgetsBgColor, command=self._create_file, pos=(0.55, 0, -0.9), scale=0.1, text_fg=gui.TextFgColor, text_pos=(-0.05,-0.15), text_scale=0.6)
        DirectButton(parent=self.frame, text="cancel", frameSize=(-1.3, 1.3, -0.5, 0.5), frameColor=gui.WidgetsBgColor, command=self._close, pos=(0.85, 0, -0.9), scale=0.1, text_fg=gui.TextFgColor, text_pos=(-0.05,-0.15), text_scale=0.6)
        #
        self.frame.accept("aspectRatioChanged", self._on_aspect_ratio_changed)
    
    def unload(self):
        log.info("unload")
        #
        self.frame.ignore("aspectRatioChanged")
        self.frame.destroy()
        self.frame=None    

    def update(self):
        if self.close_dialog_flag:
            self.close_dialog_flag=False
            self.dialog.cleanup()
            self.dialog=None
        return not self.close_flag
    
    def _close(self):
        log.info("_close")
        self.close_flag=True

    def _on_aspect_ratio_changed(self):
        log.info("_on_aspect_ratio_changed")
        ar=self.base.getAspectRatio()
        log.info("aspect ratio changed to %.3f"%ar)
        self.frame.setPos(-ar, 0, 0)

    def _create_file(self):
        log.info("_create_file")
        #
        name=self.entry_name.get()
        log.info("name is %s"%name)
        name_file="perlin_%s.txt"%name
        # validar
        if name=="" or os.path.exists(name_file):
            self.dialog=OkDialog(dialogName="error", text="file already exists", frameColor=gui.FrameBgColor, text_fg=gui.TextFgColor, command=self._close_dialog)
            self.entry_name.setFocus()
            return
        # write file
        with open(name_file, "w") as arch:
            contenido="name=%s\n"%name
            contenido+="manual_mode=%i\n"%self.manual_mode
            contenido+="scale_factor=1\n"
            if self.manual_mode:
                contenido+="num_levels=0\n"
            else:
                contenido+="num_levels=1\n"
                contenido+="sx_0=1\n"
                contenido+="sy_0=1\n"
                contenido+="seed_0=1\n"
                contenido+="amp_scale_0=1\n"
            arch.write(contenido)
        #
        self.close_flag=True

    def _check_manual_mode(self, flag):
        log.info("_check_manual_mode %s"%str(flag))
        self.manual_mode=flag
            
    def _create_entry(self, parent, pos, text):
        entry=DirectEntry(parent=parent, initialText=text, text_scale=0.6, text_pos=(0.25, 0), 
                                    pos=pos, text_fg=gui.TextFgColor, frameColor=gui.WidgetsBgColor, 
                                    scale=(0.075, 0.1, 0.1))
        return entry

    def _close_dialog(self, arg0):
        self.close_dialog_flag=True
