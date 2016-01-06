# -*- coding: utf-8 -*-

import pytest
from ffmpeg.dict import Dict

@pytest.fixture
def _dict():
	d = Dict()
	d['a'] = 'b'
	d['c'] = '8'
	return d

def test_set_get_del_count(_dict):
	assert 2 == len(_dict)
	assert 'b' == _dict['a']
	
	del(_dict['c'])
	assert 1 == len(_dict)

def test_iter(_dict):
	r = list()
	for k, v in _dict:
		r.append( (k,v) )

	assert 2 == len(r)
	assert ('a', 'b') == r[0]
	assert ('c', '8') == r[1]

def test_from_dict(_dict):
	d = dict(m='20', x='wtf')
	_dict.from_dict(d)
	assert '20' == _dict['m']
	assert 'wtf' == _dict['x']

def test_copy_from(_dict):
	_d = Dict()
	_d.copy_from(_dict)

	assert 2 == len(_d)