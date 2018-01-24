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
# temperatura_actual(temperatura_media,estacion_normalizada,hora_normalizada)
# precipitacion_frecuencia(RainPerlinNoiseParams,altitud,latitud)
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
    DiaPeriodoAmanecer=0
    DiaPeriodoDia=1
    DiaPeriodoAtardecer=2
    DiaPeriodoNoche=3
    # temperatura; [0,1]->[-50,50]; media: [0.2,0.8]->[-30,30]
    TemperaturaPerlinNoiseParams=(8*1024.0, 196) # (escala, semilla)
    # precipitaciones; [0.0,1.0): 0.0=nula, 1.0=maxima
    PrecipitacionPerlinNoiseParams=(2*1024.0, 9016) # (escala, semilla)
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
        self.ruido_vegetacion=None
        # cursor:
        self.posicion_cursor=None
        # parametros:
        self.duracion_dia_segundos=1800
        # variables externas:
        self.ano=0
        self.dia=0
        self.periodo_dia=Sistema.DiaPeriodoAmanecer
        self.hora_normalizada=0.0
        self.temperatura_actual=None
        self.precipitacion_actual_tipo=Sistema.PrecipitacionTipoAgua
        self.precipitacion_actual_intensidad=Sistema.PrecipitacionIntensidadNula
        self.precipitacion_actual_duracion=0.0
        self.precipitacion_actual_t=0.0
        # variables internas:

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

    def obtener_temperatura_amplitud_dianoche(self, posicion):
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
        _escala=Sistema.PrecipitacionPerlinNoiseParams[0]
        _semilla=Sistema.PrecipitacionPerlinNoiseParams[1]
        self.ruido_precipitacion=PerlinNoise2(_escala, _escala, 256, _semilla)
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
        pass

    def _establecer_temperatura_actual(self, dt):
        pass
    
    def _establecer_precipitacion(self, dt):
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
# Tester
#
#
class Tester:
    
    def __init__(self):
        self.sistema=Sistema()
        self.sistema.iniciar()

#
if __name__=="__main__":
    tester=Tester()
    #
    posiciones=[(0, 0), (34.69,1287.00)]
    for posicion in posiciones:
        print("# obtener_bioma_transicion posicion=%s"%str(posicion))
        print("biomas: "+str(tester.sistema.obtener_bioma_transicion(posicion)))
