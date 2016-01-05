// avformat.h
unsigned avformat_version(void);
const char *avformat_configuration(void);
const char *avformat_license(void);

void av_register_all(void);
int avformat_open_input(struct AVFormatContext **ps, const char *filename, struct AVInputFormat *fmt, struct AVDictionary **options);
int avformat_alloc_output_context2(AVFormatContext **ctx, AVOutputFormat *oformat, const char *format_name, const char *filename);
void avformat_close_input(struct AVFormatContext **s);
void avformat_free_context(AVFormatContext *s);

AVStream *avformat_new_stream(AVFormatContext *s, const AVCodec *c);
int avformat_find_stream_info(struct AVFormatContext *ic, struct AVDictionary **options);
struct AVRational av_guess_sample_aspect_ratio(struct AVFormatContext *format, struct AVStream *stream, struct AVFrame *frame);

int av_read_frame(struct AVFormatContext *s, struct AVPacket *pkt);
int av_seek_frame(struct AVFormatContext *s, int stream_index, int64_t timestamp, int flags);

AVRational av_stream_get_r_frame_rate(const AVStream *s);

int avformat_write_header(AVFormatContext *s, AVDictionary **options);
int av_write_frame(AVFormatContext *s, AVPacket *pkt);
int av_interleaved_write_frame(AVFormatContext *s, AVPacket *pkt);
int av_write_trailer(AVFormatContext *s);

void av_dump_format(AVFormatContext *ic, int index, const char *url, int is_output);

// avio.h
int64_t avio_size(struct AVIOContext *s);
int avio_open(AVIOContext **s, const char *url, int flags);
int avio_close(AVIOContext *s);
int avio_open_dyn_buf(AVIOContext **s);
int avio_close_dyn_buf(AVIOContext *s, uint8_t **pbuffer);