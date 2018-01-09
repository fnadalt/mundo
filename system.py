from panda3d.core import *

import logging
log=logging.getLogger(__name__)

#
#
# WorldSystem
#
#
# altitude(TopoPerlinNoiseParams,TopoHeight)
# latitude(position.y)
# temperature(TemperaturePerlinNoiseParams,altitude,latitude)
# rain(RainPerlinNoiseParams,altitude,latitude)
# biome(summer_temperature,winter_temperature,summer_rain_frequency,winter_rain_frequency,latitude,altitude)
class WorldSystem:
    
    # topography
    TopoHeight=300.0
    TopoOceanAltitude=TopoHeight/2.0
    TopoAltitudeLevelsCount=7 # [0,6]->[-3,-2,-1,0,1,2,3], 0=TopoOceanAltitude
    TopoLatitudeLevelsCount=7 # [0,6]->[-3,-2,-1,0,1,2,3]; 0=equator, 1=tropical, 2=cold, 3=polar
    TopoPerlinNoiseParams=[(256.0, 1.0), (128.0, 0.5)] # [(scale, amplitude), ...]
    # environment
    EnvironmentNull=0
    EnvironmentWater=1
    EnvironmentGround=2
    EnvironmentCave=3
    EnvironmentAir=4
    # year
    YearDayCount=364 # for the sake of calculations
    # seasons
    SeasonSummer=0
    SeasonAutumn=1
    SeasonWinter=2
    SeasonSpring=3
    SeasonSunInclinationRangeDeg=23
    # day
    DayPeriodDawn=0
    DayPeriodDay=1
    DayPeriodDusk=2
    DayPeriodNight=3
    # temperature
    TemperaturePerlinNoiseParams=[]
    # rain
    RainPerlinNoiseParams=[]
    RainTypeWater=0
    RainTypeSnow=1
    RainIntensityNull=0
    RainIntensityWeak=1
    RainIntensityModerate=2
    RainIntensityStorm=3
    # biomes
    BiomeNull=0
    BiomePolarDesert=1
    BiomeTundra=2
    BiomeTaiga=3
    BiomeGrassland=4
    BiomeShrubland=5
    BiomeDeciduousForest=6
    BiomeTemperateRainforest=7
    BiomeDesert=8
    BiomeSavanah=9
    BiomeTropicalSeasonalForest=10
    BiomeTropicalRainforest=11
    
    def __init__(self):
        # cursor:
        self.cursor_position=None
        # variables:
        self.year=0
        self.day=0
        self.day_period=WorldSystem.DayPeriodDawn
        self.normalized_hour=0.0
        self.current_temperature=None
        self.current_rain_type=WorldSystem.RainTypeWater
        self.current_rain_intensity=WorldSystem.RainIntensityNull
        self.current_rain_duration=0.0
        self.current_rain_time=0.0

    def load_initial_params(self, default=True):
        if default:
            self.cursor_position=Vec3(0, 0, 0)
            self.year=0
            self.day=0
            self.day_period=WorldSystem.DayPeriodDawn
            self.normalized_hour=0.0
            #set_current_temperature
            #set_rain
        else:
            # read from file
            pass
    
    def save_current_params(self):
        # write to file
        pass
    
    def init(self):
        pass
    
    def terminate(self):
        pass
    
    def update(self):
        pass

#
#
# TopoPointDescriptor
#
#
class TopoPointDescriptor:
    
    def __init__(self):
        # 3d
        self.position=None
        self.environment=None
        # 2d
        self.latitude=None
        self.biome=None
        self.daynight_temperature_amplitude=None
        self.summer_temperature=None
        self.winter_temperature=None
        self.summer_rain_frequency=None
        self.winter_rain_frequency=None
        self.summer_sun_inclination=None
        self.winter_sun_inclination=None
