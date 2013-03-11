#include <stdio.h>
#include <stdlib.h>
#include "micropolis.h"
#include "gltileengine.h"
#include "readpng.h"
#include <GL/gl.h>
#include <GL/glext.h>
#include <EGL/egl.h>

#define COL_BYTES (BYTES_PER_TILE * WORLD_H)
#define ROW_BYTES BYTES_PER_TILE

//#define USE_PBUFFER 1

/**
 * Constructor
 * @param engine a pointer to the main engine
 */
GLTileEngine::GLTileEngine(Micropolis* engine, void* mapBase)
{
	this->engine = engine;
	this->tiles = (unsigned char*) mapBase;
	this->width = this->height = this->texture = -1;
	this->display = EGL_NO_DISPLAY;
	this->surface = EGL_NO_SURFACE;
}

/**
 * Destructor
 */
GLTileEngine::~GLTileEngine()
{
	// TODO: free egl stuff here
}

/**
 * Sets the window to render to.
 * @todo support Windows; this might only work with X11 right now
 * @param win an X window ID
 */
void GLTileEngine::setWindow(int win)
{
	this->window = win;
}

/**
 * Convenience function for checking and displaying GL errors.
 * TODO: convert error messages into strings
 * @return the error code returned by glGetError()
 */
static GLenum checkGLError()
{
	GLenum error = glGetError();
	if(error)
	{
		printf("GL error: %i\n", error);
	}
	return error;
}

/**
 * Initializes the OpenGL context using EGL.
 */
bool GLTileEngine::initContext()
{
	eglBindAPI(EGL_OPENGL_API);
	this->display = eglGetDisplay(EGL_DEFAULT_DISPLAY);
	eglInitialize(this->display, NULL, NULL);
	
	// choose the default config for now
	EGLConfig config;
	int numConfig = 1;
	EGLint attribute_list[] = {
		EGL_RED_SIZE, 8,
		EGL_GREEN_SIZE, 8,
		EGL_BLUE_SIZE, 8,
		EGL_NONE
	};
	eglChooseConfig(this->display, attribute_list, &config, 1, &numConfig);
	this->context = eglCreateContext(this->display, config, EGL_NO_CONTEXT, NULL);
	
	// create the surface
#if USE_PBUFFER
	EGLint attribs[] = {
		EGL_WIDTH, -1,
		EGL_HEIGHT, -1,
		EGL_TEXTURE_FORMAT, EGL_TEXTURE_RGBA,
		EGL_TEXTURE_TARGET, EGL_TEXTURE_2D,
		EGL_NONE
	};
	attribs[1] = width;
	attribs[3] = height;
	this->surface = eglCreatePbufferSurface(this->display, config, attribs);
#else
	EGLint attribs[] = {EGL_NONE};
	this->surface = eglCreateWindowSurface(this->display, config, this->window, attribs);
#endif
	if(this->surface == EGL_NO_SURFACE)
	{
		printf("Allocating surface failed\n");
		return false;
	}
	
	return true;
}

/**
 * Sets the width and height of the area to render.
 */
bool GLTileEngine::setSize(int width, int height, unsigned char* buffer)
{
	if(width != this->width || height != this->height)
		return initGL(width, height, buffer);
	
	this->buffer = buffer;
	return true;
}

/**
 * Initializes SDL and OpenGL for use by this tile engine.
 */
bool GLTileEngine::initGL(int width, int height, unsigned char* buffer)
{
	this->width = width;
	this->height = height;
	
	initContext();
	
	// make the context current
	if(eglMakeCurrent(this->display, this->surface, this->surface, context) == EGL_FALSE)
	{
		printf("eglMakeCurrent returned false\n");
		return false;
	}
	
	glEnable(GL_TEXTURE_2D);
	glDisable(GL_DEPTH_TEST);
	glDisable(GL_LIGHTING);
	glDisable(GL_BLEND);
	glDisable(GL_DITHER);
	glViewport(0, 0, width, height);
	glMatrixMode(GL_MODELVIEW);
	glLoadIdentity();
	glClearColor(0.0, 0.0, 0.0, 0.0);
	glClear(GL_COLOR_BUFFER_BIT);
	if(checkGLError()) printf("\n");
	
	if(!loadTexture())
	{
		checkGLError();
		return false;
	}
	
	genTexCoords();
	this->buffer = buffer;
	checkGLError();
	
	return true;
}

#include <stdint.h>
static uint64_t ClockGetTime()
{
    timespec ts;
    clock_gettime(CLOCK_REALTIME, &ts);
    return (uint64_t)ts.tv_sec * 1000000LL + (uint64_t)ts.tv_nsec / 1000LL;
}

