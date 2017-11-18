from panda3d.core import StackedPerlinNoise2, PerlinNoise2
import math

import logging
log=logging.getLogger(__name__)

class HeightMap():
    """HeightMap functionally maps any x and y to the appropriate height for realistic terrain."""

    def __init__(self, id, flatHeight=0.3):

        self.id = id
        # the overall smoothness/roughness of the terrain
        self.smoothness = 150
        # how quickly altitude and roughness shift
        self.consistency = self.smoothness * 12
        # for realism the flatHeight should be at or very close to waterHeight
        self.flatHeight = flatHeight
        #creates noise objects that will be used by the getHeight function
        self.generateNoiseObjects()
        self.normalize()

    def normalize(self):
        #normalize the range of possible heights to be bounded [0,1]
        minmax = []
        for x in range(2):
            for y in range(2):
                minmax.append(self.getPrenormalizedHeight(x, y))
        min = 9999
        max = -9999
        for x in minmax:
            if x < min:
                min = x
            if x > max:
                max = x
        self.normalizerSub = min
        self.normalizerMult = 1.0 / (max-min)
        log.info("height normalized from [" + str(min) + "," + str(max) + "]")

    def generateStackedPerlin(self, perlin, frequency, layers, frequencySpread, amplitudeSpread, id):

        for x in range(layers):
            layer = PerlinNoise2(0, 0, 256, seed=id + x)
            layer.setScale(frequency / (math.pow(frequencySpread, x)))
            perlin.addLevel(layer, 1 / (math.pow(amplitudeSpread, x)))

    def generateNoiseObjects(self):
        """Create perlin noise."""

        # See getHeight() for more details....
        # where perlin 1 is low terrain will be mostly low and flat
        # where it is high terrain will be higher and slopes will be exagerrated
        # increase perlin1 to create larger areas of geographic consistency
        self.perlin1 = StackedPerlinNoise2()
        self.generateStackedPerlin(self.perlin1, self.consistency, 4, 2, 2.5, self.id)

        # perlin2 creates the noticeable noise in the terrain
        # without perlin2 everything would look unnaturally smooth and regular
        # increase perlin2 to make the terrain smoother
        self.perlin2 = StackedPerlinNoise2()
        self.generateStackedPerlin(self.perlin2, self.smoothness, 8, 2, 2.2, self.id + 100)


    def getPrenormalizedHeight(self, p1, p2):
        """Returns the height at the specified terrain coordinates.

        The input is a value from each of the noise functions

        """

        fh = self.flatHeight
        # p1 varies what kind of terrain is in the area, p1 alone would be smooth
        # p2 introduces the visible noise and roughness
        # when p1 is high the altitude will be high overall
        # when p1 is close to fh most of the visible noise will be muted
        return (p1 - fh + (p1 - fh) * (p2 - fh)) / 2 + fh
        # if p1 = fh, the whole equation simplifies to...
        # 1. (fh - fh + (fh - fh) * (p2 - fh)) / 2 + fh
        # 2. ( 0 + 0 * (p2 - fh)) / 2 + fh
        # 3. (0 + 0 ) / 2 + fh
        # 4. fh
        # The important part to understanding the equation is at step 2.
        # The closer p1 is to fh, the smaller the mutiplier for p2 becomes.
        # As p2 diminishes, so does the roughness.

    #@pstat
    def getHeight(self, x, y):
        """Returns the height at the specified terrain coordinates.

        The values returned should be between 0 and 1 and use the full range.
        Heights should be the smoothest and flatest at flatHeight.

        """
        p1 = (self.perlin1(x, y) + 1) / 2 # low frequency
        p2 = (self.perlin2(x, y) + 1) / 2 # high frequency

        return (self.getPrenormalizedHeight(p1, p2)-self.normalizerSub) * self.normalizerMult
