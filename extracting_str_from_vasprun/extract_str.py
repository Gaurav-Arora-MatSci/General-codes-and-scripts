import os, sys
from pymatgen.core import Structure
from pymatgen.io.vasp.outputs import Vasprun
from monty.serialization import loadfn, dumpfn

vrun = Vasprun('vasprun.xml')
structures = vrun.structures
print(len(structures))
dumpfn(structures, 'structure.json')

strs = loadfn('structure.json')
str_ = strs[3]
str_.to('POSCAR', fmt = 'poscar')
