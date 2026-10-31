# Pokémon Legends: Z-A – Eden mods, cheats and notes

Small mods, a cheat and reverse-engineering notes for **Pokémon Legends: Z-A** (Title ID `0100F43008C44000`) on the **Eden** Switch emulator, game version **2.0.2** (update `v393216`, main build ID `B1F12FD919EAE86A…`).

Fan project, not affiliated with Nintendo, Game Freak or The Pokémon Company. **No game files, keys or extracted data are included** – you need your own legally obtained copy of the game.

## What is here

| Path | What it is | Status |
|---|---|---|
| `mods/Mega Energy R-Force v2.0.2` | Cheat: hold **R** to Mega Evolve without a full gauge, hold **D-Pad Up** to undo the Mega. The HUD keeps working. | Tested in-game |
| `mods/experimental/Shiny Rate 1-10 (Charm 1-5)` | Code patch (`.pchtxt`): wild shiny odds ~1/10 (~1/5 with Shiny Charm). | Experimental, one line untested |
| `mods/experimental/Shiny Locked NPC-Gift Pokemon` | Code patch: shiny-locked Pokémon from data rows (NPC trainers, gifts, starters) become shiny. | Experimental |
| `tools/` | Python tools to read the Trinity `data.trpfs/trpfd` archives, patch spawner/evolution tables and unpack the NSO. | Work in progress |
| `docs/NOTES.md` | How the patches were found, function/offset notes, data formats. | |

## Install (Eden)

Copy the folder inside `mods/` to `%APPDATA%\eden\load\0100F43008C44000\` (Eden → right-click the game → *Properties* → *Add-Ons*, then tick the mod). For cheats, **restart the game** after changing the file – Eden reads it at boot. Do not enable more than one Mega cheat at a time.

The patches are tied to this exact build (`@nsobid` / the cheat file name). They will not apply to other versions.

## Mega Energy R-Force – how it works

Hold **R** (the Mega button) and the game's "gauge is full?" check passes, so you can Mega Evolve whenever you want; the gauge is spent normally afterwards, which keeps the HUD consistent. Hold **D-Pad Up** to zero the gauge and end the Mega immediately. It may also affect an opponent's Mega. Details in `docs/NOTES.md`.

Demo video (90 s, 720p): [mega-energy-r-force-demo.mp4](https://github.com/Tavim01/legends-za-eden-mods/releases/download/v1.0/mega-energy-r-force-demo.mp4). Ready-to-use zip: [Releases](https://github.com/Tavim01/legends-za-eden-mods/releases/tag/v1.0).

Credit: the idea of forcing the gauge check comes from the Mega Energy cheats by **OblivionReign** and **LaMano** in the GBAtemp "Pokémon Legends Z-A Cheat Database" thread. The code locations were re-derived for 2.0.2 and the branch encodings recomputed here.

## Tools

Python 3.12 with `lz4 capstone xxhash mmh3 flatbuffers`. Some tools need the open-source [`ooz`](https://github.com/powzix/ooz) Kraken decompressor built as a DLL (`ZA_OOZ`), your own extracted `romfs/arc` (`ZA_ARC`) and an index built with `tools/build_index.py` (`ZA_INDEX`).

## License

MIT, see `LICENSE`. Cheat credits above.
