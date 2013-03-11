#include <stdio.h>
#include <stdlib.h>
#include "png.h"
#include "readpng.h"

/**
 * Reads the contents of a PNG image into a buffer in memory.
 * @param filename the path to the PNG file
 * @param buf a pre-allocated buffer in memory
 * @param bufSize the allocated size in bytes of buf
 * @return true on success, false if an error occurs
 */
bool readPNG(const char* filename, void* buf, unsigned int bufSize)
{
	png_structp png_ptr = NULL;
	png_infop info_ptr = NULL;
	png_uint_32 width, height;
	int bitDepth, colorType;
	png_uint_32* line = (png_uint_32*)buf;
	
	// open the file
	FILE* fp = fopen(filename, "rb");
	if(!fp) { printf("file %s not found\n", filename); return false; }

	// initialize the libpng reading interface
	png_ptr = png_create_read_struct(PNG_LIBPNG_VER_STRING, NULL, NULL, NULL);
	if (!png_ptr) { printf("failed to create PNG read struct\n"); return false; }
	info_ptr = png_create_info_struct(png_ptr);
	if(!info_ptr) { printf("failed to create info struct\n"); goto error; }
	if(setjmp(png_jmpbuf(png_ptr))) { printf("failed to setjmp\n"); goto error; }
	
	// read header info from the file
	png_init_io(png_ptr, fp);
	png_read_info(png_ptr, info_ptr);
	png_get_IHDR(png_ptr, info_ptr, &width, &height, &bitDepth, &colorType, NULL, NULL, NULL);
	
	// read the image data
	if(bufSize < width * height * 4) { printf("buffer size too small %i\n", bitDepth); goto error; }
	png_set_packing(png_ptr);
	png_set_filler(png_ptr, 0xff, PNG_FILLER_AFTER);
	for(unsigned y=0; y<height; y++)
	{
		png_read_row(png_ptr, (png_bytep) line, NULL);
		line += width;
	}
	
	png_read_end(png_ptr, info_ptr);
	png_destroy_read_struct(&png_ptr, &info_ptr, NULL);
	
	return true;

error:
	fclose(fp);
	png_destroy_read_struct(&png_ptr, &info_ptr, NULL);
	return false;
}


