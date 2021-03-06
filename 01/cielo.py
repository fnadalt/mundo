from panda3d.core import *

from shader import GestorShader

import logging
log=logging.getLogger(__name__)

class Cielo:
    
    # colores
    ColorNoche=Vec4(0.0, 0.0, 0.2, 1.0)
    ColorAmanecer=Vec4(0.95, 0.75, 0.2, 1.0)
    ColorDia=Vec4(0.9, 1.0, 1.0, 1.0)
    ColorAtardecer=Vec4(0.95, 0.65, 0.3, 1.0)
    ColorIntermedioDiaNoche=(ColorDia+ColorNoche)/2.0
    ColorHaloDia=Vec4(1.0, 1.0, 0.93, 1.0)
    
    def __init__(self, base, altitud_agua):
        # referencias:
        self.base=base
        # componentes:
        # nodo
        self.nodo=self.base.cam.attachNewNode("sky_dome") # cam?
        # modelo
        self.modelo=self.base.loader.loadModel("objetos/sky_dome")
        self.modelo.reparentTo(self.nodo)
        self.modelo.setMaterialOff(1)
        self.modelo.setTextureOff(1)
        self.modelo.setLightOff(1)
        self.modelo.node().adjustDrawMask(DrawMask(3), DrawMask(2), DrawMask(0))
        # luz
#        self.luz=self.nodo.attachNewNode(AmbientLight("luz_ambiental"))
#        self.luz.node().setColor(Cielo.ColorNoche)
        # variable externas:
        self.altitud_agua=altitud_agua
        self.color_luz_ambiental=Cielo.ColorNoche
        self.offset_periodo=0.0
        self.color_cielo_base_inicial=Vec4(0, 0, 0, 0)
        self.color_cielo_base_final=Vec4(0, 0, 0, 0)
        self.color_halo_sol_inicial=Vec4(0, 0, 0, 0)
        self.color_halo_sol_final=Vec4(0, 0, 0, 0)
        # variable internas:
        self._periodo_actual=0
        self._offset_periodo_anterior=0
        self._color_ambiente_inicial=Cielo.ColorNoche
        self._color_ambiente_final=Cielo.ColorNoche
        # init:
        self._establecer_shader()
        self._procesar_cambio_periodo(self._periodo_actual, False)
        self.nodo.setZ(self.altitud_agua-0.0)
    
    def update(self, pos_pivot_camara, hora_normalizada, periodo, offset_periodo):
        # determinar periodo
        if periodo!=self._periodo_actual:
            #log.info("update cambio periodo de %i a %i; posicion_sol=[%s]; hora_normalizada=%.2f; offset_periodo=%.2f"%(self._periodo_actual, periodo, ",".join(["%.2f"%n for n in posicion_sol]), hora_normalizada, offset_periodo))
            self._periodo_actual=periodo
            self._procesar_cambio_periodo(self._periodo_actual, False)
        #
        _offset_corregido=offset_periodo
        if self._periodo_actual==1 or self._periodo_actual==3:
            if _offset_corregido>0.5:
                _offset_corregido-=0.5
                if self._offset_periodo_anterior<=0.5:
                    #log.info("update cambio subperiodo; posicion_sol=[%s]; hora_normalizada=%.2f; offset_periodo=%.2f (anterior=%.2f)"%(",".join(["%.2f"%n for n in posicion_sol]), hora_normalizada, offset_periodo, self._offset_periodo_anterior))
                    self._procesar_cambio_periodo(self._periodo_actual, True)
            _offset_corregido*=2
        # luz ambiental
        _color_luz=Vec4(self._color_ambiente_inicial*(1.0-_offset_corregido))+Vec4(self._color_ambiente_final*_offset_corregido)
        self.color_luz_ambiental=_color_luz*1.5
#        self.luz.node().setColor(_color_luz)
        #
        self.offset_periodo=_offset_corregido
        self._offset_periodo_anterior=offset_periodo
    
    def terminar(self):
        log.info("terminar")
    
    def obtener_info(self):
        info="Cielo color_luz=%s\n"%(str(self.color_luz_ambiental))
        return info

    def _procesar_cambio_periodo(self, periodo, post_pico):
        if periodo==0:
            self._color_ambiente_inicial=Cielo.ColorNoche
            self._color_ambiente_final=Cielo.ColorNoche
            self.color_cielo_base_inicial=Cielo.ColorNoche
            self.color_cielo_base_final=Cielo.ColorNoche
            self.color_halo_sol_inicial=self._color_ambiente_inicial
            self.color_halo_sol_final=self._color_ambiente_final
        elif periodo==1:
            if not post_pico:
                self._color_ambiente_inicial=Cielo.ColorNoche
                self._color_ambiente_final=Cielo.ColorAmanecer
                self.color_cielo_base_inicial=Cielo.ColorNoche
                self.color_cielo_base_final=Cielo.ColorIntermedioDiaNoche
                self.color_halo_sol_inicial=self._color_ambiente_inicial
                self.color_halo_sol_final=self._color_ambiente_final
            else:
                self._color_ambiente_inicial=Cielo.ColorAmanecer
                self._color_ambiente_final=Cielo.ColorHaloDia
                self.color_cielo_base_inicial=Cielo.ColorIntermedioDiaNoche
                self.color_cielo_base_final=Cielo.ColorDia
                self.color_halo_sol_inicial=self._color_ambiente_inicial
                self.color_halo_sol_final=self._color_ambiente_final
        elif periodo==2:
            self._color_ambiente_inicial=Cielo.ColorHaloDia
            self._color_ambiente_final=Cielo.ColorHaloDia
            self.color_cielo_base_inicial=Cielo.ColorDia
            self.color_cielo_base_final=Cielo.ColorDia
            self.color_halo_sol_inicial=self._color_ambiente_inicial
            self.color_halo_sol_final=self._color_ambiente_final
        elif self._periodo_actual==3:
            if not post_pico:
                self._color_ambiente_inicial=Cielo.ColorHaloDia
                self._color_ambiente_final=Cielo.ColorAtardecer
                self.color_cielo_base_inicial=Cielo.ColorDia
                self.color_cielo_base_final=Cielo.ColorIntermedioDiaNoche
                self.color_halo_sol_inicial=self._color_ambiente_inicial
                self.color_halo_sol_final=self._color_ambiente_final
            else:
                self._color_ambiente_inicial=Cielo.ColorAtardecer
                self._color_ambiente_final=Cielo.ColorNoche
                self.color_cielo_base_inicial=Cielo.ColorIntermedioDiaNoche
                self.color_cielo_base_final=Cielo.ColorNoche
                self.color_halo_sol_inicial=self._color_ambiente_inicial
                self.color_halo_sol_final=self._color_ambiente_final

    def _establecer_shader(self):
        GestorShader.aplicar(self.nodo, GestorShader.ClaseCielo, 2)
