import sys,os,struct; sys.path.insert(0,sys.argv[1]); sys.path.insert(0,sys.argv[1]+r"\tools\pylib")
import flatbuffers, trinity as t
M=2**64-1
def zh(p):
    h=0xcbf29ce484222645
    for c in p.encode(): h=((h^c)*0x100000001b3)&M
    return h
def read_trpfd(path):
    a=t.Archive(fd=path); d=a.d; r=d.root()
    subinfo_f0=[d.u32(d.indirect_tab(x) if False else d.indirect(d.field(x,1)),0) for x in d.vec_tab(r,2)]
    return a, subinfo_f0
def build(hashes, paths, subinfos, fileinfos):
    b=flatbuffers.Builder(1<<24)
    # subinfos: list of (index, field00)
    sub_offs=[]
    for idx,f0 in subinfos:
        b.StartObject(1); b.PrependUint32Slot(0,f0,0); si=b.EndObject()
        b.StartObject(2); b.PrependUint64Slot(0,idx,0); b.PrependUOffsetTRelativeSlot(1,si,0); sub_offs.append(b.EndObject())
    fi_offs=[]
    for sz,cnt in fileinfos:
        b.StartObject(2); b.PrependUint64Slot(0,sz,0); b.PrependUint64Slot(1,cnt,0); fi_offs.append(b.EndObject())
    path_offs=[b.CreateString(p) for p in paths]
    def vec_off(offs):
        b.StartVector(4,len(offs),4)
        for o in reversed(offs): b.PrependUOffsetTRelative(o)
        return b.EndVector()
    v_sub=vec_off(sub_offs); v_fi=vec_off(fi_offs); v_paths=vec_off(path_offs)
    b.StartVector(8,len(hashes),8)
    for h in reversed(hashes): b.PrependUint64(h)
    v_h=b.EndVector()
    b.StartObject(4)
    b.PrependUOffsetTRelativeSlot(0,v_h,0); b.PrependUOffsetTRelativeSlot(1,v_paths,0)
    b.PrependUOffsetTRelativeSlot(2,v_sub,0); b.PrependUOffsetTRelativeSlot(3,v_fi,0)
    root=b.EndObject(); b.Finish(root); return bytes(b.Output())
def load_parts(path):
    a=t.Archive(fd=path); d=a.d; r=d.root()
    f0=[]
    for x in d.vec_tab(r,2):
        sp=d.field(x,1); st=d.indirect(sp); f0.append(d.u32(st,0))
    fileinfos=[(d.u64(x,0),d.u64(x,1)) for x in d.vec_tab(r,3)]
    return dict(hashes=list(a.sub_hashes),paths=list(a.pak_paths),subinfos=list(zip(a.sub_pak,f0)),fileinfos=fileinfos)
if __name__=="__main__":
    ptbr=os.environ.get("ZA_TRPFD","data.trpfd")
    P=load_parts(ptbr)
    out=sys.argv[2]
    data=build(P["hashes"],P["paths"],P["subinfos"],P["fileinfos"])
    open(out,"wb").write(data)
    Q=load_parts(out)
    print("roundtrip equal:",all(P[k]==Q[k] for k in P), len(data),"vs orig",os.path.getsize(ptbr))
