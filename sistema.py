from panda3d.core import *
import math, random
import datetime
import sqlite3
import csv
import pickle

import config

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

    # cache
    DirectorioCache="sistema"

    # db
    NombreArchivoDB="objetos.sql"
    NombreArchivoLlenadoDB="objetos.csv"
    SqlCreacionDB="""
    DROP TABLE IF EXISTS objetos;
    CREATE TABLE objetos (_id INTEGER PRIMARY KEY, 
                          ambiente INTEGER, 
                          tipo INTEGER, 
                          densidad FLOAT, 
                          radio_inferior FLOAT, 
                          radio_superior FLOAT, 
                          terreno INTEGER,
                          temperatura_minima FLOAT, 
                          temperatura_maxima FLOAT, 
                          precipitacion_minima FLOAT, 
                          precipitacion_maxima FLOAT, 
                          nombre_archivo VARCHAR(32)
                         );
    """
    
    # topografia
    TopoTamanoParcela=32
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
    TerrenoPerlinNoiseParams=(64.0, 1069) # (escala, semilla)
    TerrenoTipoNulo=0
    TerrenoTipoNieve=1 # alpha=1.0 (tope)
    TerrenoTipoTundra=2 # alpha=0.0 (fondo)
    TerrenoTipoTierraSeca=3 # alpha=0.4
    TerrenoTipoTierraHumeda=4 # alpha=0.5
    TerrenoTipoPastoSeco=5 # alpha=0.6
    TerrenoTipoPastoHumedo=6 # alpha=0.7
    TerrenoTipoArenaSeca=7 # alpha=0.8
    TerrenoTipoArenaHumeda=8 # alpha=0.9
    TerrenoTiposTabla=[[(2, 2), (2, 3), (7, 7), (7, 7)], 
                       [(2, 1), (3, 1), (3, 5), (3, 5)], 
                       [(2, 1), (4, 6), (4, 6), (4, 6)]
                       ]
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
    BiomaTabla=[[BiomaDesiertoPolar, BiomaTundra, BiomaDesierto,           BiomaDesierto],  \
                [BiomaDesiertoPolar, BiomaTundra, BiomaBosqueMediterraneo, BiomaSavannah],  \
                [BiomaDesiertoPolar, BiomaTaiga,  BiomaBosqueCaducifolio,  BiomaSelva] \
                ] # tabla(temperatura_anual_media,precipitacion_frecuencia). Se repiten en los bordes para facilitar calculos.
    # objetos
    ObjetoTipoNulo=0
    ObjetoTipoArbol=1
    ObjetoTipoArbusto=2
    ObjetoTipoPlanta=3
    ObjetoTipoYuyo=4
    ObjetoTipoRocaPequena=5
    ObjetoTipoRocaMediana=6
    ObjetoTipoRocaGrande=7
    ObjetosNoiseParams=(32.0, 345) # (escala, semilla)
    ObjetosRadioMaximoInferior=1
    ObjetosRadioMaximoSuperior=3

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
        self.db=None
        self.ruido_topo=None
        self.ruido_islas=None
        self.ruido_terreno=None
        self.ruido_temperatura=None
        self.ruido_precipitacion=None
        self.ruido_nubosidad=None
        self.ruido_objetos=None
        # parametros:
        self.posicion_cursor=Vec3(0, 0, 0)
        self.radio_expansion_parcelas=2
        self.duracion_dia_segundos=0.0
        self.ano=0
        self.dia=0
        # variables externas:
        self.idx_pos_parcela_actual=None
        self.parcelas=dict() # {idx_pos:DatosParcela,...}
        self.directorio_general_cache="cache"
        self.directorio_cache=os.path.join(self.directorio_general_cache, "sistema")
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
        idx_pos=self.obtener_indice_parcela(self.posicion_cursor)
        bioma=self.obtener_bioma_transicion(self.posicion_cursor)
        info="Sistema posicion_cursor=(%.3f,%.3f,%.3f) idx_pos=(%i,%i)\n"%(self.posicion_cursor[0], self.posicion_cursor[1], self.posicion_cursor[2], idx_pos[0], idx_pos[1])
        info+="era: año=%i estacion=%i dia=%i hora=%.2f(%.2f/%i) periodo_dia_actual=%i\n"%(self.ano, self.estacion, self.dia, self.hora_normalizada, self._segundos_transcurridos_dia, self.duracion_dia_segundos, self.periodo_dia_actual)
        info+="temp=%.2f nubosidad=%.2f precipitacion=[tipo=%i intens=%i t=(%.2f/%2.f)] bioma=(%s) "%(self.temperatura_actual_norm, self.nubosidad, self.precipitacion_actual_tipo, self.precipitacion_actual_intensidad, self.precipitacion_actual_t, self.precipitacion_actual_duracion, str(bioma))
        if idx_pos in self.parcelas:
            x_parcela=int(self.posicion_cursor[0]%Sistema.TopoTamanoParcela)
            y_parcela=int(self.posicion_cursor[1]%Sistema.TopoTamanoParcela)
            datos_parcela=self.parcelas[idx_pos]
            loc=datos_parcela[x_parcela][y_parcela]
            info+=str(loc)
        return info

    def cargar_parametros_iniciales(self, defecto=True):
        #
        if defecto:
            log.info("cargar_parametros_iniciales por defecto")
            # parametros:
            _pos_inicial_cursor=[float(n) for n in config.vallist("sistema.pos_cursor_inicial")]
            self.posicion_cursor=Vec3(_pos_inicial_cursor[0], _pos_inicial_cursor[1], 0)
            self.radio_expansion_parcelas=int(config.val("sistema.radio_expansion_parcelas"))
            self.duracion_dia_segundos=3600.0 * 24
            self.ano=0
            self.dia=0
            ahora=datetime.datetime.now()
            ahora_hn=self.calcular_hora_normalizada(ahora.hour, ahora.minute, ahora.second)
            #ahora_hn=0.65
            self._segundos_transcurridos_dia=ahora_hn*self.duracion_dia_segundos
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
        # directorio general de cache
        self.directorio_general_cache=config.val("sistema.dir_cache")
        if not os.path.exists(self.directorio_general_cache):
            log.warning("se crea directorio_general_cache: %s"%self.directorio_general_cache)
            os.mkdir(self.directorio_general_cache)
        # directorio de cache de datos de sistema
        if not os.path.exists(self.directorio_cache):
            log.warning("se crea directorio_cache: %s"%self.directorio_cache)
            os.mkdir(self.directorio_cache)
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
        # db
        self._iniciar_db()
        #
        self.update(0.0, self.posicion_cursor)
        
    def terminar(self):
        log.info("terminar")
        #
        self._terminar_db()
    
    def update(self, dt, posicion_cursor):
        #
        self.posicion_cursor=posicion_cursor
        self.posicion_cursor[2]=self.obtener_altitud_suelo_datos_parcela(posicion_cursor) # poco eficiente?
        #
        self._establecer_fecha_hora_estacion(dt)
        self._establecer_temperatura_actual_norm(dt)
        self._establecer_precipitacion(dt)
        #
        _idx_pos_parcela_actual=self.obtener_indice_parcela(self.posicion_cursor)
        if _idx_pos_parcela_actual!=self.idx_pos_parcela_actual:
            self.idx_pos_parcela_actual=_idx_pos_parcela_actual
            self._establecer_datos_parcelas_rango(self.posicion_cursor, self.idx_pos_parcela_actual)

