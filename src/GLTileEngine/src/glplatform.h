#ifndef GLPLATFORM_H
#define GLPLATFORM_H

#include <EGL/egl.h>

/**
 * The main rendering class.  Manages OpenGL state and rendering.  Currently
 * also directly responsible for drawing the map tiles and cursor.
 *
 * @todo When refactoring, rename to GLRenderer and split the actual tile engine
 * and cursor rendering into separate classes.
 */
class GLPlatform {
public:
	virtual bool initContext() = 0;
	virtual void destroyContext() = 0;
	virtual bool initSurface() = 0;
	virtual bool makeCurrent() = 0;
	virtual void swapBuffers() = 0;
	virtual void setWindow(int win) = 0;
};

class EGLPlatform : public GLPlatform {
private:
	EGLDisplay display;
	EGLContext context;
	EGLSurface surface;
	EGLConfig config;
	NativeWindowType window;
public:
	EGLPlatform();
	~EGLPlatform();
	bool initContext();
	void destroyContext();
	bool initSurface();
	bool makeCurrent();
	void swapBuffers();
	void setWindow(int win);
};

#endif

