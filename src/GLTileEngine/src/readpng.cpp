#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <math.h>
#include <errno.h>
#include <string.h>
#include "png.h"
#include "readpng.h"
#include "gltileengine.h"

/**
 * Reads the contents of a PNG image into a buffer in memory.  Since it is meant
 * for reading texture images, the buffer it allocates and reads the image into
 * is created with power-of-two (although not necessarily equal) width and height.
 *
 * The buffer allocated by this function should be freed with free() when it is
 * no longer needed.
 *
 * @param filename the path to the PNG file
 * @param width pointer to return value for the actual width of the image
 * @param height pointer to return value for the actual height of the image
 * @param allocWidth pointer to return value for the allocated width of the image
 * @param allocHeight pointer to return value for the allocated height of the image
 * @return the allocated buffer, or NULL if an error occurs
 * @todo include "Error:" and filename in all error messages
 */
void* readPNG(const char* filename, int* width, int* height, int* allocWidth, int* allocHeight)
{
	png_structp png_ptr = NULL;
	png_infop info_ptr = NULL;
	int bitDepth, colorType;
	void* buf;
	png_uint_32* line;
	
	// open the file
	FILE* fp = fopen(filename, "rb");
	if(!fp)
	{
		printf("file %s not found (%s)\n", filename, strerror(errno));
		return NULL;
	}

	// initialize the libpng reading interface
	png_ptr = png_create_read_struct(PNG_LIBPNG_VER_STRING, NULL, NULL, NULL);
	if (!png_ptr) { printf("failed to create PNG read struct\n"); return NULL; }
	info_ptr = png_create_info_struct(png_ptr);
	if(!info_ptr) { printf("failed to create info struct\n"); goto error; }
	if(setjmp(png_jmpbuf(png_ptr))) { printf("failed to setjmp\n"); goto error; }
	
	// read header info from the file
	png_init_io(png_ptr, fp);
	png_read_info(png_ptr, info_ptr);
	png_get_IHDR(png_ptr, info_ptr, (png_uint_32*)width, (png_uint_32*)height, &bitDepth, &colorType, NULL, NULL, NULL);
	
	// allocate the buffer with power-of-two dimensions
	*allocWidth = nextPowerOfTwo(*width);
	*allocHeight = nextPowerOfTwo(*height);
	// FIXME: png_destroy_read_struct segfaults for some reason unless the "+1" is there (might actually be fixed now)
	buf = calloc((*allocWidth) * (*allocHeight+1), 4);
	line = (png_uint_32*)buf;
	
	// set color conversion settings
	if(bitDepth == 16)
		png_set_strip_16(png_ptr);
	if(colorType == PNG_COLOR_TYPE_RGB)
		png_set_filler(png_ptr, 0xff, PNG_FILLER_AFTER);
	
	// read the image data
	png_set_packing(png_ptr);
	for(unsigned y=0; y<(*height); y++)
	{
		png_read_row(png_ptr, (png_bytep) line, NULL);
		line += *allocWidth;
	}
	
	png_read_end(png_ptr, info_ptr);
	png_destroy_read_struct(&png_ptr, &info_ptr, NULL);
	fclose(fp);
	
	return buf;

error:
	fclose(fp);
	png_destroy_read_struct(&png_ptr, &info_ptr, NULL);
	return NULL;
}


// debugging function, TODO either remove or keep and write some actual documentation
void savePNG(const char* filename, unsigned char* buffer, int width, int height)
{
	uint32_t* vram32;
	int i, x, y;
	png_structp png_ptr;
	png_infop info_ptr;
	FILE* fp;
	uint8_t* line;

	fp = fopen(filename, "wb");
	if(!fp) return;
	png_ptr = png_create_write_struct(PNG_LIBPNG_VER_STRING, NULL, NULL, NULL);
	if(!png_ptr) return;
	info_ptr = png_create_info_struct(png_ptr);
	if(!info_ptr)
	{
		png_destroy_write_struct(&png_ptr, (png_infopp)NULL);
		fclose(fp);
		return;
	}
	png_init_io(png_ptr, fp);
	png_set_IHDR(png_ptr, info_ptr, width, height,
		         8, PNG_COLOR_TYPE_RGB_ALPHA, PNG_INTERLACE_NONE,
		         PNG_COMPRESSION_TYPE_DEFAULT, PNG_FILTER_TYPE_DEFAULT);
	png_write_info(png_ptr, info_ptr);
	line = (uint8_t*)malloc(width * 4);
	
	for(y=0; y<height; y++)
	{
		vram32 = (uint32_t*)(((uint8_t*)buffer)+y*width*4);
		for(i=0, x=0; x<width; x++)
		{
			uint32_t color = 0;
			uint8_t r = 0, g = 0, b = 0, a = 0;
			
			color = vram32[x];
			r = color & 0xff;
			g = (color >> 8) & 0xff;
			b = (color >> 16) & 0xff;
			a = (color >> 24) & 0xff;

			line[i++] = r;
			line[i++] = g;
			line[i++] = b;
			line[i++] = a;
		}
		png_write_row(png_ptr, line);
	}
	free(line);
	line = NULL;
	png_write_end(png_ptr, info_ptr);
	png_destroy_write_struct(&png_ptr, (png_infopp)NULL);
	fclose(fp);
}


