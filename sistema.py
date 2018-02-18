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

    def _FS_FUNC_TEX_TERRENO_4(self, tam, prec_f):
        fract_x, entero_x=math.modf(tam*3)
        fract_y, entero_y=math.modf(prec_f*2)
        fract_x_rnd=round(fract_x)
        fract_y_rnd=round(fract_y)
        idx_tabla_0=[entero_x+fract_x_rnd, entero_y+fract_y_rnd]
        idx_tabla_1=idx_tabla_0
        dist_x, dist_y=abs(fract_x_rnd-fract_x), abs(fract_y_rnd-fract_y)
        dist_0=0.0
        if dist_x>dist_y:
            fract_x_rnd_op=(fract_x_rnd+1)%2
            idx_tabla_1=[entero_x+fract_x_rnd_op, entero_y+fract_y_rnd]
            dist_0=dist_x
        else:
            fract_y_rnd_op=(fract_y_rnd+1)%2
            idx_tabla_1=[entero_x+fract_x_rnd, entero_y+fract_y_rnd_op]
            dist_0=dist_y
        tipos0=Sistema.TerrenoTiposTabla[int(idx_tabla_0[1])][int(idx_tabla_0[0])]
        tipo0=tipos0[0]
        color0=Sistema.ColoresTipoTerreno[tipo0]
        color1=None
        color=color0
        factor=0.0
        if dist_0>0.3:
            tipos1=Sistema.TerrenoTiposTabla[int(idx_tabla_1[1])][int(idx_tabla_1[0])]
            tipo1=tipos1[0]
            color1=Sistema.ColoresTipoTerreno[tipo1]
            factor=(dist_0-0.3)/((0.5-0.3)*2.0)
            color=(color0*(1.0-factor))+(color1*factor)
        return "fract=(%.2f,%.2f) idx_tabla_0=%s idx_tabla_1=%s dist_0=%.3f factor=%.3f\n\ttipo0=%s tipo1=%s\n\tc0=%s c1=%s c=%s\n"%(fract_x, fract_y, str(idx_tabla_0), str(idx_tabla_1), dist_0, factor, str(tipo0), str(tipo1), str(color0), str(color1), str(color))

    def _FS_FUNC_TEX_TERRENO_2(self, tam, prec_f):
        fract_x, entero_x=math.modf(tam*3)
        fract_y, entero_y=math.modf(prec_f*2)
        fract_x_rnd=round(fract_x)
        fract_y_rnd=round(fract_y)
        proximo_x=int(entero_x+fract_x_rnd)
        proximo_y=int(entero_y+fract_y_rnd)
        dist_proximo=math.sqrt((fract_x_rnd-fract_x)**2+(fract_y_rnd-fract_y)**2)
        tipos0=Sistema.TerrenoTiposTabla[proximo_y][proximo_x]
        tipo0=tipos0[0] #
        color0=Sistema.ColoresTipoTerreno[tipo0]/255
        info="tbl=(%.2f,%.2f) prox=%s d_prox=%.4f tipos0=%s t0=%i c0=%s\n\t"%(tam*3, prec_f*2, str((proximo_x, proximo_y)), dist_proximo, str(tipos0), tipo0, str(color0))
        if dist_proximo>0.40:
            fract_x_rnd_op, fract_y_rnd_op=(fract_x_rnd+1)%2, (fract_y_rnd+1)%2
            # b
            dist_siguiente=math.sqrt((fract_x_rnd_op-fract_x)**2+(fract_y_rnd-fract_y)**2)
            siguiente_x, siguiente_y=int(entero_x+fract_x_rnd_op), int(entero_y+fract_y_rnd)
            # c
            dist_c=math.sqrt((fract_x_rnd-fract_x)**2+(fract_y_rnd_op-fract_y)**2)
            if dist_c<dist_siguiente:
                dist_siguiente=dist_c
                siguiente_x, siguiente_y=int(entero_x+fract_x_rnd), int(entero_y+fract_y_rnd_op)
            # d
            dist_d=math.sqrt((fract_x_rnd_op-fract_x)**2+(fract_y_rnd_op-fract_y)**2)
            if dist_d<dist_siguiente: # siempre estara lejos?
                dist_siguiente=dist_d
                siguiente_x, siguiente_y=int(entero_x+fract_x_rnd_op), int(entero_y+fract_y_rnd_op)
            #
            tipos1=Sistema.TerrenoTiposTabla[siguiente_y][siguiente_x]
            tipo1=tipos1[0] #
            info+="| sgte=%s d_sgte=%.4f tipos1=%s t1=%i\n\t"%(str((siguiente_x, siguiente_y)), dist_siguiente, str(tipos1), tipo1)
            if tipo0!=tipo1:
                factor_transicion=dist_proximo#(dist_siguiente/(dist_proximo+dist_siguiente))
                color1=Sistema.ColoresTipoTerreno[tipo1]/255
                color=(color0*(1.0-factor_transicion))+(color1*(factor_transicion))
                info+="| c1=%s f=%.4f c=%s"%(str(color1), factor_transicion, str(color))
        return info

    def obtener_info(self):
        tam=self.obtener_temperatura_anual_media_norm(self.posicion_cursor)
        prec_f=self.obtener_precipitacion_frecuencia_anual(self.posicion_cursor)
        bioma=self.obtener_bioma_transicion(self.posicion_cursor)
        tipo_terreno=self.obtener_tipo_terreno(self.posicion_cursor)
        info="Sistema posicion_cursor=(%.3f,%.3f,%.3f)\n"%(self.posicion_cursor[0], self.posicion_cursor[1], self.posicion_cursor[2])
        info+="geo: tam=%.3f prec_f=%.3f\nbioma=(%s) tipo_terreno=(%s)\n"%(tam, prec_f, bioma, tipo_terreno)
        info+="FS_FUNC_TEX_TERRENO_4: %s\n"%self._FS_FUNC_TEX_TERRENO_4(tam, prec_f)
        info+="era: año=%i estacion=%i dia=%i hora=%.2f(%.2f/%i) periodo_dia_actual=%i\n"%(self.ano, self.estacion, self.dia, self.hora_normalizada, self._segundos_transcurridos_dia, self.duracion_dia_segundos, self.periodo_dia_actual)
        info+="temp=%.2f nubosidad=%.2f precipitacion=[tipo=%i intens=%i t=(%.2f/%2.f)]\n"%(self.temperatura_actual_norm, self.nubosidad, self.precipitacion_actual_tipo, self.precipitacion_actual_intensidad, self.precipitacion_actual_t, self.precipitacion_actual_duracion)
        return info

    def cargar_parametros_iniciales(self, defecto=True):
        #
        if defecto:
            log.info("cargar_parametros_iniciales por defecto")
            self.posicion_cursor=Vec3(-0, 0, 0) # Vec3(-826, 121, 0) # selva pura:Vec3(-1100, 2000, 0)
            self.duracion_dia_segundos=1800
            self.ano=0
            self.dia=0
            self._segundos_transcurridos_dia=0.55*self.duracion_dia_segundos
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
        desc.altitud_suelo=self.obtener_altitud_suelo(posicion)
        desc.altitud_tope=self.obtener_altitud_tope(posicion)
        desc.ambiente=self.obtener_ambiente(posicion)
        desc.latitud=self.obtener_latitud(posicion)
        desc.bioma=self.obtener_bioma_transicion(posicion)
        self.precipitacion_frecuencia=self.obtener_precipitacion_frecuencia_anual(posicion)
        self.inclinacion_solar_anual_media=None
        self.vegetacion=None
        self.roca=None
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
        idx_tabla_0, idx_tabla_1, factor_transicion=self._calcular_transicion_tabla_biomas(temperatura_anual_media, precipitacion_frecuencia, loguear)
        if loguear:
            log.debug("obtener_bioma_transicion idx_tabla_0=%s idx_tabla_1=%s factor_transicion=%.3f"%(str(idx_tabla_0), str(idx_tabla_1), factor_transicion))
        bioma0=Sistema.BiomaTabla[int(idx_tabla_0[1])][int(idx_tabla_0[0])]
        bioma1=Sistema.BiomaTabla[int(idx_tabla_1[1])][int(idx_tabla_1[0])]
        return (bioma0, bioma1, factor_transicion)

    def obtener_tipo_terreno(self, posicion, loguear=False):
        temperatura_anual_media=self.obtener_temperatura_anual_media_norm(posicion)
        precipitacion_frecuencia=self.obtener_precipitacion_frecuencia_anual(posicion)
        idx_tabla_0, idx_tabla_1, factor_transicion=self._calcular_transicion_tabla_biomas(temperatura_anual_media, precipitacion_frecuencia, loguear)
        tipos0=Sistema.TerrenoTiposTabla[int(idx_tabla_0[1])][int(idx_tabla_0[0])]
        tipos1=Sistema.TerrenoTiposTabla[int(idx_tabla_1[1])][int(idx_tabla_1[0])]
        ruido0=self.ruido_terreno(posicion[0], posicion[1])
        ruido1=self.ruido_terreno(posicion[1], posicion[0])
        tipo0=tipos0[0] if ruido0<0.5 else tipos0[1]
        tipo1=tipos1[0] if ruido1<0.5 else tipos1[1]
        return (tipo0, tipo1, factor_transicion)

    def _calcular_transicion_tabla_biomas(self, temperatura_anual_media, precipitacion_frecuencia, loguear=False):
        #
        pos=(temperatura_anual_media*4, precipitacion_frecuencia*3)
        celda0=(int(pos[0]), int(pos[1]))
        punto_medio0=(celda0[0]+0.5, celda0[1]+0.5)
        distancia0=(pos[0]-punto_medio0[0], pos[1]-punto_medio0[1])
        delta_celda0=((-1 if distancia0[0]<0 else 1), (-1 if distancia0[1]<0 else 1))
        distancia, celda1=0.0, None
        if abs(distancia0[0])>abs(distancia0[1]):
            celda1=(max(0, min(3, celda0[0]+delta_celda0[0])), celda0[1])
            distancia=abs(distancia0[0])
        else:
            celda1=(celda0[0], max(0, min(2, celda0[1]+delta_celda0[1])))
            distancia=abs(distancia0[0])
        factor_transicion=0.0
        corte=0.2 # quitar una vez debugged
        if distancia>corte:
            factor_transicion=(distancia-corte)/((0.5-corte)*2.0) # (distancia-0.3)/((0.5-0.3)*2.0)
        if loguear:
            log.debug("_calcular_transicion_tabla_biomas pos=(%.4f,%.4f) c0=(%.4f,%.4f) pm0=(%.4f,%.4f) d=(%.4f,%.4f) c1=(%.4f,%.4f) f=%.4f"% \
                      (pos[0], pos[1], celda0[0], celda0[1], punto_medio0[0], punto_medio0[1], \
                       distancia0[0], distancia0[1], celda1[0], celda1[1], factor_transicion))
        return (celda0, celda1, factor_transicion)

    def calcular_color_bioma_debug(self, posicion=None):
        _posicion=posicion
        if not _posicion:
            _posicion=self.posicion_cursor
        bioma0, bioma1, factor_transicion=self.obtener_bioma_transicion(_posicion)
        color0=Sistema.ColoresBioma[bioma0]
        color1=Sistema.ColoresBioma[bioma1]
        color=(color0*(1.0-factor_transicion))+(color1*factor_transicion)
        return color

    def calcular_color_terreno_debug(self, posicion=None):
        _posicion=posicion
        if not _posicion:
            _posicion=self.posicion_cursor
        terreno_base, terreno_superficie, factor_transicion=self.obtener_tipo_terreno(_posicion)
        color_base=Sistema.ColoresTipoTerreno[terreno_base]
        color_superficie=Sistema.ColoresTipoTerreno[terreno_superficie]
        color=(color_base*(1.0-factor_transicion))+(color_superficie*factor_transicion)
        color/=256
        color=Vec4(color[0], color[1], color[2], 1.0)
        return color

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
        self.posicion=posicion
        self.altitud_suelo=None
        self.altitud_tope=None # para implementar cuevas?
        self.ambiente=None
        # 2d
        self.latitud=None
        self.bioma=None # (bioma_a,bioma_b,bioma_c,bioma_d)
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
import os, os.path
class Tester(ShowBase):

    TamanoImagen=128
    PasoDesplazamiento=TamanoImagen/3.0

    TipoImagenTopo=0
    TipoImagenTemperaturaAM=1
    TipoImagenTemperaturaPrecip=2
    TipoImagenBioma=3
    TipoImagenTerreno=4
    TipoImagenInterpTabla=5

    def __init__(self):
        #
        super(Tester, self).__init__()
        self.disableMouse()
        self.win.setClearColor(Vec4(0.95, 1.0, 1.0, 1.0))
        #
        self.pos_foco=None
        #
        self.tipo_imagen=Tester.TipoImagenInterpTabla
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
                        tipo0, tipo1, factor_transicion=self.sistema.obtener_tipo_terreno((_x, _y))
                        color0=Sistema.ColoresTipoTerreno[tipo0]
                        color1=Sistema.ColoresTipoTerreno[tipo1]
                        c=(color0*(1.0-factor_transicion))+(color1*factor_transicion)
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
                        celda0, celda1, factor_transicion=self.sistema._calcular_transicion_tabla_biomas(pos_columna, pos_fila, loguear)
                        bioma_a=Sistema.BiomaTabla[int(celda0[1])][int(celda0[0])]
                        bioma_b=Sistema.BiomaTabla[int(celda1[1])][int(celda1[0])]
                        color_a=Sistema.ColoresBioma[bioma_a]/255
                        color_b=Sistema.ColoresBioma[bioma_b]/255
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