##    def obtener_descriptor_locacion(self, posicion): # ELIMINAR
#        altitud_suelo=self.obtener_altitud_suelo(posicion)
#        desc=DescriptorLocacion((posicion[0], posicion[1], altitud_suelo))
#        desc.altitud_tope=self.obtener_altitud_tope(posicion)
#        desc.ambiente=self.obtener_ambiente(posicion)
#        desc.latitud=self.obtener_latitud(posicion)
#        desc.tipo_terreno=self.obtener_tipo_terreno(posicion)
#        self.precipitacion_frecuencia=self.obtener_precipitacion_frecuencia_anual(posicion)
#        self.inclinacion_solar_anual_media=None
#        self.vegetacion=None
#        self.roca=None
#        return desc
    
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
            altura_sobre_agua_n=altura_sobre_agua/(Sistema.TopoAlturaSobreOceano)
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
        return altitud #Sistema.TopoAltitudOceano+0.05

    def obtener_altitud_suelo_cursor(self):
        return self.obtener_altitud_suelo(self.posicion_cursor)

    def obtener_altitud_suelo_datos_parcela(self, posicion, idx_pos=None):
        altitud=0.0
        _idx_pos=idx_pos if idx_pos!=None else self.obtener_indice_parcela(posicion)
        if _idx_pos in self.parcelas:
            datos_parcela=self.parcelas[_idx_pos]
            x=int(posicion[0]%Sistema.TopoTamanoParcela) # o %datos_parcela.tamano)?
            y=int(posicion[1]%Sistema.TopoTamanoParcela)
            loc=datos_parcela.datos[x][y]
            altitud=loc.posicion[2]
        else:
            altitud=self.obtener_altitud_suelo(posicion)
        return altitud
        
    def obtener_altitud_tope(self, posicion):
        # a implementar para grillas 3D, con cuevas, etc...
        return 5.0*Sistema.TopoAltura

    def obtener_altitud_suelo_supra_oceanica_norm(self, posicion, altitud_suelo=None):
        altitud=self.obtener_altitud_suelo(posicion) if altitud_suelo==None else altitud_suelo
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

    def obtener_ambiente(self, posicion, altitud_suelo=None):
        altitud=self.obtener_altitud_suelo(posicion) if altitud_suelo==None else altitud_suelo
        if posicion[2]<(Sistema.TopoAltitudOceano-0.5):
            return Sistema.AmbienteAgua
        elif abs(posicion[2]-altitud)<0.1:
            return Sistema.AmbienteSuelo
        elif (posicion[2]-altitud)>=0.1:
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

    def obtener_temperatura_anual_media_norm(self, posicion, altitud_suelo=None):
        #print("obtener_temperatura_anual_media_norm (%.2f,%.2f)"%(posicion[0], posicion[1]))
        altitud_normalizada=self.obtener_altitud_suelo_supra_oceanica_norm(posicion, altitud_suelo)
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
        temperatura_grados=(temperatura_normalizada-0.5)*2.0*40.0 # 50
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

    def obtener_bioma_transicion(self, posicion, loguear=False):
        temperatura_anual_media=self.obtener_temperatura_anual_media_norm(posicion)
        precipitacion_frecuencia=self.obtener_precipitacion_frecuencia_anual(posicion)
        idx_tabla_0, idx_tabla_1, factor_transicion, dist_0=self._calcular_transicion_tabla_biomas(temperatura_anual_media, precipitacion_frecuencia, loguear)
        if loguear:
            log.debug("obtener_bioma_transicion idx_tabla_0=%s idx_tabla_1=%s factor_transicion=%.3f"%(str(idx_tabla_0), str(idx_tabla_1), factor_transicion))
        bioma0=Sistema.BiomaTabla[int(idx_tabla_0[1])][int(idx_tabla_0[0])]
        bioma1=Sistema.BiomaTabla[int(idx_tabla_1[1])][int(idx_tabla_1[0])]
        return (bioma0, bioma1, factor_transicion)

    def obtener_tipo_terreno(self, posicion, loguear=False):
        temperatura_anual_media=self.obtener_temperatura_anual_media_norm(posicion)
        precipitacion_frecuencia=self.obtener_precipitacion_frecuencia_anual(posicion)
        idx_tabla_0, idx_tabla_1, factor_transicion, dist_0=self._calcular_transicion_tabla_biomas(temperatura_anual_media, precipitacion_frecuencia, loguear)
        #
        tipos0=Sistema.TerrenoTiposTabla[int(idx_tabla_0[1])][int(idx_tabla_0[0])]
        tipos1=Sistema.TerrenoTiposTabla[int(idx_tabla_1[1])][int(idx_tabla_1[0])]
        #
        tipo0=tipos0[0]
        tipo1=tipos1[0]
        ruido_terreno=self.calcular_ruido_continuo(self.ruido_terreno, posicion[0], posicion[1])*2.0-1.0
        if max(0, min(1, (0.2+dist_0-(ruido_terreno))))>0.4:
            tipo0=tipos0[1]
        if max(0, min(1, (0.2+dist_0-(ruido_terreno))))>0.4:
            tipo1=tipos1[1]
        #
        factor_transicion=max(0, min(1, (factor_transicion+ruido_terreno)))
        #
        if loguear:
            log.debug("obtener_tipo_terreno idx_tabla_0=%s idx_tabla_1=%s ft=%.3f dist_0=%.3f"%(str(idx_tabla_0), str(idx_tabla_1), factor_transicion, dist_0))
        return (tipo0, tipo1, factor_transicion)

    def _calcular_transicion_tabla_biomas(self, temperatura_anual_media, precipitacion_frecuencia, loguear=False):
        #
        fract_x, entero_x=math.modf(temperatura_anual_media*3)#(((temperatura_anual_media-0.2)/0.8)*3)
        fract_y, entero_y=math.modf(precipitacion_frecuencia*2)
        fract_x_rnd=round(fract_x)
        fract_y_rnd=round(fract_y)
        idx_tabla_0=[entero_x+fract_x_rnd, entero_y+fract_y_rnd]
        idx_tabla_1=idx_tabla_0
        dist_x, dist_y=abs(fract_x-fract_x_rnd), abs(fract_y-fract_y_rnd)
        dist_0=0.0
        if dist_x>dist_y:
            fract_x_rnd_op=(fract_x_rnd+1)%2
            idx_tabla_1=[entero_x+fract_x_rnd_op, entero_y+fract_y_rnd]
            dist_0=dist_x
        else:
            fract_y_rnd_op=(fract_y_rnd+1)%2
            idx_tabla_1=[entero_x+fract_x_rnd, entero_y+fract_y_rnd_op]
            dist_0=dist_y
        #
        factor_transicion=0.0
        if dist_0>0.45:
            factor_transicion=(dist_0-0.45)/((0.50-0.45)*2.0)
        #
        if loguear:
            log.debug("_calcular_transicion_tabla_biomas idx_tabla_0=%s idx_tabla_1=%s factor_transicion=%.3f"%(str(idx_tabla_0), str(idx_tabla_1), factor_transicion))
        return (idx_tabla_0, idx_tabla_1, factor_transicion, dist_0)

    def calcular_color_bioma_debug(self, posicion=None):
        _posicion=posicion
        if not _posicion:
            _posicion=self.posicion_cursor
        bioma0, bioma1, factor_transicion=self.obtener_bioma_transicion(_posicion)
        color0=Sistema.ColoresBioma[bioma0]
        color1=Sistema.ColoresBioma[bioma1]
        color=(color0*(1.0-factor_transicion))+(color1*(factor_transicion))
        color/=256
        color=Vec4(color[0], color[1], color[2], 1.0)
        return color

    def calcular_color_terreno_debug(self, posicion=None):
        _posicion=posicion
        if not _posicion:
            _posicion=self.posicion_cursor
        tipo0, tipo1, factor_transicion=self.obtener_tipo_terreno(_posicion)
        color0=Sistema.ColoresTipoTerreno[tipo0]
        color1=Sistema.ColoresTipoTerreno[tipo1]
        color=(color0*(1.0-factor_transicion))+(color1*factor_transicion)
        color/=256
        color=Vec4(color[0], color[1], color[2], 1.0)
        return color

    def calcular_ruido_continuo(self, ruido, x, y, tamano=32, rango=512):
        _x=(x%tamano)*rango/tamano
        _y=(y%tamano)*rango/tamano
        c00=ruido(_x,                 _y               )
        c10=ruido((_x+rango)        , _y               )
        c01=ruido(_x,                (_y+rango)        )
        c11=ruido((_x+rango)        ,(_y+rango)        )
        mix_x, mix_y=1.0-_x/rango, 1.0-_y/rango
        if mix_x<0.0 or mix_y<0.0 or mix_x>1.0 or mix_y>1.0:
            print("error mix_x,mix_y fuera de limites [0.0,1.0]")
        interp_x0=(c00*(1.0-mix_x))+(c10*mix_x)
        interp_x1=(c01*(1.0-mix_x))+(c11*mix_x)
        interp_y=(interp_x0*(1.0-mix_y))+(interp_x1*mix_y)
        interp_y=interp_y*0.5+0.5
        interp_y=interp_y if interp_y<1.0 else 1.0
        interp_y=interp_y if interp_y>0.0 else 0.0
        valor=interp_y
        if valor<0.0 or valor>1.0:
            print("error valor fuera de limites [0.0,1.0]")
        return valor

    def obtener_descriptor_vegetacion(self, posicion, solo_existencia=False):
        pass

    def obtener_momento_era(self):
        momento=self.ano*Sistema.DiasDelAno+self.dia+self.hora_normalizada
        return momento

    def obtener_indice_parcela(self, posicion): # ineficiente?
        x=posicion[0]/Sistema.TopoTamanoParcela
        y=posicion[1]/Sistema.TopoTamanoParcela
        if x<0.0: x=math.floor(x)
        if y<0.0: y=math.floor(y)
        return (int(x), int(y))
    
    def obtener_pos_parcela(self, idx_pos):
        x=idx_pos[0]*Sistema.TopoTamanoParcela
        y=idx_pos[1]*Sistema.TopoTamanoParcela
        return (x, y, 0.0)

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
        self.ruido_terreno=StackedPerlinNoise2(_escala, _escala, 6, 2, 0.5, 256, _semilla)
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
        _escala=Sistema.ObjetosNoiseParams[0]
        _semilla=Sistema.ObjetosNoiseParams[1]
        self.ruido_objetos=PerlinNoise2(_escala, _escala, 256, _semilla)
        
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

    def calcular_hora_normalizada(self, hora, minutos, segundos):
        hn=(segundos + 60.0 * minutos + 3600.0 * hora)/86400
        hn+=0.2
        if hn>1.0:
            hn-=1.0
        return hn

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

    def _establecer_datos_parcelas_rango(self, pos, idx_pos):
        log.info("_establecer_datos_parcelas_rango idx_pos=%s"%(str(idx_pos)))
        #
        r=self.radio_expansion_parcelas
        #
        idxs_necesarios=list()
        idxs_a_cargar=list()
        idxs_a_descargar=list()
        for x in range(2*r+1):
            for y in range(2*r+1):
                idx=(idx_pos[0]+x-r, idx_pos[1]+y-r)
                idxs_necesarios.append(idx)
        for idx in idxs_necesarios:
            if idx not in self.parcelas:
                idxs_a_cargar.append(idx)
        for idx in self.parcelas:
            if idx not in idxs_necesarios:
                idxs_a_descargar.append(idx)
        #
        for idx in idxs_a_cargar:
            ruta_archivo_cache=os.path.join(self.directorio_cache, "parcela_%i_%i.bin"%(idx[0], idx[1]))
            datos_parcela=None
            if os.path.exists(ruta_archivo_cache):
                log.info("cargar desde cache <- %s"%ruta_archivo_cache)
                with open(ruta_archivo_cache, "rb") as arch:
                    datos_parcela=pickle.load(arch)
                    self.parcelas[idx]=datos_parcela
            else:
                log.info("cargar por primera vez -> %s"%ruta_archivo_cache)
                # datos primarios
                datos_parcela=self._generar_datos_primarios_parcela(idx)
                self.parcelas[idx]=datos_parcela
                # datos secundarios
                gend_terreno=GeneradorDatosTerreno(self)
                gend_terreno.generar(idx)
                #
                gend_objetos=GeneradorDatosObjeto(self)
                gend_objetos.generar(idx)
                #
                with open(ruta_archivo_cache, "wb") as arch:
                    pickle.dump(datos_parcela, arch)
        for idx in idxs_a_descargar:
            self._remover_datos_parcela(idx)

    def _generar_datos_primarios_parcela(self, idx_pos):
        log.info("_generar_datos_primarios_parcela idx_pos=%s"%(str(idx_pos)))
        posicion=self.obtener_pos_parcela(idx_pos)
        tamano=Sistema.TopoTamanoParcela+1
        datos_parcela=DatosParcela(tamano)
        # datos generales
        for x in range(tamano):
            for y in range(tamano):
                # determinar posicion
                _posicion=Vec3(posicion[0]+x, posicion[1]+y, 0)
                altitud_suelo=self.obtener_altitud_suelo(_posicion)
                _posicion[2]=altitud_suelo
                # datos generales
                loc=DescriptorLocacion(_posicion, x, y)
                loc.ambiente=self.obtener_ambiente(_posicion, altitud_suelo)
                loc.latitud=self.obtener_latitud(_posicion)
                loc.tipo_terreno=self.obtener_tipo_terreno(_posicion)
                loc.temperatura_anual_media=self.obtener_temperatura_anual_media_norm(_posicion)
                loc.precipitacion_frecuencia=self.obtener_precipitacion_frecuencia_anual(_posicion)
                #
                loc.generar_deltas()
                #
                datos_parcela.datos[x][y]=loc
        return datos_parcela

    def _remover_datos_parcela(self, idx_pos):
        log.info("_remover_datos_parcela idx_pos=%s"%(str(idx_pos)))
        self.parcelas[idx_pos]=None
        del self.parcelas[idx_pos]

    def _iniciar_db(self):
        log.info("_iniciar_db")
        #
        if self.db!=None:
            log.warning("base de datos ya iniciada")
            return
        #
        if os.path.exists(Sistema.NombreArchivoDB):
            log.warning("se elimina el archivo de base de datos %s"%Sistema.NombreArchivoDB)
            os.remove(Sistema.NombreArchivoDB)
        #
        if not os.path.exists(Sistema.NombreArchivoDB):
            if not os.path.exists(Sistema.NombreArchivoLlenadoDB):
                raise Exception("no se encuentra el archivo %s"%Sistema.NombreArchivoLlenadoDB)
            #
            log.info("crear base de datos en archivo %s"%Sistema.NombreArchivoDB)
            con=sqlite3.connect(Sistema.NombreArchivoDB)
            con.executescript(Sistema.SqlCreacionDB)
            con.commit()
            #
            log.info("abrir archivo %s"%Sistema.NombreArchivoLlenadoDB)
            with open(Sistema.NombreArchivoLlenadoDB, "r") as archivo_csv:
                lector_csv=csv.DictReader(archivo_csv)
                for fila in lector_csv:
                    sql="INSERT INTO %s (ambiente,tipo,densidad,radio_inferior,radio_superior,terreno,temperatura_minima,temperatura_maxima,precipitacion_minima,precipitacion_maxima,nombre_archivo) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,'%s')" \
                       %(fila["tabla"], fila["ambiente"], fila["tipo"], fila["densidad"], \
                         fila["radio_inferior"], fila["radio_superior"], fila["terreno"], fila["temperatura_minima"], \
                         fila["temperatura_maxima"], fila["precipitacion_minima"], fila["precipitacion_maxima"], \
                         fila["nombre_archivo"])
                    con.execute(sql)
            con.commit()
            con.close()
            log.info("base de datos creada con exito")
            #
        #
        log.info("abrir db %s"%Sistema.NombreArchivoDB)
        self.db=sqlite3.connect(Sistema.NombreArchivoDB)
        log.info("conexion de datos establecida")

    def _terminar_db(self):
        log.info("_terminar_db")
        if self.db==None:
            log.warning("base de datos no iniciada")
            return
        self.db.close()
        self.db=None

