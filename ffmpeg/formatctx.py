from .lib import *
		
class FormatCtx(object):
	
	def __init__(self, av_fmt_ctx):
		self.av_fmt_ctx = av_fmt_ctx
	
	@classmethod
	def open(cls, path):
		if type(path) == unicode:
			path = path.encode('utf-8')
	
		ref = ffi.new('struct AVFormatContext **')
		err = avformat.avformat_open_input(ref, filepath, NULL, NULL)
		if err: return
		if ref[0] == NULL: return
		
		return cls(ref[0])
	
	@classmethod
	def create(cls, path=None, format=None):
		if type(path) == unicode:
			path = path.encode('utf-8')
			
		ref = ffi.new('struct AVFormatContext **')
		err = avformat.avformat_alloc_output_context2(ref, NULL, format, path)
		if err: return None
		if ref[0] == NULL: return
		
		return cls(ref[0])
	
	def __len__(self):
		return self.av_fmt_ctx.nb_streams
