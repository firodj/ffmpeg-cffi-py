from .lib import *

class CodecCtx(object):
	
	def __init__(self, av_codec_ctx):
		self.av_codec_ctx = av_codec_ctx
	
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
	def pix_fmt(self):
		return stringify(avutil.av_get_pix_fmt_name(self.av_codec_ctx.pix_fmt))
	
	def _get_descriptor(self):
		descriptor = avcodec.avcodec_descriptor_get(self.av_codec_ctx.codec_id)
	
	@property
	def channel_layout(self):
		val_str = ffi.new('char[128]')
		avutil.av_get_channel_layout_string(val_str, ffi.sizeof(val_str), self.av_codec_ctx.channels, self.av_codec_ctx.channel_layout)
		return stringify(val_str)
	
	@property
	def color_space(self):
		return stringify(avutil.av_get_colorspace_name(self.av_codec_ctx.colorspace))
		
	@property
	def color_range(self):
		return "tv" if self.av_codec_ctx.color_range == avutil.AVCOL_RANGE_MPEG else "pc"
	
	@property
	def sample_fmt(self):
		return stringify(avutil.av_get_sample_fmt_name(self.av_codec_ctx.sample_fmt))
		
	def parse_type(self):
		
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
		
		if self.av_codec_ctx.bits_per_raw_sample == 0:
			self.av_codec_ctx.bits_per_raw_sample = lib_avcodec.av_get_bits_per_sample(self.av_codec_ctx.codec_id)