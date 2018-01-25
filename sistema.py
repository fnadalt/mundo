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
# temperatura_media(TemperaturaPerlinNoiseParams,altitud,latitud)
# temperatura_actual(temperatura_media,estacion_normalizada,hora_normalizada,altitud)
# precipitacion_frecuencia(PrecipitacionFrecuenciaPerlinNoiseParams)
# nubosidad(PrecipitacionNubosidadPerlinNoiseParams)
# bioma(temperatura_anual_media,precipitacion_frecuencia)
# vegetacion(temperatura_anual_media,precipitacion_frecuencia) ?
class Sistema:
    
    # topografia
    TopoExtension=8*1024 # +/-TopoExtension; ecuador=0
    TopoAltura=300.0
    TopoAltitudOceano=TopoAltura/2.0
    TopoAlturaSobreOceano=TopoAltura-TopoAltitudOceano
    TopoPerlinNoiseSeed=9601
    TopoPerlinNoiseParams=[(256.0, 1.0), (64.0, 0.2), (32.0, 0.075), (16.0, 0.005), (8.0, 0.001)] # [(escala, amplitud), ...]
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
    TemperaturaPerlinNoiseParams=(8*1024.0, 196) # (escala, semilla)
    TemperaturaAmplitudTermicaMaxima=0.4
    # precipitaciones; [0.0,1.0): 0.0=nula, 1.0=maxima
    PrecipitacionFrecuenciaPerlinNoiseParams=(2*1024.0, 9016) # (escala, semilla)
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
    BiomaTabla=[[BiomaDesiertoPolar, BiomaTaiga,  BiomaBosqueCaducifolio,  BiomaSelva],  \
                [BiomaDesiertoPolar, BiomaTaiga,  BiomaBosqueMediterraneo, BiomaSavannah],  \
                [BiomaDesiertoPolar, BiomaTundra, BiomaDesierto,           BiomaDesierto],  \
                ] # tabla(temperatura_anual_media,precipitacion_frecuencia)
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
        self.ruido_terreno=None
        self.ruido_temperatura=None
        self.ruido_precipitacion=None
        self.ruido_nubosidad=None
        self.ruido_vegetacion=None
        # cursor:
        self.posicion_cursor=None
        # parametros:
        self.duracion_dia_segundos=1800
        # variables externas:
        self.ano=0
        self.estacion=Sistema.EstacionVerano
        self.dia=0
        self.periodo_dia_actual=Sistema.DiaPeriodoAtardecer
        self.periodo_dia_anterior=Sistema.DiaPeriodoDia
        self.periodo_dia_siguiente=Sistema.DiaPeriodoNoche
        self.hora_normalizada=0.0
        self.temperatura_actual=None
        self.nubosidad=0.0
        self.precipitacion_actual_tipo=Sistema.PrecipitacionTipoAgua
        self.precipitacion_actual_intensidad=Sistema.PrecipitacionIntensidadNula
        self.precipitacion_actual_duracion=0.0
        self.precipitacion_actual_t=0.0
        # variables internas:
        self._segundos_transcurridos_dia=0.0

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
        self._establecer_fecha_hora_estacion(dt)
        self._establecer_temperatura_actual(dt)
        self._establecer_precipitacion(dt)

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
        # a implementar para grillas 3D, con cuevas, etc...
        return 5.0*Sistema.TopoAltura

    def obtener_altitud_suelo_supra_oceanica_norm(self, posicion):
        altitud=self.obtener_altitud_suelo(posicion)
        altitud-=Sistema.TopoAltitudOceano
        altitud/=Sistema.TopoAlturaSobreOceano
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
    
    def obtener_latitud_norm(self, posicion):
        return abs(posicion[1]/Sistema.TopoExtension)
    
    def obtener_nivel_latitud(self, posicion):
        latitud=abs(posicion[1])
        if latitud<Sistema.LatitudTropical:
            return Sistema.LatitudTropical
        elif latitud<Sistema.LatitudSubTropical:
            return Sistema.LatitudSubTropical
        elif latitud<Sistema.LatitudFria:
            return Sistema.LatitudFria
        else:
            return Sistema.LatitudPolar

    def obtener_nivel_latitud_transicion(self, posicion): # util?
        latitud=abs(posicion[1])
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
        print("obtener_temperatura_anual_media_norm (%.2f,%.2f)"%(posicion[0], posicion[1]))
        altitud_normalizada=self.obtener_altitud_suelo_supra_oceanica_norm(posicion)
        latitud=self.obtener_latitud_norm(posicion)
        temperatura=self.ruido_temperatura(posicion[0], posicion[1])*0.5+0.5
        temperatura-=abs(latitud)*0.25
        temperatura-=abs(altitud_normalizada)*0.25
        temperatura=0.2+max(temperatura,0.0)*0.6 # ajustar a rango de temperatura_media [0.2,0.8]
        print("temperatura_anual_media %.3f"%temperatura)
        return temperatura

    def obtener_temperatura_grados(self, temperatura_normalizada):
        # temperatura_normalizada: [0,1] -> [-50,50]
        temperatura_grados=(temperatura_normalizada-0.5)*2.0*50.0
        return temperatura_grados

    def obtener_precipitacion_frecuencia_anual(self, posicion):
        print("obtener_precipitacion_frecuencia_anual (%.2f,%.2f)"%(posicion[0], posicion[1]))
        #
        frecuencia=self.ruido_precipitacion(posicion[0], posicion[1])*0.5+0.5
        print("frecuencia %.3f"%frecuencia)
        return frecuencia

    def obtener_inclinacion_solar_anual_media(self, posicion):
        latitud=posicion[1]
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
        elif temperatura_anual_media>=0.80:
            if precipitacion_frecuencia<0.33:
                return Sistema.BiomaDesierto
            elif precipitacion_frecuencia>=0.33 and precipitacion_frecuencia<0.66:
                return Sistema.BiomaSavannah
            elif precipitacion_frecuencia>=0.66:
                return Sistema.BiomaSelva

    def obtener_bioma_transicion(self, posicion):
        #
        temperatura_anual_media=self.obtener_temperatura_anual_media_norm(posicion)
        precipitacion_frecuencia=self.obtener_precipitacion_frecuencia_anual(posicion)
        #
        tabla_cantidad_filas=len(Sistema.BiomaTabla)
        tabla_cantidad_columnas=len(Sistema.BiomaTabla[0])
        pos_fila=temperatura_anual_media*len(Sistema.BiomaTabla)
        pos_columna=precipitacion_frecuencia*len(Sistema.BiomaTabla[0])
        fila=int(pos_fila)
        columna=int(pos_columna)
        if fila==tabla_cantidad_filas:
            fila-=1
        if columna==tabla_cantidad_columnas:
            columna-=1
        bioma1=Sistema.BiomaTabla[fila][columna]
        #print("obtener_bioma_transicion bioma1 fila=%i columna=%i %s"%(fila, columna, str(bioma1)))
        delta_idx_tabla, factor_transicion=self._calcular_transicion_tabla(pos_columna, pos_fila, tabla_cantidad_columnas, tabla_cantidad_filas)
        fila_delta=fila+delta_idx_tabla[1]
        columna_delta=columna+delta_idx_tabla[0]
        if fila_delta>=0 and fila_delta<tabla_cantidad_filas:
            fila=fila_delta
        if columna_delta>=0 and columna_delta<tabla_cantidad_columnas:
            columna=columna_delta
        bioma2=Sistema.BiomaTabla[fila][columna]
        #print("bioma2 delta_idx_tabla=%s factor_transicion=%.3f fila=%i columna=%i %s"%(str(delta_idx_tabla), factor_transicion, fila, columna, str(bioma2)))
        #
        return (bioma1, bioma2, factor_transicion)

    def obtener_tipo_terreno(self, posicion): # f()->(terreno_base,terreno_superficie,factor_transicion)
        bioma1, bioma2, factor_transicion=self.obtener_bioma_transicion(posicion)
        ruido_terreno=self.ruido_terreno(posicion[0], posicion[1])*0.5+0.5
        bioma_terreno_base, bioma_terreno_superficie=self._obtener_terreno_bioma(bioma1)
        if factor_transicion>0.0 and ruido_terreno>0.5:
            bioma_terreno_base, bioma_terreno_superficie=self._obtener_terreno_bioma(bioma2)
            ruido_terreno-=0.5
            ruido_terreno*=2.0
        return (bioma_terreno_base, bioma_terreno_superficie, ruido_terreno)

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

    def _calcular_transicion_tabla(self, x, y, tabla_cantidad_columnas, tabla_cantidad_filas, rango_pureza=0.75): # f()->(delta_idx_tabla,factor)
        # Surge como necesidad para calcular transicion de biomas, utilizando BiomaTabla.
        # Segun tamperatura media y precipitacion, se ubica un punto en la tabla.
        # El bioma es "puro", si el punto se encuentra dentro del 75% del rango de bioma tanto
        # para temperatura como para precipitacion. Fuera de este porcentaje, se efectuará
        # interpolacion con el bioma con el cual se encuentre mas cerca. Si la temperatura
        # se aleja mas del rango, se elegira el siguiente bioma en funcion de esta variable;
        # si no, se hara en funcion de las precipitaciones. Si ambas son iguales, se priorizara
        # precipitacion.
        # Devuelve un delta de posicion y un factor: ((0,0),0.00),((-1,0),0.76),((0,+1),0.1),etc...
        #
        longitud_rango_fila=1.0
        longitud_rango_columna=1.0
        longitud_rango_fila_puro=longitud_rango_fila*rango_pureza
        longitud_rango_columna_puro=longitud_rango_columna*rango_pureza
        #print("_calcular_transicion_tabla(col=%.2f,fila=%.2f):\n dim=(%i,%i) long_rango=(%.2f,%.2f) long_rango_puro=(%.2f,%.2f)"%(x, y, tabla_cantidad_filas, tabla_cantidad_columnas, longitud_rango_fila, longitud_rango_columna, longitud_rango_fila_puro, longitud_rango_columna_puro))
        #
        fila_actual=int(y)
        if fila_actual==tabla_cantidad_filas:
            fila_actual-=1
        columna_actual=int(x)
        if columna_actual==tabla_cantidad_columnas:
            columna_actual-=1
        #print("f_actual=%.2f[%i] c_actual=%.2f[%i]"%(y, fila_actual, x, columna_actual))
        #
        fila_actual_punto_medio=fila_actual+longitud_rango_fila/2.0
        offset_pos_fila=y-fila_actual_punto_medio
        columna_actual_punto_medio=columna_actual+longitud_rango_columna/2.0
        offset_pos_columna=x-columna_actual_punto_medio
        #print("fila_pm=%.2f off_fila_pm=%.2f col_pm=%.2f off_col_pm=%.2f"%(fila_actual_punto_medio, offset_pos_fila, columna_actual_punto_medio, offset_pos_columna))
        #
        if abs(offset_pos_fila)<=longitud_rango_fila_puro/2.0 and abs(offset_pos_columna)<=longitud_rango_columna_puro/2.0:
            # puro
            return ((0, 0), 0.0)
        else:
            # interpolar
            if abs(offset_pos_fila)>=abs(offset_pos_columna): # prioriza fila
                #print("prioriza fila")
                factor=(abs(offset_pos_fila)-longitud_rango_fila_puro/2.0)/((1.0-rango_pureza))
                delta=-1 if offset_pos_fila<0.0 else 1
                return ((0, delta), factor)
            else:
                #print("prioriza columna")
                factor=(abs(offset_pos_columna)-longitud_rango_columna_puro/2.0)/((1.0-rango_pureza))
                delta=-1 if offset_pos_columna<0.0 else 1
                return ((delta, 0), factor)

    def _obtener_terreno_bioma(self, bioma): # f()->(tipo_terreno_base,tipo_terreno_superficie)
        if bioma==Sistema.BiomaDesiertoPolar:
            tipo_terreno_base=Sistema.TerrenoTipoTundra
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
                self.estacion=(self.dia/Sistema.DiasDelAno)*4.0

    def _establecer_temperatura_actual(self, dt):
        #
        temperatura_anual_media=self.obtener_temperatura_anual_media_norm(self.posicion_cursor)
        altitud_normalizada=self.obtener_altitud_suelo_supra_oceanica_norm(self.posicion_cursor)
        estacion_termica=abs(0.5-self.dia/Sistema.DiasDelAno)
        periodo_dia_termico=abs(0.5-((self.hora_normalizada+0.25)%1)) # [0.0,0.5]->(frio,calor)
        #
        factor_termico=(periodo_dia_termico+estacion_termica+(1.0-altitud_normalizada))/2.0 # [0.0,1.0]
        self.temperatura_actual=temperatura_anual_media-(Sistema.TemperaturaAmplitudTermicaMaxima/2.0)+(factor_termico*Sistema.TemperaturaAmplitudTermicaMaxima)
    
    def _establecer_precipitacion(self, dt):
        if self.precipitacion_actual_intensidad==Sistema.PrecipitacionIntensidadNula:
            momento_era=self.ano*Sistema.DiasDelAno+self.dias+self.hora_normalizada
            precipitacion_frecuencia=self.obtener_precipitacion_frecuencia_anual(self.posicion_cursor)
            self.nubosidad=max(0.0, self.ruido_nubosidad(0.0, momento_era)-(1.0-precipitacion_frecuencia))
            if self.nubosidad>Sistema.PrecipitacionNubosidadGatillo:
                if self.temperatura_actual<=0.0:
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

    ColoresTipoTerreno={Terreno.TipoNulo:Vec4(0, 0, 0, 255), 
                        Terreno.TipoArena:Vec4(240, 230, 0, 255), 
                        Terreno.TipoTierra1:Vec4(70, 60, 0, 255), 
                        Terreno.TipoPasto:Vec4(0, 190, 10, 255), 
                        Terreno.TipoTierra2:Vec4(70, 60, 0, 255), 
                        Terreno.TipoNieve:Vec4(250, 250, 250, 255)
                        }

    def __init__(self):
        #
        super(Tester, self).__init__()
        self.disableMouse()
        self.win.setClearColor(Vec4(0.95, 1.0, 1.0, 1.0))
        #
        bullet_world=BulletWorld()
        #
        self.pos_foco=None
        self.cam_pitch=30.0
        self.escribir_archivo=False # cada update
        #
        GeneradorShader.iniciar(Terreno.AltitudAgua, Vec4(0, 0, 1, Terreno.AltitudAgua))
        GeneradorShader.aplicar(self.render, GeneradorShader.ClaseGenerico, 1)
        self.render.setShaderInput("distancia_fog_maxima", 3000.0, 0, 0, 0, priority=3)
        #
        self.terreno=Terreno(self, bullet_world)
        self.terreno.iniciar()
        #self.terreno.nodo.setRenderModeWireframe()
        #
        plano=CardMaker("plano_agua")
        r=Terreno.TamanoParcela*6
        plano.setFrame(-r, r, -r, r)
        plano.setColor((0, 0, 1, 1))
        self.plano_agua=self.render.attachNewNode(plano.generate())
        self.plano_agua=self.loader.loadModel("objetos/plano_agua")
        self.plano_agua.reparentTo(self.render)
        self.plano_agua.setScale(0.5)
        #self.plano_agua.setP(-90.0)
        #self.plano_agua.hide()
        #
        self.cam_driver=self.render.attachNewNode("cam_driver")
        self.camera.reparentTo(self.cam_driver)
        self.camera.setPos(Terreno.TamanoParcela/2, 500, 100)
        self.camera.lookAt(self.cam_driver)
        self.cam_driver.setP(self.cam_pitch)
        #
        self.luz_ambiental=self.render.attachNewNode(AmbientLight("luz_ambiental"))
        self.luz_ambiental.node().setColor(Vec4(1, 1, 1, 1))
        #
        self.sun=self.render.attachNewNode(DirectionalLight("sun"))
        self.sun.node().setColor(Vec4(1, 1, 1, 1))
        self.sun.setPos(self.terreno.nodo, 100, 100, 100)
        self.sun.lookAt(self.terreno.nodo)
        #
        self.render.setLight(self.sun)
        #
        self.texturaImagen=None
        self.imagen=None
        self.zoom_imagen=1
        #
        self.tipo_imagen=Tester.TipoImagenTopo
        #
        self.taskMgr.add(self.update, "update")
        self.accept("wheel_up", self.zoom, [1])
        self.accept("wheel_down", self.zoom, [-1])
        #
        self._cargar_ui()
        
    def update(self, task):
        nueva_pos_foco=self.pos_foco[:] if self.pos_foco else self.terreno.pos_foco_inicial
        #
        mwn=self.mouseWatcherNode
        if mwn.isButtonDown(KeyboardButton.up()):
            nueva_pos_foco[1]-=32
        elif mwn.isButtonDown(KeyboardButton.down()):
            nueva_pos_foco[1]+=32
        elif mwn.isButtonDown(KeyboardButton.left()):
            nueva_pos_foco[0]+=32
        elif mwn.isButtonDown(KeyboardButton.right()):
            nueva_pos_foco[0]-=32
        #
        if nueva_pos_foco!=self.pos_foco:
            log.info("update pos_foco=%s"%str(nueva_pos_foco))
            self.pos_foco=nueva_pos_foco
            self._actualizar_terreno(self.pos_foco)
        return task.cont
    
    def zoom(self, dir):
        dy=25*dir
        self.camera.setY(self.camera, dy)

    def analizar_altitudes(self, pos_foco, tamano=1024):
        log.info("analizar_altitudes en %ix%i"%(tamano, tamano))
        i=0
        media=0
        vals=list()
        min=999999
        max=-999999
        for x in range(tamano):
            for y in range(tamano):
                a=self.terreno.obtener_altitud((pos_foco[0]+x, pos_foco[1]+y))
                vals.append(a)
                if a>max:
                    max=a
                if a<min:
                    min=a
                media=((media*i)+a)/(i+1)
                i+=1
        sd=0
        for val in vals:  sd+=((val-media)*(val-media))
        sd/=(tamano*tamano)
        sd=math.sqrt(sd)
        log.info("analizar_altitudes rango:[%.3f/%.3f] media=%.3f sd=%.3f"%(min, max, media, sd))

    def _actualizar_terreno(self, pos):
        log.info("_actualizar_terreno pos=%s"%(str(pos)))
        #
        self.terreno.update(pos)
        if self.escribir_archivo:
            log.info("escribir_archivo")
            self.terreno.nodo.writeBamFile("terreno.bam")
        self.plano_agua.setPos(Vec3(pos[0], pos[1], Terreno.AltitudAgua))
        #
        self.cam_driver.setPos(Vec3(pos[0]+Terreno.TamanoParcela/2, pos[1]-Terreno.TamanoParcela, Terreno.AltitudAgua))
        #
        self.lblInfo["text"]=self.terreno.obtener_info()
        #
        self.pos_foco=pos
        #
        self._generar_imagen()

    def _generar_imagen(self):
        log.info("_generar_imagen")
        if self.tipo_imagen==Tester.TipoImagenTopo:
            self._generar_imagen_topo()
        elif self.tipo_imagen==Tester.TipoImagenTiposTerreno:
            self._generar_imagen_tipos_terreno()
        elif self.tipo_imagen==Tester.TipoImagenEspacios:
            self._generar_imagen_espacios()

    def _generar_imagen_topo(self):
        log.info("_generar_imagen_topo")
        #
        tamano=128
        if not self.imagen:
            self.imagen=PNMImage(tamano+1, tamano+1)
            self.texturaImagen=Texture()
            self.frmImagen["image"]=self.texturaImagen
            self.frmImagen["image_scale"]=0.4
        #
        zoom=self.zoom_imagen*Terreno.TamanoParcela/tamano
        log.info("zoom: %.2f"%(zoom))
        for x in range(tamano+1):
            for y in range(tamano+1):
                _x=tamano-self.pos_foco[0]+x
                _y=tamano-self.pos_foco[1]+y
                a=self.terreno.obtener_altitud((_x, _y))
                c=int(255*a/Terreno.AlturaMaxima)
                if x==tamano/2 or y==tamano/2:
                    c=255
                else:
                    if a>Terreno.AltitudAgua:
                        tb=self.terreno.obtener_temperatura_base((_x, _y))
                        tt=self.terreno.obtener_tipo_terreno_tuple((_x, _y), tb, a)
                        c0=None
                        c1=None
                        if tt[2]==0.0:
                            c=Tester.ColoresTipoTerreno[tt[0]]
                        elif tt[2]==1.0:
                            c=Tester.ColoresTipoTerreno[tt[1]]
                        else:
                            c0=Tester.ColoresTipoTerreno[tt[0]]
                            c1=Tester.ColoresTipoTerreno[tt[1]]
                            c=(c0*(1-tt[2]))+(c1*tt[2])
                        #log.debug("_generar_imagen tt=%s c0=%s c1=%s c=%s"%(str(tt), str(c0), str(c1), str(c)))
                        self.imagen.setPixel(x, y, PNMImageHeader.PixelSpec(int(c[0]), int(c[1]), int(c[2]), 255))
                    else:
                        self.imagen.setPixel(x, y, PNMImageHeader.PixelSpec(0, 0, c, 255))
        #
        self.texturaImagen.load(self.imagen)

    def _generar_imagen_tipos_terreno(self):
        #
        tamano=128
        if not self.imagen:
            self.imagen=PNMImage(tamano+1, tamano+1)
            self.texturaImagen=Texture()
            self.frmImagen["image"]=self.texturaImagen
            self.frmImagen["image_scale"]=0.4
        #
        for x in range(tamano+1):
            for y in range(tamano+1):
                t=x/(tamano+1)
                a=(y/(tamano+1))*Terreno.AlturaMaxima
                tt=self.terreno.obtener_tipo_terreno_tuple((0, 0), t, a)
                c0=Tester.ColoresTipoTerreno[tt[0]]
                c1=Tester.ColoresTipoTerreno[tt[1]]
                color=None
                if tt[2]>0.0:
                    color=(c0*(1.0-tt[2]))+(c1*tt[2])
                else:
                    color=c0
                color=(int(color[0]), int(color[1]), int(color[2]), 255)
                self.imagen.setPixel(x, y, PNMImageHeader.PixelSpec(color[0], color[1], color[2], 255))
        #
        self.texturaImagen.load(self.imagen)

    def _generar_imagen_espacios(self):
        log.info("_generar_imagen_espacios no implementado")

    def _ir_a_idx_pos(self):
        log.info("_ir_a_idx_pos")
        try:
            idx_x=int(self.entry_x.get())
            idx_y=int(self.entry_y.get())
            pos=self.terreno.obtener_pos_parcela((idx_x, idx_y))
            log.info("idx_pos:(%i,%i); pos:%s"%(idx_x, idx_y, str(pos)))
            self._actualizar_terreno(list(pos))
        except Exception as e:
            log.exception(str(e))

    def _cargar_ui(self):
        # frame
        self.frame=DirectFrame(parent=self.aspect2d, pos=(0, 0, -0.85), frameSize=(-1, 1, -0.15, 0.25), frameColor=(1, 1, 1, 0.5))
        # info
        self.lblInfo=DirectLabel(parent=self.frame, pos=(-1, 0, 0.15), scale=0.05, text="info terreno?", frameColor=(1, 1, 1, 0.2), frameSize=(0, 40, -2, 2), text_align=TextNode.ALeft, text_pos=(0, 1, 1))
        # idx_pos
        DirectLabel(parent=self.frame, pos=(-1, 0, 0), scale=0.05, text="idx_pos_x", frameColor=(1, 1, 1, 0), frameSize=(0, 2, -1, 1), text_align=TextNode.ALeft)
        DirectLabel(parent=self.frame, pos=(-1, 0, -0.1), scale=0.05, text="idx_pos_y", frameColor=(1, 1, 1, 0), frameSize=(0, 2, -1, 1), text_align=TextNode.ALeft)
        self.entry_x=DirectEntry(parent=self.frame, pos=(-0.7, 0, 0), scale=0.05)
        self.entry_y=DirectEntry(parent=self.frame, pos=(-0.7, 0, -0.1), scale=0.05)
        DirectButton(parent=self.frame, pos=(0, 0, -0.1), scale=0.075, text="actualizar", command=self._ir_a_idx_pos)
        #
        self.frmImagen=DirectFrame(parent=self.frame, pos=(0.8, 0, 0.2), state=DGG.NORMAL, frameSize=(-0.4, 0.4, -0.4, 0.4))
        self.frmImagen.bind(DGG.B1PRESS, self._click_imagen)
        DirectButton(parent=self.frame, pos=(0.500, 0, 0.65), scale=0.1, text="acercar", command=self._acercar_zoom_imagen, frameSize=(-1, 1, -0.4, 0.4), text_scale=0.5)
        DirectButton(parent=self.frame, pos=(0.725, 0, 0.65), scale=0.1, text="alejar", command=self._alejar_zoom_imagen, frameSize=(-1, 1, -0.4, 0.4), text_scale=0.5)
        DirectButton(parent=self.frame, pos=(0.950, 0, 0.65), scale=0.1, text="cambiar", command=self._cambiar_tipo_imagen, frameSize=(-1, 1, -0.4, 0.4), text_scale=0.5)

    def _cambiar_tipo_imagen(self):
        log.info("_cambiar_tipo_imagen a:")
        if self.tipo_imagen==Tester.TipoImagenTopo:
            log.info("TipoImagenTiposTerreno")
            self.tipo_imagen=Tester.TipoImagenTiposTerreno
        elif self.tipo_imagen==Tester.TipoImagenTiposTerreno:
            log.info("TipoImagenEspacios")
            self.tipo_imagen=Tester.TipoImagenEspacios
        elif self.tipo_imagen==Tester.TipoImagenEspacios:
            log.info("TipoImagenTopo")
            self.tipo_imagen=Tester.TipoImagenTopo
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
        if self.zoom_imagen>4096:
            self.zoom_imagen=4096
        self._generar_imagen()


#
if __name__=="__main__":
    tester=Tester()
    #
    posiciones=[(0, 0), (34.69,1287.00)]
    for posicion in posiciones:
        log.info("Tester")
        print("# obtener_bioma_transicion posicion=%s"%str(posicion))
        print("biomas: "+str(tester.sistema.obtener_bioma_transicion(posicion)))
