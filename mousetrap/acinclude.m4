dnl a macro to check for ability to create python extensions
dnl  AM_CHECK_PYTHON_HEADERS([ACTION-IF-POSSIBLE], [ACTION-IF-NOT-POSSIBLE])
dnl function also defines PYTHON_INCLUDES
AC_DEFUN([AM_CHECK_PYTHON_HEADERS],
[AC_REQUIRE([AM_PATH_PYTHON])
AC_MSG_CHECKING(for headers required to compile python extensions)
dnl deduce PYTHON_INCLUDES
py_prefix=`$PYTHON -c "import sys; print sys.prefix"`
py_exec_prefix=`$PYTHON -c "import sys; print sys.exec_prefix"`
PYTHON_INCLUDES="-I${py_prefix}/include/python${PYTHON_VERSION}"
if test "$py_prefix" != "$py_exec_prefix"; then
  PYTHON_INCLUDES="$PYTHON_INCLUDES -I${py_exec_prefix}/include/python${PYTHON_VERSION}"
fi
AC_SUBST(PYTHON_INCLUDES)
dnl check if the headers exist:
save_CPPFLAGS="$CPPFLAGS"
CPPFLAGS="$CPPFLAGS $PYTHON_INCLUDES"
AC_TRY_CPP([#include <Python.h>],dnl
[AC_MSG_RESULT(found)
$1],dnl
[AC_MSG_RESULT(not found)
$2])
CPPFLAGS="$save_CPPFLAGS"
])

dnl AM_CHECK_PYMOD(MODNAME [,SYMBOL [,ACTION-IF-FOUND [,ACTION-IF-NOT-FOUND]]])
dnl Check if a module containing a given symbol is visible to python.
AC_DEFUN([AM_CHECK_PYMOD],
[AC_REQUIRE([AM_PATH_PYTHON])
py_mod_var=`echo $1['_']$2 | sed 'y%./+-%__p_%'`
AC_MSG_CHECKING(for ifelse([$2],[],,[$2 in ])python module $1)
AC_CACHE_VAL(py_cv_mod_$py_mod_var, [
ifelse([$2],[], [prog="
import sys
try:
	import $1
except ImportError:
	sys.exit(1)
except:
	sys.exit(0)
sys.exit(0)"], [prog="
import $1
import $1.$2"])
if $PYTHON -c "$prog" 1>&AC_FD_CC 2>&AC_FD_CC
  then
    eval "py_cv_mod_$py_mod_var=yes"
  else
    eval "py_cv_mod_$py_mod_var=no"
  fi
])
py_val=`eval "echo \`echo '$py_cv_mod_'$py_mod_var\`"`
if test "x$py_val" != xno; then
  AC_MSG_RESULT(yes)
  ifelse([$3], [],, [$3
])dnl
else
  AC_MSG_RESULT(no)
  ifelse([$4], [],, [$4
])dnl
fi
])

dnl AM_CHECK_PYORBIT_MOD(MODNAME [,ACTION-IF-FOUND [,ACTION-IF-NOT-FOUND]]])
dnl Check if a module containing a given ORBit module is visible to python.
AC_DEFUN([AM_CHECK_PYORBIT_MOD],
[AC_REQUIRE([AM_PATH_PYTHON])
py_mod_var=$1
AC_MSG_CHECKING(for PyORBit module $1)
AC_CACHE_VAL(py_cv_mod_$py_mod_var, [
prog="
import sys
try:
	import bonobo 
	import ORBit
	ORBit.load_typelib(\"$1\")
	module_name = \"$1\".replace(\"_\",\".\")
	__import__(module_name)
except:
	sys.exit(1)
sys.exit(0)"
if $PYTHON -c "$prog" 1>&AC_FD_CC 2>&AC_FD_CC
  then
    eval "py_cv_mod_$py_mod_var=yes"
  else
    eval "py_cv_mod_$py_mod_var=no"
  fi
])
py_val=`eval "echo \`echo '$py_cv_mod_'$py_mod_var\`"`
if test "x$py_val" != xno; then
  AC_MSG_RESULT(yes)
  ifelse([$2], [],, [$2
])dnl
else
  AC_MSG_RESULT(no)
  ifelse([$3], [],, [$3
])dnl
fi
])

dnl   PYDOC_CHECK()
AC_DEFUN([PYDOC_CHECK],
[
  dnl enable/disable pydoc documentation building
  AC_ARG_ENABLE(pydoc,
    AC_HELP_STRING([--enable-pydoc],
                   [use pydoc to build documentation [default=no]]),,
    enable_pydoc=no)

  have_pydoc=no
  if test x$enable_pydoc = xyes; then
    BIN_FILE=`which pydoc`
    AC_CHECK_FILE($BIN_FILE, PYDOC=$BIN_FILE)
  fi

  if test -z "$PYDOC"; then
    enable_pydoc=no
  fi
  AM_CONDITIONAL(ENABLE_PYDOC, test x$enable_pydoc = xyes)
])

dnl   DOXYGEN_CHECK()
AC_DEFUN([DOXYGEN_CHECK],
[
  dnl enable/disable doxygen documentation building
  AC_ARG_ENABLE(doxygen,
    AC_HELP_STRING([--enable-doxygen],
                   [Build doxygen documentation [default=no]]),,
    enable_doxygen=no)

  have_doxygen=no
  if test x$enable_doxygen = xyes; then
    BIN_FILE=`which doxygen`
    AC_CHECK_FILE($BIN_FILE, DOXYGEN=$BIN_FILE)
  fi

  if test -z "$DOXYGEN"; then
    enable_doxygen=no
  fi
  AM_CONDITIONAL(ENABLE_DOXYGEN, test x$enable_doxygen = xyes)
])

dnl   DOCBOOK_CHECK()
AC_DEFUN([DOCBOOK_CHECK],
[
  dnl enable/disable docbook documentation building
  AC_ARG_ENABLE(docbook,
    AC_HELP_STRING([--enable-docbook],
                   [Build docbook documentation [default=no]]),,
    enable_docbook=no)

  have_docbook=no
  if test x$enable_docbook = xyes; then
    BIN_FILE=`which xsltproc`
    AC_CHECK_FILE($BIN_FILE, XSLTPROC=$BIN_FILE)
  fi

  if test -z "$XSLTPROC"; then
    enable_docbook=no
  fi
  
  if [ ! test -f /usr/share/xml/gnome/xslt/docbook/html/db2html.xsl ]; then
    echo Install gnome-doc-utils for docbook html generation.
    enable_docbook=no
  fi
  
  AM_CONDITIONAL(ENABLE_DOCBOOK, test x$enable_docbook = xyes)
])

dnl
dnl JH_ADD_CFLAG(FLAG)
dnl checks whether the C compiler supports the given flag, and if so, adds
dnl it to $CFLAGS.  If the flag is already present in the list, then the
dnl check is not performed.
AC_DEFUN([JH_ADD_CFLAG],
[
case " $CFLAGS " in
*@<:@\	\ @:>@$1@<:@\	\ @:>@*)
  ;;
*)
  save_CFLAGS="$CFLAGS"
  CFLAGS="$CFLAGS $1"
  AC_MSG_CHECKING([whether [$]CC understands $1])
  AC_TRY_COMPILE([], [], [jh_has_option=yes], [jh_has_option=no])
  AC_MSG_RESULT($jh_has_option)
  if test $jh_has_option = no; then
    CFLAGS="$save_CFLAGS"
  fi
  ;;
esac])
