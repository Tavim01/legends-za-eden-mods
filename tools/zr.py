import sys, mmap, pickle, collections
sys.path.insert(0, __import__("os").path.dirname(__import__("os").path.abspath(__file__)))
import trinity as t
class R:
    def __init__(self):
        idx = pickle.load(open(__import__("os").environ.get("ZA_INDEX","index.pkl"), "rb")); self.name2off = idx["name2off"]; self.pakinfo = idx["pakinfo"]
        fs = open(t.W + r"\data.trpfs", "rb"); self.mm = mmap.mmap(fs.fileno(), 0, access=mmap.ACCESS_READ)
    def names(self): return list(self.name2off)
    def read(self, name):
        off = self.name2off[name]; n, size = self.pakinfo[off]
        f = t.FB(self.mm[off:off + size]); r = f.root()
        hashes = f.vec_u64(r, 0); files = f.vec_tab(r, 1); out = []
        for h, tb in zip(hashes, files):
            ct = f.i8(tb, 1); usz = f.u64(tb, 3); data = f.bytes_(tb, 4)
            out.append((h, ct, usz, data))
        return out
    def get(self, name):
        res = []
        for h, ct, usz, data in self.read(name): res.append(t.decompress(ct, data, usz))
        return res

