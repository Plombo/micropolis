#ifndef GLSPRITES_H
#define GLSPRITES_H

#include "micropolis.h"
#include "sprite.h"

#define MAX_SPRITE_FRAMES 16

class GLSprites
{
private:
	GLSprite sprites[SPRITE_COUNT][MAX_SPRITE_FRAMES];
public:
	GLSprites();
	~GLSprites();
	bool loadSprites();
	void drawSprite(SimSprite* sprite);
};

#endif

