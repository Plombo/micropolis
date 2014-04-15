#ifndef SPRITE_H
#define SPRITE_H

#include <GL/gl.h>

class GLSprite
{
private:
	GLuint texture;
	float coordX;
	float coordY;
	int width;
	int height;

public:
	GLSprite();
	~GLSprite();
	bool load(char* path);
	void draw(int x, int y);
};

#endif

