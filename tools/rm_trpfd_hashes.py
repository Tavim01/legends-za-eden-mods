"""Remove do data.trpfd as entradas dos caminhos dados (para arquivos soltos em romfs/ passarem a valer).
  python rm_trpfd_hashes.py <raiz com trpfdlib.py e tools/pylib> <trpfd_entrada> <trpfd_saida> <caminho> [<caminho> ...]
Caminhos ja removidos sao ignorados."""
import sys; sys.path.insert(0, sys.argv[1])
import trpfdlib as L, trinity as t
def _init(self, fd, fs=None):  # so o indice (trpfd); nao precisa do trpfs
    d = t.FB(open(fd, "rb").read()); self.d = d; r = d.root()
    self.sub_hashes = d.vec_u64(r, 0); self.pak_paths = d.vec_str(r, 1)
    self.sub_pak = [d.u64(x, 0) for x in d.vec_tab(r, 2)]
t.Archive.__init__ = _init
src, out, paths = sys.argv[2], sys.argv[3], sys.argv[4:]
P = L.load_parts(src); rm = {L.zh(p) for p in paths}
keep = [i for i, x in enumerate(P["hashes"]) if x not in rm]
print("removendo", len(P["hashes"]) - len(keep), "de", len(rm), "pedidos")
data = L.build([P["hashes"][i] for i in keep], P["paths"], [P["subinfos"][i] for i in keep], P["fileinfos"])
open(out, "wb").write(data)
Q = L.load_parts(out)
assert Q["hashes"] == [P["hashes"][i] for i in keep] and Q["subinfos"] == [P["subinfos"][i] for i in keep] and Q["paths"] == P["paths"] and Q["fileinfos"] == P["fileinfos"]
print("verificado", len(data), "bytes; hashes", len(Q["hashes"]))
