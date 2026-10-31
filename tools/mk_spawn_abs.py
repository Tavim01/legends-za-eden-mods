"""Define o coolTimeInfo.time de todos os spawners para N segundos (so os com 0 < t <= 1000; minimo 5).
Usa a tabela original ja extraida (nao precisa do romfs):
  python mk_spawn_abs.py <orig.bin> <segundos> <pasta_saida>
Saida: <pasta_saida>/romfs/world/ik_data/field/pokemon_spawner/pokemon_spawner_data/pokemon_spawner_data_array.bin
"""
import sys, os, struct, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import trinity as t
orig = open(sys.argv[1], "rb").read(); SEC = float(sys.argv[2]); OUT = sys.argv[3]
buf = bytearray(orig); d = t.FB(bytes(orig)); root = d.root()
changed = 0; kept = collections.Counter()
for dbt in d.vec_tab(root, 0):
    for sp in d.vec_tab(dbt, 0):
        ci = d.field(sp, 4)
        if ci is None: continue
        tp = d.field(d.indirect(ci), 1)
        if tp is None: kept["sem tempo"] += 1; continue
        v = struct.unpack_from("<f", buf, tp)[0]
        if v <= 0 or v > 1000: kept[v] += 1; continue
        struct.pack_into("<f", buf, tp, max(5.0, min(v, SEC))); changed += 1
print("alterados:", changed, "mantidos:", dict(kept))
assert len(buf) == len(orig)
dst = os.path.join(OUT, "romfs", "world", "ik_data", "field", "pokemon_spawner", "pokemon_spawner_data")
os.makedirs(dst, exist_ok=True)
open(os.path.join(dst, "pokemon_spawner_data_array.bin"), "wb").write(bytes(buf))
print("escrito", len(buf), "bytes")
