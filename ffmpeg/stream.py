from .lib import *
from .dict import Dict

class Stream(object):

	def __init__(self, av_stream):
		self.av_stream = av_stream
		self.metadata = Dict(self.av_stream.metadata)
		self.type = None
		self.av_codec_ctx = self.av_stream.codec
		if self.av_stream.codec != NULL:
			self.parse_type()
		
	@property
	def is_default(self):
		return (self.av_stream.disposition & avformat.AV_DISPOSITION_DEFAULT) != 0
		
	@property
	def frame_rate(self):
		return q2d(avformat.av_stream_get_r_frame_rate(self.av_stream))
	
	def parse_type(self):
		self.type = stringify(lib_avutil.av_get_media_type_string(self.av_codec_ctx.codec_type))

		self.codec_tag_string = None
		if self.av_codec_ctx.codec_tag:
			val_str = ffi.new('char[128]')
			lib_avcodec.av_get_codec_tag_string(val_str, ffi.sizeof(val_str), self.av_codec_ctx.codec_tag)
			self.codec_tag_string = stringify(val_str)
		
		decoder = self.av_codec_ctx.codec	
		if decoder == NULL:
			decoder = lib_avcodec.avcodec_find_decoder(self.av_codec_ctx.codec_id)
			self.av_codec_ctx.codec = decoder

		if decoder == NULL:
			descriptor = lib_avcodec.avcodec_descriptor_get(self.av_codec_ctx.codec_id)
			if descriptor != NULL:
				self.codec_name = stringify(descriptor.name)
				self.codec_long_name = stringify(descriptor.long_name)
		else:
			self.codec_name = stringify(decoder.name)
			self.codec_long_name = stringify(decoder.long_name)
			self.profile_name = stringify(lib_avcodec.av_get_profile_name(decoder, self.av_codec_ctx.profile))

		self.pix_fmt_name = stringify(lib_avutil.av_get_pix_fmt_name(self.av_codec_ctx.pix_fmt))
		self.color_range_string = "tv" if self.av_codec_ctx.color_range == lib_avutil.AVCOL_RANGE_MPEG else "pc"
		self.colorspace_name = stringify(lib_avutil.av_get_colorspace_name(self.av_codec_ctx.colorspace))
		self.sample_fmt_name = stringify(lib_avutil.av_get_sample_fmt_name(self.av_codec_ctx.sample_fmt))
		
		val_str = ffi.new('char[128]')
		lib_avutil.av_get_channel_layout_string(val_str, ffi.sizeof(val_str), self.av_codec_ctx.channels, self.av_codec_ctx.channel_layout)
		self.channel_layout_string = stringify(val_str)

		if self.av_codec_ctx.bits_per_raw_sample == 0:
			self.av_codec_ctx.bits_per_raw_sample = lib_avcodec.av_get_bits_per_sample(self.av_codec_ctx.codec_id)

	def to_primitive(self):
		d = dict(
			type     = self.type,
			metadata = self.metadata.to_primitive(['language', 'title']),
			#index    = self.av_stream.index,
			start_time = fmt_q2timestr(self.av_stream.start_time, self.av_stream.time_base),
			duration   = fmt_q2timestr(self.av_stream.duration, self.av_stream.time_base),
			nb_frames  = existent(self.av_stream.nb_frames),
			#is_default = self.is_default,
			codec_tag  = self.codec_tag_string,
			codec_name = self.codec_long_name,
			profile    = self.profile_name,
			bit_rate   = existent( self.av_codec_ctx.bit_rate ),
			bits_per_sample = existent( self.av_codec_ctx.bits_per_raw_sample ),
		)

		if self.type == 'video':
			d.update(dict(
				width       = self.av_codec_ctx.width,
				height      = self.av_codec_ctx.height,
				pix_fmt     = self.pix_fmt_name,
				color_range = self.color_range_string,
				color_space = self.colorspace_name,
				frame_rate  = self.frame_rate,
			))

		if self.type == 'audio':
			d.update(dict(
				sample_fmt  = self.sample_fmt_name,
				sample_rate = self.av_codec_ctx.sample_rate,
				channels    = self.av_codec_ctx.channels,
				channel_layout  = self.channel_layout_string,
			))

		return d