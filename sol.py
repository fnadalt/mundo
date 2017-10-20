from panda3d.core import *

import logging
log=logging.getLogger(__name__)

class Sol:
    
    def __init__(self, base):
        # referencias
        self.base=base
        # componentes
        self.pivot=None
        self.nodo=None
        self.luz=None
        # variables externas
<<<<<<< HEAD
        self.hora=0.0 # debe ser normalizada [0.0,1.0); 0.0=>medianoche, 0.5=>mediodía
=======
        self.hora=0.0
>>>>>>> 82bf037d9b4b416c9e8d8df28b6db9e691ac8e07
        self.periodo=Periodo(Periodo.Atardecer)
        # variable internas
        self._datos_periodos=dict() # {periodo:[color,hora_max,duracion,prox_periodo], ...}
        # componentes:
        # pivot de rotacion
        self.pivot=self.base.render.attachNewNode("pivot_sol")
        self.pivot.setP(10.0) # inclinacion "estacional"
<<<<<<< HEAD
        self.pivot.setR(-45)
=======
>>>>>>> 82bf037d9b4b416c9e8d8df28b6db9e691ac8e07
        # esfera solar
        self.nodo=self.base.loader.loadModel("objetos/sol")
        self.nodo.reparentTo(self.pivot)
        self.nodo.setX(300.0)
        self.nodo.setScale(5.0)
        self.nodo.setColor(1.0, 1.0, 0.2, 1.0)
        self.nodo.setLightOff(1)
        self.nodo.setShaderOff(1)
        self.nodo.setFogOff(1)
#        self.nodo.setCompass()
#        self.nodo.setBin('background', 2)
#        self.nodo.setDepthWrite(False)
#        self.nodo.setDepthTest(False)
        # luz direccional
        _luz=DirectionalLight("sol_d")
        _luz.setColor(Vec4(1.0, 1.0, 0.7, 1.0))
        self.luz=self.nodo.attachNewNode(_luz)


    def update(self, dt):
        # color luz
        color_luz=self.periodo.computar_color(self.hora)
        # componentes
<<<<<<< HEAD
        self.pivot.setR(self.pivot, 7.5 * dt)
=======
        self.pivot.setR(self.pivot, 0.2 * dt)
>>>>>>> 82bf037d9b4b416c9e8d8df28b6db9e691ac8e07
        self.luz.lookAt(self.pivot)
        self.luz.node().setColor(color_luz)
        # determinar hora
        roll=self.pivot.getR()
        self.hora=18.0+24.0*((roll if roll>0 else 360.0+roll)/360.0)
        if self.hora>=24.0:
            self.hora-=24.0
        # determinar periodo
        if self.periodo.finalizado(self.hora):
            self.periodo=Periodo(self.periodo.proximo)

    def obtener_info(self):
        info="Sol hora=%i:%s\n"%(self.hora, str("0%s"%str(int((self.hora-int(self.hora))*60)))[-2:])
        info+=self.periodo.obtener_info()
        return info
    

class Periodo:

    # clase
    Noche=0
    Amanecer=1
    Dia=2
    Atardecer=3
    
    # horarios inicio
    HoraInicioNoche=20.0
    HoraInicioAmanecer=6.0
    HoraInicioDia=8.0
    HoraInicioAtardecer=18.0

    # duracion periodos
    DuracionNoche=10
    DuracionAmanecer=2
    DuracionDia=10
    DuracionAtardecer=2

    # colores
    ColorNoche=LVector4(0.0, 0.0, 0.2, 1.0)
    ColorAmanecer=LVector4(0.95, 0.75, 0.2, 1.0)
    ColorDia=LVector4(1.0, 1.0, 0.85, 1.0)
    ColorAtardecer=LVector4(0.95, 0.65, 0.3, 1.0)
    
    def __init__(self, periodo):
        self.momento=0.0
        self.color_luz=LVector4()
        if periodo==Periodo.Noche:
            self.nombre="noche"
            self.hora_inicio=Periodo.HoraInicioNoche
            self.duracion=Periodo.DuracionNoche
            self.color=Periodo.ColorNoche
