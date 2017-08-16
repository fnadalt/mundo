/*
 * This file was generated by:
 * /home/flaco/build/panda3d/built/bin/interrogate -I/home/flaco/build/panda3d/built/include -S/home/flaco/build/panda3d/built/include/parser-inc -Dvolatile -Dmutable -DCPPPARSER -D__STDC__=1 -D__cplusplus -D__inline -D__const=const -D__attribute__(x)= -D_LP64 -D_DEBUG -srcdir . -I. -oc libvoxels_igate.cxx -od libvoxels.in -fnames -string -refcount -assert -python-native -module voxels -library libvoxels -promiscuous voxels.h objeto.h 
 *
 */

#include "dtoolbase.h"
#include "interrogate_request.h"
#include "dconfig.h"
#include "pnotify.h"
#include <sstream>
#define PANDA_LIBRARY_NAME_libvoxels
#include "py_panda.h"
#include "extension.h"
#include "dcast.h"

#include "objeto.h"
#include "voxels.h"

#undef _POSIX_C_SOURCE
#undef _XOPEN_SOURCE
#define PY_SSIZE_T_CLEAN 1

#if PYTHON_FRAMEWORK
  #include <Python/Python.h>
#else
  #include "Python.h"
#endif

/**
 * Forward declarations for top-level class Objeto
 */
typedef Objeto Objeto_localtype;
Define_Module_Class(voxels, Objeto, Objeto_localtype, Objeto);
static struct Dtool_PyTypedObject *const Dtool_Ptr_Objeto = &Dtool_Objeto;
static void Dtool_PyModuleClassInit_Objeto(PyObject *module);
bool Dtool_ConstCoerce_Objeto(PyObject *args, Objeto const *&coerced, bool &manage);
bool Dtool_Coerce_Objeto(PyObject *args, Objeto *&coerced, bool &manage);

/**
 * Extern declarations for imported classes
 */
// LPoint3f
#ifndef LINK_ALL_STATIC
static struct Dtool_PyTypedObject *Dtool_Ptr_LPoint3f;
inline static LPoint3f *Dtool_Coerce_LPoint3f(PyObject *args, LPoint3f &coerced) {
  nassertr(Dtool_Ptr_LPoint3f != NULL, NULL);
  nassertr(Dtool_Ptr_LPoint3f->_Dtool_Coerce != NULL, NULL);
  return ((LPoint3f *(*)(PyObject *, LPoint3f &))Dtool_Ptr_LPoint3f->_Dtool_Coerce)(args, coerced);
}
#else
extern struct Dtool_PyTypedObject Dtool_LPoint3f;
static struct Dtool_PyTypedObject *const Dtool_Ptr_LPoint3f = &Dtool_LPoint3f;
extern LPoint3f *Dtool_Coerce_LPoint3f(PyObject *args, LPoint3f &coerced);
#endif

/**
 * Python wrappers for global functions
 */
/**
 * Python wrappers for functions of class Objeto
 */
/**
 * Python function wrapper for:
 * inline int Objeto::obtener_valor(LPoint3f index)
 * int Objeto::obtener_valor(int const &x, int const &y, int const &z)
 */
static PyObject *Dtool_Objeto_obtener_valor_4(PyObject *self, PyObject *args, PyObject *kwds) {
  Objeto *local_this = NULL;
  if (!Dtool_Call_ExtractThisPointer_NonConst(self, Dtool_Objeto, (void **)&local_this, "Objeto.obtener_valor")) {
    return NULL;
  }
  int parameter_count = (int)PyTuple_Size(args);
  if (kwds != NULL) {
    parameter_count += (int)PyDict_Size(kwds);
  }
  switch (parameter_count) {
  case 1:
    {
      PyObject *arg;
      if (Dtool_ExtractArg(&arg, args, kwds, "index")) {
        // 1-inline int Objeto::obtener_valor(LPoint3f index)
        LPoint3f arg_local;
        LPoint3f *arg_this = Dtool_Coerce_LPoint3f(arg, arg_local);
        if (!(arg_this != NULL)) {
          return Dtool_Raise_ArgTypeError(arg, 1, "Objeto.obtener_valor", "LPoint3f");
        }
        int return_value = (*local_this).obtener_valor(*arg_this);
        if (Dtool_CheckErrorOccurred()) {
          return NULL;
        }
        return Dtool_WrapValue(return_value);
      }
    }
    break;
  case 3:
    {
      // 1-int Objeto::obtener_valor(int const &x, int const &y, int const &z)
      int param1;
      int param2;
      int param3;
      static const char *keyword_list[] = {"x", "y", "z", NULL};
      if (PyArg_ParseTupleAndKeywords(args, kwds, "iii:obtener_valor", (char **)keyword_list, &param1, &param2, &param3)) {
        int return_value = (*local_this).obtener_valor((int const &)param1, (int const &)param2, (int const &)param3);
        if (Dtool_CheckErrorOccurred()) {
          return NULL;
        }
        return Dtool_WrapValue(return_value);
      }
    }
    break;
#ifndef NDEBUG
  default:
    return PyErr_Format(PyExc_TypeError,
                        "obtener_valor() takes 2 or 4 arguments (%d given)",
                        parameter_count + 1);
#endif
  }
  if (!_PyErr_OCCURRED()) {
    return Dtool_Raise_BadArgumentsError(
      "obtener_valor(const Objeto self, LPoint3f index)\n"
      "obtener_valor(const Objeto self, int x, int y, int z)\n");
  }
  return NULL;
}

