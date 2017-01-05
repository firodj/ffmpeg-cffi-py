# -*- coding: utf-8 -*-

import pytest
import ffmpeg
from ffmpeg.formatctx import *
from ffmpeg.lib import *
from fractions import Fraction
#from ffmpeg.error import FFMPEGException, AVERROR_STREAM_NOT_FOUND

from pprint import pprint as pp
from six import print_

id_h264 = avcodec.AV_CODEC_ID_H264

@pytest.fixture(scope='module')
def setup():
	register_all()

def test_open_input(setup):
	# LOCAL TEST ONLY
	path = 'tests/data/film佐伯.mp4'

	fmt_ctx = FormatCtx.open(path)

	assert InputFormat == type(fmt_ctx)

	print_(fmt_ctx)

	fmt_ctx.open_decoder()

	#print_(fmt_ctx.video_codec_ctx, fmt_ctx.video_codec_ctx.coder)
	#print_(fmt_ctx.audio_codec_ctx, fmt_ctx.audio_codec_ctx.coder)
	pp( fmt_ctx.to_primitive(True) )

	img = None
	which_frame = None

	for frame in fmt_ctx.next_frame():

		t = float(frame.pkt_pts_f)
		if frame.type == b'video':
			which_frame = frame
			if t >= 15.0:
				break

	assert ffmpeg.frame.VideoFrame == type(which_frame)

	img = which_frame.process()
	fmt_ctx.close_decoder()

	if img: img.show()


@pytest.mark.skipif(True, reason="not using check_ret since more complicated exception handling")
def test_open_input_when_error(setup, mocker):
	path = 'tests/data/film佐伯.mp4'

	mocker.patch('ffmpeg.formatctx.avformat_open_input',
		return_value=AVERROR_STREAM_NOT_FOUND)
	
	with pytest.raises(FFMPEGException) as excinfo:
		fmt_ctx = FormatCtx.open(path)

	assert "Stream not found" in excinfo.value.message


@pytest.mark.skipif(True, reason="still bug or wrong approach")
def test_create_output(setup):
	path_out = 'tests/logs/output.mp4'

	fmt_ctx = FormatCtx.create(path_out)

	assert OutputFormat == type(fmt_ctx)

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
