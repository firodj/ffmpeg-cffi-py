// avutil.h
const char *av_version_info(void);

unsigned avutil_version(void);
const char *avutil_configuration(void);
const char *avutil_license(void);

const char *av_get_media_type_string(enum AVMediaType media_type);
struct AVRational av_get_time_base_q(void);

// error.h
int av_strerror(int errnum, char *errbuf, size_t errbuf_size);

// rational.h
int av_reduce(int *dst_num, int *dst_den, int64_t num, int64_t den, int64_t max);

// mathematics.h
int64_t av_rescale(int64_t a, int64_t b, int64_t c);

// mem.h
void *av_malloc(size_t size);
void av_free(void *ptr);

// samplefmt.h
const char *av_get_sample_fmt_name(enum AVSampleFormat sample_fmt);
enum AVSampleFormat av_get_sample_fmt(const char *name);
int av_get_bytes_per_sample(enum AVSampleFormat sample_fmt);

// pixdesc.h
const char *av_get_pix_fmt_name(enum AVPixelFormat pix_fmt);
enum AVPixelFormat av_get_pix_fmt(const char *name);

// dict.h
AVDictionaryEntry *av_dict_get(const AVDictionary *m, const char *key, const AVDictionaryEntry *prev, int flags);
int av_dict_count(const AVDictionary *m);
int av_dict_set(AVDictionary **pm, const char *key, const char *value, int flags);
int av_dict_copy(AVDictionary **dst, const AVDictionary *src, int flags);
void av_dict_free(AVDictionary **m);

// frame.h
struct AVDictionary *av_frame_get_metadata(const struct AVFrame *frame);
const char *av_get_colorspace_name(enum AVColorSpace val);
struct AVFrame *av_frame_alloc(void);
int av_frame_get_buffer(AVFrame *frame, int align);
void av_frame_unref(AVFrame *frame);
void av_frame_free(AVFrame **frame);
int av_frame_make_writable(AVFrame *frame);

// timecode.h
char *av_timecode_make_mpeg_tc_string(char *buf, uint32_t tc25bit);

// channel_layout.h
void av_get_channel_layout_string(char *buf, int buf_size, int nb_channels, uint64_t channel_layout);
int av_get_channel_layout_nb_channels(uint64_t channel_layout);
