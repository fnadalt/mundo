import math

import logging
log=logging.getLogger(__name__)

class Dia:

    def __init__(self, duracion_segundos, hora_inicial_normalizada):
        # variables externas:
        self.duracion=duracion_segundos
        self.hora_normalizada=hora_inicial_normalizada # [0.0,1.0)
        self.periodo=Periodo(Periodo.Noche)
        # variables internas:
        self._tiempo=self.duracion*self.hora_normalizada
    
    def update(self, dt):
        # tiempo real
        #dt=0.0
        self._tiempo+=dt
        if self._tiempo>self.duracion:
            self._tiempo-=self.duracion
        # establecer hora normalizada
        self.hora_normalizada=self._tiempo/self.duracion
        # determinar periodo
        _hora_anterior=Periodo.HoraInicio[self.periodo.anterior]
        _hora_posterior=Periodo.HoraInicio[self.periodo.posterior]
        _hora_normalizada=self.hora_normalizada
        if _hora_posterior==0.05:
            _hora_posterior+=1.0
            if _hora_normalizada<_hora_anterior:
                _hora_normalizada+=1.0
        if _hora_normalizada>=_hora_posterior:
            self.periodo=Periodo(self.periodo.posterior)

    def obtener_info(self):
        offset=self.calcular_offset(self.periodo.actual, self.periodo.posterior)
        info="Dia d=%.2fs hn=%.2f p=%i o=%.2f _t=%.2f"%(self.duracion, self.hora_normalizada, self.periodo.actual, offset, self._tiempo)
        return info

    def calcular_offset(self, periodo1, periodo2):
        hora1=Periodo.HoraInicio[periodo1]
        hora2=Periodo.HoraInicio[periodo2]
        hn=self.hora_normalizada
        if hora2==0.05:
            hora2=1.05
            if hn<hora1:
                hn+=1.0
        offset=(hn-hora1)/(hora2-hora1)
        #log.info("calcular_offset h1=%.2f h2=%.2f hn=%.2f o=%.2f p=%i"%(hora1, hora2, hn, offset, self.periodo.actual))
        return offset
    
    def obtener_hora(self):
        _hn=self.hora_normalizada
        _hn-=0.2
        if _hn<0.0:
            _hn+=1.0
        _hn*=24.0
        _m, _h=math.modf(_hn)
        _hora_f="%i:%s"%(int(_h), str("0%i"%int(_m*60.0))[-2:])
        #log.info("obtener_hora hn=%.2f _h=%.1f _m=%.2f _texto=%s"%(self.hora_normalizada, _h, _m, _hora_f))
        return _hora_f

class Periodo:

    #
    Noche=0
    Amanecer=1
    Dia=2
    Atardecer=3
    
    # horas inicio
    HoraInicio={
                Noche:0.05, \
                Amanecer:0.45,  \
                Dia:0.55, \
                Atardecer:0.95
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
