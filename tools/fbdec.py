import struct,sys
sys.path.insert(0, __import__("os").path.dirname(__import__("os").path.abspath(__file__)))
import trinity as t
FMT={"Bool":"<B","Byte":"<b","UByte":"<B","Short":"<h","UShort":"<H","Int":"<i","UInt":"<I","Long":"<q","ULong":"<Q","Float":"<f","Double":"<d","UType":"<B"}
class Dec:
    def __init__(self,buf,objs,root_name):
        self.b=buf; self.objs=objs; self.byname={o["name"]:i for i,o in enumerate(objs)}; self.root=self.byname[root_name]
    def decode(self):
        pos=struct.unpack_from("<I",self.b,0)[0]; return self.table(pos,self.objs[self.root])
    def table(self,pos,obj):
        b=self.b; vt=pos-struct.unpack_from("<i",b,pos)[0]; vsz=struct.unpack_from("<H",b,vt)[0]
        out={}
        for f in obj["fields"]:
            o=4+2*f["id"]
            if o>=vsz: continue
            off=struct.unpack_from("<H",b,vt+o)[0]
            if not off: continue
            out[f["name"]]=self.value(pos+off,f["bt"],f["el"],f["idx"],f)
        return out
    def value(self,p,bt,el,idx,f=None):
        b=self.b
        if bt in FMT: return struct.unpack_from(FMT[bt],b,p)[0]
        if bt=="String":
            sp=p+struct.unpack_from("<I",b,p)[0]; l=struct.unpack_from("<I",b,sp)[0]; return b[sp+4:sp+4+l].decode("utf-8","replace")
        if bt=="Obj":
            o=self.objs[idx]
            if o["is_struct"]: return self.struct(p,o)
            return self.table(p+struct.unpack_from("<I",b,p)[0],o)
        if bt=="Vector":
            v=p+struct.unpack_from("<I",b,p)[0]; n=struct.unpack_from("<I",b,v)[0]; st=v+4; out=[]
            if el in FMT:
                sz=struct.calcsize(FMT[el]); return list(struct.unpack_from("<%d%s"%(n,FMT[el][1]),b,st))
            for i in range(n): out.append(self.value(st+4*i,el,"None",idx) if el in ("String",) else self.vecobj(st,i,el,idx))
            return out
        raise NotImplementedError(bt)
    def vecobj(self,st,i,el,idx):
        o=self.objs[idx]
        if o["is_struct"]:
            return self.struct(st+i*o.get("bytesize",0),o)
        return self.table(st+4*i+struct.unpack_from("<I",self.b,st+4*i)[0],o)
    def struct(self,p,o):
        out={}
        for f in o["fields"]:
            out[f["name"]]=self.value(p+f["off"],f["bt"],f["el"],f["idx"])
        return out
