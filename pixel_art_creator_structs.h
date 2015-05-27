#ifndef __PIXEL__
#define __PIXEL__

typedef struct {
  unsigned char blue;
  unsigned char green;
  unsigned char red;
} Pixel;

float tColorCorrect(float aInput);

unsigned char transToRGB(float p, float q, float aInput);

unsigned char colorQuantization(unsigned char aColor, int aLevel);

#endif
