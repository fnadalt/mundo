from panda3d.core import *
import math

import logging
log=logging.getLogger(__name__)

instancia=None
def establecer_instancia(sistema):
    global instancia
    log.info("establecer_instancia")
    if instancia:
        raise Exception("instancia de sistema ya definida")
    instancia=sistema

def obtener_instancia():
    if not instancia:
        raise Exception("instancia de sistema no iniciada.")
    return instancia

def remover_instancia():
    global instancia
    log.info("remover_instancia")
    if not instancia:
        raise Exception("instancia de sistema no iniciada.")
    instancia.terminar()
    instancia=None

#
#
# Sistema Mundo
#
#
# altitud(TopoPerlinNoiseParams,TopoAltura,latitud)
# latitud(posicion_cursor.xy)==ditancia_desde_centro (Manhattan)
# temperatura_media(TemperaturaPerlinNoiseParams,altitud,latitud)
# temperatura_actual_norm(temperatura_media,estacion_normalizada,hora_normalizada,altitud)
# precipitacion_frecuencia(PrecipitacionFrecuenciaPerlinNoiseParams)
# nubosidad(PrecipitacionNubosidadPerlinNoiseParams)
# bioma(temperatura_anual_media,precipitacion_frecuencia)
# vegetacion(temperatura_anual_media,precipitacion_frecuencia) ?
class Sistema:
    
    # topografia
    TopoExtension=8*1024 # +/-TopoExtension; ecuador=0
    TopoExtensionTransicion=TopoExtension+1024
    TopoAltura=300.0
    TopoAltitudOceano=TopoAltura/2.0
    TopoAlturaSobreOceano=TopoAltura-TopoAltitudOceano
    TopoPerlinNoiseSeed=9601
    TopoPerlinNoiseParams=[(256.0, 1.0), (64.0, 0.2), (32.0, 0.075), (16.0, 0.005), (8.0, 0.001)] # [(escala, amplitud), ...]
    TopoIslasPerlinNoiseParams=(8.0*1024.0, 1199) # (escala, semilla)
    TopoPerlinNoiseEscalaGlobal=1.0
    # terrenos; alpha para splatting
    TerrenoPerlinNoiseParams=(64.0, 1199) # (escala, semilla)
    TerrenoTipoNulo=0
    TerrenoTipoNieve=1 # alpha=1.0 (tope)
    TerrenoTipoTundra=2 # alpha=0.0 (fondo)
    TerrenoTipoTierraSeca=3 # alpha=0.4
    TerrenoTipoTierraHumeda=4 # alpha=0.5
    TerrenoTipoPastoSeco=5 # alpha=0.6
    TerrenoTipoPastoHumedo=6 # alpha=0.7
    TerrenoTipoArenaSeca=7 # alpha=0.8
    TerrenoTipoArenaHumeda=8 # alpha=0.9
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
    DiaPeriodoNoche=0
    DiaPeriodoAmanecer=1
    DiaPeriodoDia=2
    DiaPeriodoAtardecer=3
    DiaPeriodosHorariosN=(0.05, 0.45, 0.55, 0.95)
    # temperatura; [0,1]->[-50,50]; media: [0.2,0.8]->[-30,30]
    TemperaturaPerlinNoiseParams=(4*1024.0, 196) # (escala, semilla)
    TemperaturaAmplitudTermicaMaxima=0.4
    # precipitaciones; [0.0,1.0): 0.0=nula, 1.0=maxima
    PrecipitacionFrecuenciaPerlinNoiseParams=(2*1024.0, 2*9016) # (escala, semilla)
    PrecipitacionNubosidadPerlinNoiseParams=(1024.0, 9016) # (escala, semilla)
    PrecipitacionNubosidadGatillo=0.75
    PrecipitacionTipoAgua=0
    PrecipitacionTipoNieve=1
    PrecipitacionIntensidadNula=0
    PrecipitacionIntensidadDebil=1
    PrecipitacionIntensidadModerada=2
    PrecipitacionIntensidadTormenta=3
    # biomas
    BiomaNulo=0
    BiomaDesiertoPolar=1 # desierto frio
    BiomaTundra=2 # frio arido
    BiomaTaiga=3 # frio humedo
    BiomaBosqueMediterraneo=4 # templado arido
    BiomaBosqueCaducifolio=5 # templado humedo
    BiomaSavannah=6 # calido arido
    BiomaSelva=7 # calido humedo
    BiomaDesierto=8 # desierto calido
    BiomaTabla=[[BiomaDesiertoPolar, BiomaTundra, BiomaDesierto,           BiomaDesierto, BiomaDesierto],  \
                [BiomaDesiertoPolar, BiomaTundra, BiomaBosqueMediterraneo, BiomaSavannah, BiomaSavannah],  \
                [BiomaDesiertoPolar, BiomaTaiga,  BiomaBosqueCaducifolio,  BiomaSelva,    BiomaSelva],  \
                [BiomaDesiertoPolar, BiomaTaiga,  BiomaBosqueCaducifolio,  BiomaSelva,    BiomaSelva]  \
                ] # tabla(temperatura_anual_media,precipitacion_frecuencia). Se repiten en los bordes para facilitar calculos.
    # vegetacion
    VegetacionTipoNulo=0
    VegetacionTipoYuyo=1
    VegetacionTipoPlanta=2
    VegetacionTipoArbusto=3
    VegetacionTipoArbol=4
    VegetacionPerlinNoiseParams=(64.0, 9106) # (escala, semilla)

    # colores
    ColoresTipoTerreno={TerrenoTipoNulo:Vec4(0, 0, 0, 255), # negro
                        TerrenoTipoNieve:Vec4(255, 255, 255, 255), # blanco
                        TerrenoTipoTundra:Vec4(128, 128, 128, 255),  # gris
                        TerrenoTipoTierraSeca:Vec4(255, 0, 255, 255), # fucsia 
                        TerrenoTipoTierraHumeda:Vec4(255, 0, 0, 255), # rojo
                        TerrenoTipoPastoSeco:Vec4(255, 255, 0, 255), # amarillo
                        TerrenoTipoPastoHumedo:Vec4(0, 255, 0, 255), # verde
                        TerrenoTipoArenaSeca:Vec4(0, 255, 255, 255), # celeste
                        TerrenoTipoArenaHumeda:Vec4(0, 0, 255, 255), # azul
                        }
    ColoresBioma=      {BiomaNulo:Vec4(0, 0, 0, 255), # negro
                        BiomaDesiertoPolar:Vec4(255, 255, 255, 255), # blanco
                        BiomaTundra:Vec4(0, 255, 255, 255), # celeste
                        BiomaTaiga:Vec4(0, 0, 255, 255), # azul
                        BiomaBosqueCaducifolio:Vec4(255, 0, 255, 255), # fucsia 
                        BiomaBosqueMediterraneo:Vec4(255, 0, 0, 255), # rojo
                        BiomaSavannah:Vec4(255, 255, 0, 255), # amarillo
                        BiomaSelva:Vec4(0, 255, 0, 255), # verde
                        BiomaDesierto:Vec4(128, 128, 128, 255) # gris
                        }
    
    def __init__(self):
        # componentes:
        self.ruido_topo=None
        self.ruido_islas=None
        self.ruido_terreno=None
        self.ruido_temperatura=None
        self.ruido_precipitacion=None
        self.ruido_nubosidad=None
        self.ruido_vegetacion=None
        # parametros:
        self.posicion_cursor=Vec3(0, 0, 0)
        self.duracion_dia_segundos=0.0
        self.ano=0
        self.dia=0
        # variables externas:
        self.estacion=Sistema.EstacionVerano
        self.periodo_dia_actual=Sistema.DiaPeriodoAtardecer
        self.periodo_dia_anterior=Sistema.DiaPeriodoDia
        self.periodo_dia_posterior=Sistema.DiaPeriodoNoche
        self.hora_normalizada=0.0
        self.temperatura_actual_norm=None
        self.nubosidad=0.0
        self.precipitacion_actual_tipo=Sistema.PrecipitacionTipoAgua
        self.precipitacion_actual_intensidad=Sistema.PrecipitacionIntensidadNula
        self.precipitacion_actual_duracion=0.0
        self.precipitacion_actual_t=0.0
        # variables internas:
        self._segundos_transcurridos_dia=0.0
        #
        self.cargar_parametros_iniciales(defecto=True)

    def obtener_info(self):
        tam=self.obtener_temperatura_anual_media_norm(self.posicion_cursor)
        prec_f=self.obtener_precipitacion_frecuencia_anual(self.posicion_cursor)
        bioma=self.obtener_transicion_biomas(self.posicion_cursor)
        tipo_terreno=self.obtener_tipo_terreno(self.posicion_cursor)
        info="Sistema posicion_cursor=(%.3f,%.3f,%.3f)\n"%(self.posicion_cursor[0], self.posicion_cursor[1], self.posicion_cursor[2])
        info+="geo: tam=%.3f prec_f=%.3f bioma=(%s) tipo_terreno=(%s)\n"%(tam, prec_f, bioma, tipo_terreno)
        info+="era: año=%i estacion=%i dia=%i hora=%.2f(%.2f/%i) periodo_dia_actual=%i\n"%(self.ano, self.estacion, self.dia, self.hora_normalizada, self._segundos_transcurridos_dia, self.duracion_dia_segundos, self.periodo_dia_actual)
        info+="temp=%.2f nubosidad=%.2f precipitacion=[tipo=%i intens=%i t=(%.2f/%2.f)]\n"%(self.temperatura_actual_norm, self.nubosidad, self.precipitacion_actual_tipo, self.precipitacion_actual_intensidad, self.precipitacion_actual_t, self.precipitacion_actual_duracion)
        return info

    def cargar_parametros_iniciales(self, defecto=True):
        #
        if defecto:
            log.info("cargar_parametros_iniciales por defecto")
            self.posicion_cursor=Vec3(0, 0, 0)
            self.duracion_dia_segundos=1800
            self.ano=0
            self.dia=0
            self._segundos_transcurridos_dia=0.60*self.duracion_dia_segundos
        else:
            log.info("cargar_parametros_iniciales desde configuracion")
            # leer de archivo
            pass
    
    def guardar_parametros_actuales(self):
        log.info("guardar_parametros_actuales")
        # escribir archivo
        pass
    
    def iniciar(self):
        log.info("iniciar")
        #
        self.hora_normalizada=self._segundos_transcurridos_dia/self.duracion_dia_segundos
        if self.hora_normalizada>Sistema.DiaPeriodoAtardecer and self.hora_normalizada<Sistema.DiaPeriodoNoche:
            self.periodo_dia_actual=Sistema.DiaPeriodoAtardecer
            self.periodo_dia_anterior=Sistema.DiaPeriodoDia
            self.periodo_dia_posterior=Sistema.DiaPeriodoNoche
        elif self.hora_normalizada>Sistema.DiaPeriodoNoche and self.hora_normalizada<Sistema.DiaPeriodoAmanecer:
            self.periodo_dia_actual=Sistema.DiaPeriodoNoche
            self.periodo_dia_anterior=Sistema.DiaPeriodoAtardecer
            self.periodo_dia_posterior=Sistema.DiaPeriodoAmanecer
        elif self.hora_normalizada>Sistema.DiaPeriodoAmanecer and self.hora_normalizada<Sistema.DiaPeriodoDia:
            self.periodo_dia_actual=Sistema.DiaPeriodoAmanecer
            self.periodo_dia_anterior=Sistema.DiaPeriodoNoche
            self.periodo_dia_posterior=Sistema.DiaPeriodoDia
        elif self.hora_normalizada>Sistema.DiaPeriodoDia and self.hora_normalizada<Sistema.DiaPeriodoAtardecer:
            self.periodo_dia_actual=Sistema.DiaPeriodoDia
            self.periodo_dia_anterior=Sistema.DiaPeriodoAmanecer
            self.periodo_dia_posterior=Sistema.DiaPeriodoAtardecer
        self.estacion=self._determinar_estacion()
        # ruido
        self._configurar_objetos_ruido()
        #
        self.update(0.0, self.posicion_cursor)
        
    def terminar(self):
        log.info("terminar")
        pass
    
    def update(self, dt, posicion_cursor):
        self.posicion_cursor=posicion_cursor
        self._establecer_fecha_hora_estacion(dt)
        self._establecer_temperatura_actual_norm(dt)
        self._establecer_precipitacion(dt)

    def obtener_descriptor_locacion(self, posicion):
        desc=TopoDescriptorLocacion(posicion)
        return desc
    
    def obtener_altitud_suelo(self, posicion):
        #
        altitud=0
        # perlin noise object
        altitud=self.ruido_topo(posicion[0], posicion[1])*0.5+0.5
        #
        #altitud+=-0.5*abs(self.ruido_islas.noise(posicion[0], posicion[1]))
        #
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
        latitud=self.obtener_latitud(posicion)
        if latitud>Sistema.TopoExtension:
            factor_transicion=(latitud-Sistema.TopoExtension)/(Sistema.TopoExtensionTransicion-Sistema.TopoExtension)
            altitud=min(Sistema.TopoAltura, altitud+Sistema.TopoAltura*factor_transicion)
        #
        #altitud=min(Sistema.TopoAltitudOceano+1, altitud) # !!! terreno plano sobre el oceano
        return altitud

    def obtener_altitud_suelo_cursor(self):
        return self.obtener_altitud_suelo(self.posicion_cursor)
        
    def obtener_altitud_tope(self, posicion):
        # a implementar para grillas 3D, con cuevas, etc...
        return 5.0*Sistema.TopoAltura

    def obtener_altitud_suelo_supra_oceanica_norm(self, posicion):
        altitud=self.obtener_altitud_suelo(posicion)
        altitud-=Sistema.TopoAltitudOceano
        altitud/=Sistema.TopoAlturaSobreOceano
        return altitud

    def obtener_nivel_altitud(self, posicion):
        altitud=posicion[2]
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
        return math.sqrt(posicion[0]**2+posicion[1]**2)
        #return abs(posicion[0])+abs(posicion[1])
    
    def obtener_latitud_norm(self, posicion):
        return self.obtener_latitud(posicion)/Sistema.TopoExtension
    
    def obtener_nivel_latitud(self, posicion):
        latitud=self.obtener_latitud(posicion)
        if latitud<Sistema.LatitudTropical:
            return Sistema.LatitudTropical
        elif latitud<Sistema.LatitudSubTropical:
            return Sistema.LatitudSubTropical
        elif latitud<Sistema.LatitudFria:
            return Sistema.LatitudFria
        else:
            return Sistema.LatitudPolar

    def obtener_nivel_latitud_transicion(self, posicion): # util?
        latitud=self.obtener_latitud(posicion)
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

    def obtener_temperatura_amplitud_dianoche(self, posicion): # no usado
        #
        altitud=self.obtener_altitud_suelo(posicion)
        if altitud<Sistema.TopoAltitudOceano:
            return 0.0
        #
        precipitacion_frecuencia=self.obtener_precipitacion_frecuencia_anual(posicion)
        amplitud=5.0+20.0*(altitud/Sistema.TopoAlturaSobreOceano)*(1.0-precipitacion_frecuencia)
        return amplitud

    def obtener_temperatura_anual_media_norm(self, posicion):
        #print("obtener_temperatura_anual_media_norm (%.2f,%.2f)"%(posicion[0], posicion[1]))
        altitud_normalizada=self.obtener_altitud_suelo_supra_oceanica_norm(posicion)
        latitud_normalizada=self.obtener_latitud_norm(posicion)
        temperatura=1.0-(0.925*latitud_normalizada**2)
        temperatura+=0.5*self.ruido_temperatura(posicion[0], posicion[1])
        temperatura-=abs(altitud_normalizada)*0.2
        if latitud_normalizada>=1.0:
            latitud=abs(self.obtener_latitud(posicion))
            factor_transicion=(latitud-Sistema.TopoExtension)/(Sistema.TopoExtensionTransicion-Sistema.TopoExtension)
            factor_transicion=max(0.0, min(1.0, factor_transicion))
            temperatura-=(temperatura*factor_transicion)
        temperatura=0.2+max(temperatura,0.0)*0.6 # ajustar a rango de temperatura_media [0.2,0.8]
        #print("temperatura_anual_media %.3f"%temperatura)
        return temperatura

    def obtener_temperatura_grados(self, temperatura_normalizada):
        # temperatura_normalizada: [0,1] -> [-50,50]
        temperatura_grados=(temperatura_normalizada-0.5)*2.0*50.0
        return temperatura_grados

    def obtener_temperatura_actual_grados(self):
        return self.obtener_temperatura_grados(self.temperatura_actual_norm)

    def obtener_precipitacion_frecuencia_anual(self, posicion):
        #print("obtener_precipitacion_frecuencia_anual (%.2f,%.2f)"%(posicion[0], posicion[1]))
        #
        frecuencia=self.ruido_precipitacion(posicion[0], posicion[1])*0.5+0.5
        #print("frecuencia %.3f"%frecuencia)
        return frecuencia

    def obtener_inclinacion_solar_anual_media(self, posicion):
        latitud=self.obtener_latitud(posicion)
        if latitud>Sistema.TopoExtension:
            latitud=Sistema.TopoExtension
        elif latitud<-Sistema.TopoExtension:
            latitud=-Sistema.TopoExtension
        inclinacion_solar_anual_media=Sistema.EstacionRangoInclinacionSolar*latitud/Sistema.TopoExtension
        return inclinacion_solar_anual_media

    def obtener_inclinacion_solar_actual(self, posicion):
        ism=self.obtener_inclinacion_solar_anual_media(posicion)
        offset_estacional=abs(0.5-(self.dia/Sistema.DiasDelAno))
        inclinacion=ism*offset_estacional
        return inclinacion

    def obtener_bioma(self, posicion):
        #
        temperatura_anual_media=self.obtener_temperatura_anual_media_norm(posicion)
        precipitacion_frecuencia=self.obtener_precipitacion_frecuencia_anual(posicion)
        #log.debug("obtener_bioma pos=%s tam=%.3f prec_f=%.3f"%(posicion, temperatura_anual_media, precipitacion_frecuencia))
        #
        if temperatura_anual_media<0.35:
            return Sistema.BiomaDesiertoPolar
        elif temperatura_anual_media>=0.35 and temperatura_anual_media<0.50:
            if precipitacion_frecuencia<0.33:
                return Sistema.BiomaTundra
            else:
                return Sistema.BiomaTaiga
        elif temperatura_anual_media>=0.50 and temperatura_anual_media<0.65:
            if precipitacion_frecuencia<0.33:
                return Sistema.BiomaDesierto
            elif precipitacion_frecuencia>=0.33 and precipitacion_frecuencia<0.66:
                return Sistema.BiomaBosqueMediterraneo
            elif precipitacion_frecuencia>=0.66:
                return Sistema.BiomaBosqueCaducifolio
        elif temperatura_anual_media>=0.65:
            if precipitacion_frecuencia<0.33:
                return Sistema.BiomaDesierto
            elif precipitacion_frecuencia>=0.33 and precipitacion_frecuencia<0.66:
                return Sistema.BiomaSavannah
            elif precipitacion_frecuencia>=0.66:
                return Sistema.BiomaSelva
        else:
            log.error("caso no contemplado: tam=%.3f p_frec=%.3f"%(temperatura_anual_media, precipitacion_frecuencia))
            return Sistema.BiomaNulo

    def obtener_transicion_biomas(self, posicion, loguear=False):
        temperatura_anual_media=self.obtener_temperatura_anual_media_norm(posicion)
        precipitacion_frecuencia=self.obtener_precipitacion_frecuencia_anual(posicion)
        return self._calcular_transicion_tabla_biomas(temperatura_anual_media, precipitacion_frecuencia, loguear)

    def obtener_tipo_terreno(self, posicion): # f()->(tipo_terreno_base,tipo_terreno_superficie,factor_transicion)
        # Determina, segun los biomas involucrados en el punto del mapa, dos tipos de terreno y un factor de "mezcla"
        # entre ambos.
        datos_biomas=self.obtener_transicion_biomas(posicion)
        # ineficiente llamar dos veces math.modf?
        _sorted=sorted(datos_biomas, key=lambda x:math.modf(x)[0])
        distancia_a, bioma_a=math.modf(_sorted[0])
        distancia_b, bioma_b=math.modf(_sorted[1])
        factor_transicion=distancia_a/(distancia_a+distancia_b)
        tipo_terreno_base1, tipo_terreno_superficie1=self._obtener_terreno_bioma(bioma_a)
        tipo_terreno_base2, tipo_terreno_superficie2=self._obtener_terreno_bioma(bioma_b)
        return (tipo_terreno_base1, tipo_terreno_base2, factor_transicion)

    def obtener_descriptor_vegetacion(self, posicion, solo_existencia=False):
        pass

    def obtener_momento_era(self):
        momento=self.ano*Sistema.DiasDelAno+self.dia+self.hora_normalizada
        return momento

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
        # islas
        _escala=Sistema.TopoIslasPerlinNoiseParams[0]
        _semilla=Sistema.TopoIslasPerlinNoiseParams[1]
        self.ruido_islas=PerlinNoise2(_escala, _escala, 256, _semilla)
        # terreno
        _escala=Sistema.TerrenoPerlinNoiseParams[0]
        _semilla=Sistema.TerrenoPerlinNoiseParams[1]
        self.ruido_terreno=PerlinNoise2(_escala, _escala, 256, _semilla)
        # temperatura
        _escala=Sistema.TemperaturaPerlinNoiseParams[0]
        _semilla=Sistema.TemperaturaPerlinNoiseParams[1]
        self.ruido_temperatura=PerlinNoise2(_escala, _escala, 256, _semilla)
        # precipitacion
        _escala=Sistema.PrecipitacionFrecuenciaPerlinNoiseParams[0]
        _semilla=Sistema.PrecipitacionFrecuenciaPerlinNoiseParams[1]
        self.ruido_precipitacion=PerlinNoise2(_escala, _escala, 256, _semilla)
        # nubosidad
        _escala=Sistema.PrecipitacionNubosidadPerlinNoiseParams[0]
        _semilla=Sistema.PrecipitacionNubosidadPerlinNoiseParams[1]
        self.ruido_nubosidad=PerlinNoise2(_escala, _escala, 256, _semilla)
        # vegetacion
        _escala=Sistema.VegetacionPerlinNoiseParams[0]
        _semilla=Sistema.VegetacionPerlinNoiseParams[1]
        self.ruido_vegetacion=PerlinNoise2(_escala, _escala, 256, _semilla)
    
    def _calcular_transicion_tabla_biomas(self, temperatura_anual_media, precipitacion_frecuencia, loguear=False):
        # Se calcula las distancias desde el punto(temperatura_anual_media,precipitacion_frecuencia), hacia
        # cada uno de los cuatro biomas circundantes: A, el bioma mas proximo; B, el siguiente mas proximo en
        # temperatura (x); C, el mas proximo en precipitacion (y); D, el mas lejano (o diagonal).
        # Devuelve las distancias normalizadas en la porcion fraccional (dA, dB, dC, dD), y el bioma
        # correspondiente en la porcion entera; el signo indica la direccion.
        punto=(temperatura_anual_media*4, precipitacion_frecuencia*3)
        celda_a=(int(punto[0]), int(punto[1]))
        punto_max_a=(celda_a[0]+0.5, celda_a[1]+0.5)
        delta_a=[0, 0]
        delta_a[0]=1 if (punto[0]-punto_max_a[0])>0 else -1
        delta_a[1]=1 if (punto[1]-punto_max_a[1])>0 else -1
        punto_max_b=(max(0.0, punto_max_a[0]+delta_a[0]), punto_max_a[1])
        punto_max_c=(punto_max_a[0], max(0.0, punto_max_a[1]+delta_a[1]))
        punto_max_d=(max(0.0, punto_max_a[0]+delta_a[0]), max(0.0, punto_max_a[1]+delta_a[1]))
        # pitagoras
