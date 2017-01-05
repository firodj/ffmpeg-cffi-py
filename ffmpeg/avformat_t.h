typedef struct AVStreamInternal AVStreamInternal;
typedef struct AVFrac {
    int64_t val, num, den;
} AVFrac;

struct AVPacketList;

typedef struct AVProbeData {
    const char *filename;
    unsigned char *buf;
    int buf_size;
    const char *mime_type;
} AVProbeData;

enum AVStreamParseType {
    AVSTREAM_PARSE_NONE,
    // ...;
};

typedef struct AVOutputFormat {
    const char *name;
    const char *long_name;
    const char *mime_type;
    const char *extensions;
    enum AVCodecID audio_codec;
    enum AVCodecID video_codec;
    enum AVCodecID subtitle_codec;
    int flags;
    const struct AVCodecTag * const *codec_tag;
    const AVClass *priv_class;
    struct AVOutputFormat *next;
    int priv_data_size;
    int (*write_header)(void);
    int (*write_packet)(void);
    int (*write_trailer)(void);
    int (*interleave_packet)(void);
    int (*query_codec)(void);
    void (*get_output_timestamp)(void);
    int (*control_message)(void);
    int (*write_uncoded_frame)(void);
    int (*get_device_list)(void);
    int (*create_device_capabilities)(void);
    int (*free_device_capabilities)(void);
    enum AVCodecID data_codec;
} AVOutputFormat;

typedef struct AVInputFormat {
    const char *name;
    const char *long_name;
    int flags;
    const char *extensions;
    const struct AVCodecTag * const *codec_tag;
    const AVClass *priv_class;
    const char *mime_type;
    struct AVInputFormat *next;
    int raw_codec_id;
    int priv_data_size;
    int (*read_probe)(void);
    int (*read_header)(void);
    int (*read_packet)(void);
    int (*read_close)(void);
    int (*read_seek)(void);
    int64_t (*read_timestamp)(void);
    int (*read_play)(void);
    int (*read_pause)(void);
    int (*read_seek2)(void);
    int (*get_device_list)(void);
    int (*create_device_capabilities)(void);
    int (*free_device_capabilities)(void);
} AVInputFormat;

typedef struct AVIndexEntry AVIndexEntry;

#define MAX_STD_TIMEBASES 0x175

typedef struct AVStream {
    int index;
    int id;
    AVCodecContext *codec; // @deprecated
    void *priv_data;
    struct AVFrac pts;  // @deprecated
    AVRational time_base;
    int64_t start_time;
    int64_t duration;
    int64_t nb_frames;
    int disposition;
    enum AVDiscard discard;
    AVRational sample_aspect_ratio;
    AVDictionary *metadata;
    AVRational avg_frame_rate;
    AVPacket attached_pic;
    AVPacketSideData *side_data;
    int nb_side_data;
    int event_flags;

    struct {
        int64_t last_dts;
        int64_t duration_gcd;
        int duration_count;
        int64_t rfps_duration_sum;
        double (*duration_error)[2][MAX_STD_TIMEBASES];
        int64_t codec_info_duration;
        int64_t codec_info_duration_fields;
        int found_decoder;
        int64_t last_duration;
        int64_t fps_first_dts;
        int fps_first_dts_idx;
        int64_t fps_last_dts;
        int fps_last_dts_idx;
    } *info;
    int pts_wrap_bits;
    int64_t first_dts;
    int64_t cur_dts;
    int64_t last_IP_pts;
    int last_IP_duration;
    int probe_packets;
    int codec_info_nb_frames;
    enum AVStreamParseType need_parsing;
    struct AVCodecParserContext *parser;
    struct AVPacketList *last_in_packet_buffer;
    AVProbeData probe_data;
#define MAX_REORDER_DELAY 16
    int64_t pts_buffer[17];
    AVIndexEntry *index_entries;
    int nb_index_entries;
    unsigned int index_entries_allocated_size;
    AVRational r_frame_rate;
    int stream_identifier;
    int64_t interleaver_chunk_size;
    int64_t interleaver_chunk_duration;
    int request_probe;
    int skip_to_keyframe;
    int skip_samples;
    int64_t start_skip_samples;
    int64_t first_discard_sample;
    int64_t last_discard_sample;
    int nb_decoded_frames;
    int64_t mux_ts_offset;
    int64_t pts_wrap_reference;
    int pts_wrap_behavior;
    int update_initial_durations_done;
    int64_t pts_reorder_error[17];
    uint8_t pts_reorder_error_count[17];
    int64_t last_dts_for_order_check;
    uint8_t dts_ordered;
    uint8_t dts_misordered;
    int inject_global_side_data;
    char *recommended_encoder_configuration;
    AVRational display_aspect_ratio;
    struct FFFrac *priv_pts;
    AVStreamInternal *internal;
    AVCodecParameters *codecpar;
} AVStream;

