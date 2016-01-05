#define SWS_FAST_BILINEAR     1
#define SWS_BILINEAR          2
#define SWS_BICUBIC           4

typedef struct SwsVector {
    double *coeff;              ///< pointer to the list of coefficients
    int length;                 ///< number of coefficients in the vector
} SwsVector;

typedef struct SwsContext SwsContext;

typedef struct SwsFilter {
    struct SwsVector *lumH;
    struct SwsVector *lumV;
    struct SwsVector *chrH;
    struct SwsVector *chrV;
} SwsFilter;

typedef struct SwrContext SwrContext;