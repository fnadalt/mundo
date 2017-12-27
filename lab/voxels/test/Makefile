CC=g++
CFLAGS=-shared -fPIC #-g
HDRS=voxels.h objeto.h

PYTHON_INCLUDE=-I/usr/include/python3.6m
PYTHON_LIB=-L/usr/lib/python3.6 -lpython3.6m

P3D_INCLUDE=-I/usr/include/panda3d -I/usr/include/eigen3
P3D_PARSER_INC=-S/usr/include/panda3d/parser-inc -S/usr/include/panda3d -I/usr/include/panda3d -I.
P3D_LIB=-L/usr/lib/panda3d -lpanda -lpandaexpress -lp3dtoolconfig -lp3dtool
PANDA_PY=/lib/python3.6/site-packages/panda3d
P3D_BIN=/usr/bin

POLYVOX_INCLUDE=-I/usr/include/PolyVoxCore
POLYVOX_LIB=-L/usr/lib/PolyVoxCore -lPolyVoxCore

VOXELS_INCLUDE=-I.
VOXELS_LIB=-L. -lvoxels

main:
	echo ">>> main"
	$(CC) -g -I.. $(P3D_INCLUDE) $(P3D_LIB) $(POLYVOX_INCLUDE) $(POLYVOX_LIB) $(VOXELS_LIB) -o voxels main.cpp

