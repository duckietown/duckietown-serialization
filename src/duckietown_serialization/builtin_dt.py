import base58

from .serialization1 import Serializable


class GenericData(Serializable):
    def __init__(self, bytes_contents, content_type):
        self.bytes_contents = bytes_contents
        self.content_type = content_type

    def params_to_json_dict(self):
        res = {}
        res['base58'] = base58.b58encode(self.bytes_contents)
        res['content-type'] = self.content_type
        return res

    @classmethod
    def params_from_json_dict(cls, d):
        print d
        base58s = d.pop('base58')
        bytes_contents = base58.b58decode(base58s)
        content_type = d.pop('content-type')
        return dict(content_type=content_type, bytes_contents=bytes_contents)
