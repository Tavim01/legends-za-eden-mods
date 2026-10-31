import struct, sys, os, re, zlib
W = os.environ.get("ZA_ARC", os.path.join("romfs", "arc"))

def fnv1a64(s):
    h = 0xcbf29ce484222325
    for b in (s.encode() if isinstance(s, str) else s):
        h ^= b; h = (h * 0x100000001b3) & 0xFFFFFFFFFFFFFFFF
    return h

class FB:
    def __init__(self, buf): self.b = buf
    def root(self): return struct.unpack_from("<I", self.b, 0)[0]
    def field(self, tab, idx):  # absolute offset of field or None
        vt = tab - struct.unpack_from("<i", self.b, tab)[0]
        vsz = struct.unpack_from("<H", self.b, vt)[0]
        o = 4 + 2 * idx
        if o >= vsz: return None
        off = struct.unpack_from("<H", self.b, vt + o)[0]
        return tab + off if off else None
    def indirect(self, pos): return pos + struct.unpack_from("<I", self.b, pos)[0]
    def vec(self, pos):  # returns (start, length) of vector at field pos
        v = self.indirect(pos); n = struct.unpack_from("<I", self.b, v)[0]; return v + 4, n
    def vec_u64(self, tab, idx):
        p = self.field(tab, idx)
        if p is None: return []
        st, n = self.vec(p); return list(struct.unpack_from("<%dQ" % n, self.b, st))
    def vec_str(self, tab, idx):
        p = self.field(tab, idx); st, n = self.vec(p); out = []
        for i in range(n):
            sp = self.indirect(st + 4 * i); l = struct.unpack_from("<I", self.b, sp)[0]
            out.append(self.b[sp + 4: sp + 4 + l].decode("utf-8", "replace"))
        return out
    def vec_tab(self, tab, idx):
        p = self.field(tab, idx)
        if p is None: return []
        st, n = self.vec(p); return [self.indirect(st + 4 * i) for i in range(n)]
    def u64(self, tab, idx, d=0):
        p = self.field(tab, idx); return d if p is None else struct.unpack_from("<Q", self.b, p)[0]
    def u32(self, tab, idx, d=0):
        p = self.field(tab, idx); return d if p is None else struct.unpack_from("<I", self.b, p)[0]
    def i8(self, tab, idx, d=0):
        p = self.field(tab, idx); return d if p is None else struct.unpack_from("<b", self.b, p)[0]
    def u8(self, tab, idx, d=0):
        p = self.field(tab, idx); return d if p is None else self.b[p]
    def bytes_(self, tab, idx):
        p = self.field(tab, idx); st, n = self.vec(p); return self.b[st:st + n]

class Archive:
    def __init__(self, fd=W + r"\data.trpfd", fs=W + r"\data.trpfs"):
        self.fsf = open(fs, "rb")
        magic, ofs = struct.unpack("<QQ", self.fsf.read(16)); assert magic == 0x004B434150454E4F, hex(magic)
        self.fsf.seek(ofs); meta = self.fsf.read()
        m = FB(meta); r = m.root()
        mh = m.vec_u64(r, 0); mo = m.vec_u64(r, 1)
        self.meta = dict(zip(mh, mo))
        d = FB(open(fd, "rb").read()); self.d = d; r = d.root()
        self.sub_hashes = d.vec_u64(r, 0)
        self.pak_paths = d.vec_str(r, 1)
        self.sub_pak = [d.u64(t, 0) for t in d.vec_tab(r, 2)]
        self.pak_size = [d.u64(t, 0) for t in d.vec_tab(r, 3)]
        self.sub2pak = dict(zip(self.sub_hashes, self.sub_pak))
    def pak(self, i):
        h = fnv1a64(self.pak_paths[i]); off = self.meta[h]
        self.fsf.seek(off); data = self.fsf.read(self.pak_size[i])
        f = FB(data); r = f.root()
        hashes = f.vec_u64(r, 0); files = f.vec_tab(r, 1)
        return f, hashes, files
    def get(self, h):
        if isinstance(h, str): h = fnv1a64(h)
        i = self.sub2pak[h]; f, hashes, files = self.pak(i)
        k = hashes.index(h); t = files[k]
        ctype = f.i8(t, 1); usz = f.u64(t, 3); data = f.bytes_(t, 4)
        return decompress(ctype, data, usz)

def decompress(ctype, data, usz):
    if ctype == -1 or ctype == 0 and len(data) == usz: return bytes(data)
    if ctype == 1: return zlib.decompress(data)
    if ctype == 2:
        pass
        import lz4.block; return lz4.block.decompress(data, uncompressed_size=usz)
    if ctype == 3:
        import ctypes
        global _ooz
        try: _ooz
        except NameError:
            _ooz = ctypes.CDLL(os.environ.get("ZA_OOZ", "ooz.dll"))
            _ooz.zk_decompress.argtypes = [ctypes.c_char_p, ctypes.c_size_t, ctypes.c_void_p, ctypes.c_size_t]
            _ooz.zk_decompress.restype = ctypes.c_int
        src = bytes(data) + b"\0" * 64
        dst = ctypes.create_string_buffer(usz + 512)
        n = _ooz.zk_decompress(src, len(data), dst, usz)
        if n != usz: raise ValueError("kraken decode %d != %d" % (n, usz))
        return dst.raw[:usz]
    raise NotImplementedError("compression %d" % ctype)

if __name__ == "__main__":
    a = Archive()
    print("subfiles:", len(a.sub_hashes), " paks:", len(a.pak_paths), " meta entries:", len(a.meta))
    print("first paks:", a.pak_paths[:3])
    from collections import Counter
    f, hashes, files = a.pak(0)
    print("pak0 files:", len(files), Counter(f.i8(t, 1) for t in files))