typedef struct AVProgram AVProgram;
typedef struct AVChapter AVChapter;
struct AVInputFormat;
struct AVOutputFormat;

typedef struct AVIOContext AVIOContext;

typedef struct AVIOInterruptCB {
    int (*callback)(void);
    void *opaque;
} AVIOInterruptCB;

enum AVDurationEstimationMethod {
    AVFMT_DURATION_FROM_PTS,
    AVFMT_DURATION_FROM_STREAM,
    AVFMT_DURATION_FROM_BITRATE
};

typedef struct AVFormatInternal AVFormatInternal;

typedef struct AVFormatContext {
    const AVClass *av_class;
    struct AVInputFormat *iformat;
    struct AVOutputFormat *oformat;
    void *priv_data;
    AVIOContext *pb;
    int ctx_flags;
    unsigned int nb_streams;
    AVStream **streams;
    char filename[1024];
    int64_t start_time;
    int64_t duration;
    int64_t bit_rate;
    unsigned int packet_size;
    int max_delay;
    int flags;
    int64_t probesize;
    int64_t max_analyze_duration;
    const uint8_t *key;
    int keylen;
    unsigned int nb_programs;
    AVProgram **programs;
    enum AVCodecID video_codec_id;
    enum AVCodecID audio_codec_id;
    enum AVCodecID subtitle_codec_id;
    unsigned int max_index_size;
    unsigned int max_picture_buffer;
    unsigned int nb_chapters;
    AVChapter **chapters;
    AVDictionary *metadata;
    int64_t start_time_realtime;
    int fps_probe_size;
    int error_recognition;
    AVIOInterruptCB interrupt_callback;
    int debug;
    int64_t max_interleave_delta;
    int strict_std_compliance;
    int event_flags;
    int max_ts_probe;
    int avoid_negative_ts;
    int ts_id;
    int audio_preload;
    int max_chunk_duration;
    int max_chunk_size;
    int use_wallclock_as_timestamps;
    int avio_flags;
    enum AVDurationEstimationMethod duration_estimation_method;
    int64_t skip_initial_bytes;
    unsigned int correct_ts_overflow;
    int seek2any;
    int flush_packets;
    int probe_score;
    int format_probesize;
    char *codec_whitelist;
    char *format_whitelist;
    AVFormatInternal *internal;
    int io_repositioned;
    AVCodec *video_codec;
    AVCodec *audio_codec;
    AVCodec *subtitle_codec;
    AVCodec *data_codec;
    int metadata_header_padding;
    void *opaque;
    int (*control_message_cb)(void);
    int64_t output_ts_offset;
    uint8_t *dump_separator;
    enum AVCodecID data_codec_id;
    int (*open_cb)(void);
} AVFormatContext;


// thanksto: http://eli.thegreenplace.net/2013/03/09/python-ffi-with-ctypes-and-cffi

// Demuxer will use avio_open, no opened file should be provided by the caller.
#define AVFMT_NOFILE        0x0001
#define AVFMT_SHOW_IDS      0x0008 /**< Show format stream IDs numbers. */
#define AVFMT_GLOBALHEADER  0x0040 /**< Format wants global header. */

#define AV_DISPOSITION_DEFAULT   0x0001

#define AVIO_FLAG_READ  1                                      /**< read-only */
#define AVIO_FLAG_WRITE 2                                      /**< write-only */
#define AVIO_FLAG_READ_WRITE 3  /**< read-write pseudo flag */

#define AVSEEK_FLAG_BACKWARD 1 ///< seek backward
#define AVSEEK_FLAG_BYTE     2 ///< seeking based on position in bytes
#define AVSEEK_FLAG_ANY      4 ///< seek to any frame, even non-keyframes
#define AVSEEK_FLAG_FRAME    8 ///< seeking based on frame number
