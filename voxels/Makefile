CC=g++
CFLAGS=-shared -fPIC #-g
HDRS=voxels.h objeto.h
OBJS=objeto.o

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

sharedlib: $(HDRS) $(OBJS)
	echo ">>> sharedlib"
	$(CC) $(CFLAGS) $(P3D_LIB) $(POLYVOX_LIB) $(PYTHON_LIB) -g -o libvoxels.so $(OBJS)

objeto.o: objeto.cpp objeto.h
	echo ">>> objeto.o"
	$(CC) $(CFLAGS) $(POLYVOX_INCLUDE) $(P3D_INCLUDE) -c -o objeto.o objeto.cpp

libvoxels.in: $(HDRS)
	echo ">>> python_interrogate: libvoxels.in libvoxels_igate.cxx"
	$(P3D_BIN)/interrogate $(P3D_PARSER_INC) -Dvolatile -Dmutable -DCPPPARSER -D__STDC__=1 -D__cplusplus -D__inline -D__const=const -D__attribute__\(x\)= -D_LP64 -D__cplusplus=201103L \
			-DEIGEN_MPL2_ONLY= -DEIGEN_NO_DEBUG= \
			-fnames -string -refcount -assert -noangles \
			-srcdir=. -oc libvoxels_igate.cxx -od libvoxels.in -python-native -module voxels -library voxels $(HDRS)

voxels_module.cxx: libvoxels.in
	echo ">>> python_interrogate: voxels_module.cxx"
	$(P3D_BIN)/interrogate_module -oc voxels_module.cxx -module voxels -library voxels -python-native libvoxels.in

python_interrogate: voxels_module.cxx
	echo ">>> python_interrogate: module"
	$(CC) $(CFLAGS) $(PYTHON_INCLUDE) $(P3D_INCLUDE) $(POLYVOX_INCLUDE) -c libvoxels_igate.cxx
	$(CC) $(CFLAGS) $(PYTHON_INCLUDE) $(P3D_INCLUDE) $(POLYVOX_INCLUDE) -c -o voxels_module.o voxels_module.cxx

python: python_interrogate sharedlib $(OBJS)
	echo ">>> python module"
	$(CC) $(CFLAGS) -o voxels.so voxels_module.o libvoxels_igate.o $(POLYVOX_LIB) $(OBJS) $(PANDA_PY)/core.*

clean:
	echo ">>> clean"
	rm -rf main *.o *_igate* *_module* *.in

clean_all: clean
	echo ">>> clean all"
	rm -rf voxels *.so
