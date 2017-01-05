# -*- coding: utf-8 -*-

import pytest
from ffmpeg.coder import *
from ffmpeg.codecctx import *
from ffmpeg.lib import *
from fractions import Fraction

id_h264 = avcodec.AV_CODEC_ID_H264

@pytest.fixture(scope='module')
def setup():
	register_all()

def test_create_free(setup):
	encoder = Coder.find_encoder(id_h264)

	ctx = CodecCtx.create( encoder )
	assert True == ctx.is_allocated
	assert NULL != ctx.av_codec_ctx

	ctx.free()
	assert False == ctx.is_allocated
	assert NULL == ctx.av_codec_ctx

def test_open_close(setup):
	decoder = Coder.find_decoder(id_h264)

	ctx = CodecCtx.create( decoder )
	assert False == ctx.is_open()
	assert True == ctx.open()
	assert True == ctx.is_open()
	assert True == ctx.close()
	assert False == ctx.is_open()

def test_clone(setup):
	decoder = Coder.find_decoder(id_h264)
	ctx = CodecCtx.create( decoder )

	ctx.width = 352
	ctx.height = 288
	ctx.pix_fmt = "yuv420p"

	assert b"yuv420p" == ctx.pix_fmt

	cloned = ctx.clone()
	assert cloned.av_codec_ctx != ctx.av_codec_ctx
	assert cloned.coder.av_coder == ctx.coder.av_coder

	assert 352 == cloned.width
	assert 288 == cloned.height
	assert b"yuv420p" == cloned.pix_fmt
