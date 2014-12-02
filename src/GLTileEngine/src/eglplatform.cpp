#include <stdio.h>
#include <stdlib.h>
#include <EGL/egl.h>
#include "glplatform.h"

EGLPlatform::EGLPlatform()
{
	// initialize EGL
	this->display = eglGetDisplay(EGL_DEFAULT_DISPLAY);
	eglBindAPI(EGL_OPENGL_API);
	eglInitialize(this->display, NULL, NULL);
	this->window = 0;
}

EGLPlatform::~EGLPlatform()
{
	destroyContext();
}

/**
 * Frees all resources associated with the current OpenGL context, if there is
 * one.
 */
void EGLPlatform::destroyContext()
{
	// release the current context and surface
	eglMakeCurrent(this->display, EGL_NO_SURFACE, EGL_NO_SURFACE, EGL_NO_CONTEXT);

	// destroy the context
	if(this->context != EGL_NO_CONTEXT)
	{
		eglDestroyContext(this->display, this->context);
		this->context = EGL_NO_CONTEXT;
	}

	// destroy the surface
	if(this->surface != EGL_NO_SURFACE)
	{
		//eglDestroySurface(this->display, this->surface);
		this->surface = EGL_NO_SURFACE;
	}
}

/**
 * Initializes the OpenGL context using EGL.
 */
bool EGLPlatform::initContext()
{
	// if there is already a current context, destroy it first
	destroyContext();

	// choose the default config for now
	int numConfigs = 1;
	
	EGLint attribute_list[] = {
		EGL_RED_SIZE, 8,
		EGL_GREEN_SIZE, 8,
		EGL_BLUE_SIZE, 8,
		EGL_SURFACE_TYPE, EGL_WINDOW_BIT,
		EGL_RENDERABLE_TYPE, EGL_OPENGL_BIT,
		EGL_NONE
	};
	if(!eglChooseConfig(this->display, attribute_list, &this->config, 1, &numConfigs))
	{
		printf("Choosing EGL config failed (error code: 0x%x)\n", eglGetError());
		return false;
	}
	else if(numConfigs == 0)
	{
		printf("No matching EGL configs\n");
		return false;
	}
	
	this->context = eglCreateContext(this->display, this->config, EGL_NO_CONTEXT, NULL);
	if(this->context == EGL_NO_CONTEXT)
	{
		printf("Error: creating OpenGL context failed (error code: 0x%x)\n", eglGetError());
		return false;
	}

#if USE_PBUFFER
	if(this->surface == EGL_NO_SURFACE)
	{
		if(!initSurface()) return false;
	}
#endif
	
	return true;
}

bool EGLPlatform::initSurface()
{
	// create the surface
#if USE_PBUFFER
	EGLint attribs[] = {
		EGL_WIDTH, width,
		EGL_HEIGHT, height,
		EGL_TEXTURE_FORMAT, EGL_TEXTURE_RGBA,
		EGL_TEXTURE_TARGET, EGL_TEXTURE_2D,
		EGL_NONE
	};
	this->surface = eglCreatePbufferSurface(this->display, this->config, attribs);
#elif USE_PIXMAP
	EGLint attribs[] = {EGL_NONE};
	this->surface = eglCreatePixmapSurface(this->display, this->config, this->pixmap, attribs);
#else
	EGLint attribs[] = {EGL_NONE};
	this->surface = eglCreateWindowSurface(this->display, this->config, this->window, NULL);
#endif
	if(this->surface == EGL_NO_SURFACE)
	{
		printf("Error: EGL surface creation failed (error code: 0x%x)\n", eglGetError());
		return false;
	}
	
	return true;
}

bool EGLPlatform::makeCurrent()
{
	return eglMakeCurrent(this->display, this->surface, this->surface, this->context) == EGL_TRUE;
}

void EGLPlatform::swapBuffers()
{
	eglSwapBuffers(this->display, this->surface);
}

void EGLPlatform::setWindow(int win)
{
	this->window = win;
}