#ifndef NDEBUG
static const char *Dtool_Objeto_obtener_valor_4_comment =
  "C++ Interface:\n"
  "obtener_valor(const Objeto self, LPoint3f index)\n"
  "obtener_valor(const Objeto self, int x, int y, int z)\n";
#else
static const char *Dtool_Objeto_obtener_valor_4_comment = NULL;
#endif

/**
 * Python function wrapper for:
 * void Objeto::establecer_valor(int const &x, int const &y, int const &z, int const &valor)
 */
static PyObject *Dtool_Objeto_establecer_valor_5(PyObject *self, PyObject *args, PyObject *kwds) {
  Objeto *local_this = NULL;
  if (!Dtool_Call_ExtractThisPointer_NonConst(self, Dtool_Objeto, (void **)&local_this, "Objeto.establecer_valor")) {
    return NULL;
  }
  // 1-void Objeto::establecer_valor(int const &x, int const &y, int const &z, int const &valor)
  int param1;
  int param2;
  int param3;
  int param4;
  static const char *keyword_list[] = {"x", "y", "z", "valor", NULL};
  if (PyArg_ParseTupleAndKeywords(args, kwds, "iiii:establecer_valor", (char **)keyword_list, &param1, &param2, &param3, &param4)) {
    (*local_this).establecer_valor((int const &)param1, (int const &)param2, (int const &)param3, (int const &)param4);
    return Dtool_Return_None();
  }
  if (!_PyErr_OCCURRED()) {
    return Dtool_Raise_BadArgumentsError(
      "establecer_valor(const Objeto self, int x, int y, int z, int valor)\n");
  }
  return NULL;
}

#ifndef NDEBUG
static const char *Dtool_Objeto_establecer_valor_5_comment =
  "C++ Interface:\n"
  "establecer_valor(const Objeto self, int x, int y, int z, int valor)\n";
#else
static const char *Dtool_Objeto_establecer_valor_5_comment = NULL;
#endif

/**
 * Python function wrapper for:
 * void Objeto::establecer_valores(int const &valor)
 */
static PyObject *Dtool_Objeto_establecer_valores_6(PyObject *self, PyObject *arg) {
  Objeto *local_this = NULL;
  if (!Dtool_Call_ExtractThisPointer_NonConst(self, Dtool_Objeto, (void **)&local_this, "Objeto.establecer_valores")) {
    return NULL;
  }
  // 1-void Objeto::establecer_valores(int const &valor)
  if (PyLongOrInt_Check(arg)) {
    long arg_val = PyLongOrInt_AS_LONG(arg);
#if (SIZEOF_LONG > SIZEOF_INT) && !defined(NDEBUG)
    if (arg_val < INT_MIN || arg_val > INT_MAX) {
      return PyErr_Format(PyExc_OverflowError,
                          "value %ld out of range for signed integer",
                          arg_val);
    }
#endif
    (*local_this).establecer_valores((int)arg_val);
    return Dtool_Return_None();
  }
  if (!_PyErr_OCCURRED()) {
    return Dtool_Raise_BadArgumentsError(
      "establecer_valores(const Objeto self, int valor)\n");
  }
  return NULL;
}

#ifndef NDEBUG
static const char *Dtool_Objeto_establecer_valores_6_comment =
  "C++ Interface:\n"
  "establecer_valores(const Objeto self, int valor)\n";
#else
static const char *Dtool_Objeto_establecer_valores_6_comment = NULL;
#endif