#
#
# DatosParcela
#
#
class DatosParcela:
    
    def __init__(self, tamano):
        self.datos=list() # [x][y]->[[DescriptorLocacion,...], ...]
        self.tamano=tamano
        for x in range(tamano):
            self.datos.append(list())
            for y in range(tamano):
                self.datos[x].append(None)

    def __getitem__(self, idx):
        return self.datos[idx]
    
#
#
# DescriptorLocacion
#
#
class DescriptorLocacion:
    
    def __init__(self, posicion, x_parcela, y_parcela):
        # primarios:
        self.posicion=posicion
        self.posicion_rel_parcela=Vec3(x_parcela, y_parcela, posicion[2])
        self.altitud_tope=None # para implementar cuevas?
        self.ambiente=None
        self.latitud=None
        self.tipo_terreno=None
        self.temperatura_anual_media=None
        self.precipitacion_frecuencia=None
        # secundarios:
        # terreno
        self.normal=Vec3(0, 0, 1)
        self.tangente=Vec3(0, 1, 0)
        self.texcoord=Vec2(0, 0)
        # objetos
        self.factor_ruido=0.0
        self.datos_objeto=None
        self.delta_pos=Vec3(0.0, 0.0, 0.0)
        self.delta_hpr=Vec3(0.0, 0.0, 0.0)
        self.delta_scl=Vec3(0.0, 0.0, 0.0)
    
    def generar_deltas(self):
        self.delta_pos.setX(0.75*(random.random()*2.0-1.0))
        self.delta_pos.setY(0.75*(random.random()*2.0-1.0))
        self.delta_hpr.setX(180.0*(random.random()*2.0-1.0))
        self.delta_hpr.setY(3.50*(random.random()*2.0-1.0))
        self.delta_scl.setX(0.85+0.15*random.random())
        self.delta_scl.setY(0.85+0.15*random.random())
        self.delta_scl.setZ(0.75+0.25*random.random())

    def __str__(self):
        texto ="\nDescriptorLocacion(%.2f,%.2f,%.2f)|(%.2f,%.2f,%.2f):\n"
        texto+="    amb=%i ztop=%s lat=%2.f tam=%.2f prec_f=%.2f tterr=%s\n"
        texto+="    n,t,tc=%s %s %s\n"
        texto+="    o=%s\n"
        texto+="    fr=%.2f dp=%s dr=%s ds=%s\n"
        return texto%(self.posicion[0], self.posicion[1], self.posicion[2], self.posicion_rel_parcela[0], self.posicion_rel_parcela[1], self.posicion_rel_parcela[2], \
                      self.ambiente, self.altitud_tope, self.latitud, self.temperatura_anual_media, self.precipitacion_frecuencia, self.tipo_terreno,  \
                      self.normal, self.tangente, self.texcoord,  \
                      str(self.datos_objeto), self.factor_ruido, str(self.delta_pos), str(self.delta_hpr), str(self.delta_scl))

