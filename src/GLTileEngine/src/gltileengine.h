#ifndef H_GLRENDERER
#define H_GLRENDERER

#include "micropolis.h"
#include <EGL/egl.h>

class GLTileEngine {
private:
	EGLDisplay display;
	EGLContext context;
	EGLSurface surface;
	NativeWindowType window;

	int width;
	int height;
	unsigned int texture;
	float texCoords[1920]; // 1920 == 960 * 2
	float tcxInc;
	float tcyInc;
	Micropolis* engine;
	unsigned char* tiles;
	unsigned char* buffer;

	bool initContext();
	bool createSurface();
	bool loadTexture();
	void genTexCoords();
	void renderTile(float x, float y, int tile);
public:
	GLTileEngine(Micropolis* engine, void* mapBase);
	~GLTileEngine();
	void setWindow(int window);
	bool initGL(int width, int height, unsigned char* buffer);
	bool setSize(int width, int height, unsigned char* buffer);
	void renderTiles(int xOffset, int yOffset);
};

#endif