/**
 * Python function wrapper for:
 * Objeto::Objeto(std::string const &nombre, int const &nx, int const &ny, int const &nz, int const valor_inicial)
 */
static int Dtool_Init_Objeto(PyObject *self, PyObject *args, PyObject *kwds) {
  // 1-Objeto::Objeto(std::string const &nombre, int const &nx, int const &ny, int const &nz, int const valor_inicial)
  char *param0_str = NULL;
  Py_ssize_t param0_len;
  int param1;
  int param2;
  int param3;
  int param4;
  static const char *keyword_list[] = {"nombre", "nx", "ny", "nz", "valor_inicial", NULL};
  if (PyArg_ParseTupleAndKeywords(args, kwds, "s#iiii:Objeto", (char **)keyword_list, &param0_str, &param0_len, &param1, &param2, &param3, &param4)) {
    Objeto *return_value = new Objeto(std::string(param0_str, param0_len), (int const &)param1, (int const &)param2, (int const &)param3, (int const)param4);
    if (return_value == NULL) {
      PyErr_NoMemory();
      return -1;
    }
    if (Dtool_CheckErrorOccurred()) {
      delete return_value;
      return -1;
    }
    return DTool_PyInit_Finalize(self, (void *)return_value, &Dtool_Objeto, true, false);
  }
  if (!_PyErr_OCCURRED()) {
    Dtool_Raise_BadArgumentsError(
      "Objeto(str nombre, int nx, int ny, int nz, int valor_inicial)\n");
  }
  return -1;
}

bool Dtool_ConstCoerce_Objeto(PyObject *args, Objeto const *&coerced, bool &manage) {
  DTOOL_Call_ExtractThisPointerForType(args, &Dtool_Objeto, (void**)&coerced);
  if (coerced != NULL) {
    return true;
  }

  if (PyTuple_Check(args)) {
    if (PyTuple_GET_SIZE(args) == 5) {
      // 1-Objeto::Objeto(std::string const &nombre, int const &nx, int const &ny, int const &nz, int const valor_inicial)
      char *param0_str = NULL;
      Py_ssize_t param0_len;
      int param1;
      int param2;
      int param3;
      int param4;
      if (PyArg_ParseTuple(args, "s#iiii:Objeto", &param0_str, &param0_len, &param1, &param2, &param3, &param4)) {
        Objeto *return_value = new Objeto(std::string(param0_str, param0_len), (int const &)param1, (int const &)param2, (int const &)param3, (int const)param4);
        if (return_value == NULL) {
          PyErr_NoMemory();
          return false;
        }
        if (_PyErr_OCCURRED()) {
          delete return_value;
          return false;
        } else {
          coerced = return_value;
          manage = true;
          return true;
        }
      }
      PyErr_Clear();
    }
  }

  return false;
}

bool Dtool_Coerce_Objeto(PyObject *args, Objeto *&coerced, bool &manage) {
  DTOOL_Call_ExtractThisPointerForType(args, &Dtool_Objeto, (void**)&coerced);
  if (coerced != NULL) {
    if (!((Dtool_PyInstDef *)args)->_is_const) {
      // A non-const instance is required, which this is.
      return true;
    }
  }

  if (PyTuple_Check(args)) {
    if (PyTuple_GET_SIZE(args) == 5) {
      // 1-Objeto::Objeto(std::string const &nombre, int const &nx, int const &ny, int const &nz, int const valor_inicial)
      char *param0_str = NULL;
      Py_ssize_t param0_len;
      int param1;
      int param2;
      int param3;
      int param4;
      if (PyArg_ParseTuple(args, "s#iiii:Objeto", &param0_str, &param0_len, &param1, &param2, &param3, &param4)) {
        Objeto *return_value = new Objeto(std::string(param0_str, param0_len), (int const &)param1, (int const &)param2, (int const &)param3, (int const)param4);
        if (return_value == NULL) {
          PyErr_NoMemory();
          return false;
        }
        if (_PyErr_OCCURRED()) {
          delete return_value;
          return false;
        } else {
          coerced = return_value;
          manage = true;
          return true;
        }
      }
      PyErr_Clear();
    }
  }

  return false;
}

