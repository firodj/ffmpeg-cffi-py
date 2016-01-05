// swscale.h
unsigned swscale_version(void);
const char *swscale_configuration(void);
const char *swscale_license(void);

struct SwsContext *sws_getContext(int srcW, int srcH, enum AVPixelFormat srcFormat,
                                  int dstW, int dstH, enum AVPixelFormat dstFormat,
                                  int flags, struct SwsFilter *srcFilter,
                                  struct SwsFilter *dstFilter, const double *param);
int sws_scale(struct SwsContext *c, const uint8_t *const srcSlice[],
              const int srcStride[], int srcSliceY, int srcSliceH,
              uint8_t *const dst[], const int dstStride[]);
void sws_freeContext(struct SwsContext *swsContext);

// swresample.h
unsigned swresample_version(void);
const char *swresample_configuration(void);
const char *swresample_license(void);