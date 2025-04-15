import os
from six import iteritems
from six.moves import xrange
from struct import pack, unpack
from collections import namedtuple

from ctypes.util import find_library
from cffi import FFI
from fractions import Fraction
import sys

cwd = lambda x: os.path.join(os.path.dirname(__file__), x)
ffi = FFI()

def dll(name):
    if sys.platform == 'linux':
        return name

    path = find_library(name)
    if not path:
        path = cwd(name)
    if not os.path.exists(path):
        xname = name.replace("-",".")
        path = find_library(xname)
        if not path:
            path = cwd(xname)
    if not os.path.exists(path):
        raise Exception("dll not found {name}".format(name=name))
    return path

ffi.cdef(open(cwd('avutil_t.h')).read())
ffi.cdef(open(cwd('avcodec_t.h')).read())
ffi.cdef(open(cwd('avformat_t.h')).read())
ffi.cdef(open(cwd('swscale_t.h')).read())

ffi.cdef(open(cwd('avutil.h')).read())
ffi.cdef(open(cwd('avcodec.h')).read())
ffi.cdef(open(cwd('avformat.h')).read())
ffi.cdef(open(cwd('swscale.h')).read())

avutil = ffi.dlopen(dll('avutil'))
avcodec = ffi.dlopen(dll('avcodec'))
avformat = ffi.dlopen(dll('avformat'))
swscale = ffi.dlopen(dll('swscale'))

NULL = ffi.NULL

Version = namedtuple('Version', ('major', 'minor', 'micro'))

def stringify(s):
    return ffi.string(s) if s != NULL else None

def existent(n):
    return n if n > 0 else None

def q2d(a):
    if a.den==0: return float('nan')
    return float(a.num) / float(a.den)

def is_q_eq(a, num, den):
    return a.num == num and a.den == den

def fmt_timestr(bigs):
    if bigs is None: return None

    past = bigs < 0
    if past: bigs = -bigs
    
    secs  = bigs // 1000
    msecs = bigs % 1000
    
    mins = secs // 60
    secs %= 60
    hours = mins // 60
    mins %= 60
    days = hours // 24
    hours %= 24
    
    s = "%02d:%02d:%02d.%03d" % (hours, mins, secs, msecs)
    if days > 0: s = "%dd %s" % (days, s)
    if past: s = "-%s" % (s,)

    return s

def fmt_d2timestr(ts):
    if ts is None: return None

    bigs = ts * 1000.0 + 0.5
    return fmt_timestr(bigs)

def fmt_f2timestr(ts):
    if ts is None: return None

    bigs = int( float(ts * 1000) + 0.5 )
    return fmt_timestr(bigs)

def fmt_q2timestr(dur, tb):
    if dur is None or tb is None or tb == avutil.AV_NOPTS_VALUE: return None

    ts = dur * q2d(tb)
    return fmt_d2timestr(ts)

def avutil_version():
    v = unpack('BBBB', pack('>L', avutil.avutil_version())) 
    return Version(major=v[1], minor=v[2], micro=v[3])

def avformat_version():
    v = unpack('BBBB', pack('>L', avformat.avformat_version())) 
    return Version(major=v[1], minor=v[2], micro=v[3])

def avcodec_version():
    v = unpack('BBBB', pack('>L', avcodec.avcodec_version()))   
    return Version(major=v[1], minor=v[2], micro=v[3])

def swscale_version():
    v = unpack('BBBB', pack('>L', swscale.swscale_version()))   
    return Version(major=v[1], minor=v[2], micro=v[3])

def register_all():
    avformat.av_register_all()

def flatten_primitives(value, level=''):
    output = dict()

    if type(value) == dict:
        keys = value.iterkeys()
    elif type(value) == list:
        keys = xrange(0, len(value))
    else:
        return

    for k in keys:
        v = value[k]
        if type(v) in (dict, list):
            output.update( flatten_primitives(v, level+ str(k)+'.') )
        else:
            if v is not None:
                if type(v) not in (unicode, str):
                    v = str(v)
                output[ level+ str(k) ] = v

    return output

def correct_pix_fmt(pix_fmt):
    if pix_fmt == avutil.AV_PIX_FMT_YUVJ420P:
        return avutil.AV_PIX_FMT_YUV420P
    elif pix_fmt == avutil.AV_PIX_FMT_YUVJ422P:
        return avutil.AV_PIX_FMT_YUV422P
    elif pix_fmt == avutil.AV_PIX_FMT_YUVJ444P:
        return avutil.AV_PIX_FMT_YUV444P
    elif pix_fmt == avutil.AV_PIX_FMT_YUVJ440P:
        return avutil.AV_PIX_FMT_YUV440P
    return pix_fmt

def rational(r):
    if r.den == 0: return None
    return Fraction(r.num, r.den)

def time_base_q():
    r = avutil.av_get_time_base_q()
    return rational( r )
