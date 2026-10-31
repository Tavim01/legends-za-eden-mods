import sys,re,struct; sys.path.insert(0, __import__("os").path.dirname(__import__("os").path.abspath(__file__)))
import trinity as t
FB=t.FB
BT=["None","UType","Bool","Byte","UByte","Short","UShort","Int","UInt","Long","ULong","Float","Double","String","Vector","Obj","Union","Array"]
def str_at(f,p):
    sp=f.indirect(p); l=struct.unpack_from("<I",f.b,sp)[0]; return f.b[sp+4:sp+4+l].decode("utf-8","replace")
def parse_bfbs(buf):
    f=FB(buf); r=f.root()
    objs=[]
    for o in f.vec_tab(r,0):
        name=str_at(f,f.field(o,0)); fields=[]
        for fl in f.vec_tab(o,1):
            fn=str_at(f,f.field(fl,0)); ty=f.field(fl,1); tt=f.indirect(ty)
            bt=f.u8(tt,0); el=f.u8(tt,1); idx=struct.unpack_from("<i",f.b,f.field(tt,2))[0] if f.field(tt,2) else -1
            fid=struct.unpack_from("<H",f.b,f.field(fl,2))[0] if f.field(fl,2) else 0
            off=struct.unpack_from("<H",f.b,f.field(fl,3))[0] if f.field(fl,3) else 0
            fields.append(dict(name=fn,bt=BT[bt],el=BT[el],idx=idx,id=fid,off=off))
        is_struct=bool(f.u8(o,2))
        objs.append(dict(name=name,fields=fields,is_struct=is_struct))
    ri=f.field(r,4); root=None
    if ri:
        ro=f.indirect(ri); root=str_at(f,f.field(ro,0))
    return objs,root
