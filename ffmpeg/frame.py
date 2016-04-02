from .lib import *
from PIL import Image

class Frame(object):

    def __init__(self):
        self._stream = None
        self.av_frame = None
        self.alloc()

    @property
    def type(self):
        if self._stream:
            return self._stream.type

    @property
    def stream(self):
        return self._stream
    @stream.setter
    def stream(self, v):
        self._stream = v

    def alloc(self):
        self.av_frame = avutil.av_frame_alloc()

    def free(self):
        ref = ffi.new('AVFrame**')
        ref[0] = self.av_frame
        avutil.av_frame_free(ref)
        self.av_frame = ref[0]

    @property
    def time_base(self):
        if self.stream is None: return
        return self.stream.time_base

    @property
    def pkt_pts(self):
        return None if self.av_frame.pkt_pts == ffi.cast('int64_t',avutil.AV_NOPTS_VALUE) else self.av_frame.pkt_pts

    @property
    def pkt_dts(self):
        return None if self.av_frame.pkt_dts == ffi.cast('int64_t',avutil.AV_NOPTS_VALUE) else self.av_frame.pkt_dts

    @property
    def pkt_pts_f(self):
        if self.pkt_pts is None or self.time_base is None: return
        return self.pkt_pts * self.time_base

    @property
    def pkt_dts_f(self):
        if self.pkt_dts is None or self.time_base is None: return
        return self.pkt_dts * self.time_base

    def process(self):
        raise NotImplemented()

class VideoFrame(Frame):

    @property
    def type(self):
        return "video"

    @property
    def pix_fmt(self):
        pix_fmt = correct_pix_fmt(self.av_frame.format)
        return stringify( avutil.av_get_pix_fmt_name( pix_fmt ) )

    @property
    def height(self):
        return self.av_frame.height

    @property
    def width(self):
        return self.av_frame.width

    def process(self, width=None, height=None):

        if width is None:
            width = self.width
        if height is None:
            height = self.height
        
        pix_fmt = "rgb24"

        img = None

        sws_ctx = swscale.sws_getContext(self.width,
            self.height, 
            avutil.av_get_pix_fmt( self.pix_fmt ),
            width,
            height,
            avutil.av_get_pix_fmt( pix_fmt ),
            swscale.SWS_BICUBIC,
            NULL, NULL, NULL)
                
        if sws_ctx != NULL:
            image_rgb = ffi.new('struct AVPicture *')

            avcodec.avpicture_alloc(image_rgb, 
                avutil.av_get_pix_fmt( pix_fmt),
                width, 
                height)

            swscale.sws_scale(sws_ctx,
                self.av_frame.data,
                self.av_frame.linesize,
                0, 
                self.av_frame.height,
                image_rgb.data,
                image_rgb.linesize)

            length = image_rgb.linesize[0] * height
            b = ffi.buffer(image_rgb.data[0], length)
            img = Image.frombuffer('RGB', (image_rgb.linesize[0]//3,
                height),
                b, 'raw',
                'RGB', 0, 1)

            avcodec.avpicture_free(image_rgb)
        
            swscale.sws_freeContext(sws_ctx)

        return img

class AudioFrame(Frame):

    @property
    def type(self):
        return "audio"

    @property
    def nb_samples(self):
        return self.av_frame.nb_samples
    
    @property
    def sample_fmt(self):
        return stringify(avutil.av_get_sample_fmt_name( self.av_frame.firnat ))

    @property
    def sample_rate(self):
        return self.av_frame.sample_rate

    @property
    def channels(self):
        return self.av_frame.channels

    @property
    def channel_layout(self):
        val_str = ffi.new('char[128]')
        avutil.av_get_channel_layout_string(val_str, ffi.sizeof(val_str), self.av_frame.channels, self.av_frame.channel_layout)
        return stringify(val_str)