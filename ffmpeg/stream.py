from .lib import *
from .dict import Dict
from .codecctx import CodecCtx

class Stream(object):

	def __init__(self, av_stream):
		self.av_stream = av_stream
		self.metadata = Dict(self.av_stream.metadata)
		self.coder = None
		self.codec_ctx = None

	@classmethod
	def _decoded(cls, av_stream):
		stream = cls(av_stream)
		stream.codec_ctx = CodecCtx._decoded(av_stream.codec)
		return stream

	@property
	def type(self):
		return self.codec_ctx.type

	@property
	def is_default(self):
		return (self.av_stream.disposition & avformat.AV_DISPOSITION_DEFAULT) != 0
		
	@property
	def frame_rate(self):
		return q2d(avformat.av_stream_get_r_frame_rate(self.av_stream))

	@property
	def nb_frames(self):
		return self.av_stream.nb_frames
	
	@property
	def start_time(self):
		return None if self.av_stream.start_time == ffi.cast('int64_t',avutil.AV_NOPTS_VALUE) else self.av_stream.start_time

	@property
	def start_time_f(self):
		if self.start_time is None or self.time_base is None: return None
		return float(self.start_time) * self.time_base

	@property
	def duration(self):
		return None if self.av_stream.duration == ffi.cast('int64_t',avutil.AV_NOPTS_VALUE) else self.av_stream.duration

	@property
	def duration_f(self):
		if self.duration is None or self.time_base is None: return None
		return float(self.duration) * self.time_base

	@property
	def time_base(self):
		return rational( self.av_stream.time_base )

	@property
	def index(self):
		return self.av_stream.index
	
	def to_primitive(self):
		d = dict(
			type     = self.codec_ctx.type,
			metadata = self.metadata.to_primitive(['language', 'title']),
			start_time = fmt_q2timestr(self.av_stream.start_time, self.av_stream.time_base),
			duration   = fmt_q2timestr(self.av_stream.duration, self.av_stream.time_base),
			nb_frames  = existent(self.nb_frames),
			codec_tag  = self.codec_ctx.codec_tag,
			codec_name = self.codec_ctx.coder.long_name,
			profile    = self.codec_ctx.profile,
			bit_rate   = existent( self.codec_ctx.bit_rate ),
			bits_per_sample = existent( self.codec_ctx.bits_per_sample ),
		)

		if self.codec_ctx.type == 'video':
			d['frame_rate'] = self.frame_rate

		if self.codec_ctx.type == 'audio':
			pass

		d.update(self.codec_ctx.to_primitive())

		return d