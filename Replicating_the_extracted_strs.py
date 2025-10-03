# replicate_with_pymatgen.py
# Replicate POSCAR-like files under BASE_IN into BASE_OUT using pymatgen,
# picking an n x n x n supercell to land near a target atom-count range.
# Writes clean VASP5 POSCARs with species line + integer counts (no per-atom spam).

import os
import shutil
from pathlib import Path

from pymatgen.core import Structure

BASE_IN = Path("out")            # input root: out/<category>/<structures or POSCARs>
BASE_OUT = Path("out_repeated")  # output root
POSCAR_NAME = "POSCAR"

RANGE_MIN, RANGE_MAX = 50, 150   # desired total-atom range after replication
N_MAX = 20                       # max supercell factor along each axis


def pick_cubic_n(n0, lo=RANGE_MIN, hi=RANGE_MAX, nmax=N_MAX):
    """Pick n (1..nmax) for n^3 * n0 close to mid of [lo,hi]; prefer inside range."""
    mid = (lo + hi) / 2
    best_in = None
    best_out = None
    for n in range(1, nmax + 1):
        total = (n ** 3) * n0
        score = abs(total - mid)
        if lo <= total <= hi:
            if best_in is None or score < best_in[0]:
                best_in = (score, n, total)
        else:
            if best_out is None or score < best_out[0]:
                best_out = (score, n, total)
    return (best_in or best_out)[1:]  # (n, total)


def ensure_subfolder_with_poscar(struct_file: Path) -> Path:
    """
    Make out/<cat>/<structure>/ and place struct_file inside as POSCAR.
    Handles the case where a FILE exists with the same name as the target folder.
    Returns the created/ensured structure directory path.
    """
    cat_dir = struct_file.parent
    struct_name = struct_file.name
    struct_dir = cat_dir / struct_name
    target_poscar = struct_dir / POSCAR_NAME

    # Directory already exists
    if struct_dir.exists() and struct_dir.is_dir():
        if not target_poscar.exists():
            shutil.move(str(struct_file), str(target_poscar))
        return struct_dir

    # FILE exists where the directory should be -> convert safely
    if struct_dir.exists() and struct_dir.is_file():
        tmp_dir = cat_dir / f"{struct_name}__tmpdir"
        i = 1
        while tmp_dir.exists():
            tmp_dir = cat_dir / f"{struct_name}__tmpdir_{i}"
            i += 1
        tmp_dir.mkdir(parents=True)
        shutil.move(str(struct_dir), str(tmp_dir / POSCAR_NAME))  # struct_dir is the FILE here
        tmp_dir.rename(struct_dir)
        return struct_dir

    # Path doesn't exist -> create directory and move file in
    struct_dir.mkdir(parents=True, exist_ok=True)
    shutil.move(str(struct_file), str(target_poscar))
    return struct_dir


def process_to_out_repeated(poscar_like_path: Path, out_dir: Path):
    """
    Read a POSCAR-like file with pymatgen, choose n, build n×n×n supercell,
    write POSCAR_{n}x{n}x{n} with a clean VASP5 header.
    """
    # Robust read: parse explicitly as POSCAR regardless of filename
    txt = Path(poscar_like_path).read_text()
    s = Structure.from_str(txt, fmt="poscar")

    n0 = len(s)
    n, total = pick_cubic_n(n0)

    # Build supercell (copy, then expand)
    s_big = s.copy()
    s_big.make_supercell([[n, 0, 0], [0, n, 0], [0, 0, n]])

    # Sort species alphabetically for a consistent header order
    s_big = s_big.get_sorted_structure()

    out_dir.mkdir(parents=True, exist_ok=True)
    outname = out_dir / f"POSCAR_{n}x{n}x{n}"
    s_big.to(filename=str(outname), fmt="poscar")

    # Progress + log
    species_line = " ".join([sp.symbol for sp in s_big.composition.elements])
    counts_line = " ".join(str(int(s_big.composition[sp])) for sp in s_big.composition.elements)

    print(f"[OK] {poscar_like_path} | n0={n0} -> {n}x{n}x{n} ({total}) -> {outname}")
    print(f"     species: {species_line}")
    print(f"     counts : {counts_line}")

    with open(out_dir / "repeat_info.txt", "a", encoding="utf-8") as f:
        f.write(f"{poscar_like_path} -> {outname.name} | n0={n0} n={n} total={total} | "
                f"species={species_line} counts={counts_line}\n")


def is_probable_structure_file(p: Path) -> bool:
    """Heuristic: treat files with no extension or VASP-ish names as POSCARs."""
    if not p.is_file():
        return False
    if p.name.startswith("."):
        return False
    return (p.suffix == "" or p.name.upper() in {"POSCAR", "CONTCAR"})


def main():
    if not BASE_IN.exists():
        raise FileNotFoundError(f"Input root '{BASE_IN}' not found.")

    BASE_OUT.mkdir(parents=True, exist_ok=True)

    for cat in sorted(BASE_IN.iterdir()):
        if not cat.is_dir():
            continue

        # 1) Move any bare POSCAR-like files into subfolders as out/<cat>/<name>/POSCAR
        struct_files = [p for p in cat.iterdir() if is_probable_structure_file(p)]
        struct_dirs = []
        for sf in struct_files:
            try:
                sd = ensure_subfolder_with_poscar(sf)
                struct_dirs.append(sd)
                print(f"[MOVE] {sf} -> {sd / POSCAR_NAME}")
            except Exception as e:
                print(f"[ERR-MOVE] {sf}: {e}")
                # Fallback: still process directly to an out_repeated mirror
                rel_cat = cat.relative_to(BASE_IN)
                out_dir = BASE_OUT / rel_cat / sf.name
                try:
                    process_to_out_repeated(sf, out_dir)
                except Exception as ee:
                    print(f"[ERR-PROC-FALLBACK] {sf}: {ee}")

        # 2) Include any subfolders that already contain a POSCAR
        for sub in cat.iterdir():
            if sub.is_dir() and (sub / POSCAR_NAME).exists():
                if sub not in struct_dirs:
                    struct_dirs.append(sub)

        # 3) Process every POSCAR found in subfolders to the mirrored out_repeated tree
        for sd in sorted(struct_dirs):
            rel = sd.relative_to(BASE_IN)      # e.g., 7-Cr-V/2-mp_XXXXX
            out_dir = BASE_OUT / rel
            poscar_in = sd / POSCAR_NAME
            try:
                process_to_out_repeated(poscar_in, out_dir)
            except Exception as e:
                print(f"[ERR-PROC] {poscar_in}: {e}")


if __name__ == "__main__":
    main()
