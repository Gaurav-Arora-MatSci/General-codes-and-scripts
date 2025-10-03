# pip install mp-api pymatgexn
# Get your API key at https://materialsproject.org -> My Account -> API Key

from mp_api.client import MPRester
from pymatgen.io.vasp import Poscar
from itertools import combinations
from pathlib import Path
import csv

API_KEY = "**"   # <-- your key
CHEMSYS = "Cr-Mn-V-Ti-Al-Co"        # works for 3, 4, or more elements
OUTDIR = Path("out")        # root folder to save everything
USE_PRIMITIVE = False       # True -> save primitive cells
SIZES = (1, 2, 3,4,5,6, "all")    # for 4 elems: add 3 for ternaries

def make_combos(chemsys_str, sizes=(1, 2, 3, "all")):
    elems = [e.strip() for e in chemsys_str.split("-") if e.strip()]
    n = len(elems)
    out = []
    for s in sizes:
        k = n if s == "all" else int(s)
        if 1 <= k <= n:
            from itertools import combinations
            for combo in combinations(sorted(elems), k):
                out.append("-".join(combo))
    seen, uniq = set(), []
    for tag in out:
        if tag not in seen:
            seen.add(tag)
            uniq.append(tag)
    return uniq

# Build all combinations to fetch
CHEMSYS_LIST = make_combos(CHEMSYS, sizes=SIZES)
OUTDIR.mkdir(parents=True, exist_ok=True)

# One consolidated CSV only
csv_path = OUTDIR / "energies_per_atom.csv"
write_header = not csv_path.exists()
with open(csv_path, "a", newline="", encoding="utf-8") as csvf:
    writer = csv.writer(csvf)
    if write_header:
        writer.writerow(["combo_tag", "combo_index", "material_id", "saved_filename", "energy_per_atom_eV"])

    with MPRester(API_KEY) as mpr:
        for combo_idx, tag in enumerate(CHEMSYS_LIST, start=1):
            combo_folder = OUTDIR / f"{combo_idx}-{tag}"   # e.g., "1-Co", "2-Co-Ti"
            combo_folder.mkdir(parents=True, exist_ok=True)
            print(f"\n=== Fetching {tag} → {combo_folder} ===")

            # Query structures + energy per atom for this combo
            docs = mpr.materials.summary.search(
                chemsys=[tag],
                fields=["material_id", "structure", "energy_per_atom"],
            )

            if not docs:
                print("  No results.")
                continue

            for mat_idx, d in enumerate(docs, start=1):
                struct = d.structure
                if USE_PRIMITIVE:
                    try:
                        struct = struct.get_primitive_structure()
                    except Exception:
                        pass

                # sanitize material_id for filesystem (mp-12345 -> mp_12345)
                mid = str(d.material_id).replace("-", "_")
                base = combo_folder / f"{mat_idx}-{mid}"   # e.g., "1-mp_12345"
                Poscar(struct).write_file(base)
                print("  Saved:", base)

                # Append only to the global CSV (no per-folder files)
                epa = getattr(d, "energy_per_atom", None)
                writer.writerow([tag, combo_idx, d.material_id, base.name, "" if epa is None else epa])

print("\nDone!")
