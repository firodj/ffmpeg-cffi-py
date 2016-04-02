from .lib import *
from .dict import Dict
from .stream import Stream
from .frame import VideoFrame, AudioFrame
from .packet import Packet
from .coder import Coder
from .error import check_ret

avformat_open_input = getattr(avformat, 'avformat_open_input')

class FormatCtx(object):
	
	def __init__(self, av_format_ctx):
		self.av_format_ctx = av_format_ctx
		self.metadata = Dict(self.av_format_ctx.metadata)
		self.filepath = None

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
		check_ret(avformat_open_input(ref, path, NULL, NULL))

		if ref[0] == NULL: return
		
		format_ctx = InputFormat(ref[0])
		format_ctx._init_streams()
		format_ctx._guess_aspect_ratio()

		format_ctx.filepath = path
		return format_ctx
	
	@classmethod
	def create(cls, path=None, format=None):
		if type(path) == unicode:
			path = path.encode('utf-8')
		if format is None:
			format = NULL
			
		ref = ffi.new('struct AVFormatContext **')
		err = avformat.avformat_alloc_output_context2(ref, NULL, format, path)
		if err: return None
		if ref[0] == NULL: return
		
		format_ctx = OutputFormat(ref[0])
		format_ctx.filepath = path

		return format_ctx
	
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

	@property
	def start_time(self):
		return None if self.av_format_ctx.start_time == int(ffi.cast('int64_t',avutil.AV_NOPTS_VALUE)) else self.av_format_ctx.start_time

	@property
	def start_time_f(self):
		if self.start_time is None or self.time_base is None: return None
		return float(self.start_time) * self.time_base

	@property
	def duration(self):
		return None if self.av_format_ctx.duration == int(ffi.cast('int64_t',avutil.AV_NOPTS_VALUE)) else self.av_format_ctx.duration

	@property
	def duration_f(self):
		if self.duration is None or self.time_base is None: return None
		return float(self.duration) * self.time_base

	@property
	def time_base(self):
		return time_base_q()

	def to_primitive(self, full=False):
		d = dict(
			#filepath = self.filepath,
			nb_streams   = self.nb_streams,
			start_time   = fmt_f2timestr(self.start_time_f),
			duration     = fmt_f2timestr(self.duration_f),
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
		if size < 0:
			print "Error:", str_error(size), pkt.size
			return (0, None)

		if pkt.size != size:
			print "Warning: decoded size differ", abs(pkt.size - size)
			pkt.consume(pkt.size)
		else:
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
		if size < 0:
			print "Error:", str_error(size), pkt.size
			return (0, None)

		if pkt.size != size:
			print "Warning: decoded size differ", abs(pkt.size - size)
			pkt.consume(pkt.size)
		else:
			pkt.consume(size)

		if got_frame[0]:
			frame.stream = pkt.stream
			return (size, frame)

		return (size, None)
			
class OutputFormat(FormatCtx):

	def close(self):
		if self.av_format_ctx != NULL:
			avformat.avformat_free_context(self.av_format_ctx)
			self.av_format_ctx = NULL

	def new_stream(self, codec_id):
		encoder = Coder.find_encoder(codec_id)
		av_stream = avformat.avformat_new_stream(self.av_format_ctx, encoder.av_coder)
		stream = Stream._encoded( av_stream )
		return stream

	def create_video_stream(self, v_codec_id=avcodec.AV_CODEC_ID_NONE):
		if v_codec_id == avcodec.AV_CODEC_ID_NONE:
			v_codec_id = self.av_format_ctx.oformat.video_codec
		if v_codec_id == avcodec.AV_CODEC_ID_NONE:
			return None
		
		video_stream = self.new_stream( v_codec_id )

		self.video_stream = video_stream
		self.video_codec_ctx = video_stream.codec_ctx
		self.streams.append(self.video_stream)

		v_encoder_ctx = self.video_codec_ctx.av_codec_ctx

		assert video_stream.av_stream == self.av_format_ctx.streams[ video_stream.index ]
		assert "video" == video_stream.codec_ctx.type

		v_encoder_ctx.bit_rate = 400000
		
		v_encoder_ctx.width = 352
		v_encoder_ctx.height = 288
		v_encoder_ctx.qmin = 4
		v_encoder_ctx.qmax = 63

		v_encoder_ctx.gop_size      = 12 
		v_encoder_ctx.pix_fmt = avutil.AV_PIX_FMT_YUV420P
		
		v_encoder_ctx.framerate.num = 25
		v_encoder_ctx.framerate.den = 1
		
		v_encoder_ctx.time_base.num = v_encoder_ctx.framerate.den
		v_encoder_ctx.time_base.den = v_encoder_ctx.framerate.num
		video_stream.av_stream.time_base = v_encoder_ctx.time_base

		if v_encoder_ctx.codec_id == avcodec.AV_CODEC_ID_MPEG2VIDEO:
			v_encoder_ctx.max_b_frames = 2

		if v_encoder_ctx.codec_id == avcodec.AV_CODEC_ID_MPEG1VIDEO:
			v_encoder_ctx.mb_decision = 2

		if (self.av_format_ctx.oformat.flags & avformat.AVFMT_GLOBALHEADER) != 0:
			v_encoder_ctx.flags |= avcodec.AV_CODEC_FLAG_GLOBAL_HEADER

	def create_audio_stream(self, a_codec_id=avcodec.AV_CODEC_ID_NONE):
		if a_codec_id == avcodec.AV_CODEC_ID_NONE:
			a_codec_id = self.av_format_ctx.oformat.audio_codec
		if a_codec_id == avcodec.AV_CODEC_ID_NONE:
			return None
		
		audio_stream = self.new_stream( a_codec_id )
		
		self.audio_stream = audio_stream
		self.audio_codec_ctx = self.audio_stream.codec_ctx
		self.streams.append(self.audio_stream)

		a_encoder_ctx = self.audio_codec_ctx.av_codec_ctx

		assert audio_stream.av_stream == self.av_format_ctx.streams[audio_stream.index]
		assert "audio" == audio_stream.codec_ctx.type
		
		a_encoder_ctx.sample_fmt  = avutil.AV_SAMPLE_FMT_FLT
	
		a_encoder_ctx.bit_rate    = 64000
		a_encoder_ctx.sample_rate = 48000

		a_encoder_ctx.channel_layout = avutil.AV_CH_LAYOUT_STEREO
		
		a_encoder_ctx.channels = avutil.av_get_channel_layout_nb_channels(a_encoder_ctx.channel_layout)
		a_encoder_ctx.time_base.num = 1
		a_encoder_ctx.time_base.den = a_encoder_ctx.sample_rate
		audio_stream.av_stream.time_base = a_encoder_ctx.time_base

		if (self.av_format_ctx.oformat.flags & avformat.AVFMT_GLOBALHEADER) != 0:
			a_encoder_ctx.flags |= avcodec.AV_CODEC_FLAG_GLOBAL_HEADER

	@property
	def name(self):
	    return stringify( self.av_format_ctx.oformat.name )

	@property
	def long_name(self):
	    return stringify( self.av_format_ctx.oformat.long_name )

	def __init__(self, *args, **kwargs):
		super(OutputFormat, self).__init__(*args, **kwargs)

	def open_encoder(self):
	 	if self.video_codec_ctx:
			self.video_codec_ctx.open()

			self.v_next_pts = 0

			self.picture = avutil.av_frame_alloc()

			self.picture.format = self.video_codec_ctx.av_codec_ctx.pix_fmt
			self.picture.width  = self.video_codec_ctx.av_codec_ctx.width
			self.picture.height = self.video_codec_ctx.av_codec_ctx.height

			ret = avutil.av_frame_get_buffer(self.picture, 32)
			if ret < 0:
				raise Exception

		if self.audio_codec_ctx:
			self.audio_codec_ctx.open()

			if (self.audio_codec_ctx.coder.av_coder.capabilities & avcodec.AV_CODEC_CAP_VARIABLE_FRAME_SIZE) != 0:
				nb_samples = 10000
			else:
				nb_samples = self.audio_codec_ctx.av_codec_ctx.frame_size
			
			self.a_next_pts = 0

			self.sound = avutil.av_frame_alloc()
			
			self.sound.format         = self.audio_codec_ctx.av_codec_ctx.sample_fmt
			self.sound.channel_layout = self.audio_codec_ctx.av_codec_ctx.channel_layout
			self.sound.sample_rate    = self.audio_codec_ctx.av_codec_ctx.sample_rate
			self.sound.nb_samples     = nb_samples
			
			#if nb_samples:
			ret = avutil.av_frame_get_buffer(self.sound, 0)
			if ret < 0:
				raise Exception()

	def close_encoder(self):
		ref = ffi.new('AVFrame**')

		if self.video_codec_ctx:
			self.video_codec_ctx.close()
			self.video_codec_ctx = None

			if self.picture != NULL:
				ref[0] = self.picture
				avutil.av_frame_free(ref)
				self.picture = ref[0]

		if self.audio_codec_ctx:
			self.audio_codec_ctx.close()
			self.audio_codec_ctx = None

			if self.sound != NULL:
				ref[0] = self.sound
				avutil.av_frame_free(ref)
				self.sound = ref[0]

	@property
	def a_next_pts_f(self):
		return self.a_next_pts * float(self.audio_codec_ctx.time_base)

	@property
	def v_next_pts_f(self):
		return self.v_next_pts * float(self.video_codec_ctx.time_base)

	def write_header(self):
		avformat.av_dump_format(self.av_format_ctx, 0, self.filepath, 1)

		if (self.av_format_ctx.oformat.flags & avformat.AVFMT_NOFILE) == 0:
			pb = ffi.new('AVIOContext **')

			#ret = avformat.avio_open_dyn_buf(pb)

			ret = avformat.avio_open(pb, self.filepath, avformat.AVIO_FLAG_WRITE)
			if ret < 0:
				raise Exception()

			self.av_format_ctx.pb = pb[0]

		ret = avformat.avformat_write_header(self.av_format_ctx, NULL)
		if ret < 0:
			raise Exception()

	def write_trailer(self):
		avformat.av_write_trailer(self.av_format_ctx)

		#pbuffer = ffi.new('uint8_t **')
		#length = avformat.avio_close_dyn_buf(self.av_format_ctx.pb, pbuffer)
		#b = ffi.buffer(pbuffer, length)
		#open('tests/logs/test.webm', 'wb').write(b)
		#avutil.av_free(pbuffer)
		
		if (self.av_format_ctx.oformat.flags & avformat.AVFMT_NOFILE) == 0:
			avformat.avio_close(self.av_format_ctx.pb)
			self.av_format_ctx.pb = NULL

	def write_video_frame(self):
		if not self.video_stream: return

		av_frame = self.picture
		
		ret = avutil.av_frame_make_writable(av_frame)
		
		av_frame.pts = self.v_next_pts
		self.v_next_pts += 1

		got_packet = ffi.new('int*')
		got_packet[0] = 0

		pkt = Packet()
		pkt.reset()
		pkt.init()

		ret = avcodec.avcodec_encode_video2(self.video_codec_ctx.av_codec_ctx, pkt.av_packet, av_frame, got_packet)
		if ret < 0:
			raise Exception()
			
		if got_packet[0]:
			self._write_video_packet(pkt)
			return True

	def _write_video_packet(self, pkt):
		avcodec.av_packet_rescale_ts(pkt.av_packet, self.video_codec_ctx.av_codec_ctx.time_base, self.video_stream.av_stream.time_base)
		pkt.stream = self.video_stream

		print pkt

		ret = avformat.av_interleaved_write_frame(self.av_format_ctx, pkt.av_packet)

		pkt.unref()

	def flush_video_frame(self):
		got_packet = ffi.new('int*')
		got_packet[0] = 0

		pkt = Packet()
		pkt.reset()
		pkt.init()

		while True:
			ret = avcodec.avcodec_encode_video2(self.video_codec_ctx.av_codec_ctx, pkt.av_packet, NULL, got_packet)
			if ret < 0:
				raise Exception()
			if got_packet[0]:
				self._write_video_packet(pkt)
			else:
				break

	def flush_audio_frame(self):
		got_packet = ffi.new('int*')
		got_packet[0] = 0

		pkt = Packet()
		pkt.reset()
		pkt.init()

		while True:
			ret = avcodec.avcodec_encode_audio2(self.audio_codec_ctx.av_codec_ctx, pkt.av_packet, NULL, got_packet)
			if ret < 0:
				raise Exception()
			if got_packet[0]:
				self._write_audio_packet(pkt)
			else:
				break
	
	def _write_audio_packet(self, pkt):
		avcodec.av_packet_rescale_ts(pkt.av_packet, self.audio_codec_ctx.av_codec_ctx.time_base, self.audio_stream.av_stream.time_base)
		pkt.stream = self.audio_stream

		print pkt

		ret = avformat.av_interleaved_write_frame(self.av_format_ctx, pkt.av_packet)
		pkt.unref()

	def write_audio_frame(self):
		if not self.audio_stream: return

		av_frame = self.sound
		
		ret = avutil.av_frame_make_writable(av_frame)
		
		av_frame.pts = self.a_next_pts
		self.a_next_pts += av_frame.nb_samples
	
		got_packet = ffi.new('int*')
		got_packet[0] = 0
		
		pkt = Packet()
		pkt.reset()
		pkt.init()

		ret = avcodec.avcodec_encode_audio2(self.audio_codec_ctx.av_codec_ctx, pkt.av_packet, av_frame, got_packet);
		if ret < 0:
			raise Exception()
			
		if got_packet[0]:
			self._write_audio_packet(pkt)
			return True
