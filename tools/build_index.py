import sys, mmap, pickle, struct, time
sys.path.insert(0, sys.argv[1])
import trinity as t
a = t.Archive()
fs = open(t.W + r"\data.trpfs", "rb"); mm = mmap.mmap(fs.fileno(), 0, access=mmap.ACCESS_READ)
offs = sorted(a.meta.values()); total = len(mm)
t0 = time.time()
hash2off = {}   # subfile hash -> pak offset
pakinfo = {}    # pak offset -> (n_files)
for k, off in enumerate(offs):
    end = offs[k + 1] if k + 1 < len(offs) else total
    data = mm[off:min(end, off + 1 << 20)] if False else mm[off:end]
    f = t.FB(data); r = f.root()
    hs = f.vec_u64(r, 0)
    pakinfo[off] = (len(hs), end - off)
    for h in hs: hash2off[h] = off
print("paks:", len(offs), "subfiles:", len(hash2off), "time %.0fs" % (time.time() - t0))
# pak index -> offset via first subhash
by_pak = {}
for h, i in a.sub2pak.items(): by_pak.setdefault(i, h)
name2off = {a.pak_paths[i]: hash2off[h] for i, h in by_pak.items() if h in hash2off}
print("named paks:", len(name2off), "of", len(a.pak_paths))
pickle.dump({"hash2off": hash2off, "name2off": name2off, "pakinfo": pakinfo}, open(__import__("os").environ.get("ZA_INDEX","index.pkl"), "wb"))
