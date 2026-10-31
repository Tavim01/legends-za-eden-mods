import sys,os; sys.path.insert(0,sys.argv[1]); sys.path.insert(0,sys.argv[1]+r"\tools\pylib")
import trpfdlib as L
src=sys.argv[2]; out=sys.argv[3]
SP="world/ik_data/field/pokemon_spawner/pokemon_spawner_data/pokemon_spawner_data_array.bin"
h=L.zh(SP); P=L.load_parts(src)
assert h in P["hashes"], "spawner hash not present (already removed?)"
keep=[i for i,x in enumerate(P["hashes"]) if x!=h]
print("removing",len(P["hashes"])-len(keep),"entry")
data=L.build([P["hashes"][i] for i in keep],P["paths"],[P["subinfos"][i] for i in keep],P["fileinfos"])
open(out,"wb").write(data)
Q=L.load_parts(out)
assert Q["hashes"]==[P["hashes"][i] for i in keep] and Q["subinfos"]==[P["subinfos"][i] for i in keep] and Q["paths"]==P["paths"] and Q["fileinfos"]==P["fileinfos"]
print("verified",len(data),"bytes; hashes",len(Q["hashes"]))
