import logging
log=logging.getLogger(__name__)

class Dia:

    def __init__(self, duracion_segundos, tiempo_inicial):
        # variables externas:
        self.duracion=duracion_segundos
        self.hora_normalizada=0.0 # [0.0,1.0); 0.0=>medianoche, 0.5=>mediodia
        self.periodo=Periodo(Periodo.Noche)
        # variables internas:
        self._tiempo=tiempo_inicial
    
    def update(self, dt):
        # tiempo real
        self._tiempo+=dt
        if self._tiempo>self.duracion:
            self._tiempo-=self.duracion
        # establecer hora normalizada
        self.hora_normalizada=self._tiempo/self.duracion
        # determinar periodo
        _hora_anterior=Periodo.HoraInicio[self.periodo.anterior]
        _hora_posterior=Periodo.HoraInicio[self.periodo.posterior]
        if _hora_posterior==0.0 and self.hora_normalizada>_hora_anterior:
            _hora_posterior+=1.0
        if self.hora_normalizada>=_hora_posterior:
            self.periodo=Periodo(self.periodo.posterior)

    def obtener_info(self):
        offset=self.calcular_offset(self.periodo.actual, self.periodo.posterior)
        info="Dia d=%.2fs hn=%.2f p=%i o=%.2f _t=%.2f"%(self.duracion, self.hora_normalizada, self.periodo.actual, offset, self._tiempo)
        return info

    def calcular_offset(self, periodo1, periodo2):
        hora1=Periodo.HoraInicio[periodo1]
        hora2=Periodo.HoraInicio[periodo2]
        if hora2==0.0:
            hora2=1.0
        #log.info("calcular_offset h1=%.2f h2=%.2f hn=%.2f"%(hora1, hora2, self.hora_normalizada))
        offset=(self.hora_normalizada-hora1)/(hora2-hora1)
        return offset

class Periodo:

    #
    Noche=0
    Amanecer=1
    Dia=2
    Atardecer=3
    
    # horas inicio
    HoraInicio={
                Noche:0.0, \
                Amanecer:0.4,  \
                Dia:0.5, \
                Atardecer:0.9
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
