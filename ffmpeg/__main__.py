import sys
import ffmpeg
from ffmpeg.formatctx import *
from ffmpeg.lib import *
from fractions import Fraction
from pprint import pprint as pp
from six import print_
import time

if len(sys.argv) <= 1:
	print_("python -m ffmpeg <file>")
	exit()


path = sys.argv[1]

register_all()

fmt_ctx = FormatCtx.open(path)

pp(fmt_ctx)

fmt_ctx.open_decoder()

if fmt_ctx.video_codec_ctx:
	print_(fmt_ctx.video_codec_ctx, fmt_ctx.video_codec_ctx.coder)
if fmt_ctx.audio_codec_ctx:
	print_(fmt_ctx.audio_codec_ctx, fmt_ctx.audio_codec_ctx.coder)

pp( fmt_ctx.to_primitive(True) )
print_(fmt_ctx.duration, fmt_ctx.duration_f)

fmt_ctx.seek_frame( 1000.0 )
video_frame_cnt = 0
t = None

start_time = time.time()
next_time = 1.0

for frame in fmt_ctx.next_frame():
	elapsed_time = time.time() - start_time

	t = float(frame.pkt_pts_f)
	if frame.type == 'video': 
		video_frame_cnt += 1

	if elapsed_time >= next_time:
		print_(fmt_f2timestr(t), video_frame_cnt, video_frame_cnt / next_time)
		next_time += 1.0

print_(fmt_f2timestr(t), video_frame_cnt)

fmt_ctx.close_decoder()
