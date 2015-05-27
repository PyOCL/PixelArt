#include "pixel_art_creator_structs.h"

float tColorCorrect(float aInput)
{
  if (aInput < 0) {
    return aInput + 1;
  } else if (aInput > 1) {
    return aInput - 1;
  }
  return aInput;
}

unsigned char transToRGB(float p,
                         float q,
                         float aInput)
{
  if (aInput < 1/6.0f) {
    return (unsigned char)(p+((q-p)*6*aInput));
  } else if ( 1/6.0f < aInput && aInput < 0.5f) {
    return (unsigned char)q;
  } else if ( 0.5f <= aInput && aInput < 2/3.0f) {
    return (unsigned char)(p+((q-p)*6*(2/3.0f - aInput)));
  }
  return (unsigned char)p;
}

unsigned char colorQuantization(unsigned char aColor,
                                int aLevel)
{
  float b = round(255.0f / aLevel);
  unsigned char result = floor(fmin(255.0f, round(aColor / b) * b));
  return result;
}

__kernel void rgb_to_hsl_adjust_saturation_and_to_rgb(int aWidth,
                                                      int aHeight,
                                                      float aSaturationWeight,
                                                      __global Pixel* aBufferIn,
                                                      __global Pixel* aBufferOut) {
  // Please implement your kernel code here.
  unsigned int gid_x = get_global_id(0);
  unsigned int gid_y = get_global_id(1);
  unsigned int gid = gid_x + gid_y * aWidth;

  float r = aBufferIn[gid].red;
  float g = aBufferIn[gid].green;
  float b = aBufferIn[gid].blue;

  float max = fmax( fmax(r, g), b);
  float min = fmin( fmin(r, g), b);

  float h = 0.0f;
  float diff = max - min;
  if (max == min) {
  } else if (max == r && g >= b) {
    h = 60 * ((float)(g-b) / diff);
  } else if (max == r && g < b) {
    h = 60 * ((float)(g-b) / diff) + 360;
  } else if (max == g) {
    h = 60 * ((float)(b-r) / diff) + 120;
  } else if (max == b) {
    h = 60 * ((float)(r-g) / diff) + 240;
  }

  float l = (max+min) / 2.0f;
  float s = 0.0f;
  if (l==0 || max == min) {
  } else if (0 < l && l <= 0.5f) {
    s = diff / (2 * l);
  } else {
    s = diff / (2 - 2 * l);
  }

  s = fmin(1.0f, s * aSaturationWeight);

  float q = l < 0.5f ? l * (1+s) : l + s - (l*s);
  float p = 2 * l - q;
  float hk = h / 360.0f;

  float tr = tColorCorrect(hk + 1/3.0f);
  float tg = tColorCorrect(hk);
  float tb = tColorCorrect(hk - 1/3.0f);

  aBufferOut[gid].red = transToRGB(p, q, tr) ;
  aBufferOut[gid].green = transToRGB(p, q, tg);
  aBufferOut[gid].blue = transToRGB(p, q, tb);
}

__kernel void to_indexed_color(int aWidth,
                               int aHeight,
                               int aLevel,
                               __global Pixel* aBufferIn,
                               __global Pixel* aBufferOut) {
  // Please implement your kernel code here.
  unsigned int gid_x = get_global_id(0);
  unsigned int gid_y = get_global_id(1);
  unsigned int gid = gid_x + gid_y * aWidth;

  unsigned char nr = colorQuantization(aBufferIn[gid].red, aLevel);
  unsigned char ng = colorQuantization(aBufferIn[gid].green, aLevel);
  unsigned char nb = colorQuantization(aBufferIn[gid].blue, aLevel);

  aBufferOut[gid].red = nr;
  aBufferOut[gid].green = ng;
  aBufferOut[gid].blue = nb;
}

__kernel void down_scale(int aInWidth,
                         int aInHeight,
                         int aOutWidth,
                         int aOutHeight,
                         float aScaleFactor,
                         __global Pixel* aBufferIn,
                         __global Pixel* aBufferOut) {
  // Please implement your kernel code here.
  unsigned int gid_x = get_global_id(0);
  unsigned int gid_y = get_global_id(1);

  // Nearest-neighbor, could be optimized for quality
  unsigned int des_idx = gid_x + gid_y * aOutWidth;
  unsigned int src_idx = round(gid_x / aScaleFactor) + round(gid_y / aScaleFactor) * aInWidth;

  unsigned char r = aBufferIn[src_idx].red;
  unsigned char g = aBufferIn[src_idx].green;
  unsigned char b = aBufferIn[src_idx].blue;

  aBufferOut[des_idx].red = r;
  aBufferOut[des_idx].green = g;
  aBufferOut[des_idx].blue = b;
}

__kernel void up_scale(int aInWidth,
                       int aInHeight,
                       int aOutWidth,
                       int aOutHeight,
                       float aScaleFactor,
                       __global Pixel* aBufferIn,
                       __global Pixel* aBufferOut) {
  // Please implement your kernel code here.
  unsigned int gid_x = get_global_id(0);
  unsigned int gid_y = get_global_id(1);

  // Nearest-neighbor, could be optimized for quality
  unsigned int des_idx = gid_x + gid_y * aOutWidth;
  unsigned int src_idx = floor(gid_x * aScaleFactor) + floor(gid_y * aScaleFactor) * aInWidth;

  unsigned char r = aBufferIn[src_idx].red;
  unsigned char g = aBufferIn[src_idx].green;
  unsigned char b = aBufferIn[src_idx].blue;

  aBufferOut[des_idx].red = r;
  aBufferOut[des_idx].green = g;
  aBufferOut[des_idx].blue = b;
}

