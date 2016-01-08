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