/**
 * Render a single tile using OpenGL.
 * @param x the x coordinate of the tile
 * @param y the y coordinate of the tile
 * @todo convert this from ye olde deprecated GL 1.1 glBegin() to something
 *	   more efficient like vertex arrays or VBOs
 */
void GLTileEngine::renderTile(float x, float y, int tile)
{
	if(tile < 0 || tile >= 960)
		return;

	float tcx = texCoords[tile<<1], tcy = texCoords[(tile<<1)+1];
	
	glTexCoord2f(tcx, tcy+tcyInc);
	glVertex2f(x, y+16);
	glTexCoord2f(tcx+tcxInc, tcy+tcyInc);
	glVertex2f(x+16, y+16);
	glTexCoord2f(tcx+tcxInc, tcy);
	glVertex2f(x+16, y);
	glTexCoord2f(tcx, tcy);
	glVertex2f(x, y);
}

/**
 * Render the tiles for a frame.
 * @param xOffset the leftmost X coordinate
 * @param yOffset the topmost Y coordinate
 */
void GLTileEngine::renderTiles(int xOffset, int yOffset)
{
	//uint64_t before = ClockGetTime();
#if USE_PBUFFER
	// copy the previous frame into the buffer that pycairo can use
	glReadPixels(0, 0, width, height, GL_BGRA, GL_UNSIGNED_BYTE, this->buffer);
#else
	eglSwapBuffers(this->display, this->surface); // we actually don't need to call SwapBuffers
#endif
	//printf("1/copy time: %f\r", 1000000.0/(ClockGetTime()-before));
	
	static uint64_t lasttime = 0;
	int width = this->width, height = this->height;
	glClear(GL_COLOR_BUFFER_BIT);
	glMatrixMode(GL_PROJECTION);
	glLoadIdentity();
#if USE_PBUFFER
	glOrtho(xOffset, xOffset + width, yOffset, yOffset + height, -1, 1);
#else
	glOrtho(xOffset, xOffset + width, yOffset + height, yOffset, -1, 1);
#endif

	int xMax = (xOffset + width) | 15;
	int yMax = (yOffset + width) | 15;
	xOffset &= 0xfffffff0;
	yOffset &= 0xfffffff0;

	glBindTexture(GL_TEXTURE_2D, this->texture);

	// do the actual drawing
	glBegin(GL_QUADS);
	for(int y=yOffset; y <= yMax; y+=16)
	{
		for(int x=xOffset; x <= xMax; x+=16)
		{
			int tileX = x>>4;
			int tileY = y>>4;

			if(tileX < 0 || tileX >= WORLD_W || tileY < 0 || tileY >= WORLD_H)
				continue;
			
			int tile = *(unsigned short*)(this->tiles + ROW_BYTES*tileY + COL_BYTES*tileX) & LOMASK;
			renderTile(x, y, tile);
		}
	}
	glEnd();
	
	// check for GL errors
	checkGLError();
	
	// finally finish the frame
	glFlush();

	if(lasttime)
		printf("FPS: %f\r", 1000000.0/(ClockGetTime()-lasttime));
	lasttime = ClockGetTime();
}

/**
 * Loads the texture with the tile images.
 */
bool GLTileEngine::loadTexture()
{
	// allocate a temporary buffer to hold the pixel data
	GLubyte* textureBuffer = (GLubyte*)malloc(256 * 1024 * 4);
	if(!textureBuffer)
	{
		printf("Couldn't alloc texture buffer, out of memory?\n");
		return false;
	}
	if(!readPNG("images/tileEngine/tiles.png", textureBuffer, 256 * 1024 * 4))
	{
		printf("Failed to load tile image!\n");
		free(textureBuffer);
		return false;
	}
	
	// actually create the tile map texture
	glGenTextures(1, &this->texture);
	glBindTexture(GL_TEXTURE_2D, this->texture);
	glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP);
	glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP);
	glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST);
	glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST);
	glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, 256, 1024, 0, GL_RGBA, GL_UNSIGNED_BYTE, textureBuffer);
	
	free(textureBuffer);
	
	return true;
}

void GLTileEngine::genTexCoords()
{
	const int texHeight = 1024; // use a POT texture for better compatibility
	
	this->tcxInc = 16.0 / 256.0;
	this->tcyInc = 16.0 / texHeight;
	
	int index = 0;
	for(int y=0; y<60; y++)
	{
		for(int x=0; x<16; x++)
		{
			this->texCoords[index++] = x * this->tcxInc;
			this->texCoords[index++] = y * this->tcyInc;
		}
	}
	assert(index == LENGTH_OF(this->texCoords));
}

void GLTileEngine::render


