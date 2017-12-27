#include "objeto.h"

#include "PolyVoxCore/CubicSurfaceExtractorWithNormals.h"
#include "PolyVoxCore/MarchingCubesSurfaceExtractor.h"
#include "PolyVoxCore/DefaultMarchingCubesController.h"
#include "PolyVoxCore/SurfaceMesh.h"
#include "PolyVoxCore/SimpleVolume.h"

#include "geomVertexFormat.h"
#include "geomVertexArrayFormat.h"
#include "internalName.h"
#include "geomVertexData.h"
#include "geomVertexWriter.h"
#include "geomTristrips.h"
#include "geomTriangles.h"
#include "geom.h"
#include "geomNode.h"
#include "boundingBox.h"

#include <iostream>
#include <string>
#include <sstream>

Objeto::Objeto(const string& nombre, const int& nx, const int& ny, const int& nz, const int& valor_inicial) :
	_nombre(nombre), _nx(nx), _ny(ny), _nz(nz)
{
	using namespace PolyVox;
	SimpleVolume<uint8_t>* volData=new SimpleVolume<uint8_t>(Region(Vector3DInt32(0,0,0), Vector3DInt32(_nx-1,_ny-1,_nz-1)));
	_volData=(void*)volData;
}

Objeto::~Objeto()
{
	using namespace PolyVox;
	SimpleVolume<uint8_t>* volData=static_cast<SimpleVolume<uint8_t>*>(_volData);
	delete volData;
}

int Objeto::obtener_valor(const int& x, const int& y, const int& z)
{
	if(x<0||x>=_nx){
		std::cout << "Objeto::obtener_valor valor incorrecto de x(" << x << ") dimension x=" << _nx << std::endl;
		return 0;
	}
	if(y<0||y>=_ny){
		std::cout << "Objeto::obtener_valor valor incorrecto de y(" << y << ") dimension y=" << _ny << std::endl;
		return 0;
	}
	if(z<0||z>=_nz){
		std::cout << "Objeto::obtener_valor valor incorrecto de z(" << z << ") dimension z=" << _nz << std::endl;
		return 0;
	}
	using namespace PolyVox;
	SimpleVolume<uint8_t>* volData=static_cast<SimpleVolume<uint8_t>*>(_volData);
	return volData->getVoxelAt(x,y,z);
}

void Objeto::establecer_valor(const int& x, const int& y, const int& z, const int& valor)
{
	if(x<0||x>=_nx){
		std::cout << "Objeto::establecer_valor valor incorrecto de x(" << x << ") dimension x=" << _nx << std::endl;
		return;
	}
	if(y<0||y>=_ny){
		std::cout << "Objeto::establecer_valor valor incorrecto de y(" << y << ") dimension y=" << _ny << std::endl;
		return;
	}
	if(z<0||z>=_nz){
		std::cout << "Objeto::establecer_valor valor incorrecto de z(" << z << ") dimension z=" << _nz << std::endl;
		return;
	}
	using namespace PolyVox;
	SimpleVolume<uint8_t>* volData=static_cast<SimpleVolume<uint8_t>*>(_volData);
	volData->setVoxelAt(x,y,z,valor);
}

void Objeto::establecer_valores(const int& valor)
{
	using namespace PolyVox;
	SimpleVolume<uint8_t>* volData=static_cast<SimpleVolume<uint8_t>*>(_volData);
	for(int ix=0; ix<_nx; ix++){
		for(int iy=0; iy<_ny; iy++){
			for(int iz=0; iz<_nz; iz++){
				volData->setVoxelAt(ix,iy,iz,valor);
			}
		}
	}
}

PT(GeomNode)  Objeto::construir_cubos()
{
	std::cout << "Objeto::construir_cubos():" << std::endl;
	using namespace PolyVox;
	SimpleVolume<uint8_t>* volData=static_cast<SimpleVolume<uint8_t>*>(_volData);
	SurfaceMesh<PositionMaterialNormal> mesh;
	// surface extraction
	CubicSurfaceExtractorWithNormals< SimpleVolume<uint8_t> > surfaceExtractor(volData, volData->getEnclosingRegion(), &mesh);
	surfaceExtractor.execute();
	// format
	PT(GeomVertexArrayFormat) array = new GeomVertexArrayFormat();
	array->add_column(InternalName::get_vertex(), 3, Geom::NT_stdfloat, Geom::C_point);
	array->add_column(InternalName::get_normal(), 3, Geom::NT_stdfloat, Geom::C_normal);
	PT(GeomVertexFormat) format = new GeomVertexFormat();
	format->add_array(array);
	// vertex data writers
	PT(GeomVertexData) vdata = new GeomVertexData(_nombre, GeomVertexFormat::register_format(format), Geom::UH_stream);
	vdata->unclean_set_num_rows(mesh.getNoOfVertices());
	GeomVertexWriter vwriter (vdata, InternalName::get_vertex());
	GeomVertexWriter nwriter (vdata, InternalName::get_normal());
	// primitive
	PT(GeomTriangles) prim = new GeomTriangles(Geom::UH_stream);
	// loop
	const std::vector<PositionMaterialNormal>& verts=mesh.getVertices();
	std::cout << "cantidad de vértices: " << verts.size() << std::endl;
	for(long i=0;i<verts.size();++i){
		const PositionMaterialNormal& vert=verts[i];
		Vector3DFloat pos=vert.getPosition();
		Vector3DFloat norm=vert.getNormal();
		vwriter.set_data3(pos.getX(),pos.getY(),pos.getZ());
		nwriter.set_data3(norm.getX(),norm.getY(),norm.getZ());
		std::cout << "vertice=" << pos << " normal=" << norm << std::endl;
	}
	std::cout << "primitivas:" << std::endl;
	for(long i=0;i<verts.size();i+=4){
		std::cout << "tris: " << i << std::endl;
		prim->add_vertex(i+0);
		prim->add_vertex(i+1);
		prim->add_vertex(i+2);
		prim->add_vertex(i+2);
		prim->add_vertex(i+1);
		prim->add_vertex(i+3);
	}
	// geom
	PT(Geom) geom=new Geom(vdata);
	geom->add_primitive(prim);
	geom->set_bounds_type(BoundingVolume::BT_box);
	// geom node
	PT(GeomNode) geom_node=new GeomNode(_nombre);
	geom_node->add_geom(geom);
	geom_node->set_bounds_type(BoundingVolume::BT_box);
	return geom_node;
}

