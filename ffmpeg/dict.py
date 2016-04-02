from .lib import *

class Dict(object):
    def __init__(self, av_dict = NULL):
        self.av_dict = av_dict
        self._owned = False

    def __len__(self):
        return avutil.av_dict_count(self.av_dict)

    def __setitem__(self, key, value):
        pm = ffi.new('AVDictionary *[1]')
        pm[0] = self.av_dict
        
        if value is None:
            value = NULL
        elif type(value) == unicode:
            value = value.encode('utf-8')
        elif type(value) != str:
            value = str(value)
        
        err = avutil.av_dict_set(pm, key, value, 0)
        if err < 0:
            raise Exception()

        if self.av_dict == NULL:
            self._owned = True
        self.av_dict = pm[0]

    def __getitem__(self, key):
        DictEntry = avutil.av_dict_get(self.av_dict, key, NULL, avutil.AV_DICT_MATCH_CASE)
        return stringify(DictEntry.value) if DictEntry != NULL else None

    def __delitem__(self, key):
        self.__setitem__(key, None)

    def __iter__(self):
        self.prev = NULL
        return self

    def __del__(self):
        if self._owned:
            self.free()

    def from_dict(self, _dict):
        for k, v in iteritems(_dict):
            self.__setitem__(k, v)

    def next(self):
        DictEntry = avutil.av_dict_get(self.av_dict, "", self.prev, avutil.AV_DICT_IGNORE_SUFFIX)
        self.prev = DictEntry
        if DictEntry == NULL:
            raise StopIteration
        return stringify(DictEntry.key), stringify(DictEntry.value)

    def free(self):
        pm = ffi.new('AVDictionary *[1]')
        pm[0] = self.av_dict
        
        avutil.av_dict_free(pm)
        
        self.av_dict = pm[0]
        self._owned = False

    def copy_from(self, src):
        pm = ffi.new('AVDictionary *[1]')
        pm[0] = self.av_dict
        avutil.av_dict_copy(pm, src.av_dict, 0)

        if self.av_dict == NULL:
            self._owned = True
        self.av_dict = pm[0]

    def to_primitive(self):
        return {k: v for k, v in self if not k.startswith('_')}
