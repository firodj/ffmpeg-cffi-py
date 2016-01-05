from .lib import *
from itertools import count

class Coder(object):
	def __init__(self, av_coder):
		self.av_coder = av_coder

	@classmethod
	def find_encoder(cls, codec_id):
		encoder = avcodec.avcodec_find_encoder(codec_id)
		if encoder == NULL:
			raise Exception(avcodec.avcodec_get_name(v_codec_id))
		if avutil.AVMEDIA_TYPE_VIDEO == encoder.type:
			return VideoEncoder(encoder)
		elif avutil.AVMEDIA_TYPE_AUDIO == encoder.type:
			return AudioEncoder(encoder)
		else:
			raise Exception(avutil.av_get_media_type_string(encoder.type))

class VideoEncoder(Coder):

	def supported_framerates(self):
		if self.av_coder.supported_framerates == NULL: return

		values = []
		for i in count():
			v = rational( self.av_coder.supported_framerates[i] )
			if v is None: break
			values.append(v)

		if len(values):	return values

	def supported_pix_fmts(self):
		if self.av_coder.pix_fmts == NULL: return

		values = []
		for i in count():
			v = self.av_coder.pix_fmts[i]
			if v == lib_avutil.AV_PIX_FMT_NONE: break
			values.append(v)

		if len(values):	return values

class AudioEncoder(Coder):

	def supported_samplerates(self):
		if self.av_coder.supported_samplerates == NULL: return

		values = []
		for i in count():
			v = self.av_coder.supported_samplerates[i]
			if v == 0: break
			values.append(v)

		if len(values):	return values

	def supported_sample_fmts(self):
		if self.av_coder.sample_fmts == NULL: return

		values = []
		for i in count():
			v = self.av_coder.sample_fmts[i]
			if v == lib_avutil.AV_SAMPLE_FMT_NONE: break
			values.append(v)

		if len(values):	return values

	def supported_channel_layouts(self):
		if self.av_coder.channel_layouts == NULL: return

		values = []
		for i in count():
			v = self.av_coder.channel_layouts[i]
			if v == 0: break
			values.append(v)

		if len(values):	return values