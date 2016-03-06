from .lib import *
from .coder import Coder
from .packet import Packet

class CodecCtx(object):
	
	@classmethod
	def create(cls, coder):
		av_codec_ctx = avcodec.avcodec_alloc_context3(coder.av_coder)

		ctx = cls._new(av_codec_ctx)
		if ctx:
			assert coder.av_coder == ctx.av_codec_ctx.codec

			ctx.is_allocated = True
			ctx.coder = Coder.create( ctx.av_codec_ctx.codec )
		return ctx

	@classmethod
	def _new(cls, av_codec_ctx):
		if av_codec_ctx == NULL: return

		if avutil.AVMEDIA_TYPE_VIDEO == av_codec_ctx.codec_type:
			ctx = VideoCodecCtx(av_codec_ctx)
		elif avutil.AVMEDIA_TYPE_AUDIO == av_codec_ctx.codec_type:
			ctx = AudioCodecCtx(av_codec_ctx)
		else:
			ctx = cls(av_codec_ctx)

		return ctx

	@classmethod
	def _decoded(cls, av_codec_ctx):
		ctx = cls._new(av_codec_ctx)
		if ctx:
			ctx.coder = Coder.find_decoder( ctx.av_codec_ctx.codec_id )
		return ctx

	@classmethod
	def _encoded(cls, av_codec_ctx):
		ctx = cls._new(av_codec_ctx)
		if ctx:
			ctx.coder = Coder.create( av_codec_ctx.codec )
		return ctx

	def __init__(self, av_codec_ctx):
		self.av_codec_ctx = av_codec_ctx
		self.is_allocated = False
		self.coder = None

	def __del__(self):
		self.close()
		self.free()
				
	def close(self):
		if self.is_open():
			return avcodec.avcodec_close(self.av_codec_ctx) == 0

	def free(self):
		if self.is_allocated:
			ref = ffi.new('AVCodecContext **')
			ref[0] = self.av_codec_ctx
			avcodec.avcodec_free_context(ref)
			self.av_codec_ctx = ref[0]
			self.is_allocated = False
	
	@property
	def type(self):
		return stringify(avutil.av_get_media_type_string(self.av_codec_ctx.codec_type))
	
	@property
	def codec_tag(self):
		if self.av_codec_ctx.codec_tag:
			val_str = ffi.new('char[128]')
			avcodec.av_get_codec_tag_string(val_str, ffi.sizeof(val_str), self.av_codec_ctx.codec_tag)
			return stringify(val_str)
	
	@property
	def profile(self):
		if self.coder and self.coder.av_coder != NULL:
			return stringify(avcodec.av_get_profile_name(self.coder.av_coder, self.av_codec_ctx.profile))
	
	@property
	def long_name(self):
		if self.coder: return self.coder.long_name

	@property
	def bit_rate(self):
		return self.av_codec_ctx.bit_rate

	@property
	def bits_per_sample(self):
		return self.av_codec_ctx.bits_per_raw_sample

	@property
	def time_base(self):
	    return rational( self.av_codec_ctx.time_base )
	
	def clone(self):
		codec_ctx = CodecCtx.create(self.coder)
		if codec_ctx:
			err = avcodec.avcodec_copy_context(codec_ctx.av_codec_ctx, self.av_codec_ctx)
			if err != 0: return

		return codec_ctx

	def open(self):
		if avcodec.avcodec_open2(self.av_codec_ctx, self.coder.av_coder, NULL) != 0:
			return False
		return True

	def is_open(self):
		if self.av_codec_ctx != NULL:
			return avcodec.avcodec_is_open(self.av_codec_ctx) != 0
		return None

	def to_primitive(self):
		d = dict()
		return d

	def __repr__(self):
		return "<%s: %s %s>" % (self.__class__.__name__, self.type, repr(self.av_codec_ctx))

class VideoCodecCtx(CodecCtx):

	@property
	def height(self):
		return self.av_codec_ctx.height
	@height.setter
	def height(self, v):
		self.av_codec_ctx.height = v

	@property
	def width(self):
		return self.av_codec_ctx.width
	@width.setter
	def width(self, v):
		self.av_codec_ctx.width = v

	@property
	def pix_fmt(self):
		return stringify( avutil.av_get_pix_fmt_name(self.av_codec_ctx.pix_fmt) )
	@pix_fmt.setter
	def pix_fmt(self, v):
		self.av_codec_ctx.pix_fmt = avutil.av_get_pix_fmt(v)
	
	@property
	def color_space(self):
		return stringify(avutil.av_get_colorspace_name(self.av_codec_ctx.colorspace))
		
	@property
	def color_range(self):
		if self.av_codec_ctx.color_range != avutil.AVCOL_RANGE_UNSPECIFIED:
			return "tv" if self.av_codec_ctx.color_range == avutil.AVCOL_RANGE_MPEG else "pc"

	def to_primitive(self):
		d = dict(
			width = self.width,
			height      = self.height,
			pix_fmt     = self.pix_fmt,
			color_range = self.color_range,
			color_space = self.color_space,
		)
		return d

	def __repr__(self):
		return "<%s: %d x %d %s %s>" % (self.__class__.__name__,
			self.width,
			self.height,
			self.pix_fmt,
			repr(self.av_codec_ctx))

class AudioCodecCtx(CodecCtx):
	
	@property
	def sample_fmt(self):
		return stringify(avutil.av_get_sample_fmt_name(self.av_codec_ctx.sample_fmt))

	@property
	def sample_rate(self):
		return self.av_codec_ctx.sample_rate

	@property
	def channels(self):
		return self.av_codec_ctx.channels

	@property
	def channel_layout(self):
		val_str = ffi.new('char[128]')
		avutil.av_get_channel_layout_string(val_str, ffi.sizeof(val_str), self.av_codec_ctx.channels, self.av_codec_ctx.channel_layout)
		return stringify(val_str)

	def to_primitive(self):
		d = dict(
			sample_fmt  = self.sample_fmt,
			sample_rate = self.sample_rate,
			channels    = self.channels,
			channel_layout  = self.channel_layout
		)
		return d

	def __repr__(self):
		return "<%s: %d hz %s %s %s>" % (self.__class__.__name__,
			self.sample_rate,
			self.sample_fmt,
			self.channel_layout,
			repr(self.av_codec_ctx)
			)