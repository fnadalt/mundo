#ifndef _OBJETO_H_
#define _OBJETO_H_

#include "pandabase.h"
#include "dtoolbase.h"
#include "geomNode.h"

class Objeto
{
private:
	string _nombre;
	int _nx, _ny, _nz;
	int _centro[3];
	void* _volData;
	int region[8]; // [x1,y1,z1,x2,y2,z2]

PUBLISHED:
	Objeto(const string& nombre, const int& nx, const int& ny, const int& nz, const int& valor_inicial);
	~Objeto();

	// nombre
	inline void establecer_nombre(const string& nombre) {_nombre=nombre;}
	inline string& obtener_nombre() {return _nombre;}
	
	// descripción
	string obtener_descripcion();
	
	// dimensiones
	inline int obtener_dimension_x() const {return _nx;}
	inline int obtener_dimension_y() const {return _ny;}
	inline int obtener_dimension_z() const {return _nz;}
	
	// valores
	int obtener_valor(const int& x, const int& y, const int& z);
	inline int obtener_valor(const LPoint3f& index) {return obtener_valor(index.get_x(),index.get_y(),index.get_z());}
	void establecer_valor(const int& x, const int& y, const int& z, const int& valor);
	inline void establecer_valor(const LPoint3f& index, const int& valor) {establecer_valor(index.get_x(),index.get_y(),index.get_z(), valor);}
	void establecer_valores(const int& valor);
	
	PT(GeomNode) construir_cubos();
	PT(GeomNode) construir_smooth();

};

#endif
