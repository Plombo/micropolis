// this actually goes in Mesa

#include <windows.h>
#include <EGL/egl.h>

#include "eglconfig.h"
#include "eglcontext.h"
#include "egldefines.h"
#include "egldisplay.h"
#include "egldriver.h"
#include "eglcurrent.h"
#include "egllog.h"
#include "eglsurface.h"

struct WGL_egl_driver
{
	_EGLDriver base;
};

/** driver data of _EGLDisplay */
struct WGL_egl_display
{
	HDC deviceContext; // NULL for default display
};


/** subclass of _EGLContext */
struct WGL_egl_context
{
	_EGLContext Base;	/**< base class */

	HGLRC context;
};


/** subclass of _EGLSurface */
struct WGL_egl_surface
{
	_EGLSurface Base;	/**< base class */
	
	HDC deviceContext;

	void (*destroy)(Display *, GLXDrawable);
};


/** subclass of _EGLConfig */
struct WGL_egl_config
{
	_EGLConfig Base;	/**< base class */
	EGLBoolean double_buffered;
	int index;
};

