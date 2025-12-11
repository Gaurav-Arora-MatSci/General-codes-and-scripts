#!/usr/bin/env python3
"""
build_structure_from_bonds_complete.py

Usage: edit USER INPUTS below and run:
    python build_structure_from_bonds_complete.py

Requirements: ASE, numpy
"""

import math
import time
from collections import defaultdict, Counter
import numpy as np
from ase.io import read, write
from ase.neighborlist import neighbor_list

# ==========================
# USER INPUTS (edit these)
# ==========================
TEMPLATE_FILE = "template.lmp"       # input template (LAMMPS data, POSCAR, ...)
TEMPLATE_FORMAT = "lammps-data"      # change to "vasp" for POSCAR
CUTOFF = 2.8                         # neighbor cutoff (Å)
# target bond counts (unordered, pair keys as (min_type, max_type))
target_bonds = {
    (1, 1): 901,
    (1, 2): 413,
    (1, 3): 512,
    (2, 2): 60,
    (2,3):2190,
    (3,3):13
}
# composition: integer type -> number atoms
composition = {1: 341, 2: 341, 3: 341}         # sum must equal number of sites in template

# mapping integer type -> element symbol (must be valid element symbols)
type_to_symbol = {1: "Cr", 2: "Mn", 3: "V"}

# simulated annealing params (tune as needed)
SA_N_STEPS = 1000000     # try 200k; increase for better results
SA_T0 = 2.0
SA_T_FINAL = 0.01
SA_PRINT_EVERY = 20000

# greedy fixer params
GREEDY_MAX_NO_IMPROVE = 100000

# output
OUTPUT_FILE = "optimized_structure.lmp"
OUTPUT_FORMAT = "lammps-data"

# Optional: create a simple template automatically if TEMPLATE_FILE missing.
CREATE_TEMPLATE_IF_MISSING = True
SIMPLE_TEMPLATE_SYMBOL = "Cr"
SIMPLE_TEMPLATE_CELLS = (4, 4, 4)  # will produce roughly prod(cells) * basis atoms

# RNG seed for reproducibility (set to None for random)
RNG_SEED = None

# ==========================
# HELPERS
# ==========================

def create_simple_template(n_cells=(4,4,4), symbol="Cr", out="template.lmp"):
    """Create a simple BCC supercell and write as LAMMPS data using ASE."""
    from ase.build import bulk
    base = bulk(symbol, crystalstructure="bcc", a=3.0)
    atoms = base.repeat(n_cells)
    write(out, atoms, format="lammps-data")
    print(f"Created simple template '{out}' with {len(atoms)} atoms (symbol={symbol}).")
    return out

def build_neighbor_pairs(atoms, cutoff):
    """Return unique sorted array of neighbor pairs (i,j) with i<j."""
    i_list, j_list, d_list = neighbor_list("ijd", atoms, cutoff)
    pairs = []
    for i, j in zip(i_list, j_list):
        if i == j:
            continue
        if i < j:
            pairs.append((i, j))
        else:
            pairs.append((j, i))
    pairs = sorted(set(pairs))
    return np.array(pairs, dtype=int)

def build_adjacency_list(pairs, n_sites):
    """Return neighbors list per site for quick local updates."""
    neigh = [[] for _ in range(n_sites)]
    for a, b in pairs:
        neigh[a].append(b)
        neigh[b].append(a)
    return neigh

def random_types_from_composition(n_sites, composition, rng):
    """Return shuffled int array of types respecting composition."""
    assigned = []
    for t, n in composition.items():
        assigned += [int(t)] * int(n)
    assigned = np.array(assigned, dtype=int)
    assert len(assigned) == n_sites, "Composition does not match number of sites"
    rng.shuffle(assigned)
    return assigned

def init_counts_from_pairs(types, pairs):
    """Return dict counts of unordered pairs given types and pairs list."""
    counts = defaultdict(int)
    for a, b in pairs:
        t1, t2 = int(types[a]), int(types[b])
        key = (t1, t2) if t1 <= t2 else (t2, t1)
        counts[key] += 1
    return counts

def total_bonds_from_pairs(pairs):
    return len(pairs)