#
#
# GeneradorDatosTerreno
#
#
class GeneradorDatosTerreno:
    
    def __init__(self, sistema):
        self.sistema=sistema
    
    def generar(self, idx_pos):
        #
        datos_parcela=self.sistema.parcelas[idx_pos]
        tc_x, tc_y=0.0, 0.0
        frac_tc=1/datos_parcela.tamano # o /Sistema.TopoTamanoParcela?
        for x in range(datos_parcela.tamano):
            if x==1: # 1, en vez de 0?
                tc_x=0.0
            else:
                tc_x=x*frac_tc
            for y in range(datos_parcela.tamano):
                if y==1: # 1, en vez de 0?
                    tc_y=0.0
                else:
                    tc_y=y*frac_tc
                loc=datos_parcela.datos[x][y]
                # posicion
                _x, _y=loc.posicion[0], loc.posicion[1]
                # normal
                v0=loc.posicion # [x][y]
                v1=Vec3(_x+1, _y  , self.sistema.obtener_altitud_suelo_datos_parcela((_x+1, _y  )))
                v2=Vec3(_x,   _y+1, self.sistema.obtener_altitud_suelo_datos_parcela((_x  , _y+1)))
                v3=Vec3(_x+1, _y-1, self.sistema.obtener_altitud_suelo_datos_parcela((_x+1, _y-1)))
                v4=Vec3(_x-1, _y+1, self.sistema.obtener_altitud_suelo_datos_parcela((_x-1, _y+1)))
                v5=Vec3(_x-1, _y  , self.sistema.obtener_altitud_suelo_datos_parcela((_x-1, _y  )))
                v6=Vec3(_x  , _y-1, self.sistema.obtener_altitud_suelo_datos_parcela((_x  , _y-1)))
                tc0=Vec2(tc_x        , tc_y        )
                tc1=Vec2(tc_x+frac_tc, tc_y        )
                tc2=Vec2(tc_x        , tc_y+frac_tc)
                tc3=Vec2(tc_x+frac_tc, tc_y-frac_tc)
                tc4=Vec2(tc_x-frac_tc, tc_y+frac_tc)
                tc5=Vec2(tc_x-frac_tc, tc_y        )
                tc6=Vec2(tc_x        , tc_y-frac_tc)
                n0=self._calcular_normal(v0, v1, v2)
                n1=self._calcular_normal(v0, v3, v1)
                n2=self._calcular_normal(v0, v2, v4)
                n3=self._calcular_normal(v0, v5, v6)
                n_avg=(n0+n1+n2+n3)/4.0
                t0=self._calcular_tangente(v0, v1, v2, tc0, tc1, tc2, n_avg)
                t1=self._calcular_tangente(v0, v3, v1, tc0, tc3, tc1, n_avg)
                t2=self._calcular_tangente(v0, v2, v4, tc0, tc2, tc4, n_avg)
                t3=self._calcular_tangente(v0, v5, v6, tc0, tc5, tc6, n_avg)
                t_avg=(t0+t1+t2+t3)/4.0
                #
                loc.normal=n_avg
                loc.tangente=t_avg
                loc.texcoord=tc0

    def _calcular_normal(self, v0, v1, v2):
        U=v1-v0
        V=v2-v0
        return U.cross(V)

    def _calcular_tangente(self, v0, v1, v2, tc0, tc1, tc2, n0):
        """
        Lengyel, Eric. “Computing Tangent Space Basis Vectors for an Arbitrary Mesh”. Terathon Software, 2001. http://terathon.com/code/tangent.html
        //
        struct Triangle
        {
            unsigned short  index[3];
        };
        void CalculateTangentArray(long vertexCount, const Point3D *vertex, const Vector3D *normal,
                const Point2D *texcoord, long triangleCount, const Triangle *triangle, Vector4D *tangent)
        {
            Vector3D *tan1 = new Vector3D[vertexCount * 2];
            Vector3D *tan2 = tan1 + vertexCount;
            ZeroMemory(tan1, vertexCount * sizeof(Vector3D) * 2);
            
            for (long a = 0; a < triangleCount; a++)
            {
                long i1 = triangle->index[0];
                long i2 = triangle->index[1];
                long i3 = triangle->index[2];
                
                const Point3D& v1 = vertex[i1];
                const Point3D& v2 = vertex[i2];
                const Point3D& v3 = vertex[i3];
                
                const Point2D& w1 = texcoord[i1];
                const Point2D& w2 = texcoord[i2];
                const Point2D& w3 = texcoord[i3];
                
                float x1 = v2.x - v1.x;
                float x2 = v3.x - v1.x;
                float y1 = v2.y - v1.y;
                float y2 = v3.y - v1.y;
                float z1 = v2.z - v1.z;
                float z2 = v3.z - v1.z;
                
                float s1 = w2.x - w1.x;
                float s2 = w3.x - w1.x;
                float t1 = w2.y - w1.y;
                float t2 = w3.y - w1.y;
                
                float r = 1.0F / (s1 * t2 - s2 * t1);
                Vector3D sdir((t2 * x1 - t1 * x2) * r, (t2 * y1 - t1 * y2) * r,
                        (t2 * z1 - t1 * z2) * r);
                Vector3D tdir((s1 * x2 - s2 * x1) * r, (s1 * y2 - s2 * y1) * r,
                        (s1 * z2 - s2 * z1) * r);
                
                tan1[i1] += sdir;
                tan1[i2] += sdir;
                tan1[i3] += sdir;
                
                tan2[i1] += tdir;
                tan2[i2] += tdir;
                tan2[i3] += tdir;
                
                triangle++;
            }
            
            for (long a = 0; a < vertexCount; a++)
            {
                const Vector3D& n = normal[a];
                const Vector3D& t = tan1[a];
                
                // Gram-Schmidt orthogonalize
                tangent[a] = (t - n * Dot(n, t)).Normalize();
                
                // Calculate handedness
                tangent[a].w = (Dot(Cross(n, t), tan2[a]) < 0.0F) ? -1.0F : 1.0F;
            }
            
            delete[] tan1;
        }
        """
        #
        x1=v1[0]-v0[0]
        x2=v2[0]-v0[0]
        y1=v1[1]-v0[1]
        y2=v2[1]-v0[1]
        z1=v1[2]-v0[2]
        z2=v2[2]-v0[2]
        #
        s1=tc1[0]-tc0[0]
        s2=tc2[0]-tc0[0]
        t1=tc1[1]-tc0[1]
        t2=tc2[1]-tc0[1]
        #
        r_div=(s1*t2-s2*t1)
        r=1.0/r_div if r_div>0.0 else 0.0
        sdir=Vec3((t2 * x1 - t1 * x2) * r, (t2 * y1 - t1 * y2) * r, (t2 * z1 - t1 * z2) * r);
        tdir=Vec3((s1 * x2 - s2 * x1) * r, (s1 * y2 - s2 * y1) * r, (s1 * z2 - s2 * z1) * r);
        tan1=sdir
        tan2=tdir
        #
        t=(tan1-n0*Vec3.dot(n0, tan1)).normalized()
        th=-1.0 if (Vec3.dot(Vec3.cross(n0, tan1), tan2)<0.0) else 1.0
        #bn=Vec3.cross(n0, t)*th
        return Vec4(t[0], t[1], t[2], th) #, bn.normalized())

