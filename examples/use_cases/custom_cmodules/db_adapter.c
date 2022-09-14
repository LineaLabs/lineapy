#include <Python.h>

// actual place where stuff happens.
char *c_db_adapter(char *query)
{

	return query;
}

// python method wrapper for the c method. this is the one that interfaces with python calls and parses args etc,
// calls the c method and parses back the result to serve the python frontend
static PyObject *py_dbadapter(PyObject *self, PyObject *args)
{

	// Declare pointers that hold arg values passed
	char *query = NULL;

	// Parse arguments - expects a string query
	// instead of, use i for integers etc. eg isi will be integer, string, integer and
	// subsequent args will be vars that will be assigned in that order
	if (!PyArg_ParseTuple(args, "s", &query))
	{
		return NULL;
	}

	// Call c-function. pass all the args that were parsed above
	char *query_result = c_db_adapter(query);

	// return the results of the call. here, string is returned
	// for other concrete object types, refer https://docs.python.org/3/c-api/concrete.html
	return PyUnicode_FromString(query_result);
}

// wrapper around all the methods added. this is similar to __all__ variable that lists all methods exposed
static PyMethodDef DBMethods[] = {
	{"linea_db_execute", py_dbadapter, METH_VARARGS, "Function for counting primes in a range in c"},
	{NULL, NULL, 0, NULL}};

// this struct is equivalent to the module/__init__ file that holds the __all__ var.
static struct PyModuleDef dbmodule = {
	PyModuleDef_HEAD_INIT,
	"DBAdapters", // module name
	"C library for db connectivity",
	-1,
	DBMethods};

// this is equivalent to the entrypoint that exposes the module.
// The c file containing this init method should be used in the setup step to install this module
PyMODINIT_FUNC PyInit_DBAdapters(void)
{
	return PyModule_Create(&dbmodule);
};