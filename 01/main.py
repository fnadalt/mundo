#!/usr/bin/python

"""
Cambios:
* sistema de objetos
* personajes (objetos manejados por input)
* shaders, utilizar ShaderGenerator de base; modularizar shaders
* texturizador de terreno para probar alternativas
* modularizar Sistema
"""

from aplicacion import Aplicacion

if __name__=="__main__":
    aplic=Aplicacion()
    aplic.iniciar()