#
#
# GeneradorDatosObjeto
#
#
class GeneradorDatosObjeto:
    
    def __init__(self, sistema):
        self.sistema=sistema
        self.ruido_perlin=PerlinNoise2(Sistema.ObjetosNoiseParams[0], Sistema.ObjetosNoiseParams[0], 256, Sistema.ObjetosNoiseParams[1])
    
    def generar(self, idx_pos):
        random.seed(Sistema.ObjetosNoiseParams[1])
        #
        cantidad_total_locaciones=Sistema.TopoTamanoParcela**2
        indexado_objetos=dict() # {ambiente:{tipo_terreno:GrupoObjetosLocaciones,...},...}
        ambientes=list() # para sql
        tipos_terreno=list() # para sql
        temperatura_minima, temperatura_maxima=1.0, 0.0 # para sql
        precipitacion_minima, precipitacion_maxima=1.0, 0.0 # para sql
        #
        datos_parcela=self.sistema.parcelas[idx_pos]
        #
        for x in range(datos_parcela.tamano):
            for y in range(datos_parcela.tamano):
                #
                loc=datos_parcela.datos[x][y]
                # ambiente
                if loc.ambiente not in ambientes:
                    ambientes.append(loc.ambiente)
                if loc.ambiente not in indexado_objetos.keys():
                    #log.debug("agregando indexado_objetos[%i]"%loc.ambiente)
                    indexado_objetos[loc.ambiente]=dict()
                # tipo terreno
                tipo_terreno0, tipo_terreno1, factor_transicion=loc.tipo_terreno
                tipo_terreno=tipo_terreno0 if factor_transicion<0.5 else tipo_terreno1
                if not tipo_terreno in tipos_terreno:
                    tipos_terreno.append(tipo_terreno)
                if not tipo_terreno in indexado_objetos[loc.ambiente]:
                    #log.debug("agregando indexado_objetos[%i][%i]"%(loc.ambiente, tipo_terreno))
                    indexado_objetos[loc.ambiente][tipo_terreno]=GrupoObjetosLocaciones(cantidad_total_locaciones)
                # temperatura anual media
                if loc.temperatura_anual_media<temperatura_minima:
                    temperatura_minima=loc.temperatura_anual_media
                if loc.temperatura_anual_media>temperatura_maxima:
                    temperatura_maxima=loc.temperatura_anual_media
                # precipitacion frecuencia anual
                if loc.precipitacion_frecuencia<precipitacion_minima:
                    precipitacion_minima=loc.precipitacion_frecuencia
                if loc.precipitacion_frecuencia>precipitacion_maxima:
                    precipitacion_maxima=loc.precipitacion_frecuencia
                #
                loc.factor_ruido=self.ruido_perlin(loc.posicion[0], loc.posicion[1])
                indexado_objetos[loc.ambiente][tipo_terreno].locaciones_disponibles.append(loc)
        # obtener tipos de objeto segun datos de terreno
        condicion_ambientes="(%s)"%(" OR ".join(["ambiente=%i"%amb for amb in ambientes]))
        condicion_tipos_terreno="(%s)"%(" OR ".join(["terreno=%i"%tipo for tipo in tipos_terreno]))
        condicion_temperatura=("(temperatura_minima<=%.2f AND temperatura_maxima>=%.2f)"%(temperatura_minima, temperatura_maxima))
        condicion_precipitacion=("(precipitacion_minima<=%.2f AND precipitacion_maxima>=%.2f)"%(precipitacion_minima, precipitacion_maxima))
        condiciones="%s AND %s AND %s AND %s"%(condicion_ambientes, condicion_tipos_terreno, condicion_temperatura, condicion_precipitacion)
        sql="SELECT * FROM objetos WHERE %(condiciones)s ORDER BY radio_superior DESC, densidad ASC"%{"condiciones":condiciones}
        try:
            db_cursor=self.sistema.db.execute(sql)
        except Exception as e:
            log.exception(str(e)) # !!!
            return list()
        filas_tipos_objeto=db_cursor.fetchall()
        # distribuir los tipos de objeto segun datos de terreno
        for fila in filas_tipos_objeto:
            ambiente=fila[1]
            tipo_terreno=fila[6]
            #log.debug("solicitar indexado_objetos[%i][%i]"%(ambiente, tipo_terreno))
            try:
                grupo_objetos_locaciones=indexado_objetos[ambiente][tipo_terreno]
                grupo_objetos_locaciones.tipos_objeto.append(fila)
            except Exception as e:
                log.exception("tipo_objeto no posicionable en indexado_objetos[%i][%i] %s Mensaje: %s"%(ambiente, tipo_terreno, str(fila), str(e)))
                pass
        # recolectar grupos_objetos_locaciones
        grupos_objetos_locaciones=list()
        for ambiente in sorted(indexado_objetos.keys()):
            for tipo_terreno in sorted(indexado_objetos[ambiente].keys()):
                grupo_objetos_locaciones=indexado_objetos[ambiente][tipo_terreno]
                if len(grupo_objetos_locaciones.tipos_objeto)==0:
                    continue
                grupos_objetos_locaciones.append(grupo_objetos_locaciones)
        # realizar operaciones pertinentes sobre grupos_objetos_locaciones
        for grupo_objetos_locaciones in grupos_objetos_locaciones:
            grupo_objetos_locaciones.ordenar_locaciones_disponibles()
            grupo_objetos_locaciones.determinar_cantidades_tipos_objeto()
            #log.debug(str(grupo_objetos_locaciones))
            for tipo_objeto in grupo_objetos_locaciones.tipos_objeto:
                cant_obj_remanentes=grupo_objetos_locaciones.cantidades_tipos_objeto[tipo_objeto[2]]
                #log.debug("colocar %i objetos '%s' en ambiente=%i y tipo_terreno=%i"%(cant_obj_remanentes, tipo_objeto[11], tipo_objeto[1], tipo_objeto[6]))
                for loc in grupo_objetos_locaciones.locaciones_disponibles:
                    if cant_obj_remanentes>0 and \
                       self._chequear_espacio_disponible(loc.posicion_rel_parcela, tipo_objeto[4], tipo_objeto[5], datos_parcela):
                        cant_obj_remanentes-=1
                        loc.datos_objeto=tipo_objeto

    def _obtener_vecino(self, datos_parcela, posicion_rel_parcela, dx, dy):
        if (posicion_rel_parcela[0]==0 and dx<0) or \
           (posicion_rel_parcela[0]==(len(datos_parcela.datos[0])-1) and dx>0) or \
           (posicion_rel_parcela[1]==0 and dy<0) or \
           (posicion_rel_parcela[1]==(len(datos_parcela.datos[1])-1) and dy>0):
               return None
        return datos_parcela.datos[int(posicion_rel_parcela[0])+dx][int(posicion_rel_parcela[1])+dy]

    def _chequear_espacio_disponible(self, _pos_parcela, radio_inferior, radio_superior, datos_locales):
        radio_maximo=radio_superior if radio_superior>radio_inferior else radio_inferior
        # distancia del borde de parcela
        if abs(_pos_parcela[0]-Sistema.TopoTamanoParcela)<radio_maximo or \
           abs(_pos_parcela[1]-Sistema.TopoTamanoParcela)<radio_maximo:
               return False
        #
        #radio_maximo_total_inferior=Objetos.RadioMaximoInferior+radio_inferior
        radio_maximo_total_superior=Sistema.ObjetosRadioMaximoSuperior+radio_superior
        for dx in range(round(radio_maximo_total_superior)):
            for dy in range(round(radio_maximo_total_superior)):
                #
                vecinos=list()
                vecinos.append(self._obtener_vecino(datos_locales, _pos_parcela, -1, -1))
                vecinos.append(self._obtener_vecino(datos_locales, _pos_parcela,  0, -1))
                vecinos.append(self._obtener_vecino(datos_locales, _pos_parcela,  1, -1))
                vecinos.append(self._obtener_vecino(datos_locales, _pos_parcela, -1,  0))
                vecinos.append(self._obtener_vecino(datos_locales, _pos_parcela,  1,  0))
                vecinos.append(self._obtener_vecino(datos_locales, _pos_parcela, -1,  1))
                vecinos.append(self._obtener_vecino(datos_locales, _pos_parcela,  0,  1))
                vecinos.append(self._obtener_vecino(datos_locales, _pos_parcela,  1,  1))
                #
                for vecino in vecinos:
                    if not vecino:
                        continue
                    datos_objeto=vecino.datos_objeto
                    if not datos_objeto:
                        continue
                    radio_inferior_vecino=datos_objeto[4]
                    radio_superior_vecino=datos_objeto[5]
                    #log.debug("_chequear_espacio_disponible: radios_maximos_totales(i/s)=(%.1f,%.1f) \n candidato _pos_parcela=%s radios(i/s)=(%.1f,%.1f)\n vecino _pos_parcela=%s radios(i/s)=(%.1f,%.1f)" \
                    #          %(0.0, radio_maximo_total_superior,  \
                    #            str(_pos_parcela), radio_inferior, radio_superior, \
                    #            str(vecino.posicion_rel_parcela), radio_inferior_vecino, radio_superior_vecino))
                    dmax=dx if dx>dy else dy
                    radios_inferiores=(radio_inferior+radio_inferior_vecino)
                    if dmax>(radios_inferiores):
                    #    log.debug("False\n")
                        return False
                    elif radio_superior>0.0:
                        radios_superiores=(radio_superior+radio_superior_vecino)
                        if dmax>(radios_superiores):
                    #        log.debug("False\n")
                            return False
        #
        #log.debug("True\n")
        return True

