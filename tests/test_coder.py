# -*- coding: utf-8 -*-

import pytest
from ffmpeg.coder import *
from ffmpeg.lib import *
from fractions import Fraction

id_mpeg1video = avcodec.AV_CODEC_ID_MPEG1VIDEO
id_mp2 = avcodec.AV_CODEC_ID_MP2
id_dvdsubtitle = avcodec.AV_CODEC_ID_DVD_SUBTITLE

@pytest.fixture(scope='module')
def setup():
	register_all()

def test_find_decoder(setup):
	assert 'mpeg1video' == Coder.get_name(id_mpeg1video)

	decoder = Coder.find_decoder(id_mpeg1video)
	assert VideoCoder == type(decoder)
	assert True == decoder.is_decoder()
	assert False == decoder.is_encoder()
	assert False == decoder.is_descriptor()
	assert 'mpeg1video' == decoder.name
	assert 'MPEG-1 video' == decoder.long_name
	assert 'video' == decoder.type
	assert id_mpeg1video == decoder.id

def test_find_encoder(setup):
	assert 'mp2' == Coder.get_name(id_mp2)

	encoder = Coder.find_encoder(id_mp2)
	assert AudioCoder == type(encoder)
	assert True == encoder.is_encoder()
	assert False == encoder.is_decoder()
	assert False == encoder.is_descriptor()
	assert 'mp2' == encoder.name
	assert 'MP2 (MPEG audio layer 2)' == encoder.long_name
	assert 'audio' == encoder.type
	assert id_mp2 == encoder.id

def test_find_descriptor(setup):
	assert 'dvd_subtitle' == Coder.get_name(id_dvdsubtitle)

	coder = Coder.find_descriptor(id_dvdsubtitle)
	assert Coder == type(coder)
	assert 'dvd_subtitle' == coder.name
	assert 'DVD subtitles' == coder.long_name
	assert True == coder.is_descriptor()
	assert id_dvdsubtitle == coder.id
	assert 'subtitle' == coder.type

def test_video_coder(setup):
	encoder = Coder.find_encoder(id_mpeg1video)

	assert 1 <= len(encoder.supported_framerates())
	assert Fraction(25,1) in encoder.supported_framerates()

	assert 1 <= len(encoder.supported_pix_fmts())
	assert 'yuv420p' in encoder.supported_pix_fmts()
 
def test_audio_coder(setup):
	encoder = Coder.find_encoder(id_mp2)

	assert 1 <= len(encoder.supported_samplerates())
	assert 44100 in encoder.supported_samplerates()

	assert 1 <= len(encoder.supported_sample_fmts())
	assert 's16' in encoder.supported_sample_fmts()

	assert 1 <= len(encoder.supported_channel_layouts())
	assert 'mono' in encoder.supported_channel_layouts()