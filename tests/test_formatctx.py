# -*- coding: utf-8 -*-

import pytest
from ffmpeg.formatctx import *
from ffmpeg.lib import *
from fractions import Fraction

from pprint import pprint as pp

id_h264 = avcodec.AV_CODEC_ID_H264

@pytest.fixture(scope='module')
def setup():
	register_all()

def test_open_input(setup):
	# LOCAL TEST ONLY
	path = 'tests/data/film佐伯.mp4'
	fmt_ctx = FormatCtx.open(path)

	assert InputFormat == type(fmt_ctx)

	print fmt_ctx

	fmt_ctx.open_decoder()
	print fmt_ctx.video_codec_ctx, fmt_ctx.video_codec_ctx.coder
	print fmt_ctx.audio_codec_ctx, fmt_ctx.audio_codec_ctx.coder

	img = None

	for frame in fmt_ctx.next_frame():
 
		t = float(frame.pkt_pts_f)
		if frame.type == 'video' and t >= 15.0:
			img = frame.process()
			break

	fmt_ctx.close_decoder()

	if img: img.show()

def test_create_output(setup):
	path_out = 'tests/logs/output.webm'

	fmt_ctx = FormatCtx.create(path_out)

	fmt_ctx.create_video_stream()
	fmt_ctx.create_audio_stream()

	fmt_ctx.open_encoder()

	fmt_ctx.write_header()

	while fmt_ctx.v_next_pts_f <= 1.0:
		if fmt_ctx.v_next_pts_f <= fmt_ctx.a_next_pts_f:
			fmt_ctx.write_video_frame()
		else:
			fmt_ctx.write_audio_frame()

		if fmt_ctx.v_next_pts_f <= fmt_ctx.a_next_pts_f:
			fmt_ctx.flush_video_frame()
			fmt_ctx.flush_audio_frame()
		else:
			fmt_ctx.flush_audio_frame()
			fmt_ctx.flush_video_frame()

	fmt_ctx.write_trailer()

	fmt_ctx.close_encoder()
