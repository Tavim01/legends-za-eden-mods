# Notes (v2.0.2, main `B1F12FD919EAE86A…`)

Offsets below are in the `text` segment (no 0x100 header). The `.pchtxt` files use `@flag offset_shift 0x100`.

## Mega gauge (cheat)

* `0x200454` – `SetGauge(float value)`: clamps `value` to `[0, max]` and stores it in `[x19+0x1A8]` (`max` is `[x19+0x1AC]`). The store is at `0x200484` (`str s1,[x19,#0x1A8]`). The game calls it while a Mega is active; when the gauge reaches 0 the Mega ends.
  * Replacing the store with `str wzr,[x19,#0x1A8]` (`B901AA7F`) zeroes the gauge and ends the Mega at once → used for **D-Pad Up**.
  * Replacing it so the gauge is always refilled ("infinite energy") makes the Mega never end, but the HUD (attack/switch menus) breaks on the 2nd+ Mega, because the gauge is never spent.
* `0x181558` – `ldr s0,[x19,#0x1A8]` followed by `ldr s1,[x19,#0x1AC]; fcmp s0,s1; b.mi …`: the "gauge full?" check when a Mega is requested. A code cave at `0x3163F80` (`ldr s0,[x19,#0x1AC]; str s0,[x19,#0x1A8]; b 0x18155C`) makes it read/store the maximum. It is only branched to while **R** (key mask `0x80`) is held.
* The caves live in the padding after the end of `text` (`0x3163F70`–`0x3163FFF`).
* Cheat VM: `040A0000 <addr> <word>` writes a word at main+addr; `80000080 … 20000000` is a key-press conditional (R = `0x80`, D-Pad Up = `0x2000`). `B` branch encodings: `0x14000000 | ((target-pc)/4 & 0x3FFFFFF)`.

## Shiny patches (experimental)

* Data-row Pokémon creator (NPC trainers, gifts, starters): the "locked" mode constant `0x1ffffffff` is made to force shiny (`00656150 E98340B2`, `00656154 1F0109EB`, `00656160 2801889A`). An earlier version edited the shared routine at `0x6570CC`, but the Pokédex UI uses the same routine with the locked flag and started showing shiny icons.
* Wild shiny odds: rerolls = 320 + 128·r, r = the game's roll count (1 base, 4 with the Shiny Charm). Estimated ~1/9.7 base and ~1/5.4 with the Charm.
* Wild generator mode lives in `[x19+0x20]`: `0x1ffffffff` never shiny, `0xFFFF0002FFFFFFFF` always shiny, `0x3ffffffff` lottery with `[x19+0x28]` rolls.

## Data (romfs)

* `romfs/arc/data.trpfs` is a Trinity-engine package of FlatBuffers compressed with Kraken/Oodle; `data.trpfd` is the index (path hashes, sub-info with offset/size/compression).
* Path hash: FNV-1a 64-bit, offset basis `0xcbf29ce484222645`, over the exact path with extension (`tools/trpfdlib.py: zh`).
* A loose file under `romfs/<path>` only takes effect if its hash is removed from `data.trpfd` (`tools/rm_trpfd_hashes.py`). Two mods that replace `data.trpfd` cannot coexist as separate folders.
* Wild spawner respawn time: `world/ik_data/field/pokemon_spawner/pokemon_spawner_data/pokemon_spawner_data_array.bin`, field `coolTimeInfo.time` (`tools/mk_spawn.py`, `tools/mk_spawn_abs.py`).
* `avalon/data/personal_array.bin`: slot 21 of each Personal entry is a vector of 16-byte evolution structs `[u16 level][u16 method][u16 arg]…[u16 species @12]`. Methods: 1/2/3 friendship (any/day/night), 4 level, 5 trade, 6 trade+item, 7 trade for a partner, 8 use item, 29 friendship+Fairy move, 32/33 level (day/night). `tools/mk_no_friendship.py` turns friendship evolutions into level evolutions.

## Getting the executable

Extract `main` from the update NCA with `nstool` (needs your own keys), decompress the NSO (`tools/nso.py`, LZ4) and disassemble `text` with Capstone.
