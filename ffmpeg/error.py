MKTAG = lambda a, b, c, d: a | b << 8 | c << 16 | d << 24
myord = lambda c: ord(c) if isinstance(c, str) else c
FFERRTAG = lambda a, b, c, d: -MKTAG(myord(a), myord(b), myord(c), myord(d))

AVERROR_BSF_NOT_FOUND = FFERRTAG(0xF8, 'B', 'S', 'F')
AVERROR_BUG = FFERRTAG('B', 'U', 'G', '!')
AVERROR_BUFFER_TOO_SMALL = FFERRTAG('B', 'U', 'F', 'S')
AVERROR_DECODER_NOT_FOUND = FFERRTAG(0xF8, 'D', 'E', 'C')
AVERROR_DEMUXER_NOT_FOUND = FFERRTAG(0xF8, 'D', 'E', 'M')
AVERROR_ENCODER_NOT_FOUND = FFERRTAG(0xF8, 'E', 'N', 'C')
AVERROR_EOF = FFERRTAG('E', 'O', 'F', ' ')
AVERROR_EXIT = FFERRTAG('E', 'X', 'I', 'T')
AVERROR_EXTERNAL = FFERRTAG('E', 'X', 'T', ' ')
AVERROR_FILTER_NOT_FOUND = FFERRTAG(0xF8, 'F', 'I', 'L')
AVERROR_INVALIDDATA = FFERRTAG('I', 'N', 'D', 'A')
AVERROR_MUXER_NOT_FOUND = FFERRTAG(0xF8, 'M', 'U', 'X')
AVERROR_OPTION_NOT_FOUND = FFERRTAG(0xF8, 'O', 'P', 'T')
AVERROR_PATCHWELCOME = FFERRTAG('P', 'A', 'W', 'E')
AVERROR_PROTOCOL_NOT_FOUND = FFERRTAG(0xF8, 'P', 'R', 'O')
AVERROR_STREAM_NOT_FOUND = FFERRTAG(0xF8, 'S', 'T', 'R')
AVERROR_BUG2 = FFERRTAG('B', 'U', 'G', ' ')
AVERROR_UNKNOWN = FFERRTAG('U', 'N', 'K', 'N')
AVERROR_EXPERIMENTAL = (-0x2bb2afa8)
AVERROR_INPUT_CHANGED = (-0x636e6701)
AVERROR_OUTPUT_CHANGED = (-0x636e6702)
AVERROR_HTTP_BAD_REQUEST = FFERRTAG(0xF8, '4', '0', '0')
AVERROR_HTTP_UNAUTHORIZED = FFERRTAG(0xF8, '4', '0', '1')
AVERROR_HTTP_FORBIDDEN = FFERRTAG(0xF8, '4', '0', '3')
AVERROR_HTTP_NOT_FOUND = FFERRTAG(0xF8, '4', '0', '4')
AVERROR_HTTP_OTHER_4XX = FFERRTAG(0xF8, '4', 'X', 'X')
AVERROR_HTTP_SERVER_ERROR = FFERRTAG(0xF8, '5', 'X', 'X')

err_dict = {
    AVERROR_BSF_NOT_FOUND: "Bitstream filter not found",
    AVERROR_BUG: "Internal bug, also see AVERROR_BUG2",
    AVERROR_BUFFER_TOO_SMALL: "Buffer too small",
    AVERROR_DECODER_NOT_FOUND: "Decoder not found",
    AVERROR_DEMUXER_NOT_FOUND: "Demuxer not found",
    AVERROR_ENCODER_NOT_FOUND: "Encoder not found",
    AVERROR_EOF: "End of file",
    AVERROR_EXIT:
    "Immediate exit was requested; "
    "the called function should not be restarted",
    AVERROR_EXTERNAL: "Generic error in an external library",
    AVERROR_FILTER_NOT_FOUND: "Filter not found",
    AVERROR_INVALIDDATA: "Invalid data found when processing input",
    AVERROR_MUXER_NOT_FOUND: "Muxer not found",
    AVERROR_OPTION_NOT_FOUND: "Option not found",
    AVERROR_PATCHWELCOME: "Not yet implemented in FFmpeg, patches welcome",
    AVERROR_PROTOCOL_NOT_FOUND: "Protocol not found",
    AVERROR_STREAM_NOT_FOUND: "Stream not found",
    AVERROR_BUG2: "Bug2",
    AVERROR_UNKNOWN: "Unknown error, typically from an external library",
    AVERROR_EXPERIMENTAL: "Requested feature is flagged experimental. "
    "Set strict_std_compliance if you really want to use it.",
    AVERROR_INPUT_CHANGED: "Input changed between calls. "
    "Reconfiguration is required. (can be OR-ed with AVERROR_OUTPUT_CHANGED)",
    AVERROR_OUTPUT_CHANGED: "Output changed between calls. "
    "Reconfiguration is required. (can be OR-ed with AVERROR_INPUT_CHANGED)",
    AVERROR_HTTP_BAD_REQUEST: "Bad request",
    AVERROR_HTTP_UNAUTHORIZED: "Unauthorized",
    AVERROR_HTTP_FORBIDDEN: "Forbidden",
    AVERROR_HTTP_NOT_FOUND: "Not_found",
    AVERROR_HTTP_OTHER_4XX: "Other_4xx",
    AVERROR_HTTP_SERVER_ERROR: "Server_error",
}


class FFMPEGException(Exception):
    pass


def check_ret(ret):
    if ret:
        if ret in err_dict:
            raise FFMPEGException(err_dict[ret])
        else:
            raise Exception("Unknown Error `{}`".format(ret))
