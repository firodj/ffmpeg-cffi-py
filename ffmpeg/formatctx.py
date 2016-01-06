from .lib import *
		
class FormatCtx(object):
	
	def __init__(self, av_format_ctx):
		self.av_format_ctx = av_format_ctx
		self.metadata = Dict(self.av_format_ctx.metadata)

		self.video_stream = None
		self.audio_stream = None
		self.streams = []

		self.audio_codec_ctx = None
		self.video_codec_ctx = None

		self.aspect_ratio = None
	
	@classmethod
	def open(cls, path):
		if type(path) == unicode:
			path = path.encode('utf-8')
	
		ref = ffi.new('struct AVFormatContext **')
		err = avformat.avformat_open_input(ref, filepath, NULL, NULL)
		if err: return
		if ref[0] == NULL: return
		
		format_ctx = InputFormat(ref[0])
		format_ctx._init_streams()
		format_ctx._guess_aspect_ratio()
		return format_ctx
	
	@classmethod
	def create(cls, path=None, format=None):
		if type(path) == unicode:
			path = path.encode('utf-8')
			
		ref = ffi.new('struct AVFormatContext **')
		err = avformat.avformat_alloc_output_context2(ref, NULL, format, path)
		if err: return None
		if ref[0] == NULL: return
		
		return OutputFormat(ref[0])
	
	@property
	def nb_streams(self):
		return self.av_format_ctx.nb_streams

	@property
	def video_codec_id(self):
	    codec_id = self.av_format_ctx.video_codec_id
	    return None if codec_id == avcodec.AV_CODEC_ID_NONE else codec_id

	@property
	def audio_codec_id(self):
	    codec_id = self.av_format_ctx.audio_codec_id
	    return None if codec_id == avcodec.AV_CODEC_ID_NONE else codec_id
	
class InputFormat(FormatCtx):

	def close(self):
		ref = ffi.new('AVFormatContext **')
		ref[0] = self.av_format_ctx
		avformat.avformat_close_input(ref)
		self.av_format_ctx = ref[0]

	def _init_streams(self):
		err = avformat.avformat_find_stream_info(self.av_format_ctx, NULL)
		
		for i in xrange(0, self.nb_streams):
			stream = Stream._decoded( self.av_format_ctx.streams[i] )
			if stream.codec_ctx.type == 'video':
				if self.video_stream is None or stream.is_default:
					self.video_stream = stream
			elif stream.codec_ctx.type == 'audio':
				if self.audio_stream is None or stream.is_default:
					self.audio_stream = stream
			
			self.streams.append( stream )

	def _guess_aspect_ratio(self):
		if not self.video_stream: return

		width  = self.video_stream.codec_ctx.width
		height = self.video_stream.codec_ctx.height

		dar = ffi.new('AVRational *')
		sar = avformat.av_guess_sample_aspect_ratio(self.av_format_ctx, self.video_stream.av_stream, NULL)

		if sar.den != 0:
			avutil.av_reduce(ffi.addressof(dar, 'num'), ffi.addressof(dar, 'den'),
				width * sar.num,
				height * sar.den,
				1024*1024)

			self.aspect_ratio = rational( dar )

	def _open_decoder(self):
		if self.video_stream and not self.video_codec_ctx:
			video_codec_ctx = self.video_stream.codec_ctx.clone()
			if video_codec_ctx:
				if video_codec_ctx.open( self.video_stream.codec_ctx.coder ):
					self.video_codec_ctx = video_codec_ctx

		if self.audio_stream and not self.audio_codec_ctx:
			audio_codec_ctx = self.audio_stream.codec_ctx.clone()
			if audio_codec_ctx:
				if audio_codec_ctx.open( self.audio_stream.codec_ctx.coder ):
					self.audio_codec_ctx = audio_codec_ctx

	@property
	def name(self):
	    return stringify( self.av_format_ctx.iformat.name )

	@property
	def long_name(self):
	    return stringify( self.av_format_ctx.iformat.long_name )
	
	def reading_frames(self):
		pkt = Packet()

		while avformat.av_read_frame(self.av_format_ctx, pkt.av_packet) >= 0:
			

class OutputFormat(FormatCtx):

	def new_stream(self, codec_id):
		encoder = Coder.find_encoder(codec_id)
		av_stream = avformat.avformat_new_stream(self.av_format_ctx, encoder.av_codec)

	@property
	def name(self):
	    return stringify( self.av_format_ctx.oformat.name )

	@property
	def long_name(self):
	    return stringify( self.av_format_ctx.oformat.long_name )


