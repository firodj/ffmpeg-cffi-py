// avcodec.h
unsigned avcodec_version(void);
const char *avcodec_configuration(void);
const char *avcodec_license(void);

int avcodec_open2(struct AVCodecContext *avctx, const struct AVCodec *codec, struct AVDictionary **options);
int avcodec_close(struct AVCodecContext *avctx);

AVCodecContext *avcodec_alloc_context3(const AVCodec *codec);
void avcodec_free_context(AVCodecContext **avctx);

const char *avcodec_get_name(enum AVCodecID id);
AVCodec *avcodec_find_decoder(enum AVCodecID id);
AVCodec *avcodec_find_decoder_by_name(const char *name);

const AVCodecDescriptor *avcodec_descriptor_get(enum AVCodecID id);
const AVCodecDescriptor *avcodec_descriptor_get_by_name(const char *name);

const char *av_get_profile_name(const struct AVCodec *codec, int profile);
size_t av_get_codec_tag_string(char *buf, size_t buf_size, unsigned int codec_tag);
void avcodec_flush_buffers(struct AVCodecContext *avctx);
int av_get_bits_per_sample(enum AVCodecID codec_id);
int avcodec_copy_context(struct AVCodecContext *, const struct AVCodecContext *);

AVCodec *avcodec_find_encoder(enum AVCodecID id);
AVCodec *avcodec_find_encoder_by_name(const char *name);

int avcodec_is_open(AVCodecContext *s);
int av_codec_is_encoder(const AVCodec *codec);
int av_codec_is_decoder(const AVCodec *codec);

// packet
AVPacket *av_packet_alloc(void);
void av_packet_free(AVPacket **pkt);
void av_init_packet(AVPacket *pkt);
void av_packet_unref(AVPacket *pkt);
void av_packet_rescale_ts(AVPacket *pkt, AVRational tb_src, AVRational tb_dst);

int avcodec_decode_video2(struct AVCodecContext *avctx, struct AVFrame *picture, int *got_picture_ptr, const struct AVPacket *avpkt);
int avcodec_decode_audio4(struct AVCodecContext *avctx, struct AVFrame *frame, int *got_frame_ptr, const struct AVPacket *avpkt);

int avcodec_encode_video2(AVCodecContext *avctx, AVPacket *avpkt, const AVFrame *frame, int *got_packet_ptr);
int avcodec_encode_audio2(AVCodecContext *avctx, AVPacket *avpkt, const AVFrame *frame, int *got_packet_ptr);

// deprecated
int avpicture_alloc(struct AVPicture *picture, enum AVPixelFormat pix_fmt, int width, int height);
void avpicture_free(struct AVPicture *picture);
int avpicture_fill(struct AVPicture *picture, const uint8_t *ptr, enum AVPixelFormat pix_fmt, int width, int height);
int avpicture_get_size(enum AVPixelFormat pix_fmt, int width, int height);