# ==========================
# SIMULATED ANNEALING (local updates)
# ==========================
def simulated_annealing_swaps(types, pairs, targ_counts, neigh,
                              n_steps=200000, T0=2.0, T_final=0.01,
                              print_every=20000, rng=None):
    """
    Simulated annealing swapping with local bond-count updates.
    Returns best_types, best_cost, stats, best_counts
    """
    if rng is None:
        rng = np.random.default_rng()

    n_sites = len(types)
    counts = init_counts_from_pairs(types, pairs)

    def cost_fn(cnts):
        c = 0.0
        for pair, targ in targ_counts.items():
            c += (cnts.get(pair, 0) - targ) ** 2
        return c

    current_cost = cost_fn(counts)
    best_cost = current_cost
    best_types = types.copy()
    best_counts = counts.copy()

    attempted = accepted = rejected = 0
    t0 = time.time()

    for step in range(1, n_steps + 1):
        frac = step / n_steps
        # exponential schedule
        T = T0 * (T_final / T0) ** frac

        # pick site i uniformly
        i = int(rng.integers(0, n_sites))
        ti = types[i]

        # attempt to find j with different type quickly
        found = False
        for _ in range(6):
            j = int(rng.integers(0, n_sites))
            if j != i and types[j] != ti:
                found = True
                break
        if not found:
            # fallback: sample subset
            sample = rng.choice(n_sites, size=min(50, n_sites), replace=False)
            for jj in sample:
                if jj != i and types[jj] != ti:
                    j = int(jj); found = True; break
        if not found:
            continue

        attempted += 1
        tj = types[j]

        # compute delta counts for neighbors of i and j (excluding cross pair handled implicitly)
        delta = Counter()
        # process neighbors excluding the other swapped site to avoid double count
        for s, t_old, t_new in ((i, ti, tj), (j, tj, ti)):
            for nb in neigh[s]:
                if nb == i or nb == j:
                    continue
                tnb = types[nb]
                key_before = (t_old, tnb) if t_old <= tnb else (tnb, t_old)
                key_after  = (t_new, tnb) if t_new <= tnb else (tnb, t_new)
                delta[key_before] -= 1
                delta[key_after]  += 1

        # note: i-j unordered pair doesn't change count when swapping different types (still one bond of that unordered pair),
        # so we don't need to modify delta for i-j.

        # compute new cost using only affected keys (sparse update)
        affected = set(delta.keys()) | set(targ_counts.keys())
        new_cost = current_cost
        for key in affected:
            old = counts.get(key, 0)
            new = old + delta.get(key, 0)
            old_term = (old - targ_counts.get(key, 0)) ** 2
            new_term = (new - targ_counts.get(key, 0)) ** 2
            new_cost += (new_term - old_term)

        delta_cost = new_cost - current_cost

        # metropolis acceptance
        if delta_cost <= 0 or rng.random() < math.exp(-delta_cost / max(T, 1e-12)):
            # accept
            types[i], types[j] = types[j], types[i]
            # apply delta
            for k, v in delta.items():
                counts[k] = counts.get(k, 0) + v
            current_cost = new_cost
            accepted += 1
            if current_cost < best_cost:
                best_cost = current_cost
                best_types = types.copy()
                best_counts = counts.copy()
        else:
            rejected += 1

        if step % print_every == 0 or step == 1:
            elapsed = time.time() - t0
            acc_rate = accepted / attempted if attempted else 0.0
            print(f"SA step {step}/{n_steps}, T={T:.4f}, cost={current_cost:.1f}, best={best_cost:.1f}, "
                  f"attempted={attempted}, accepted={accepted}, acc_rate={acc_rate:.3f}, time={elapsed:.1f}s")

    stats = {"attempted": attempted, "accepted": accepted, "rejected": rejected}
    return best_types, best_cost, stats, best_counts

# ==========================
# GREEDY LOCAL SEARCH (reduces L1 residual)
# ==========================
def total_l1_residual(counts, targ_counts):
    s = 0
    for pair, targ in targ_counts.items():
        s += abs(counts.get(pair, 0) - targ)
    return s

def greedy_random_local_search(types, pairs, neigh, targ_counts, counts,
                               max_no_improve_iters=100000, rng=None):
    """Randomized greedy local search: accept only strict L1 improvements."""
    if rng is None:
        rng = np.random.default_rng()
    n = len(types)
    cur_counts = counts.copy()
    cur_score = total_l1_residual(cur_counts, targ_counts)
    best_score = cur_score
    best_types = types.copy()
    no_improve = 0
    iters = 0

    while no_improve < max_no_improve_iters:
        iters += 1
        # pick i and j of different types
        i = int(rng.integers(0, n))
        ti = types[i]
        found = False
        for _ in range(8):
            j = int(rng.integers(0, n))
            if j != i and types[j] != ti:
                found = True
                break
        if not found:
            for jj in rng.choice(n, size=min(50, n), replace=False):
                if jj != i and types[jj] != ti:
                    j = int(jj); found = True; break
        if not found:
            break

        tj = types[j]
        delta = Counter()
        for s, t_old, t_new in ((i, ti, tj), (j, tj, ti)):
            for nb in neigh[s]:
                if nb == i or nb == j:
                    continue
                tnb = types[nb]
                kb = (t_old, tnb) if t_old <= tnb else (tnb, t_old)
                ka = (t_new, tnb) if t_new <= tnb else (tnb, t_new)
                delta[kb] -= 1
                delta[ka] += 1

        affected = set(delta.keys()) | set(targ_counts.keys())
        new_score = cur_score
        for key in affected:
            old = cur_counts.get(key, 0)
            new = old + delta.get(key, 0)
            new_score += abs(new - targ_counts.get(key, 0)) - abs(old - targ_counts.get(key, 0))

        if new_score < cur_score:
            # accept
            types[i], types[j] = types[j], types[i]
            for k, v in delta.items():
                cur_counts[k] = cur_counts.get(k, 0) + v
            cur_score = new_score
            no_improve = 0
            if cur_score < best_score:
                best_score = cur_score
                best_types = types.copy()
        else:
            no_improve += 1

    print(f"Greedy finished after {iters} tries. best L1 residual = {best_score}")
    return best_types, cur_counts

