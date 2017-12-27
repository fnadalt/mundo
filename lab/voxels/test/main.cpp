#include "PolyVoxCore/CubicSurfaceExtractorWithNormals.h"
#include "PolyVoxCore/MarchingCubesSurfaceExtractor.h"
#include "PolyVoxCore/SurfaceMesh.h"
#include "PolyVoxCore/SimpleVolume.h"

#include "pandabase.h"
#include "dtoolbase.h"
#include "lvector3.h"
#include "geomNode.h"
#include "geomVertexFormat.h"
#include "geomVertexArrayFormat.h"
#include "internalName.h"
#include "geomVertexData.h"
#include "geomVertexWriter.h"
#include "geomTristrips.h"
#include "geomTriangles.h"
#include "geom.h"
#include "boundingBox.h"

#include "objeto.h"

using namespace PolyVox;

void createSphere(Objeto& objeto, float fRadius)
{
        //This vector hold the position of the center of the volume
		//Vector3DFloat v3dVolCenter(volData.getWidth() / 2, volData.getHeight() / 2, volData.getDepth() / 2);
        LVector3 v3dVolCenter(objeto.obtener_dimension_x()/2,objeto.obtener_dimension_y()/2,objeto.obtener_dimension_z()/2);
        

        //This three-level for loop iterates over every voxel in the volume
        for (int z = 0; z < objeto.obtener_dimension_z(); z++)
        {
                for (int y = 0; y < objeto.obtener_dimension_y(); y++)
                {
                        for (int x = 0; x < objeto.obtener_dimension_x(); x++)
                        {
                                //Store our current position as a vector...
                                LVector3 v3dCurrentPos(x,y,z);
                                //And compute how far the current position is from the center of the volume
                                float fDistToCenter = (v3dCurrentPos - v3dVolCenter).length();

                                uint8_t uVoxelValue = 0;

                                //If the current voxel is less than 'radius' units from the center then we make it solid.
                                if(fDistToCenter <= fRadius)
                                {
                                        //Our new voxel value
                                        uVoxelValue = 255;
                                }

                                //Wrte the voxel value into the volume
                                objeto.establecer_valor(x, y, z, uVoxelValue);
                        }
                }
        }
}

int main(int argc, char *argv[])
{
	//
	Objeto obj("nombre",64,64,64,0);
	createSphere(obj,30.0);
	//
	obj.construir_cubos();
	//
	obj.construir_smooth();
	//
	return 0;
}
