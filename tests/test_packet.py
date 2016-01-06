# -*- coding: utf-8 -*-

import pytest
from ffmpeg.packet import Packet
from ffmpeg.lib import avutil, ffi, NULL

def test_alloc_free():
	pkt = Packet()
	assert NULL != pkt.av_packet

	pkt._free()
	assert NULL == pkt.av_packet

def test_dts_pts():
	pkt = Packet()
	pkt.dts = None
	pkt.pts = None

	nopts = int( ffi.cast('int64_t', avutil.AV_NOPTS_VALUE) )

	assert nopts == pkt.av_packet.dts
	assert nopts == pkt.av_packet.pts