<<<<<<< HEAD
            # directamente...
            # self.proximo=Periodo()
            # self.anterior=Periodo()
=======
>>>>>>> 82bf037d9b4b416c9e8d8df28b6db9e691ac8e07
            self.proximo=Periodo.Amanecer
            self.color_anterior=(Periodo.ColorAtardecer+self.color)/2.0
            self.color_proximo=(Periodo.ColorAmanecer+self.color)/2.0
        elif periodo==Periodo.Amanecer:
            self.nombre="amanecer"
            self.hora_inicio=Periodo.HoraInicioAmanecer
            self.duracion=Periodo.DuracionAmanecer
            self.color=Periodo.ColorAmanecer
            self.proximo=Periodo.Dia
            self.color_anterior=(Periodo.ColorNoche+self.color)/2.0
            self.color_proximo=(Periodo.ColorDia+self.color)/2.0
        elif periodo==Periodo.Dia:
            self.nombre="dia"
            self.hora_inicio=Periodo.HoraInicioDia
            self.duracion=Periodo.DuracionDia
            self.color=Periodo.ColorDia
            self.proximo=Periodo.Atardecer
            self.color_anterior=(Periodo.ColorAmanecer+self.color)/2.0
            self.color_proximo=(Periodo.ColorAtardecer+self.color)/2.0
        elif periodo==Periodo.Atardecer:
            self.nombre="atardecer"
            self.hora_inicio=Periodo.HoraInicioAtardecer
            self.duracion=Periodo.DuracionAtardecer
            self.color=Periodo.ColorAtardecer
            self.proximo=Periodo.Noche
            self.color_anterior=(Periodo.ColorDia+self.color)/2.0
            self.color_proximo=(Periodo.ColorNoche+self.color)/2.0

    def computar_color(self, hora):
        #
        _hora_pico=self.hora_inicio+self.duracion/2.0
        _hora_final=self.hora_inicio+self.duracion
        _hora=hora
<<<<<<< HEAD
        if (_hora_pico>24 or _hora_final>24) and hora<self.hora_inicio: # arroja horas >24 !!!
=======
        if (_hora_pico>24 or _hora_final>24) and hora<self.hora_inicio:
>>>>>>> 82bf037d9b4b416c9e8d8df28b6db9e691ac8e07
            _hora+=24
        #
        hora1=None
        hora2=None
        color1=None
        color2=None
        if _hora<_hora_pico:
            hora1=self.hora_inicio
            hora2=_hora_pico
            color1=self.color_anterior
            color2=self.color
        else:
            hora1=_hora_pico
            hora2=_hora_final
            color1=self.color
            color2=self.color_proximo
        #
        self.momento=(_hora-hora1)/(hora2-hora1)
        self.color_luz=color1+(color2-color1)*self.momento
        self.color_luz[3]=1.0
        #log.debug("hi=%.1f d=%i h1=%.1f h2=%.1f h=%.1f _h=%.1f ci=%s cf=%s m=%.2f color=%s"%(self.hora_inicio, self.duracion, hora1, hora2, hora, _hora, str(color1), str(color2), self.momento, str(self.color_luz)))
        return self.color_luz
    
    def finalizado(self, hora):
        hora2=self.hora_inicio+self.duracion # arroja horas >24 !!!
        _hora=hora
        if hora<self.hora_inicio:
            hora2-=24
        if _hora>=hora2:
            return True
        return False
    
    def obtener_info(self):
        return "Periodo %s:\nhi=%i d=%i color=%s momento=%.2f\ncolor_luz=%s"%(self.nombre, self.hora_inicio, self.duracion, str(self.color), self.momento, str(self.color_luz))
