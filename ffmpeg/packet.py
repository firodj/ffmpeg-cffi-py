from .lib import *

class Packet(object):
	
	def __init__(self):
		self.av_packet = avcodec.av_packet_alloc()
		self._stream = None
		self.reset()		
	
	def __del__(self):
		self._free()

	def _free(self):
		ref = ffi.new('AVPacket **')
		ref[0] = self.av_packet		
		avcodec.av_packet_free(ref)
		self.av_packet = ref[0]

	def reset(self):
		self.av_packet.data = NULL
		self.av_packet.size = 0

	def init(self):
		avcodec.av_init_packet(self.av_packet)
		
	def unref(self):
		avcodec.av_packet_unref(self.av_packet)
		
	@property
	def stream(self):
		return self._stream
	@stream.setter
	def stream(self, v):
		self._stream = v
		self.av_packet.stream_index = self._stream.index

	def stream_eq(self, stream):
		if self.av_packet.stream_index == stream.index:
			self._stream = stream
			return True
		return False

	@property
	def pts(self):
		return None if self.av_packet.pts == ffi.cast('int64_t',avutil.AV_NOPTS_VALUE) else self.av_packet.pts
	@pts.setter
	def pts(self, v):
		self.av_packet.pts = ffi.cast('int64_t',avutil.AV_NOPTS_VALUE) if v is None else v

	@property
	def dts(self):
		return None if self.av_packet.dts == ffi.cast('int64_t',avutil.AV_NOPTS_VALUE) else self.av_packet.dts
	@dts.setter
	def dts(self, v):
		self.av_packet.dts = ffi.cast('int64_t',avutil.AV_NOPTS_VALUE) if v is None else v

	@property
	def duration(self):
		return None if self.av_packet.duration == ffi.cast('int64_t',avutil.AV_NOPTS_VALUE) else self.av_packet.duration

	@property
	def pos(self):
		return None if self.av_packet.pos == -1 else self.av_packet.pos

	@property
	def size(self):
		return self.av_packet.size

	def consume(self, size):
		self.av_packet.size -= size
		self.av_packet.data += size

	def __repr__(self):
		return "<%s %d stream=%d %s>" % (self.__class__.__name__,
			self.size,
			self.av_packet.stream_index,
			repr(self.av_packet))