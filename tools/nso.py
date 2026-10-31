import sys, struct
sys.path.insert(0, sys.argv[1] + r"\tools\pylib")
import lz4.block
def load(path):
    d = open(path, "rb").read()
    assert d[:4] == b"NSO0"
    flags = struct.unpack_from("<I", d, 0xC)[0]
    segs = [struct.unpack_from("<III", d, 0x10 + i*16) for i in range(3)]
    csz = struct.unpack_from("<III", d, 0x60)
    bid = d[0x40:0x60].hex().upper()
    out = {}
    for i, (name, (fo, mo, ds)) in enumerate(zip(("text","ro","data"), segs)):
        raw = d[fo:fo+csz[i]]
        out[name] = (mo, lz4.block.decompress(raw, uncompressed_size=ds) if flags & (1<<i) else raw)
    return bid, out
if __name__ == "__main__":
    s = sys.argv[1]
    for v in ("exefs100", "exefs202"):
        bid, seg = load(f"{s}\\{v}\\main")
        print(v, bid[:40], {k:(hex(a), hex(len(b))) for k,(a,b) in seg.items()})
        open(f"{s}\\{v}\\text.bin", "wb").write(seg["text"][1])
        open(f"{s}\\{v}\\ro.bin", "wb").write(seg["ro"][1])
