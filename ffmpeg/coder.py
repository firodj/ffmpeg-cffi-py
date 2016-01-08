from .lib import *
from itertools import count

class Coder(object):
	
	@staticmethod
	def get_name(codec_id):
		return stringify( avcodec.avcodec_get_name(codec_id) )

	@classmethod
	def create(cls, av_coder):
		if av_coder == NULL: return

		if avutil.AVMEDIA_TYPE_VIDEO == av_coder.type:
			return VideoCoder(av_coder)
		elif avutil.AVMEDIA_TYPE_AUDIO == av_coder.type:
			return AudioCoder(av_coder)
		else:
			return Coder(av_coder)

	@classmethod
	def find_encoder(cls, codec_id):
		encoder = avcodec.avcodec_find_encoder(codec_id)
		if encoder == NULL:
			return cls.find_descriptor(codec_id)

		return cls.create(encoder)

	@classmethod
	def find_decoder(cls, codec_id):
		decoder = avcodec.avcodec_find_decoder(codec_id)
		if decoder == NULL:
			return cls.find_descriptor(codec_id)

		return cls.create(decoder)

	@classmethod
	def find_descriptor(cls, codec_id):
		descriptor = avcodec.avcodec_descriptor_get(codec_id)
		if descriptor == NULL: return None

		return cls(av_descriptor = descriptor)

	def __init__(self, av_coder=None, av_descriptor=None):
		self.av_coder = av_coder if av_coder is not None else NULL
		self.av_descriptor = av_descriptor if av_descriptor is not None else NULL

	def is_encoder(self):
		if self.av_coder != NULL:
			return avcodec.av_codec_is_encoder(self.av_coder) != 0
		return False

	def is_decoder(self):
		if self.av_coder != NULL:
			return avcodec.av_codec_is_decoder(self.av_coder) != 0
		return False

	def is_descriptor(self):
		return self.av_descriptor != NULL and self.av_coder == NULL

	def _get_struct(self):
		if self.av_coder != NULL:
			return self.av_coder
		elif self.av_descriptor != NULL:
			return self.av_descriptor

	@property
	def name(self):
		obj = self._get_struct()
		if not obj: return
		return stringify( obj.name )

	@property
	def long_name(self):
		obj = self._get_struct()
		if not obj: return
		return stringify( obj.long_name )

	@property
	def type(self):
		obj = self._get_struct()
		if not obj: return
		return stringify( avutil.av_get_media_type_string(obj.type) )

	@property
	def id(self):
		obj = self._get_struct()
		if not obj: return
		return obj.id

	@property
	def bits_per_sample(self):
		return avcodec.av_get_bits_per_sample(self.id)

class VideoCoder(Coder):

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
			if v == avutil.AV_PIX_FMT_NONE: break
			values.append( stringify(avutil.av_get_pix_fmt_name(v)) )

		if len(values):	return values

	def __repr__(self):
		if self.is_descriptor():
			n = "VideoDescriptor"
		elif self.is_encoder():
			n = "VideoEncoder"
		elif self.is_decoder():
			n = "VideoDecoder"
		else:
			n = "VideoCoder"

		return "<%s: %s>" % (n, self.long_name)

class AudioCoder(Coder):

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
			if v == avutil.AV_SAMPLE_FMT_NONE: break
			values.append( stringify(avutil.av_get_sample_fmt_name(v)) )

		if len(values):	return values

	def supported_channel_layouts(self):
		if self.av_coder.channel_layouts == NULL: return

		values = []
		val_str = ffi.new('char[128]')
		for i in count():
			v = self.av_coder.channel_layouts[i]
			if v == 0: break

			avutil.av_get_channel_layout_string(val_str, ffi.sizeof(val_str), 0, v)
			values.append(stringify(val_str))

		if len(values):	return values

	def __repr__(self):
		if self.is_descriptor():
			n = "AudioDescriptor"
		elif self.is_encoder():
			n = "AudioEncoder"
		elif self.is_decoder():
			n = "AudioDecoder"
		else:
			n = "AudioCoder"

		return "<%s: %s>" % (n, self.long_name)