#ifndef H_MAP
#define H_MAP

#include "micropolis.h"

void renderMap(void* tileBuffer, unsigned char* buf);
void* createMapBuffer();

// XXX: hackity hack
size_t pointerAsInt(unsigned char* ptr);

#endif

