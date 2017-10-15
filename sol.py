from panda3d.core import *

class Sol:
    
    # periodo
    PeriodoAmanecer=0
    PeriodoDia=1
    PeriodoAtardecer=2
    PeriodoNoche=3
    
    # colores
    ColorAmanecer=LVector4(0.95, 0.75, 0.2, 1.0)
    ColorDia=LVector4(1.0, 1.0, 0.25, 1.0)
    ColorAtardecer=LVector4(0.95, 0.65, 0.3, 1.0)
    ColorNoche=LVector4(0.0, 0.0, 0.0, 1.0)
    
    def __init__(self, base):
        self.base=base
        # estado
        self.periodo=Sol.PeriodoAtardecer
        # hora?
        self.hora=0.0 # (0.0,1.0) 0.0=>19:00
        # pivot de rotacion
        self.pivot=self.base.render.attachNewNode("pivot_sol")
        self.pivot.setP(10.0) # inclinacion "estacional"
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
        #
        #self.pivot.setR(self.pivot, 5.0 * dt)
        #
        self.luz.lookAt(self.pivot)
        #
        roll=self.pivot.getR()
        self.hora=19.0+24.0*((roll if roll>0 else 360.0+roll)/360.0)
        if self.hora>=24.0:
            self.hora-=24.0
        #
        if self.periodo==Sol.PeriodoDia:
            if self.hora<180.0:
                self.periodo=Sol.PeriodoNoche
                self.luz.node().setColor(LVector4(0.1, 0.1, 0.1, 1)) # luz solar "de noche"
        elif self.periodo==Sol.PeriodoNoche:
            if self.hora>180.0:
                self.periodo=Sol.PeriodoDia
                self.luz.node().setColor(LVector4(1.0, 1.0, 1.0, 1))
        
    def obtener_info(self):
        info="Sol hora=%0.2f"%(self.hora)
        return info
    