#
#
# GrupoObjetosLocaciones
#
#
class GrupoObjetosLocaciones:
    
    def __init__(self, cantidad_total_locaciones):
        self.cantidad_total_locaciones=cantidad_total_locaciones
        self.tipos_objeto=list() # [fila,...]
        self.locaciones_disponibles=list() # [DatosLocalesObjetos,...]
        self.cantidades_tipos_objeto=dict() # {tipo_objeto:n,...}
    
    def __str__(self):
        return "GrupoObjetosLocaciones:\ntipos_objeto:%s\nlocaciones_disponibles:%s\ncantidades_tipos_objeto:%s\n" \
                %(str(self.tipos_objeto), str(["%s\n"%str(loc) for loc in self.locaciones_disponibles]), str(self.cantidades_tipos_objeto))
    
    def ordenar_locaciones_disponibles(self):
        self.locaciones_disponibles.sort(key=lambda x:x.factor_ruido)

    def determinar_cantidades_tipos_objeto(self):
        cantidad_tipos_objeto=len(self.tipos_objeto)
        cantidad_locaciones_disponibles=len(self.locaciones_disponibles)
        #log.debug("determinar_cantidades_tipos_objeto cantidad_tipos_objeto=%i cantidad_locaciones_disponibles=%i cantidad_total_locaciones=%i" \
        #        %(cantidad_tipos_objeto, cantidad_locaciones_disponibles, self.cantidad_total_locaciones))
        for fila in self.tipos_objeto:
            tipo_objeto=fila[2]
            densidad=fila[3]/cantidad_tipos_objeto
            cantidad=densidad*cantidad_locaciones_disponibles#(self.cantidad_total_locaciones/cantidad_locaciones_disponibles)#cantidad_locaciones_disponibles/self.cantidad_total_locaciones)
            if tipo_objeto in self.cantidades_tipos_objeto:
                log.error("el tipo de objeto %i ya se encuentra en self.cantidades_tipos_objeto"%tipo_objeto)
                continue
            #log.debug("cantidad de objetos '%s' a colocar: %i"%(fila[11], cantidad))
            self.cantidades_tipos_objeto[tipo_objeto]=int(cantidad)

