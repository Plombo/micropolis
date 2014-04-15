#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include "micropolis.h"
#include "gltileengine.h"
#include "sprite.h"
#include "overlay.h"
#include "readpng.h"
#include <GL/gl.h>
#include <GL/glext.h>
#include <EGL/egl.h>

#define COL_BYTES (BYTES_PER_TILE * WORLD_H)
#define ROW_BYTES BYTES_PER_TILE

//#define USE_PBUFFER 1
//#define USE_PIXMAP 1

/**
 * Constructor
 * @param engine a pointer to the main engine
 */
GLTileEngine::GLTileEngine(Micropolis* engine, void* mapBase)
{
	this->engine = engine;
	this->tiles = (unsigned char*) mapBase;
	this->width = this->height = this->texture = -1;
	this->surface = EGL_NO_SURFACE;
	this->context = EGL_NO_CONTEXT;
	this->window = 0;

	// we can go ahead and initialize EGL here
	this->display = eglGetDisplay(EGL_DEFAULT_DISPLAY);
	eglBindAPI(EGL_OPENGL_API);
	eglInitialize(this->display, NULL, NULL);
	
	// TODO: move this into a separate init() function so we can return false
	//if(!initContext()) return false;
	initContext();
}

/**
 * Destructor
 */
GLTileEngine::~GLTileEngine()
{
	// destroying the context will free everything that needs to be freed
	destroyContext();
}

/**
 * Sets the window to render to.
 * @todo support Windows; this might only work with X11 right now
 * @param win an X window ID
 */
void GLTileEngine::setWindow(int win)
{
	this->window = win;
	initSurface();
	initGL();
	setSize(this->width, this->height, this->buffer);
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
 * Frees all resources associated with the current OpenGL context, if there is
 * one.
 */
void GLTileEngine::destroyContext()
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
bool GLTileEngine::initContext()
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

bool GLTileEngine::initSurface()
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

/**
 * Sets the width and height of the area to render.
 * @param width the width of the displayed area
 * @param height the height of the displayed area
 * @param buffer the buffer to do glReadPixels into, with a size of at least
 *               (width*height*4)
 * @return true on success, false on error
 * @todo remove buffer as soon as we can remove the glReadPixels fallback
 */
bool GLTileEngine::setSize(int width, int height, unsigned char* buffer)
{
	this->buffer = buffer;
	if(width != this->width || height != this->height)
	{
		this->width = width;
		this->height = height;
		glViewport(0, 0, width, height); //return initGL(width, height);
	}
	return true;
}

/**
 * Initializes EGL and OpenGL for use by this tile engine.
 */
bool GLTileEngine::initGL()
{
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
	
	// initialize overlay texture
	glGenTextures(1, &this->overlayTexture);
	glBindTexture(GL_TEXTURE_2D, this->overlayTexture);
	glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE);
	glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE);
	glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR);
	glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR);
	
	genTexCoords();
	if(!this->sprites.loadSprites())
	{
		printf("Failed to load one or more sprites\n");
		return false;
	}
	
	checkGLError();
	
	return true;
}

void GLTileEngine::startFrame(int xOffset, int yOffset, float scale)
{
	glClear(GL_COLOR_BUFFER_BIT);
	glMatrixMode(GL_PROJECTION);
	glLoadIdentity();
	
	float xMax = roundf(xOffset + this->width / scale);
	float yMax = roundf(yOffset + this->height / scale);
	
#if USE_PBUFFER
	glOrtho(xOffset, xMax, yOffset, yMax, -1, 1);
#else
	glOrtho(xOffset, xMax, yMax, yOffset, -1, 1);
#endif

	this->xOffset = xOffset;
	this->yOffset = yOffset;
	this->xMax = (int)xMax;
	this->yMax = (int)yMax;
	this->scale = scale;
}

