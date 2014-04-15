#ifndef GLRENDERER_H
#define GLRENDERER_H

#include "micropolis.h"
#include "glsprites.h"
#include <EGL/egl.h>

/** @return the smallest power of two that is greater than or equal to num */
static inline int nextPowerOfTwo(int num)
{
	if((num & (num - 1)) == 0) return num;
	else return (int)pow(2.0, ceil(log(num) / log(2.0)));
}

/**
 * The main rendering class.  Manages OpenGL state and rendering.  Currently
 * also directly responsible for drawing the map tiles and cursor.
 *
 * @todo When refactoring, rename to GLRenderer and split the actual tile engine
 * and cursor rendering into separate classes.
 */
class GLTileEngine {
private:
	EGLDisplay display;
	EGLContext context;
	EGLSurface surface;
	EGLConfig config;
	NativeWindowType window;

	int width;
	int height;
	int xOffset;
	int yOffset;
	int xMax;
	int yMax;
	float scale;
	
	unsigned int texture;
	unsigned int overlayTexture;
	float texCoords[1920]; // 1920 == 960 * 2
	float tcxInc;
	float tcyInc;
	Micropolis* engine;
	unsigned char* tiles;
	unsigned char* buffer;
	GLSprites sprites;

	void destroyContext();
	bool initContext();
	bool initSurface();
	bool loadTexture();
	void genTexCoords();
	void renderTile(float x, float y, int tile);
	bool initGL();
public:
	GLTileEngine(Micropolis* engine, void* mapBase);
	~GLTileEngine();
	void setWindow(int window);
	bool setSize(int width, int height, unsigned char* buffer);
	void renderTiles();
	void drawCursor(int x, int y, int cols, int rows);
	void drawSprite(SimSprite* sprite);
	void drawOverlay(void* buffer, int overlayType);
	void startFrame(int xOffset, int yOffset, float scale);
	void finishFrame();
};

#endif