static void *Dtool_UpcastInterface_Objeto(PyObject *self, Dtool_PyTypedObject *requested_type) {
  Dtool_PyTypedObject *SelfType = ((Dtool_PyInstDef *)self)->_My_Type;
  if (SelfType != Dtool_Ptr_Objeto) {
    printf("Objeto ** Bad Source Type-- Requesting Conversion from %s to %s\n", Py_TYPE(self)->tp_name, requested_type->_PyType.tp_name); fflush(NULL);
    return NULL;
  }

  Objeto *local_this = (Objeto *)((Dtool_PyInstDef *)self)->_ptr_to_object;
  if (requested_type == Dtool_Ptr_Objeto) {
    return local_this;
  }
  return NULL;
}

static void *Dtool_DowncastInterface_Objeto(void *from_this, Dtool_PyTypedObject *from_type) {
  if (from_this == NULL || from_type == NULL) {
    return NULL;
  }
  if (from_type == Dtool_Ptr_Objeto) {
    return from_this;
  }
  return (void *) NULL;
}

/**
 * Python method tables for Objeto (Objeto)
 */
static PyMethodDef Dtool_Methods_Objeto[] = {
  {"obtener_valor", (PyCFunction) &Dtool_Objeto_obtener_valor_4, METH_VARARGS | METH_KEYWORDS, (const char *)Dtool_Objeto_obtener_valor_4_comment},
  {"obtenerValor", (PyCFunction) &Dtool_Objeto_obtener_valor_4, METH_VARARGS | METH_KEYWORDS, (const char *)Dtool_Objeto_obtener_valor_4_comment},
  {"establecer_valor", (PyCFunction) &Dtool_Objeto_establecer_valor_5, METH_VARARGS | METH_KEYWORDS, (const char *)Dtool_Objeto_establecer_valor_5_comment},
  {"establecerValor", (PyCFunction) &Dtool_Objeto_establecer_valor_5, METH_VARARGS | METH_KEYWORDS, (const char *)Dtool_Objeto_establecer_valor_5_comment},
  {"establecer_valores", &Dtool_Objeto_establecer_valores_6, METH_O, (const char *)Dtool_Objeto_establecer_valores_6_comment},
  {"establecerValores", &Dtool_Objeto_establecer_valores_6, METH_O, (const char *)Dtool_Objeto_establecer_valores_6_comment},
  {NULL, NULL, 0, NULL}
};

static PyNumberMethods Dtool_NumberMethods_Objeto = {
  0, // nb_add
  0, // nb_subtract
  0, // nb_multiply
#if PY_MAJOR_VERSION < 3
  0, // nb_divide
#endif
  0, // nb_remainder
  0, // nb_divmod
  0, // nb_power
  0, // nb_negative
  0, // nb_positive
  0, // nb_absolute
  0, // nb_bool
  0, // nb_invert
  0, // nb_lshift
  0, // nb_rshift
  0, // nb_and
  0, // nb_xor
  0, // nb_or
#if PY_MAJOR_VERSION < 3
  0, // nb_coerce
#endif
  0, // nb_int
  0, // nb_long
  0, // nb_float
#if PY_MAJOR_VERSION < 3
  0, // nb_oct
  0, // nb_hex
#endif
  0, // nb_inplace_add
  0, // nb_inplace_subtract
  0, // nb_inplace_multiply
#if PY_MAJOR_VERSION < 3
  0, // nb_inplace_divide
#endif
  0, // nb_inplace_remainder
  0, // nb_inplace_power
  0, // nb_inplace_lshift
  0, // nb_inplace_rshift
  0, // nb_inplace_and
  0, // nb_inplace_xor
  0, // nb_inplace_or
  0, // nb_floor_divide
  0, // nb_true_divide
  0, // nb_inplace_floor_divide
  0, // nb_inplace_true_divide
#if PY_VERSION_HEX >= 0x02050000
  0, // nb_index
#endif
#if PY_VERSION_HEX >= 0x03050000
  0, // nb_matrix_multiply
  0, // nb_inplace_matrix_multiply
#endif
};