void GLTileEngine::finishFrame()
{
	checkGLError();
	glFinish();
#if USE_PBUFFER
	// copy the frame contents into a buffer that pycairo can use
	glReadPixels(0, 0, this->width, this->height, GL_BGRA, GL_UNSIGNED_BYTE, this->buffer);
#else
	// render directly into the target window
	eglSwapBuffers(this->display, this->surface);
#endif
}

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
 * @todo This can be simplified and improved significantly by just rendering a
 *       pre-created vertex array of the entire tilemap on each frame.  It will
 *       reduce overhead and actually be faster.
 */
void GLTileEngine::renderTiles()
{
	static uint64_t lasttime = 0;
	int width = this->width, height = this->height;
	int xOffset = this->xOffset, yOffset = this->yOffset;

	xOffset &= 0xfffffff0;
	yOffset &= 0xfffffff0;

	glBindTexture(GL_TEXTURE_2D, this->texture);
	GLenum filter = this->scale == 1.0f ? GL_NEAREST : GL_LINEAR;
	glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, filter);
	glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, filter);

	// do the actual drawing
	glBegin(GL_QUADS);
	for(int y=yOffset; y <= this->yMax; y+=16)
	{
		for(int x=xOffset; x <= this->xMax; x+=16)
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

	if(lasttime)
		printf("FPS: %f\r", 1000000.0/(ClockGetTime()-lasttime));
	lasttime = ClockGetTime();
}

/**
 * Loads the texture with the tile images.
 */
bool GLTileEngine::loadTexture()
{
	int width, height, allocWidth, allocHeight;

	// read the tile data from a PNG image on the filesystem
	void* textureBuffer = readPNG("images/micropolisEngine/tiles_borders.png", &width, &height, &allocWidth, &allocHeight);
	if(textureBuffer == NULL) return false;

	// actually create the tile map texture
	glGenTextures(1, &this->texture);
	glBindTexture(GL_TEXTURE_2D, this->texture);
	glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE);
	glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE);
	glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST);
	glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST);
	glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, allocWidth, allocHeight, 0, GL_RGBA, GL_UNSIGNED_BYTE, textureBuffer);

	// don't forget to free the buffer allocated by readPNG!
	free(textureBuffer);
	
	return true;
}

void GLTileEngine::genTexCoords()
{
	// using POT texture dimensions for better compatibility with outdated hardware
	const int texWidth = 512;
	const int texHeight = 2048;
	
	this->tcxInc = 16.0 / texWidth;
	this->tcyInc = 16.0 / texHeight;
	
	double tcxPerTile = 18.0 / texWidth;
	double tcyPerTile = 18.0 / texHeight;
	double tcxOffset = 1.0 / texWidth;
	double tcyOffset = 1.0 / texHeight;
	
	int index = 0;
	for(int y=0; y<60; y++)
	{
		for(int x=0; x<16; x++)
		{
			this->texCoords[index++] = x * tcxPerTile + tcxOffset;
			this->texCoords[index++] = y * tcyPerTile + tcyOffset;
		}
	}
	assert(index == LENGTH_OF(this->texCoords));
}

void GLTileEngine::drawCursor(int x, int y, int cols, int rows)
{
	// align to top left of tile
	x = x & 0xfffffff0;
	y = y & 0xfffffff0;

	glBindTexture(GL_TEXTURE_2D, 0);
	glEnable(GL_BLEND);
	glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA);
	glColor4f(0.4f, 0.75f, 1.0f, 0.6f);
	GLint verts[8];
	glEnableClientState(GL_VERTEX_ARRAY);
	for(int ty=0; ty<rows; ty++)
	{
		verts[1] = verts[3] = y + 16*(ty+1);
		verts[5] = verts[7] = y + 16*ty;
		for(int tx=0; tx<cols; tx++)
		{
			verts[0] = verts[6] = x + 16*tx;
			verts[2] = verts[4] = x + 16*(tx+1);
			glVertexPointer(2, GL_INT, 0, verts);
			glDrawArrays(GL_QUADS, 0, 4);
		}
	}
	glDisableClientState(GL_VERTEX_ARRAY);
	glDisable(GL_BLEND);
	glColor4f(1.0f, 1.0f, 1.0f, 1.0f);
}

void GLTileEngine::drawSprite(SimSprite* sprite)
{
	this->sprites.drawSprite(sprite);
}


