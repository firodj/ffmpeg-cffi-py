from .lib import *
from .dict import Dict
from .stream import Stream
from .frame import VideoFrame, AudioFrame
from .packet import Packet

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
		err = avformat.avformat_open_input(ref, path, NULL, NULL)
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

	@property
	def bit_rate(self):
	    return self.av_format_ctx.bit_rate
	
	def to_primitive(self, full=False):
		d = dict(
			#filepath = self.filepath,
			nb_streams   = self.nb_streams,
			#start_time   = fmt_q2timestr(self.av_format_ctx.start_time, lib_avutil.av_get_time_base_q()),
			#duration     = fmt_q2timestr(self.av_format_ctx.duration, lib_avutil.av_get_time_base_q()),
			bit_rate     = existent( self.bit_rate ),
			
			name         = self.long_name,
			metadata     = self.metadata.to_primitive(),
			aspect_ratio = self.aspect_ratio,
		)
		if full:
			d['streams'] = [s.to_primitive() for s in self.streams]
		return d

	def __repr__(self):
		return "<%s: %s, %d streams %s %s>" % (self.__class__.__name__,
			self.long_name,
			self.nb_streams,
			repr(self.metadata.to_primitive()),
			repr(self.av_format_ctx)
			)
	
class InputFormat(FormatCtx):

	def close(self):
		if self.av_format_ctx != NULL:
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

	def open_decoder(self):
		if self.video_stream and not self.video_codec_ctx:
			video_codec_ctx = self.video_stream.codec_ctx.clone()
			if video_codec_ctx:
				if video_codec_ctx.open(): #self.video_stream.codec_ctx.coder 
					self.video_codec_ctx = video_codec_ctx

		if self.audio_stream and not self.audio_codec_ctx:
			audio_codec_ctx = self.audio_stream.codec_ctx.clone()
			if audio_codec_ctx:
				if audio_codec_ctx.open(): #self.audio_stream.codec_ctx.coder 
					self.audio_codec_ctx = audio_codec_ctx

	def close_decoder(self):
		if self.video_codec_ctx:
			self.video_codec_ctx.close()
			self.video_codec_ctx = None
			
		if self.audio_codec_ctx:
			self.audio_codec_ctx.close()
			self.audio_codec_ctx = None

	@property
	def name(self):
	    return stringify( self.av_format_ctx.iformat.name )

	@property
	def long_name(self):
	    return stringify( self.av_format_ctx.iformat.long_name )
	
	def next_frame(self):
		pkt = Packet()
		do_next = False

		while avformat.av_read_frame(self.av_format_ctx, pkt.av_packet) >= 0:
			while pkt.size > 0:
				(do_next, frame) = self._decode_pkt(pkt)
				if frame is not None:
					yield frame
				if not do_next: break
			pkt.unref()

		pkt.reset()

		while True:
			(do_next, frame) = self._decode_pkt(pkt)
			if frame is not None: 
				yield frame
			if not do_next: break

	def _decode_pkt(self, pkt):
		if self.video_codec_ctx and pkt.stream_eq(self.video_stream):
			return self._decode_video(pkt)
		elif self.audio_codec_ctx and pkt.stream_eq(self.audio_stream):
			return self._decode_audio(pkt)

		return (0, None)

	def _decode_video(self, pkt):
		got_frame = ffi.new('int*')
		got_frame[0] = 0
		frame = VideoFrame()

		size = avcodec.avcodec_decode_video2(self.video_codec_ctx.av_codec_ctx, frame.av_frame, got_frame, pkt.av_packet)

		pkt.consume(size)

		if got_frame[0]:
			frame.stream = pkt.stream
			return (size, frame)

		return (size, None)

	def _decode_audio(self, pkt):
		got_frame = ffi.new('int*')
		got_frame[0] = 0
		frame = AudioFrame()

		size = avcodec.avcodec_decode_audio4(self.audio_codec_ctx.av_codec_ctx, frame.av_frame, got_frame, pkt.av_packet)
		pkt.consume(size)

		if got_frame[0]:
			frame.stream = pkt.stream
			return (size, frame)

		return (size, None)
			
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