struct Dtool_PyTypedObject Dtool_Objeto = {
  {
    PyVarObject_HEAD_INIT(NULL, 0)
    "voxels.Objeto",
    sizeof(Dtool_PyInstDef),
    0, // tp_itemsize
    &Dtool_FreeInstance_Objeto,
    0, // tp_print
    0, // tp_getattr
    0, // tp_setattr
#if PY_MAJOR_VERSION >= 3
    0, // tp_reserved
#else
    0, // tp_compare
#endif
    0, // tp_repr
    &Dtool_NumberMethods_Objeto,
    0, // tp_as_sequence
    0, // tp_as_mapping
    0, // tp_hash
    0, // tp_call
    0, // tp_str
    PyObject_GenericGetAttr,
    PyObject_GenericSetAttr,
    0, // tp_as_buffer
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE | Py_TPFLAGS_CHECKTYPES,
    0, // tp_doc
    0, // tp_traverse
    0, // tp_clear
    0, // tp_richcompare
    0, // tp_weaklistoffset
    0, // tp_iter
    0, // tp_iternext
    Dtool_Methods_Objeto,
    0, // tp_members
    0, // tp_getset
    0, // tp_base
    0, // tp_dict
    0, // tp_descr_get
    0, // tp_descr_set
    0, // tp_dictoffset
    Dtool_Init_Objeto,
    PyType_GenericAlloc,
    Dtool_new_Objeto,
    PyObject_Del,
    0, // tp_is_gc
    0, // tp_bases
    0, // tp_mro
    0, // tp_cache
    0, // tp_subclasses
    0, // tp_weaklist
    0, // tp_del
#if PY_VERSION_HEX >= 0x02060000
    0, // tp_version_tag
#endif
#if PY_VERSION_HEX >= 0x03040000
    0, // tp_finalize
#endif
  },
  TypeHandle::none(),
  Dtool_PyModuleClassInit_Objeto,
  Dtool_UpcastInterface_Objeto,
  Dtool_DowncastInterface_Objeto,
  (CoerceFunction)Dtool_ConstCoerce_Objeto,
  (CoerceFunction)Dtool_Coerce_Objeto,
};

static void Dtool_PyModuleClassInit_Objeto(PyObject *module) {
  (void) module; // Unused
  static bool initdone = false;
  if (!initdone) {
    initdone = true;
    // Dependent objects
    Dtool_Objeto._PyType.tp_base = (PyTypeObject *)Dtool_Ptr_DTOOL_SUPER_BASE;
    PyObject *dict = PyDict_New();
    Dtool_Objeto._PyType.tp_dict = dict;
    PyDict_SetItemString(dict, "DtoolClassDict", dict);
    if (PyType_Ready((PyTypeObject *)&Dtool_Objeto) < 0) {
      Dtool_Raise_TypeError("PyType_Ready(Objeto)");
      return;
    }
    Py_INCREF((PyTypeObject *)&Dtool_Objeto);
  }
}


/**
 * Module Object Linker ..
 */
void Dtool_libvoxels_RegisterTypes() {
#ifndef LINK_ALL_STATIC
  RegisterNamedClass("Objeto", Dtool_Objeto);
#endif
}

void Dtool_libvoxels_ResolveExternals() {
#ifndef LINK_ALL_STATIC
  // Resolve externally imported types.
  Dtool_Ptr_LPoint3f = LookupRuntimeTypedClass(LPoint3f::get_class_type());
#endif
}

void Dtool_libvoxels_BuildInstants(PyObject *module) {
  (void) module;
  PyModule_AddStringConstant(module, "_OBJETO_H_", "");
  PyModule_AddStringConstant(module, "OBJETOH", "");
  PyModule_AddStringConstant(module, "_VOXELS_H_", "");
  PyModule_AddStringConstant(module, "VOXELSH", "");
  // Objeto
  Dtool_PyModuleClassInit_Objeto(module);
  PyModule_AddObject(module, "Objeto", (PyObject *)&Dtool_Objeto);
}

static PyMethodDef python_simple_funcs[] = {
  // Support Function For Dtool_types ... for now in each module ??
  {"Dtool_BorrowThisReference", &Dtool_BorrowThisReference, METH_VARARGS, "Used to borrow 'this' pointer (to, from)\nAssumes no ownership."},
  {"Dtool_AddToDictionary", &Dtool_AddToDictionary, METH_VARARGS, "Used to add items into a tp_dict"},
  {NULL, NULL, 0, NULL}
};

struct LibraryDef libvoxels_moddef = {python_simple_funcs};
static InterrogateModuleDef _in_module_def = {
  1502912298,  /* file_identifier */
  "libvoxels",  /* library_name */
  "_kLK",  /* library_hash_name */
  "voxels",  /* module_name */
  "libvoxels.in",  /* database_filename */
  (InterrogateUniqueNameDef *)0,  /* unique_names */
  0,  /* num_unique_names */
  (void **)0,  /* fptrs */
  0,  /* num_fptrs */
  1,  /* first_index */
  21  /* next_index */
};

Configure(_in_configure_libvoxels);
ConfigureFn(_in_configure_libvoxels) {
  interrogate_request_module(&_in_module_def);
}

