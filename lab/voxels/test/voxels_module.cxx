
#include "dtoolbase.h"
#include "interrogate_request.h"

#include "py_panda.h"

extern LibraryDef voxels_moddef;
extern void Dtool_voxels_RegisterTypes();
extern void Dtool_voxels_ResolveExternals();
extern void Dtool_voxels_BuildInstants(PyObject *module);

#if PY_MAJOR_VERSION >= 3 || !defined(NDEBUG)
#ifdef _WIN32
extern "C" __declspec(dllexport) PyObject *PyInit_voxels();
#elif __GNUC__ >= 4
extern "C" __attribute__((visibility("default"))) PyObject *PyInit_voxels();
#else
extern "C" PyObject *PyInit_voxels();
#endif
#endif
#if PY_MAJOR_VERSION < 3 || !defined(NDEBUG)
#ifdef _WIN32
extern "C" __declspec(dllexport) void initvoxels();
#elif __GNUC__ >= 4
extern "C" __attribute__((visibility("default"))) void initvoxels();
#else
extern "C" void initvoxels();
#endif
#endif

#if PY_MAJOR_VERSION >= 3
static struct PyModuleDef py_voxels_module = {
  PyModuleDef_HEAD_INIT,
  "voxels",
  NULL,
  -1,
  NULL,
  NULL, NULL, NULL, NULL
};

PyObject *PyInit_voxels() {
  Dtool_voxels_RegisterTypes();
  Dtool_voxels_ResolveExternals();

  LibraryDef *defs[] = {&voxels_moddef, NULL};

  PyObject *module = Dtool_PyModuleInitHelper(defs, &py_voxels_module);
  if (module != NULL) {
    Dtool_voxels_BuildInstants(module);
  }
  return module;
}

#ifndef NDEBUG
void initvoxels() {
  PyErr_SetString(PyExc_ImportError, "voxels was compiled for Python " PY_VERSION ", which is incompatible with Python 2");
}
#endif
#else  // Python 2 case

void initvoxels() {
  Dtool_voxels_RegisterTypes();
  Dtool_voxels_ResolveExternals();

  LibraryDef *defs[] = {&voxels_moddef, NULL};

  PyObject *module = Dtool_PyModuleInitHelper(defs, "voxels");
  if (module != NULL) {
    Dtool_voxels_BuildInstants(module);
  }
}

#ifndef NDEBUG
PyObject *PyInit_voxels() {
  PyErr_SetString(PyExc_ImportError, "voxels was compiled for Python " PY_VERSION ", which is incompatible with Python 3");
  return (PyObject *)NULL;
}
#endif
#endif