PT(GeomNode) Objeto::construir_smooth()
{
	std::cout << "Objeto::construir_smooth():" << std::endl;
	using namespace PolyVox;
	SimpleVolume<uint8_t>* volData=static_cast<SimpleVolume<uint8_t>*>(_volData);
	SurfaceMesh<PositionMaterialNormal> mesh;
	// surface extraction
	DefaultMarchingCubesController<uint8_t> controller;
	Region region=volData->getEnclosingRegion();
	std::cout << "Objeto::construir_smooth() región: " << region.getLowerCorner() << " - " << region.getUpperCorner() << std::endl;
	MarchingCubesSurfaceExtractor< SimpleVolume<uint8_t> > surfaceExtractor(volData, region, &mesh, controller);
	surfaceExtractor.execute();
	// format
	PT(GeomVertexArrayFormat) array = new GeomVertexArrayFormat();
	array->add_column(InternalName::get_vertex(), 3, Geom::NT_stdfloat, Geom::C_point);
	array->add_column(InternalName::get_normal(), 3, Geom::NT_stdfloat, Geom::C_normal);
	PT(GeomVertexFormat) format = new GeomVertexFormat();
	format->add_array(array);
	// vertex data writers
	PT(GeomVertexData) vdata = new GeomVertexData(_nombre, GeomVertexFormat::register_format(format), Geom::UH_stream);
	vdata->unclean_set_num_rows(mesh.getNoOfVertices());
	GeomVertexWriter vwriter (vdata, InternalName::get_vertex());
	GeomVertexWriter nwriter (vdata, InternalName::get_normal());
	// primitive
	PT(GeomTriangles) prim = new GeomTriangles(Geom::UH_stream);
	// loops
	const std::vector<PositionMaterialNormal>& verts=mesh.getVertices();
	std::cout << "Objeto::construir_smooth() cantidad de vértices: " << mesh.getNoOfVertices() << std::endl;
	for(long i=0;i<mesh.getNoOfVertices();++i){
		const PositionMaterialNormal& vert=verts[i];
		Vector3DFloat pos=vert.getPosition();
		Vector3DFloat norm=vert.getNormal();
		vwriter.set_data3(pos.getX(),pos.getY(),pos.getZ());
		nwriter.set_data3(norm.getX(),norm.getY(),norm.getZ());
		std::cout << "vertice@" << i << "=" << pos << " normal=" << norm << std::endl;
	}
	const std::vector<uint32_t>& indices=mesh.getIndices();
	std::cout << "Objeto::construir_smooth() cantidad de índices: " << mesh.getNoOfIndices() << std::endl;
	for(long i=0;i<mesh.getNoOfIndices();++i){
		const uint32_t& indice=indices[i];
		std::cout << "índice@" << i << "=" << indice << std::endl;
		prim->add_vertex(indice);
	}
	//std::cout << "construir primitivas:" << std::endl;
	//for(long i=0;i<verts.size();i+=3){
		//std::cout << "tris: " << i << std::endl;
		//prim->add_vertex(i+0);
		//prim->add_vertex(i+1);
		//prim->add_vertex(i+2);
	//}
	// geom
	PT(Geom) geom=new Geom(vdata);
	geom->add_primitive(prim);
	geom->set_bounds_type(BoundingVolume::BT_box);
	// geom node
	PT(GeomNode) geom_node=new GeomNode(_nombre);
	geom_node->add_geom(geom);
	geom_node->set_bounds_type(BoundingVolume::BT_box);
	return geom_node;
}

std::string Objeto::obtener_descripcion()
{
	std::stringstream _descripcion;
	_descripcion << "Objeto::descripcion(): ";
	_descripcion << "nombre:'" << this->_nombre << "' ";
	_descripcion << "dimensiones:(" << this->_nx << "," << this->_ny << "," << this->_nz << ") ";
	_descripcion << std::endl;
	return _descripcion.str();
}

