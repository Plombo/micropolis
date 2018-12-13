#ifndef READPNG_H
#define READPNG_H

void* readPNG(const char* filename, int* width, int* height, int *allocWidth, int *allocHeight);
void savePNG(const char* filename, unsigned char* buffer, int width, int height);

#endif

