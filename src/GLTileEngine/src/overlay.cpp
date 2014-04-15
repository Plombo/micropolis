#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <assert.h>
#include <GL/gl.h>
#include "micropolis.h"
#include "gltileengine.h"
#include "readpng.h"

/* The colormaps are used only by this file, but keep them in a header since they
 * are a lot of data. */
#include "colormaps.h"

typedef int (*TileFunction)(Micropolis* engine, int x, int y, int tile);

template <typename TileFormat>
class MapTextureMaker
{
private:
	int width;
	int height;
	int texWidth;
	int texHeight;
	const int* colorMap;
	TileFunction tileFunction;

public:
	float tcxScale;
	float tcyScale;
	
	MapTextureMaker(int width, int height, const int* colorMap, TileFunction func);
	void setOverlayTexture(Micropolis* engine, const void* mapBuf);
};

template <typename TileFormat>
MapTextureMaker<TileFormat>::MapTextureMaker(int width, int height, const int* colorMap, TileFunction func)
{
	this->colorMap = colorMap;
	this->tileFunction = func;
	this->width = width;
	this->height = height;
	this->texWidth = nextPowerOfTwo(width);
	this->texHeight = nextPowerOfTwo(height);
	this->tcxScale = (float)width / this->texWidth;
	this->tcyScale = (float)height / this->texHeight;
}

/**
 * Sets the texture image for the current GL texture to a visual representation
 * of the data in the given buffer.
 */
template <typename TileFormat>
void MapTextureMaker<TileFormat>::setOverlayTexture(Micropolis* engine, const void* mapBuf)
{
	int* texImage = (int*)malloc(texWidth * texHeight * sizeof(int));
	int* dst = texImage;
	TileFormat* base = (TileFormat*)mapBuf;
	for(int y=0; y < height; y++)
	{
		TileFormat* src = base;
		for(int x=0; x < width; x++)
		{
			int result;
			if(tileFunction)
				result = tileFunction(engine, x, y, *src);
			else
				result = *src;
			*dst++ = colorMap[result];
			src += height;
		}
		base++;
		dst += (texWidth - width);
	}
	
	glTexImage2D(GL_TEXTURE_2D, 0, 4, texWidth, texHeight, 0, GL_RGBA,
	             GL_UNSIGNED_BYTE, texImage);

#if 0
	// save buffer overlay as PNG (for debugging)
	FILE* fp = fopen("overlay.png", "rb");
	if(fp) fclose(fp);
	else savePNG("overlay.png", (Byte*)texImage, texWidth, texHeight);
#endif
	
	free(texImage);
}

int powerGridTileFunction(Micropolis* engine, int x, int y, int value)
{
	enum powerState {transparent, unpowered, powered, conductive};
	
	short tile = engine->map[x][y];
	if((tile & LOMASK) < LASTFIRE)
		return transparent;
	else if(tile & ZONEBIT)
		return (tile & PWRBIT) ? powered : unpowered;
	else
		return (tile & CONDBIT) ? conductive : transparent;
}

int coverageTileFunction(Micropolis* engine, int x, int y, int value)
{
	return max(0, min(value, 255));
}

int growthTileFunction(Micropolis* engine, int x, int y, int value)
{
	return max(0, min(int(((value * 256) / 200) + 128), 255));
}

/**
 * Draws the given map overlay in the current GL context.
 * @param mapBuf the map buffer (from the engine) with the data for the overlay
 * @param overlayType the type of the overlay (one of enum MapType in micropolis.h)
 */
void GLTileEngine::drawOverlay(void* mapBuf, int overlayType)
{
	static MapTextureMaker<Byte> powerOverlay(WORLD_W, WORLD_H, powerGridColorMap, powerGridTileFunction);
	static MapTextureMaker<Byte> densityOverlay(WORLD_W_2, WORLD_H_2, dataColorMap, NULL);
	static MapTextureMaker<unsigned short> coverageOverlay(WORLD_W_8, WORLD_H_8, dataColorMap, coverageTileFunction);
	static MapTextureMaker<short> growthOverlay(WORLD_W_8, WORLD_H_8, rateColorMap, growthTileFunction);
	
	float tcxScale = 1.0f, tcyScale = 1.0f;
	
	glBindTexture(GL_TEXTURE_2D, this->overlayTexture);
	
	switch(overlayType)
	{
	case MAP_TYPE_POWER:
		powerOverlay.setOverlayTexture(this->engine, mapBuf);
		tcxScale = powerOverlay.tcxScale;
		tcyScale = powerOverlay.tcyScale;
		break;
	case MAP_TYPE_TRAFFIC_DENSITY:
	case MAP_TYPE_POLLUTION:
	case MAP_TYPE_POPULATION_DENSITY:
	case MAP_TYPE_CRIME:
	case MAP_TYPE_LAND_VALUE:
		densityOverlay.setOverlayTexture(this->engine, mapBuf);
		tcxScale = densityOverlay.tcxScale;
		tcyScale = densityOverlay.tcyScale;
		break;
	case MAP_TYPE_FIRE_RADIUS:
	case MAP_TYPE_POLICE_RADIUS:
		coverageOverlay.setOverlayTexture(this->engine, mapBuf);
		tcxScale = coverageOverlay.tcxScale;
		tcyScale = coverageOverlay.tcyScale;
		break;
	case MAP_TYPE_RATE_OF_GROWTH:
		growthOverlay.setOverlayTexture(this->engine, mapBuf);
		tcxScale = growthOverlay.tcxScale;
		tcyScale = growthOverlay.tcyScale;
		break;
	default:
		return;
	}
	
	int left = max(0, this->xOffset);
	int right = min(WORLD_W*16, this->xMax);
	int top = max(0, this->yOffset);
	int bottom = min(WORLD_H*16, this->yMax);
	float tcLeft = tcxScale * left / (WORLD_W * 16.0);
	float tcRight = tcxScale * right / (WORLD_W * 16.0);
	float tcTop = tcyScale * top / (WORLD_H * 16.0);
	float tcBottom = tcyScale * bottom / (WORLD_H * 16.0);
	
	glEnable(GL_BLEND);
	glBegin(GL_QUADS);
	glTexCoord2f(tcLeft, tcTop);
	glVertex2f(left, top);
	glTexCoord2f(tcRight, tcTop);
	glVertex2f(right, top);
	glTexCoord2f(tcRight, tcBottom);
	glVertex2f(right, bottom);
	glTexCoord2f(tcLeft, tcBottom);
	glVertex2f(left, bottom);
	glEnd();
	glDisable(GL_BLEND);
}

