#include "PolyVoxCore/CubicSurfaceExtractorWithNormals.h"
#include "PolyVoxCore/MarchingCubesSurfaceExtractor.h"
#include "PolyVoxCore/SurfaceMesh.h"
#include "PolyVoxCore/SimpleVolume.h"

#include "objeto.h"

using namespace PolyVox;

void createSphereInVolume(SimpleVolume<uint8_t>& volData, float fRadius)
{
        //This vector hold the position of the center of the volume
        Vector3DFloat v3dVolCenter(volData.getWidth() / 2, volData.getHeight() / 2, volData.getDepth() / 2);

        //This three-level for loop iterates over every voxel in the volume
        for (int z = 0; z < volData.getDepth(); z++)
        {
                for (int y = 0; y < volData.getHeight(); y++)
                {
                        for (int x = 0; x < volData.getWidth(); x++)
                        {
                                //Store our current position as a vector...
                                Vector3DFloat v3dCurrentPos(x,y,z);
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
                                volData.setVoxelAt(x, y, z, uVoxelValue);
                        }
                }
        }
}

int main(int argc, char *argv[])
{
	SimpleVolume<uint8_t> volData(PolyVox::Region(Vector3DInt32(0,0,0), Vector3DInt32(63, 63, 63)));
	createSphereInVolume(volData, 30.0);
	SurfaceMesh<PositionMaterialNormal> mesh;
	CubicSurfaceExtractorWithNormals< SimpleVolume<uint8_t> > surfaceExtractor(&volData, volData.getEnclosingRegion(), &mesh);
	surfaceExtractor.execute();
	//
	Objeto obj("nombre",64,64,64,0);
	obj.construir_cubos();
	obj.construir_smooth();
	//
	return 0;
	//
	std::cout << "Numero de vertices: " << mesh.getNoOfVertices() << std::endl;
	std::cout << "Posicion Material Normal" << std::endl;
	const std::vector<PositionMaterialNormal>& verts=mesh.getVertices();
	std::vector<PositionMaterialNormal>::const_iterator iter_pmn(verts.begin());
	while(iter_pmn!=verts.end()){
		std::cout << (*iter_pmn).getPosition() << (*iter_pmn).getMaterial() << (*iter_pmn).getNormal() << std::endl;
		iter_pmn++;
	}
	//
	std::cout << "Numero de indices: " << mesh.getNoOfIndices() << std::endl;
	std::cout << "Indices" << std::endl;
	const std::vector<uint32_t>& indices=mesh.getIndices();
	std::vector<uint32_t>::const_iterator iter_i(indices.begin());
	while(iter_i!=indices.end()){
		std::cout << (*iter_i) << "\t";
		iter_i++;
	}
	std::cout << std::endl;
}
