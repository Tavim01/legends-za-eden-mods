import sys,os,struct,pickle,collections; sys.path.insert(0,sys.argv[1]); sys.path.insert(0,sys.argv[1]+r"\tools\pylib")
import zr,trinity as t,trpfdlib as L
FACTOR=float(sys.argv[2]); OUTROOT=sys.argv[3]
SP="world/ik_data/field/pokemon_spawner/pokemon_spawner_data/pokemon_spawner_data_array.bin"
h=L.zh(SP); r=zr.R(); h2o=pickle.load(open(__import__("os").environ.get("ZA_INDEX","index.pkl"),"rb"))["hash2off"]
off=h2o[h]; n,size=r.pakinfo[off]; f=t.FB(r.mm[off:off+size]); rt=f.root(); hs=f.vec_u64(rt,0); fl=f.vec_tab(rt,1); tb=fl[hs.index(h)]
orig=t.decompress(f.i8(tb,1),f.bytes_(tb,4),f.u64(tb,3))
os.makedirs(os.path.join(OUTROOT,"backup"),exist_ok=True)
open(os.path.join(OUTROOT,"backup","pokemon_spawner_data_array.orig.bin"),"wb").write(orig)
buf=bytearray(orig); d=t.FB(bytes(orig)); root=d.root()
changed=0; seen=0; skipped=collections.Counter(); before=collections.Counter(); after=collections.Counter()
for dbt in d.vec_tab(root,0):
    for sp in d.vec_tab(dbt,0):
        ci=d.field(sp,4)
        if ci is None: continue
        ct=d.indirect(ci); tp=d.field(ct,1)
        seen+=1
        if tp is None: skipped["no time"]+=1; continue
        v=struct.unpack_from("<f",buf,tp)[0]; before[v]+=1
        if v<=0 or v>1000: skipped["kept (%g)"%v]+=1; after[v]+=1; continue
        nv=max(5.0,round(v*FACTOR,1)); struct.pack_into("<f",buf,tp,nv); changed+=1; after[nv]+=1
print("spawners with coolTimeInfo:",seen,"changed:",changed,"skipped:",dict(skipped))
print("before:",sorted(before.items())[:12]); print("after:",sorted(after.items())[:12])
assert len(buf)==len(orig)
dst=os.path.join(OUTROOT,"romfs","world","ik_data","field","pokemon_spawner","pokemon_spawner_data"); os.makedirs(dst,exist_ok=True)
open(os.path.join(dst,"pokemon_spawner_data_array.bin"),"wb").write(bytes(buf))
print("wrote",len(buf),"bytes")
