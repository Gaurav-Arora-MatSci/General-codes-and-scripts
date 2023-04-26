#!/usr/bin/env python
# coding: utf-8

# ## This code reads the E-V data from EV_data.txt file and fits it to Birch-Murnaghan EOS and outputs bulk modulus and approximated C11 and C44 using 

# In[ ]:


from pymatgen.analysis.eos import Birch
from pymatgen.analysis.eos import EOS
import numpy as np

# Load data from file
data = np.loadtxt('EV_data.txt', usecols=(0, 1))

# Extract the two columns as separate arrays
volumes = data[:, 0]
energies = data[:, 1]
eos = EOS(eos_name='birch_murnaghan')
eos_fit = eos.fit(volumes, energies)
eos_fit.plot()

K = round(eos_fit.b0_GPa,2)
print(f'Bulk modulus is {K} GPa')
dk_by_dp = eos_fit.b1

C11 = round((K + (4/3)*(dk_by_dp)),3)
C44 = round((K - (4/3)*(dk_by_dp)),3)
print(f'~C11: {C11} GPa ~C44: {C44} GPa:')