#        distancia_a=min(0.99, math.sqrt((punto[0]-punto_max_a[0])**2 + (punto[1]-punto_max_a[1])**2)) # min() necesario?
#        distancia_b=min(0.99, math.sqrt((punto[0]-punto_max_b[0])**2 + (punto[1]-punto_max_b[1])**2)) # min() necesario?
#        distancia_c=min(0.99, math.sqrt((punto[0]-punto_max_c[0])**2 + (punto[1]-punto_max_c[1])**2)) # min() necesario?
#        distancia_d=min(0.99, math.sqrt((punto[0]-punto_max_d[0])**2 + (punto[1]-punto_max_d[1])**2))
        # manhattan
        distancia_a=min(0.99, abs(punto[0]-punto_max_a[0])+abs(punto[1]-punto_max_a[1]))
        distancia_b=min(0.99, abs(punto[0]-punto_max_b[0])+abs(punto[1]-punto_max_b[1]))
        distancia_c=min(0.99, abs(punto[0]-punto_max_c[0])+abs(punto[1]-punto_max_c[1]))
        distancia_d=min(0.99, abs(punto[0]-punto_max_d[0])+abs(punto[1]-punto_max_d[1]))
        #
        bioma_a=Sistema.BiomaTabla[celda_a[1]][celda_a[0]]
        bioma_b=Sistema.BiomaTabla[int(punto_max_b[1])][int(punto_max_b[0])]
        bioma_c=Sistema.BiomaTabla[int(punto_max_c[1])][int(punto_max_c[0])]
        bioma_d=Sistema.BiomaTabla[int(punto_max_d[1])][int(punto_max_d[0])]
        #
