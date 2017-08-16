#include "objeto.h"

#include <iostream>

Objeto::Objeto(const std::string& nombre, const int& nx, const int& ny, const int& nz, const int valor_inicial) :
	_nombre(nombre), _nx(nx), _ny(ny), _nz(nz)
{
	vector<int> vz(_nz, valor_inicial);
	vector<vector<int>> vy(_ny, vz);
	_data=vector<vector<vector<int>>>(_nx, vy);
}

Objeto::~Objeto()
{
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
	return _data[x][y][z];
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
	_data[x][y][z]=valor;
}

void Objeto::establecer_valores(const int& valor)
{
	for(int ix=0; ix<_nx; ix++){
		for(int iy=0; iy<_ny; iy++){
			for(int iz=0; iz<_nz; iz++){
				_data[ix][iy][iz]=valor;
			}
		}
	}
}
