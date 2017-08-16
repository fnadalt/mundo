#ifndef _OBJETO_H_
#define _OBJETO_H_

#include "PolyVoxCore/CubicSurfaceExtractorWithNormals.h"
#include "PolyVoxCore/MarchingCubesSurfaceExtractor.h"
#include "PolyVoxCore/SurfaceMesh.h"
#include "PolyVoxCore/SimpleVolume.h"

#include "pandabase.h"
#include "lpoint3.h"

#include <vector>
#include <string>

class Objeto
{
public:
	Objeto(const std::string& nombre, const int& nx, const int& ny, const int& nz, const int valor_inicial);
	~Objeto();

	int obtener_valor(const int& x, const int& y, const int& z);
	inline int obtener_valor(LPoint3f index) {return 0;}
	void establecer_valor(const int& x, const int& y, const int& z, const int& valor);
	void establecer_valores(const int& valor);

private:
	std::string _nombre;
	int _nx, _ny, _nz;
	vector<vector<vector<int> > > _data;
	int _centro[3];
};

#endif