#        if distancia_a<=0.25:
#            distancia_a=0.0
#            distancia_b, distancia_c, distancia_d=0.99, 0.99, 0.99
#        else:
#            distancia_a=(distancia_a-0.25)/0.75
        #
        if loguear:
            print("_calcular_transicion_tabla_biomas:\n" \
                  "p=(%s) celda_a=(%s) pmax=(%s) delta_a=(%s)\n" \
                  "d=(%s) b=(%s)" % (str(punto), str(celda_a), str((punto_max_a, punto_max_b, punto_max_c, punto_max_d)), str(delta_a), str((distancia_a, distancia_b, distancia_c, distancia_d)), str((bioma_a, bioma_b, bioma_c, bioma_d)))
                  )
        #
        return (bioma_a+distancia_a, 
                bioma_b+distancia_b, 
                bioma_c+distancia_c, 
                bioma_d+distancia_d
                )

    def _obtener_terreno_bioma(self, bioma): # f()->(tipo_terreno_base,tipo_terreno_superficie)
        if bioma==Sistema.BiomaDesiertoPolar:
            tipo_terreno_base=Sistema.TerrenoTipoNieve # TerrenoTipoTundra
            tipo_terreno_superficie=Sistema.TerrenoTipoNieve
        elif bioma==Sistema.BiomaTundra:
            tipo_terreno_base=Sistema.TerrenoTipoTundra
            tipo_terreno_superficie=Sistema.TerrenoTipoTundra
        elif bioma==Sistema.BiomaBosqueMediterraneo or bioma==Sistema.BiomaSavannah:
            tipo_terreno_base=Sistema.TerrenoTipoTierraSeca
            tipo_terreno_superficie=Sistema.TerrenoTipoPastoSeco
        elif bioma==Sistema.BiomaTaiga or bioma==Sistema.BiomaBosqueCaducifolio or bioma==Sistema.BiomaSelva:
            tipo_terreno_base=Sistema.TerrenoTipoTierraHumeda
            tipo_terreno_superficie=Sistema.TerrenoTipoPastoHumedo
        elif bioma==Sistema.BiomaDesierto:
            tipo_terreno_base=Sistema.TerrenoTipoArenaSeca
            tipo_terreno_superficie=Sistema.TerrenoTipoArenaSeca
        return (tipo_terreno_base, tipo_terreno_superficie)

    def calcular_offset_periodo_dia(self):
        hora1=Sistema.DiaPeriodosHorariosN[self.periodo_dia_actual]
        hora2=Sistema.DiaPeriodosHorariosN[self.periodo_dia_posterior]
        hn=self.hora_normalizada
        if hora2==Sistema.DiaPeriodosHorariosN[Sistema.DiaPeriodoNoche]:
            hora2+=1.0
            if hn<hora1:
                hn+=1.0
        offset=(hn-hora1)/(hora2-hora1)
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

    def _establecer_fecha_hora_estacion(self, dt):
        # tiempo transcurrido en segundos
        self._segundos_transcurridos_dia+=dt
        if self._segundos_transcurridos_dia>self.duracion_dia_segundos:
            self._segundos_transcurridos_dia-=self.duracion_dia_segundos
        # establecer horma normalizada
        self.hora_normalizada=self._segundos_transcurridos_dia/self.duracion_dia_segundos
        # determinar periodo dia
        _hora_anterior=Sistema.DiaPeriodosHorariosN[self.periodo_dia_anterior]
        _hora_posterior=Sistema.DiaPeriodosHorariosN[self.periodo_dia_posterior]
        _hora_normalizada=self.hora_normalizada
        if _hora_posterior==0.05:
            _hora_posterior+=1.0
            if _hora_normalizada<_hora_anterior:
                _hora_normalizada+=1.0
        if _hora_normalizada>=_hora_posterior:
            self.periodo_dia_actual=(self.periodo_dia_actual+1 if self.periodo_dia_actual<Sistema.DiaPeriodoAtardecer else Sistema.DiaPeriodoNoche)
            self.periodo_dia_anterior=(self.periodo_dia_anterior+1 if self.periodo_dia_anterior<Sistema.DiaPeriodoAtardecer else Sistema.DiaPeriodoNoche)
            self.periodo_dia_posterior=(self.periodo_dia_posterior+1 if self.periodo_dia_posterior<Sistema.DiaPeriodoAtardecer else Sistema.DiaPeriodoNoche)
            # actualizar dia?
            if self.periodo_dia_actual==Sistema.DiaPeriodoNoche:
                self.dia+=1
                # actualizar ano?
                if self.dia>Sistema.DiasDelAno:
                    self.ano+=1
                    self.dia=0
                # establecer estacion
                self.estacion=self._determinar_estacion()

    def _determinar_estacion(self):
        return min(3, int((self.dia/Sistema.DiasDelAno)*4))

    def _establecer_temperatura_actual_norm(self, dt):
        #
        temperatura_anual_media=self.obtener_temperatura_anual_media_norm(self.posicion_cursor)
        altitud_normalizada=self.obtener_altitud_suelo_supra_oceanica_norm(self.posicion_cursor)
        estacion_termica=abs(0.5-self.dia/Sistema.DiasDelAno)
        periodo_dia_termico=abs(0.5-((self.hora_normalizada+0.25)%1)) # [0.0,0.5]->(frio,calor)
        #
        factor_termico=(periodo_dia_termico+estacion_termica+(1.0-altitud_normalizada))/2.0 # [0.0,1.0]
        self.temperatura_actual_norm=temperatura_anual_media-(Sistema.TemperaturaAmplitudTermicaMaxima/2.0)+(factor_termico*Sistema.TemperaturaAmplitudTermicaMaxima)
    
    def _establecer_precipitacion(self, dt):
        if self.precipitacion_actual_intensidad==Sistema.PrecipitacionIntensidadNula:
            momento_era=self.ano*Sistema.DiasDelAno+self.dia+self.hora_normalizada
            precipitacion_frecuencia=self.obtener_precipitacion_frecuencia_anual(self.posicion_cursor)
            self.nubosidad=max(0.0, self.ruido_nubosidad(0.0, momento_era)-(1.0-precipitacion_frecuencia))
            if self.nubosidad>Sistema.PrecipitacionNubosidadGatillo:
                if self.temperatura_actual_norm<=0.0:
                    self.precipitacion_actual_tipo=Sistema.PrecipitacionTipoNieve
                else:
                    self.precipitacion_actual_tipo=Sistema.PrecipitacionTipoAgua
                self.precipitacion_actual_t=0.0
                self.precipitacion_actual_duracion=0.5*precipitacion_frecuencia
                self.precipitacion_actual_intensidad=4.0*precipitacion_frecuencia
        else:
            self.precipitacion_actual_t+=dt
            if self.precipitacion_actual_t>self.precipitacion_actual_duracion:
                self.precipitacion_actual_tipo=Sistema.PrecipitacionIntensidadNula

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
        # objetos; XOR
        self.vegetacion=None # DescriptorVegetacion
        self.roca=None # id_roca?

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

