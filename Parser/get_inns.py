from b2b import get_inns_by_category
import sys


class Unbuffered(object):
    def __init__(self, stream):
        self.stream = stream

    def write(self, data):
        self.stream.write(data)
        self.stream.flush()

    def writelines(self, datas):
        self.stream.writelines(datas)
        self.stream.flush()

    def __getattr__(self, attr):
        return getattr(self.stream, attr)


def parse_category(name):
    inns = get_inns_by_category(name)
    return inns


sys.stdout = Unbuffered(sys.stdout)
print(parse_category(""))