#
#
# TESTER
#
#
from direct.showbase.ShowBase import ShowBase
from direct.gui.DirectGui import *
import os, os.path
class Tester(ShowBase):

    TamanoImagen=128
    PasoDesplazamiento=TamanoImagen/4.0

    TipoImagenTopo=0
    TipoImagenTemperaturaAM=1
    TipoImagenTemperaturaPrecip=2
    TipoImagenBioma=3
    TipoImagenTerreno=4
    TipoImagenRuidoTerreno=5
    TipoImagenInterpTabla=6

    def __init__(self):
        #
        super(Tester, self).__init__()
        self.disableMouse()
        self.win.setClearColor(Vec4(0.95, 1.0, 1.0, 1.0))
        #
        self.pos_foco=None
        #
        self.tipo_imagen=Tester.TipoImagenRuidoTerreno
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
        self.sistema.obtener_bioma_transicion(self.pos_foco, loguear=True)
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
                _y=(self.pos_foco[1]+(y-tamano/2)*zoom)
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
                        if a>Sistema.TopoAltitudOceano:
                            c=self.sistema.calcular_color_terreno_debug((_x, _y))
                            self.imagen.setXelA(x, y, c)
                        else:
                            self.imagen.setXel(x, y, 0.0)
                    elif self.tipo_imagen==Tester.TipoImagenRuidoTerreno:
                        a=self.sistema.obtener_altitud_suelo((_x, _y))
                        if a>Sistema.TopoAltitudOceano:
                            c=self.sistema.calcular_ruido_continuo(self.sistema.ruido_terreno, _x, _y)#*0.5+0.5
                            self.imagen.setXel(x, y, c)
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
                            _c=self.sistema.calcular_color_bioma_debug((_x, _y, 0))
                            self.imagen.setXelA(x, y, _c)
                        else:
                            self.imagen.setXel(x, y, 0.0)
                    elif self.tipo_imagen==Tester.TipoImagenInterpTabla:
                        pos_columna=x/(tamano+1)
                        pos_fila=y/(tamano+1)
                        #
                        loguear=False
                        if x==63:
                            log.debug("_generar_imagen (%.2f,%.2f)"%(pos_columna, pos_fila))
                            loguear=True
                        celda0, celda1, factor_transicion, dist_0=self.sistema._calcular_transicion_tabla_biomas(pos_columna, pos_fila, loguear)
                        bioma_a=Sistema.BiomaTabla[int(celda0[1])][int(celda0[0])]
                        bioma_b=Sistema.BiomaTabla[int(celda1[1])][int(celda1[0])]
                        color_a=Sistema.ColoresBioma[bioma_a]/256
                        color_b=Sistema.ColoresBioma[bioma_b]/256
                        color=(color_a*(1.0-factor_transicion))+(color_b*(factor_transicion))
                        if x==63:
                            log.debug("biomas (%i %i f=%.3f) colores %s %s %s"%(bioma_a, bioma_b, factor_transicion, str(color_a), str(color_b), str(color)))
                        self.imagen.setXel(x, y, color[0], color[1], color[2])
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
        self.sistema.obtener_bioma_transicion((x, y), loguear=True)
        self.pos_foco=(x, y)
        self._generar_imagen()
    
    def _guardar_imagen(self):
        ruta_archivo_imagen="sistema.png"
        log.info("_guardar_imagen ruta_archivo_imagen=%s"%ruta_archivo_imagen)
        if os.path.exists(ruta_archivo_imagen):
            log.warning("se eliminara el archivo")
            os.remove(ruta_archivo_imagen)
        self.imagen.write(ruta_archivo_imagen)
        log.info("archivo escrito")

    def _dump_data(self):
        log.info("_dump_data")
        #
        ruta_archivo_data="datadump.txt"
        #
        tamano=Tester.TamanoImagen
        #
        zoom=self.zoom_imagen
        #
        with open(ruta_archivo_data, "w+") as archivo:
            #
            archivo.write("pos_foco=%s ruta_archivo_data=%s\n"%(str(self.pos_foco), ruta_archivo_data))
            #
            for x in range(tamano+1):
                for y in range(tamano+1):
                    _x=self.pos_foco[0]+(x-tamano/2)*zoom
                    _y=self.pos_foco[1]+(y-tamano/2)*zoom
                    altitud_suelo=self.sistema.obtener_altitud_suelo((_x, _y, 0.0))
                    temperatura_anual_media=self.sistema.obtener_temperatura_anual_media_norm((_x, _y, 0.0))
                    precipitacion_frecuencia=self.sistema.obtener_precipitacion_frecuencia_anual((_x, _y, 0.0))
                    bioma=self.sistema.obtener_bioma_transicion((_x, _y, 0.0))
                    terreno=self.sistema.obtener_tipo_terreno((_x, _y, 0.0))
                    #
                    texto="(%.2f,%.2f,%.2f) tam=%.2f prec_f=%.2f bioma=%s terreno=%s\n"%(_x, _y, altitud_suelo, temperatura_anual_media, precipitacion_frecuencia, bioma, terreno)
                    archivo.write(texto)
        #
        log.info("archivo escrito %s"%ruta_archivo_data)

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
        DirectButton(parent=self.frmControles, pos=(0.4, 0, -0.05), scale=0.075, text="dump data", command=self._dump_data)
        DirectButton(parent=self.frmControles, pos=(0.9, 0, -0.05), scale=0.075, text="guardar imagen", command=self._guardar_imagen)
        #
        DirectButton(parent=self.frmControles, pos=(-0.05, 0, -0.15), scale=0.075, text="acercar", command=self._acercar_zoom_imagen, frameSize=(-1.5, 1.5, -0.60, 0.60), text_scale=0.75)
        DirectButton(parent=self.frmControles, pos=(0.20, 0, -0.15), scale=0.075, text="alejar", command=self._alejar_zoom_imagen, frameSize=(-1.5, 1.5, -0.60, 0.60), text_scale=0.75)
        DirectButton(parent=self.frmControles, pos=(0.475, 0, -0.15), scale=0.075, text="alejar max", command=self._alejar_zoom_imagen_max, frameSize=(-2.0, 2.0, -0.60, 0.60), text_scale=0.75)
        DirectButton(parent=self.frmControles, pos=(0.75, 0, -0.15), scale=0.075, text="cambiar", command=self._cambiar_tipo_imagen, frameSize=(-1.5, 1.5, -0.60, 0.60), text_scale=0.75)

    def _cambiar_tipo_imagen(self):
        self.tipo_imagen=(self.tipo_imagen+1)%7
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