#
#
# TESTER
#
#
from direct.showbase.ShowBase import ShowBase
from direct.gui.DirectGui import *
class Tester(ShowBase):

    TamanoImagen=128
    PasoDesplazamiento=TamanoImagen/3.0

    TipoImagenTopo=0
    TipoImagenTemperaturaAM=1
    TipoImagenTemperaturaPrecip=2
    TipoImagenBioma=3
    TipoImagenTerreno=4
    TipoImagenInterpTabla=5
    
    ColoresTipoTerreno={Sistema.TerrenoTipoNulo:Vec4(0, 0, 0, 255), # negro
                        Sistema.TerrenoTipoNieve:Vec4(255, 255, 255, 255), # blanco
                        Sistema.TerrenoTipoTundra:Vec4(128, 128, 128, 255),  # gris
                        Sistema.TerrenoTipoTierraSeca:Vec4(255, 0, 255, 255), # fucsia 
                        Sistema.TerrenoTipoTierraHumeda:Vec4(255, 0, 0, 255), # rojo
                        Sistema.TerrenoTipoPastoSeco:Vec4(255, 255, 0, 255), # amarillo
                        Sistema.TerrenoTipoPastoHumedo:Vec4(0, 255, 0, 255), # verde
                        Sistema.TerrenoTipoArenaSeca:Vec4(0, 255, 255, 255), # celeste
                        Sistema.TerrenoTipoArenaHumeda:Vec4(0, 0, 255, 255), # azul
                        }

    ColoresBioma={Sistema.BiomaNulo:Vec4(0, 0, 0, 255), # negro
                        Sistema.BiomaDesiertoPolar:Vec4(255, 255, 255, 255), # blanco
                        Sistema.BiomaTundra:Vec4(0, 255, 255, 255), # celeste
                        Sistema.BiomaTaiga:Vec4(0, 0, 255, 255), # azul
                        Sistema.BiomaBosqueCaducifolio:Vec4(255, 0, 255, 255), # fucsia 
                        Sistema.BiomaBosqueMediterraneo:Vec4(255, 0, 0, 255), # rojo
                        Sistema.BiomaSavannah:Vec4(255, 255, 0, 255), # amarillo
                        Sistema.BiomaSelva:Vec4(0, 255, 0, 255), # verde
                        Sistema.BiomaDesierto:Vec4(128, 128, 128, 255) # gris
                        }

    def __init__(self):
        #
        super(Tester, self).__init__()
        self.disableMouse()
        self.win.setClearColor(Vec4(0.95, 1.0, 1.0, 1.0))
        #
        self.pos_foco=None
        #
        plano=CardMaker("plano_agua")
        r=0.0 # !!!
        plano.setFrame(-r, r, -r, r)
        plano.setColor((0, 0, 1, 1))
        self.plano=self.render.attachNewNode(plano.generate())
        #
        self.tipo_imagen=Tester.TipoImagenTopo
        #
        self.texturaImagen=None
        self.imagen=None
        self.zoom_imagen=8
        #
        self.accept("arrow_up", self.mover, [(0, -1)])
        self.accept("arrow_down", self.mover, [(0, 1)])
        self.accept("arrow_left", self.mover, [(-1, 0)])
        self.accept("arrow_right", self.mover, [(1, 0)])
        #
        self.sistema=Sistema()
        self.sistema.iniciar()
        #
        self._cargar_ui()
        self._ir_a_pos()
        
    def mover(self, delta_pos):
        paso=Tester.PasoDesplazamiento
        nueva_pos=(int(self.pos_foco[0]+delta_pos[0]*paso), int(self.pos_foco[1]+delta_pos[1]*paso))
        self.pos_foco=nueva_pos
        self.sistema.obtener_transicion_biomas(self.pos_foco, loguear=True)
        self._generar_imagen()

    def _generar_imagen(self):
        log.info("_generar_imagen")
        #
        info="pos_foco=%s"%(str(self.pos_foco))
        self.lblInfo["text"]=info
        #
        tamano=Tester.TamanoImagen
        if not self.imagen:
            self.imagen=PNMImage(tamano+1, tamano+1)
            self.texturaImagen=Texture()
            self.frmImagen["image"]=self.texturaImagen
            self.frmImagen["image_scale"]=0.75
        #
        zoom=self.zoom_imagen
        for x in range(tamano+1):
            for y in range(tamano+1):
                _x=self.pos_foco[0]+(x-tamano/2)*zoom
                _y=self.pos_foco[1]+(y-tamano/2)*zoom
                if x==(tamano/2.0) or y==(tamano/2.0):
                    self.imagen.setXel(x, y, 0)
                else:
                    if self.tipo_imagen==Tester.TipoImagenTopo:
                        a=self.sistema.obtener_altitud_suelo((_x, _y))
                        c=3*[int(255*a/Sistema.TopoAltura)]
                        if a>Sistema.TopoAltitudOceano:
                            self.imagen.setPixel(x, y, PNMImageHeader.PixelSpec(int(c[0]), int(c[1]), int(c[2]), 255))
                        else:
                            self.imagen.setPixel(x, y, PNMImageHeader.PixelSpec(0, 0, c[0], 255))
                    elif self.tipo_imagen==Tester.TipoImagenTerreno:
                        a=self.sistema.obtener_altitud_suelo((_x, _y))
                        terreno_base, terreno_superficie, factor_transicion=self.sistema.obtener_tipo_terreno((_x, _y))
                        color_base=Sistema.ColoresTipoTerreno[terreno_base]
                        color_superficie=Sistema.ColoresTipoTerreno[terreno_superficie]
                        c=(color_base*(1.0-factor_transicion))+(color_superficie*factor_transicion)
                        c[3]=1.0
                        if a>Sistema.TopoAltitudOceano:
                            self.imagen.setXelA(x, y, c/255)
                        else:
                            self.imagen.setXel(x, y, 0.0)
                    elif self.tipo_imagen==Tester.TipoImagenTemperaturaAM:
                        c=self.sistema.obtener_temperatura_anual_media_norm((_x, _y))
                        self.imagen.setXel(x, y, c)
                    elif self.tipo_imagen==Tester.TipoImagenTemperaturaPrecip:
                        c=self.sistema.obtener_precipitacion_frecuencia_anual((_x, _y))
                        self.imagen.setXel(x, y, c)
                    elif self.tipo_imagen==Tester.TipoImagenBioma:
                        a=self.sistema.obtener_altitud_suelo((_x, _y))
                        if a>Sistema.TopoAltitudOceano:
                            datos_biomas=self.sistema.obtener_transicion_biomas((_x, _y))
                            distancia_a, bioma_a=math.modf(datos_biomas[0])
                            distancia_b, bioma_b=math.modf(datos_biomas[1])
                            distancia_c, bioma_c=math.modf(datos_biomas[2])
                            distancia_d, bioma_d=math.modf(datos_biomas[3])
                            distancias=distancia_a+distancia_b+distancia_c+distancia_d
                            _c= (Sistema.ColoresBioma[bioma_a]*(1.0-distancia_a))+ \
                                (Sistema.ColoresBioma[bioma_b]*(1.0-distancia_b))+ \
                                (Sistema.ColoresBioma[bioma_c]*(1.0-distancia_c))+ \
                                (Sistema.ColoresBioma[bioma_d]*(1.0-distancia_d))
                            _c/=distancias
                            self.imagen.setXelA(x, y, _c/256)
                        else:
                            self.imagen.setXel(x, y, 0.0)
                    elif self.tipo_imagen==Tester.TipoImagenInterpTabla:
                        pos_columna=x/(tamano+1)
                        pos_fila=y/(tamano+1)
                        #
                        loguear=False
                        #if y==63:
                        #    loguear=True
                        data=self.sistema._calcular_transicion_tabla_biomas(pos_columna, pos_fila, loguear)
                        distancia_a, bioma_a=math.modf(data[0])
                        distancia_b, bioma_b=math.modf(data[1])
                        distancia_c, bioma_c=math.modf(data[2])
                        distancia_d, bioma_d=math.modf(data[3])
                        color_a=Sistema.ColoresBioma[bioma_a]
                        color_b=Sistema.ColoresBioma[bioma_b]
                        color_c=Sistema.ColoresBioma[bioma_c]
                        color_d=Sistema.ColoresBioma[bioma_d]
                        distancia_a=1.0-distancia_a
                        distancia_b=1.0-distancia_b
                        distancia_c=1.0-distancia_c
                        distancia_d=1.0-distancia_d
                        distancias=distancia_a+distancia_b+distancia_c+distancia_d
                        color=(color_a*distancia_a+color_b*distancia_b+color_c*distancia_c+color_d*distancia_d)/256
                        #if y==63:
                        #    print("(x,y)=(%s) pos=(%s) d=(%s) c=(%s)"%(str((x, y)), str((pos_columna, pos_fila)), str((distancia_a, distancia_b, distancia_c, distancia_d)), str((color_a, color_b, color_c, color_d))))
                        color/=distancias
                        self.imagen.setXel(x, y, color[0], color[1], color[2])
        #self.imagen.write("sistema.png")
        #
        self.texturaImagen.load(self.imagen)

    def _ir_a_pos(self):
        txt_x=self.entry_x.get()
        txt_y=self.entry_y.get()
        if txt_x=="":
            txt_x="0"
        if txt_y=="":
            txt_y="0"
        x, y=0, 0
        try:
            x=int(txt_x)
            y=int(txt_y)
        except Exception as e:
            log.exception(str(e))
        log.info("_ir_a_pos (%.3f,%.3f)"%(x, y))
        self.sistema.obtener_transicion_biomas((x, y), loguear=True)
        self.pos_foco=(x, y)
        self._generar_imagen()

    def _cargar_ui(self):
        # frame root
        self.frame=DirectFrame(parent=self.aspect2d, pos=(0, 0, 0), frameSize=(-1, 1, -1, 1), frameColor=(1, 1, 1, 0.5))
        # frame imagen
        self.frmImagen=DirectFrame(parent=self.frame, pos=(0.0, 0.0, 0.25), frameSize=(-0.75, 0.75, -0.75, 0.75))
        # frame controles
        self.frmControles=DirectFrame(parent=self.frame, pos=(0.0, 0.0, -0.75), frameSize=(-1, 1, -0.225, 0.225), frameColor=(1, 1, 1, 0.5))
        # info
        self.lblInfo=DirectLabel(parent=self.frmControles, pos=(-1, 0, 0.125), scale=0.05, text="info terreno?", frameColor=(0.5, 1, 1, 0.2), frameSize=(0, 40, -2, 2), text_align=TextNode.ALeft, text_pos=(0, 1, 0))
        # idx_pos
        DirectLabel(parent=self.frmControles, pos=(-1, 0, -0.05), scale=0.05, text="idx_pos_x", frameColor=(1, 1, 1, 0), frameSize=(0, 2, -1, 1), text_align=TextNode.ALeft)
        DirectLabel(parent=self.frmControles, pos=(-1, 0, -0.15), scale=0.05, text="idx_pos_y", frameColor=(1, 1, 1, 0), frameSize=(0, 2, -1, 1), text_align=TextNode.ALeft)
        self.entry_x=DirectEntry(parent=self.frmControles, pos=(-0.7, 0, -0.05), scale=0.05)
        self.entry_y=DirectEntry(parent=self.frmControles, pos=(-0.7, 0, -0.15), scale=0.05)
        DirectButton(parent=self.frmControles, pos=(0, 0, -0.05), scale=0.075, text="actualizar", command=self._ir_a_pos)
        DirectButton(parent=self.frmControles, pos=(-0.05, 0, -0.15), scale=0.075, text="acercar", command=self._acercar_zoom_imagen, frameSize=(-1.5, 1.5, -0.60, 0.60), text_scale=0.75)
        DirectButton(parent=self.frmControles, pos=(0.20, 0, -0.15), scale=0.075, text="alejar", command=self._alejar_zoom_imagen, frameSize=(-1.5, 1.5, -0.60, 0.60), text_scale=0.75)
        DirectButton(parent=self.frmControles, pos=(0.475, 0, -0.15), scale=0.075, text="alejar max", command=self._alejar_zoom_imagen_max, frameSize=(-2.0, 2.0, -0.60, 0.60), text_scale=0.75)
        DirectButton(parent=self.frmControles, pos=(0.75, 0, -0.15), scale=0.075, text="cambiar", command=self._cambiar_tipo_imagen, frameSize=(-1.5, 1.5, -0.60, 0.60), text_scale=0.75)

    def _cambiar_tipo_imagen(self):
        self.tipo_imagen=(self.tipo_imagen+1)%6
        self._generar_imagen()

    def _click_imagen(self, *args):
        log.info("_click_imagen %s"%str(args))

    def _acercar_zoom_imagen(self):
        log.info("_acercar_zoom_imagen")
        self.zoom_imagen-=4
        if self.zoom_imagen<1:
            self.zoom_imagen=1
        self._generar_imagen()

    def _alejar_zoom_imagen(self):
        log.info("_alejar_zoom_imagen")
        self.zoom_imagen+=4
        if self.zoom_imagen>512:
            self.zoom_imagen=512
        self._generar_imagen()

    def _alejar_zoom_imagen_max(self):
        log.info("_alejar_zoom_imagen_max")
        self.zoom_imagen=128+32
        self._generar_imagen()

#
if __name__=="__main__":
    logging.basicConfig(level=logging.DEBUG)
    PStatClient.connect()
    tester=Tester()
    tester.run()

