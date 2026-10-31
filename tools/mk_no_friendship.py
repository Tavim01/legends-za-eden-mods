"""Troca as evolucoes por amizade de avalon/data/personal_array.bin por nivel (ou item/dia/noite).
  python mk_no_friendship.py <personal_array.bin entrada> <saida>
Tabela: root.field0 = vetor de Personal; cada Personal tem, no slot 21, um vetor de structs de 16 bytes
[u16 nivel][u16 metodo][u16 arg][..][u16 especie @12]. Metodos: 1 amizade, 2 amizade/dia, 3 amizade/noite,
4 nivel, 8 usar item (arg = id do item), 29 amizade+golpe tipo (Sylveon), 32 nivel de dia, 33 nivel de noite."""
import struct, sys
b = bytearray(open(sys.argv[1], "rb").read())
u32 = lambda p: struct.unpack_from("<I", b, p)[0]; u16 = lambda p: struct.unpack_from("<H", b, p)[0]; i32 = lambda p: struct.unpack_from("<i", b, p)[0]
def slots(pos):
    v = pos - i32(pos); return [u16(v + 4 + 2 * i) for i in range((u16(v) - 4) // 2)]
# (especie de origem, forma, metodo antigo) -> (novo metodo, nivel, arg)
NEW = {(42,0,1):(4,35,0), (52,1,1):(4,28,0), (113,0,1):(4,35,0), (172,0,1):(4,15,0), (173,0,1):(4,15,0),
       (174,0,1):(4,15,0), (175,0,1):(4,20,0), (298,0,1):(4,15,0), (427,0,1):(4,25,0), (446,0,1):(4,30,0),
       (527,0,1):(4,20,0), (541,0,1):(4,25,0), (772,0,1):(4,40,0),
       (133,0,2):(32,30,0), (406,0,2):(4,15,0), (447,0,2):(4,25,0),
       (133,0,3):(33,30,0), (433,0,3):(4,20,0), (872,0,3):(4,30,0),
       (133,0,29):(8,0,7)}   # Eevee->Sylveon: Shiny Stone (id 7)
root = u32(0); p = root + slots(root)[0]; vec = p + u32(p); done = set()
for k in range(u32(vec)):
    t = vec + 4 + 4 * k + u32(vec + 4 + 4 * k); so = slots(t)
    if len(so) <= 21 or not so[21]: continue
    dev, form = u16(t + so[0]), u16(t + so[0] + 2)
    v = t + so[21] + u32(t + so[21])
    for j in range(u32(v)):
        e = v + 4 + 16 * j; meth = u16(e + 2)
        if (dev, form, meth) in NEW:
            m, lvl, arg = NEW[(dev, form, meth)]
            struct.pack_into("<HHH", b, e, lvl, m, arg); done.add((dev, form, meth))
print("alteradas", len(done), "de", len(NEW), "| faltaram:", sorted(set(NEW) - done))
assert len(done) == len(NEW)
open(sys.argv[2], "wb").write(b)
