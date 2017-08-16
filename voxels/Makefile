CC=g++
CFLAGS=-shared -fPIC -g
HDRS=voxels.h objeto.h
OBJS=objeto.o
PANDA=/home/flaco/build/panda3d/built
PANDA_INCLUDE=$(PANDA)/include
PANDA_LIB=$(PANDA)/lib
PANDA_BIN=$(PANDA)/bin
PANDA_PY=$(PANDA)/panda3d
INCLUDE_PATH=-I./include -I$(PANDA_INCLUDE) -I/usr/include/python2.7 -I/usr/include/eigen3
LIBRARY_PATH=-L. -L /home/flaco/build/polyvox-0.2.1/build/library/PolyVoxCore/ -L$(PANDA_LIB)
LIBS=-lPolyVoxCore -lpanda -lpandaexpress -lp3dtoolconfig -lp3dtool
LD_LIBRARY_PATH=$(PANDA_LIB)

%.o: %.cpp %.h
	$(CC) $(CFLAGS) $(INCLUDE_PATH) $(LIBRARY_PATH) $(LIBS) -c -o $@ $<

main: sharedlib
	$(CC) $(INCLUDE_PATH) $(LIBRARY_PATH) $(LIBS) -lvoxels -o main main.cpp

sharedlib: $(OBJS)
	$(CC) $(CFLAGS) $(LIBRARY_PATH) $(LIBS) -g -o libvoxels.so $(OBJS)

python_interrogate: $(HDRS)
	$(PANDA_BIN)/interrogate -I$(PANDA_INCLUDE) -S$(PANDA_INCLUDE)/parser-inc -Dvolatile -Dmutable -DCPPPARSER -D__STDC__=1 -D__cplusplus -D__inline -D__const=const -D__attribute__\(x\)= -D_LP64 -D_DEBUG -srcdir . -I. -oc libvoxels_igate.cxx -od libvoxels.in -fnames -string -refcount -assert -python-native -module voxels -library libvoxels -promiscuous $(HDRS)
	$(PANDA_BIN)/interrogate_module -oc voxels_module.cxx -module voxels -library voxels -python-native libvoxels.in
	$(CC) $(CFLAGS) -c $(INCLUDE_PATH) libvoxels_igate.cxx
	$(CC) $(CFLAGS) $(INCLUDE_PATH) -c -o voxels_module.o voxels_module.cxx

python: python_interrogate sharedlib $(OBJS)
	$(CC) $(CFLAGS) $(LIBRARY_PATH) $(LIBS) -o voxels.so voxels_module.o libvoxels_igate.o $(OBJS) $(PANDA_LIB)/libpanda.so $(PANDA_LIB)/libpandaexpress.so $(PANDA_LIB)/libp3dtool.so $(PANDA_LIB)/libp3dtoolconfig.so $(PANDA_PY)/core.so


clean:
	rm -rf main *.o *.so *_igate* *_module*
