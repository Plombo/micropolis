#include "glsprites.h"

static const int numFrames[SPRITE_COUNT] = {
	-1,
	5,
	8,
	11,
	8,
	16,
	3,
	6,
	4
};

GLSprites::GLSprites()
{
}

GLSprites::~GLSprites()
{
}

bool GLSprites::loadSprites()
{
	char filename[128];
	for(int snum = 1; snum < SPRITE_COUNT; snum++)
	{
		for(int frm = 0; frm < numFrames[snum]; frm++)
		{
			sprintf(filename, "/home/bryan/src/micropolis/src/images/micropolisEngine/obj%i-%i.png", snum, frm);
			if(!this->sprites[snum][frm].load(filename)) return false;
		}
	}
	
	return true;
}

void GLSprites::drawSprite(SimSprite* sprite)
{
	if(sprite->type == SPRITE_NOTUSED || sprite->type >= SPRITE_COUNT) return;
	if(sprite->frame == 0 || sprite->frame > numFrames[sprite->type]) return;
	this->sprites[sprite->type][sprite->frame-1].draw(sprite->x + sprite->xOffset,
	                                                  sprite->y + sprite->yOffset);
}