# ==========================
# MAIN
# ==========================
def main():
    rng = np.random.default_rng(RNG_SEED)

    # 1) Ensure template exists or create one
    try:
        atoms = read(TEMPLATE_FILE, format=TEMPLATE_FORMAT)
    except Exception as e:
        if CREATE_TEMPLATE_IF_MISSING:
            print(f"Template '{TEMPLATE_FILE}' not found or failed to read. Creating a simple template.")
            create_simple_template(n_cells=SIMPLE_TEMPLATE_CELLS, symbol=SIMPLE_TEMPLATE_SYMBOL, out=TEMPLATE_FILE)
            atoms = read(TEMPLATE_FILE, format=TEMPLATE_FORMAT)
        else:
            raise

    n_sites = len(atoms)
    print(f"Read template with {n_sites} sites from '{TEMPLATE_FILE}'.")

    if sum(composition.values()) != n_sites:
        raise ValueError(f"Composition sum {sum(composition.values())} != number of sites {n_sites}")

    # 2) Build pairs & adjacency
    pairs = build_neighbor_pairs(atoms, CUTOFF)
    n_pairs = len(pairs)
    neigh = build_adjacency_list(pairs, n_sites)
    print(f"Found {n_pairs} neighbor pairs (bonds) with cutoff {CUTOFF} Å.")

    # Feasibility quick check: totals must match if exact matching is required
    sum_target = sum(target_bonds.values())
    print(f"Sum target bonds = {sum_target}, available unordered bonds = {n_pairs}")
    if sum_target != n_pairs:
        print("NOTE: sum(target_bonds) != total available bonds. Exact match impossible unless you change targets.")
        # continue anyway to attempt best approximation.

    # 3) Initialize random types
    types = random_types_from_composition(n_sites, composition, rng)
    unique_initial = np.unique(types)
    print("Initial unique types:", unique_initial.tolist())

    # 4) Simulated annealing
    print("\nStarting simulated annealing...")
    best_types_sa, best_cost_sa, sa_stats, best_counts_sa = simulated_annealing_swaps(
        types.copy(), pairs, target_bonds, neigh,
        n_steps=SA_N_STEPS, T0=SA_T0, T_final=SA_T_FINAL,
        print_every=SA_PRINT_EVERY, rng=rng
    )
    print("SA stats:", sa_stats)
    print("SA best cost:", best_cost_sa)

    # 5) Greedy local search
    print("\nStarting greedy local search to reduce L1 residual...")
    improved_types, improved_counts = greedy_random_local_search(
        best_types_sa.copy(), pairs, neigh, target_bonds, best_counts_sa,
        max_no_improve_iters=GREEDY_MAX_NO_IMPROVE, rng=rng
    )

    # 6) Write output with element symbols
    symbols_list = [type_to_symbol[int(t)] for t in improved_types]
    atoms_new = atoms.copy()
    atoms_new.set_chemical_symbols(symbols_list)
    write(OUTPUT_FILE, atoms_new, format=OUTPUT_FORMAT)
    print(f"\nWrote optimized structure to '{OUTPUT_FILE}' with symbols: {sorted(set(symbols_list))}")

    # 7) Print final verification
    actual_counts = improved_counts
    print("\nFinal bond counts and residuals (actual - target):")
    for pair, targ in sorted(target_bonds.items()):
        act = actual_counts.get(pair, 0)
        print(f"  {pair}: target={targ:6d}, actual={act:6d}, residual={act - targ:6d}")

    # summary stats
    print("\nSummary:")
    print("  Total available bonds:", n_pairs)
    print("  Sum target bonds:", sum_target)
    print("  Unique atom types in final:", sorted(set(symbols_list)))
    print("  L2 cost (sum squared errors):", sum((actual_counts.get(p,0)-t)**2 for p,t in target_bonds.items()))
    print("  L1 residual:", total_l1_residual(actual_counts, target_bonds))

if __name__ == "__main__":
    main()
