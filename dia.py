from panda3d.core import *

import logging
log=logging.getLogger(__name__)

class Dia:

    def __init__(self, duracion_segundos):
        # variables externas:
        self.duracion=duracion_segundos
        self.hora_normalizada=0.0 # [0.0,1.0); 0.0=>mediodía, 0.5=>medianoche
        self.periodo=Periodo(Periodo.Dia)
        # variables internas:
        self._tiempo=0.0
    
    def update(self, dt):
        # tiempo real
        self._tiempo+=dt
        if self._tiempo>1.0:
            self._tiempo-=1.0
        # establecer hora normalizada
        self.hora_normalizada=self._tiempo/self.duracion
        # determinar periodo
        if self.periodo.finalizado(self.hora_normalizada):
            self.periodo=Periodo(self.periodo.proximo)

    def calcular_offset(self, hora_normalizada, periodo_anterior, periodo_posterior):
        #
        hora=hora_normalizada
        hora_anterior=Periodo.HoraPico[periodo_anterior]
        hora_proxima=Periodo.HoraPico[periodo_posterior]
        #print("input hn=%.2f pa=%i pp=%i ha=%.2f hp=%.2f"%(hora_normalizada, periodo_anterior, periodo_posterior, hora_anterior, hora_proxima))
        #
        if hora_anterior==hora_proxima:
            #print("horas iguales")
            if hora<hora_anterior:
                #print("...incrementar hora +1")
                hora+=1.0
            hora_proxima+=1.0
        elif hora_proxima<hora_anterior:
            #print("horas proxima<anterior")
            if hora<hora_anterior:
                #print("...incrementar hora +1")
                hora+=1.0
            hora_proxima+=1.0
        elif hora_proxima>hora_anterior:
            pass
        #
        offset=(hora-hora_anterior)/(hora_proxima-hora_anterior)
        #print("output hn=%.2f pa=%i pp=%i ha=%.2f hp=%.2f offset=%.2f"%(hora_normalizada, periodo_anterior, periodo_posterior, hora_anterior, hora_proxima, offset))
        return offset

class Periodo:

    #
    Dia=0
    Atardecer=1
    Noche=2
    Amanecer=3
    
    # horas pico
    HoraPicoMediodia=0.0
    HoraPicoAtardecer=0.25
    HoraPicoMedianoche=0.5
    HoraPicoAmanecer=0.75
    HoraPico={
                Dia:HoraPicoMediodia, \
                Atardecer:HoraPicoAtardecer, \
                Noche:HoraPicoMedianoche, \
                Amanecer:HoraPicoAmanecer
                }

    # duracion periodos
    DuracionDia=0.4
    DuracionAtardecer=0.1
    DuracionNoche=0.4
    DuracionAmanecer=0.1
    Duracion={
                Dia:DuracionDia, \
                Atardecer:DuracionAtardecer, \
                Noche:DuracionNoche, \
                Amanecer:DuracionAmanecer
                }

    # colores
    ColorDia=LVector4(1.0, 1.0, 0.85, 1.0)
    ColorAtardecer=LVector4(0.95, 0.65, 0.3, 1.0)
    ColorNoche=LVector4(0.0, 0.0, 0.2, 1.0)
    ColorAmanecer=LVector4(0.95, 0.75, 0.2, 1.0)
    Color={
            Dia:ColorDia, \
            Atardecer:ColorAtardecer, \
            Noche: ColorNoche, \
            Amanecer:ColorAmanecer
            }
    
    def __init__(self, periodo_actual):
        #
        self.actual=periodo_actual
        self.anterior=None
        self.posterior=None
        #
        if self.actual==Periodo.Dia:
            self.anterior=Periodo.Amanecer
            self.posterior=Periodo.Atardecer
        elif self.actual==Periodo.Atardecer:
            self.anterior=Periodo.Dia
            self.posterior=Periodo.Noche
        elif self.actual==Periodo.Noche:
            self.anterior=Periodo.Atardecer
            self.posterior=Periodo.Amanecer
        elif self.actual==Periodo.Amanecer:
            self.anterior=Periodo.Noche
            self.posterior=Periodo.Dia

    def finalizado(self, hora_normalizada):
        pass
    
    def obtener_info(self):
        return "Periodo %s:\nhi=%i d=%i color=%s momento=%.2f\ncolor_luz=%s"%(self.nombre, self.hora_inicio, self.duracion, str(self.color), self.momento, str(self.color_luz))
