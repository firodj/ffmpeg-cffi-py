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
	ctx = FormatCtx.open(path)

	assert InputFormat == type(ctx)

	pp( ctx.to_primitive(True) )