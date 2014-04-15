#include <stdio.h>
#include <stdlib.h>
#include <GL/gl.h>
#include <GL/glext.h>
#include "sprite.h"
#include "readpng.h"

/**
 * @file sprite.cpp
 * 
 * The GLSprite class is a wrapper for a frame of the sprite animations used by
 * Micropolis.
 */

GLSprite::GLSprite()
{
	this->texture = 0;
	this->coordX = this->coordY = 0.0f;
}

GLSprite::~GLSprite()
{
}

/**
 * Loads the frame into a texture in the current OpenGL context.
 * @param path the path to the sprite frame in PNG format
 * @return true on success, false if the file could not be read
 */
bool GLSprite::load(char* path)
{
	int allocWidth, allocHeight;
	glGenTextures(1, &this->texture);
	glBindTexture(GL_TEXTURE_2D, this->texture);
	//printf("loading sprite %s\n", path);
	void* imageData = readPNG(path, &this->width, &this->height, &allocWidth, &allocHeight);
	if(imageData == NULL) return false;
	this->coordX = this->width / (float)allocWidth;
	this->coordY = this->height / (float)allocHeight;

	glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, allocWidth, allocHeight, 0,
	             GL_RGBA, GL_UNSIGNED_BYTE, imageData);
	free(imageData);
	
	glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE);
	glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE);
	glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR);
	glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR);
	
	return true;
}

/**
 * Draws the sprite at the given position.  Assumes that the texture for the
 * sprite has already been initialized with load() for the current GL context.
 */
void GLSprite::draw(int x, int y)
{
	int left = x;
	int right = x + this->width;
	int top = y;
	int bottom = y + this->height;
	int verts[8] = {left, top,
	                right, top,
	                right, bottom,
	                left, bottom};
	float texCoords[8] = {0, 0,
	                      coordX, 0,
	                      coordX, coordY,
	                      0, coordY};

	glEnable(GL_BLEND);
	glBindTexture(GL_TEXTURE_2D, this->texture);
	glEnableClientState(GL_VERTEX_ARRAY);
	glEnableClientState(GL_TEXTURE_COORD_ARRAY);
	glVertexPointer(2, GL_INT, 0, verts);
	glTexCoordPointer(2, GL_FLOAT, 0, texCoords);
	glDrawArrays(GL_QUADS, 0, 4);
	glDisableClientState(GL_TEXTURE_COORD_ARRAY);
	glDisableClientState(GL_VERTEX_ARRAY);
	glDisable(GL_BLEND);
}



