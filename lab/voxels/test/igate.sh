#!/bin/bash
echo "interrogate"
interrogate  -Dvolatile -Dmutable -DCPPPARSER -D__STDC__=1 -D__cplusplus -D__inline -D__const=const -D__attribute__\(x\)= -D_LP64 -D__cplusplus=201103L \
			-fnames -string -refcount -assert -noangles \
			-srcdir=. -I. -S/usr/include/panda3d/parser-inc -S/usr/include/panda3d -I/usr/include/panda3d \
			-DEIGEN_MPL2_ONLY= -DEIGEN_NO_DEBUG= \
			-oc libvoxels_igate.cxx -od libvoxels.in -python-native -module voxels -library voxels voxels.h
echo "interrogate_module"
interrogate_module -oc voxels_module.cxx -library voxels -module voxels -python-native libvoxels.in
echo "libvoxels_igate"
g++ -fPIC -shared -I/usr/include/panda3d -I/usr/include/python3.6m -I/usr/include/eigen3 -c -o libvoxels_igate.o libvoxels_igate.cxx
echo "voxels_module"
g++ -fPIC -shared -I/usr/include/panda3d -I/usr/include/python3.6m -I/usr/include/eigen3 -c -o voxels_module.o voxels_module.cxx
echo "voxels.so!"
g++ -fPIC -shared -o voxels.so -L/usr/lib/python3.6/site-packages/panda3d -I/usr/include/panda3d -I/usr/include/python3.6m -lpython3.6m libvoxels_igate.o voxels_module.o /usr/lib/panda3d/libpanda.so.1.10 /usr/lib/panda3d/libpandaexpress.so.1.10 /usr/lib/panda3d/libp3dtool.so.1.10 /usr/lib/panda3d/libp3dtoolconfig.so.1.10 /usr/lib/python3.6/site-packages/panda3d/core.cpython-36m-x86_64-linux-gnu.so
