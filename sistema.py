from panda3d.core import *

import logging
log=logging.getLogger(__name__)

#
#
# Sistema Mundo
#
#
# altitud(TopoPerlinNoiseParams,TopoAltura)
# latitud(posicion_cursor.y)
# temperatura(TemperaturaPerlinNoiseParams,altitud,latitud)
# precipitacion(RainPerlinNoiseParams,altitud,latitud)
# bioma(temperatura_anual_media,precipitacion_frecuencia,latitud,altitud)
# vegetacion(bioma,?)
class Sistema:
    
    # topografia
    TopoExtension=8*1024 # +/- TopoExtension; ecuador=0
    TopoAltura=300.0
    TopoAltitudOceano=TopoAltura/2.0
    TopoAlturaSobreOceano=TopoAltura-TopoAltitudOceano
    TopoPerlinNoiseSeed=9601
    TopoPerlinNoiseParams=[(256.0, 1.0), (64.0, 0.2), (32.0, 0.075), (16.0, 0.005), (8.0, 0.001)] # [(escala, amplitud), ...]
    TopoPerlinNoiseEscalaGlobal=1.0
    # terrenos
    TerrenoTipoArena=0
    TerrenoTipoTierra=1
    TerrenoTipoYuyo=2
    TerrenoTipoPedregoso=3
    TerrenoTipoBarro=4
    TerrenoTipoNieve=5
    # altitud
    AltitudNivelSubacuatico=0.0
    AltitudNivelLlano=TopoAltitudOceano+(1/4*TopoAlturaSobreOceano)
    AltitudNivelPremontana=TopoAltitudOceano+(2/4*TopoAlturaSobreOceano)
    AltitudNivelMontana=TopoAltitudOceano+(3/4*TopoAlturaSobreOceano)
    AltitudNivelAlpina=TopoAltitudOceano+(4/4*TopoAlturaSobreOceano)
    # latitud
    LatitudTropical=1/4*TopoExtension
    LatitudSubTropical=2/4*TopoExtension
    LatitudFria=3/4*TopoExtension
    LatitudPolar=4/4*TopoExtension
    # ambiente
    AmbienteNulo=0
    AmbienteAgua=1
    AmbienteSuelo=2
    AmbienteCueva=3
    AmbienteAire=4
    # ano
    DiasDelAno=364 # para facilitar calculos
    # estaciones
    EstacionVerano=0
    EstacionOtono=1
    EstacionInvierno=2
    EstacionPrimavera=3
    EstacionRangoInclinacionSolar=23 # grados
    # dia
    DiaPeriodoAmanecer=0
    DiaPeriodoDia=1
    DiaPeriodoAtardecer=2
    DiaPeriodoNoche=3
    # temperatura
    TemperaturaNiveles=5 # [0,4]->polar a tropical
    TemperaturaPerlinNoiseParams=(8*1024.0, 196) # (escala, semilla)
    # precipitaciones; [0.0,1.0): 0.0=nula, 1.0=todo el tiempo
    PrecipitacionPerlinNoiseParams=(2*1024.0, 9016) # (escala, semilla)
    PrecipitacionTipoAgua=0
    PrecipitacionTipoNieve=1
    PrecipitacionIntensidadNula=0
    PrecipitacionIntensidadDebil=1
    PrecipitacionIntensidadModerada=2
    PrecipitacionIntensidadTormenta=3
    # biomas
    BiomaNulo=0
    BiomaDesiertoPolar=1
    BiomaTundra=2
    BiomaTaiga=3
    BiomaBosqueMediterraneo=4
    BiomaBosqueCaducifolio=5
    BiomaDesierto=6
    BiomaSavanah=7
    BiomaSelvaTropical=8
    # vegetacion
    VegetacionTipoNulo=0
    VegetacionTipoYuyo=1
    VegetacionTipoPlanta=2
    VegetacionTipoArbusto=3
    VegetacionTipoArbol=4
    VegetacionPerlinNoiseParams=(64.0, 9106) # (escala, semilla)
    
    def __init__(self):
        # componentes:
        self.ruido_topo=None
        self.ruido_temperatura=None
        self.ruido_precipitacion=None
        self.ruido_vegetacion=None
        # cursor:
        self.posicion_cursor=None
        # variables:
        self.ano=0
        self.dia=0
        self.periodo_dia=WorldSystem.DayPeriodDawn
        self.hora_normalizada=0.0
        self.temperatura_actual=None
        self.precipitacion_actual_tipo=Sistema.PrecipitacionTipoAgua
        self.precipitacion_actual_intensidad=Sistema.PrecipitacionIntensidadNula
        self.precipitacion_actual_duracion=0.0
        self.precipitacion_actual_t=0.0

    def cargar_parametros_iniciales(self, defecto=True):
        if defecto:
            self.posicion_cursor=Vec3(0, 0, 0)
            self.ano=0
            self.dia=0
            self.periodo_dia=WorldSystem.DayPeriodDawn
            self.hora_normalizada=0.0
            self._establecer_temperatura_actual()
            self._establecer_precipitacion()
        else:
            # leer de archivo
            pass
    
    def guardar_parametros_actuales(self):
        # escribir archivo
        pass
    
    def iniciar(self):
        log.info("iniciar")
        # ruido
        self._configurar_objetos_ruido()
        
    def terminar(self):
        log.info("terminar")
        pass
    
    def update(self, dt):
        self._establecer_fecha_hora_estacion()
        self._establecer_temperatura_actual()
        self._establecer_precipitacion()

    def _configurar_objetos_ruido(self):
        log.info("_configurar_objetos_ruido")
        # topografia
        self.ruido_topo=StackedPerlinNoise2()
        self.ruido_topo_escalas_amplitud=list()
        suma_amplitudes=0.0
        for escala, amplitud in Sistema.TopoPerlinNoiseParams:
            suma_amplitudes+=amplitud
        for escala, amplitud in Sistema.TopoPerlinNoiseParams:
            _amp=amplitud/suma_amplitudes
            _escala=escala*Sistema.TopoPerlinNoiseEscalaGlobal
            _ruido=PerlinNoise2(_escala, _escala, 256, Sistema.TopoPerlinNoiseSeed)
            self.ruido_topo.addLevel(_ruido, _amp)
        # temperatura
        _escala=Sistema.TemperaturaPerlinNoiseParams[0]
        _semilla=Sistema.TemperaturaPerlinNoiseParams[1]
        self.ruido_temperatura=PerlinNoise2(_escala, _escala, 256, _semilla)
        # precipitacion
        _escala=Sistema.PrecipitacionPerlinNoiseParams[0]
        _semilla=Sistema.PrecipitacionPerlinNoiseParams[1]
        self.ruido_precipitacion=PerlinNoise2(_escala, _escala, 256, _semilla)
        # vegetacion
        _escala=Sistema.VegetacionPerlinNoiseParams[0]
        _semilla=Sistema.VegetacionPerlinNoiseParams[1]
        self.ruido_vegetacion=PerlinNoise2(_escala, _escala, 256, _semilla)

    def _establecer_fecha_hora_estacion(self):
        pass

    def _establecer_temperatura_actual(self):
        pass
    
    def _establecer_precipitacion(self):
        pass
    
    def obtener_descriptor_locacion(self, posicion):
        desc=TopoDescriptorLocacion(posicion)
        return desc
    
    def obtener_altitud_suelo(self, posicion):
        #
        altitud=0
        # perlin noise object
        altitud=self.ruido_topo(posicion[0], posicion[1])*0.5+0.5
        altitud*=Sistema.TopoAltura
        if altitud>Sistema.TopoAltitudOceano+0.25:
            altura_sobre_agua=altitud-Sistema.TopoAltitudOceano
            altura_sobre_agua_n=altura_sobre_agua/Sistema.TopoAlturaSobreOceano
            altitud=Sistema.TopoAltitudOceano
            altitud+=0.25+altura_sobre_agua*altura_sobre_agua_n*altura_sobre_agua_n
            altitud+=75.0*altura_sobre_agua_n*altura_sobre_agua_n
            if altitud>Sistema.TopoAltura:
                log.warning("obtener_altitud_suelo altitud>Sistema.TopoAltura, recortando...")
                altitud=Sistema.TopoAltura
        #
        return altitud

    def obtener_altitud_tope(self, posicion):
        # a implementar para terrenos 3D, con cuevas, etc...
        return 5.0*Sistema.TopoAltura

    def obtener_altitud_suelo_supra_oceanica_norm(self, posicion):
        altitud=self.obtener_altitud_suelo(posicion)
        altitud-=TopoAltitudOceano
        altitud/=TopoAlturaSobreOceano
        return altitud

    def obtener_nivel_altitud(self, posicion):
        altitud=posicion.z
        if altitud<Sistema.AltitudNivelSubacuatico:
            return Sistema.AltitudNivelSubacuatico
        elif altitud<Sistema.AltitudNivelLlano:
            return Sistema.AltitudNivelLlano
        elif altitud<Sistema.AltitudNivelPremontana:
            return Sistema.AltitudNivelPremontana
        elif altitud<Sistema.AltitudNivelMontana:
            return Sistema.AltitudNivelMontana
        else:
            return Sistema.AltitudNivelAlpina
    
    def obtener_latitud(self, posicion):
        latitud=abs(posicion.y)
        if latitud<Sistema.LatitudTropical:
            return Sistema.LatitudTropical
        elif latitud<Sistema.LatitudSubTropical:
            return Sistema.LatitudSubTropical
        elif latitud<Sistema.LatitudFria:
            return Sistema.LatitudFria
        else:
            return Sistema.LatitudPolar

    def obtener_latitud_transicion(self, posicion):
        latitud=abs(posicion.y)
        transicion=0.0
        if latitud<Sistema.LatitudTropical:
            latitud_normalizada=latitud/Sistema.LatitudTropical
            if latitud_normalizada>0.66:
                transicion=((1.0-latitud_normalizada)/0.33)
            return (Sistema.LatitudTropical, transicion)
        elif latitud<Sistema.LatitudSubTropical:
            latitud_normalizada=(latitud-Sistema.LatitudTropical)/(Sistema.LatitudSubTropical-Sistema.LatitudTropical)
            if latitud_normalizada>0.66:
                transicion=((1.0-latitud_normalizada)/0.33)
            return (Sistema.LatitudSubTropical, transicion)
        elif latitud<Sistema.LatitudFria:
            latitud_normalizada=(latitud-Sistema.LatitudSubTropical)/(Sistema.LatitudFria-Sistema.LatitudSubTropical)
            if latitud_normalizada>0.66:
                transicion=((1.0-latitud_normalizada)/0.33)
            return (Sistema.LatitudFria, transicion)
        else:
            latitud_normalizada=(latitud-Sistema.LatitudFria)/(Sistema.LatitudPolar-Sistema.LatitudFria)
            if latitud_normalizada>0.66:
                transicion=((1.0-latitud_normalizada)/0.33)
            return (Sistema.LatitudPolar, transicion)

    def obtener_ambiente(self, posicion):
        altitud=self.obtener_altitud_suelo(posicion)
        if posicion<(Sistema.TopoAltitudOceano-0.5):
            return Sistema.AmbienteAgua
        elif abs(posicion-altitud)<0.1:
            return Sistema.AmbienteSuelo
        elif (posicion-altitud)>=0.1:
            return Sistema.AmbienteAire

    def obtener_temperatura_amplitud_dianoche(self, posicion):
        #
        altitud=self.obtener_altitud_suelo(posicion)
        if altitud<Sistema.TopoAltitudOceano:
            return 0.0
        #
        precipitacion_frecuencia=self.obtener_precipitacion_frecuencia(posicion)
        amplitud=5.0+20.0*(altitud/Sistema.TopoAlturaSobreOceano)*(1.0-precipitacion_frecuencia)
        return amplitud

    def obtener_temperatura_anual_media(self, posicion):
        altitud_normalizada=self.obtener_altitud_suelo_supra_oceanica_norm(posicion)
        latitud=self.obtener_latitud(posicion)
        temperatura=self.ruido_temperatura(posicion[0], posicion[1])*0.5+0.5
        temperatura-=abs(latitud)*0.2
        temperatura-=abs(altitud_normalizada)*0.2
        return temperatura

    def obtener_precipitacion_frecuencia(self, posicion):
        frecuencia=self.ruido_precipitacion(posicion[0], posicion[1])
        return frecuencia

    def obtener_inclinacion_solar_anual_media(self, posicion):
        latitud=posicion.y
        if latitud>Sistema.TopoExtension:
            latitud=Sistema.TopoExtension
        elif latitud<-Sistema.TopoExtension:
            latitud=-Sistema.TopoExtension
        inclinacion_solar_anual_media=Sistema.EstacionRangoInclinacionSolar*latitud/Sistema.TopoExtension
        return inclinacion_solar_anual_media

    def obtener_bioma(self, posicion):
        #
        altitud=self.obtener_altitud_suelo(posicion)
        latitud, transicion_latitud=self.obtener_latitud_transicion(posicion)
        temperatura_anual_media=self.obtener_temperatura_anual_media(posicion)
        precipitacion_frecuencia=self.obtener_precipitacion_frecuencia(posicion)
        #
        if latitud==Sistema.LatitudPolar and transicion_latitud>0.0:
            return (Sistema.BiomaDesiertoPolar, Sistema.BiomaNulo, 0.0)
        if precipitacion_frecuencia<0.1:
            return (Sistema.BiomaDesierto, Sistema.BiomaNulo, 0.0)

    def obtener_tipo_terreno(self, posicion):
        return (TerrenoTipoArena, TerrenoTipoTierra, 0.5)

    def obtener_descriptor_vegetacion(self, posicion, solo_existencia=False):
        pass

#
#
# TopoDescriptorLocacion
#
#
class TopoDescriptorLocacion:
    
    def __init__(self, posicion):
        # 3d
        self.posicion=None # (latitud,transicion)
        self.altitud_tope=None # cuevas
        self.ambiente=None
        # 2d
        self.latitud=None
        self.bioma=None # (bioma1,bioma2,factor_transicion)
        self.temperatura_amplitud_dianoche=None
        self.temperatura_anual_media=None # smooth noise
        self.precipitacion_frecuencia=None # smooth noise
        self.inclinacion_solar_anual_media=None

#
#
# DescriptorVegetacion
#
#
class DescriptorVegetacion:
    
    def __init__(self):
        self.tipo=Sistema.VegetacionTipoNulo
        self.variedad=None
        self.nombre=None
        self.edad=None
        self.altura=0.0
        self.radio_inferior=0.0
        self.radio_superior=0.0
