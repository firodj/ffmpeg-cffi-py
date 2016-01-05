from .lib import *

class Packet(object):
	
	def __init__(self):
		self.av_pkt = avcodec.av_packet_alloc()
		self.reset()		
	
	def __del__(self):
		self._free()

	def _free(self):
		ref = ffi.new('AVPacket **')
		ref[0] = self.av_pkt		
		avcodec.av_packet_free(ref)
		self.av_pkt = ref[0]

	def reset(self):
		self.av_pkt.data = NULL
		self.av_pkt.size = 0

	def init(self):
		avcodec.av_init_packet(self.av_pkt)
		
	def unref(self):
		avcodec.av_packet_unref(self.av_pkt)
		
	@property
	def stream(self):
		return self.stream
	@stream.setter
	def stream(self, v):
		self.stream = v
		self.av_pkt.stream_index = self.stream.index

	@property
	def pts(self):
		return None if self.av_pkt.pts == ffi.cast('int64_t',avutil.AV_NOPTS_VALUE) else self.av_pkt.pts
	@pts.setter
	def pts(self, v):
		self.av_pkt.pts = ffi.cast('int64_t',avutil.AV_NOPTS_VALUE) if v is None else v

	@property
	def dts(self):
		return None if self.av_pkt.dts == ffi.cast('int64_t',avutil.AV_NOPTS_VALUE) else self.av_pkt.dts
	@dts.setter
	def dts(self, v):
		self.av_pkt.dts = ffi.cast('int64_t',avutil.AV_NOPTS_VALUE) if v is None else v

	@property
	def duration(self):
		return None if self.av_pkt.duration == ffi.cast('int64_t',avutil.AV_NOPTS_VALUE) else self.av_pkt.duration

	@property
	def pos(self):
		return None if self.av_pkt.pos == -1 else self.av_pkt.pos

	@property
	def size(self):
		return self.av_pkt.size
	