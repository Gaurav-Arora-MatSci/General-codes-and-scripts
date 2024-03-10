#!/usr/bin/env python
# coding: utf-8

# ## This script can be used to calculate SRO for a given cell with given cutoff radius (rc)

def calc_WC_parameter(filename, ele1, ele2, ele3, cutoff):

    import mdapy as mp
    import numpy as np
    mp.init()


    ## Reading the dump file and converting the atom types into array
    system = mp.System(filename)
    np.array(system.data['type'])

    ## Computing neighbors and calculating warren-cowley parameters
    neigh = mp.Neighbor(system.pos, system.box, rc= cutoff , boundary=[1,1,1])
    neigh.compute()
    wcp = mp.WarrenCowleyParameter(np.array(system.data["type"]), neigh.verlet_list, neigh.neighbor_number) # Initilize the WCP class.
    wcp.compute()
    wc_array = wcp.WCP

    ## Storing the array and printing if needed
    wc_11, wc_12, wc_13, wc_22, wc_23, wc_33 = wc_array[0][0], wc_array[0][1], wc_array[0][2], wc_array[1][1], wc_array[1][2], wc_array[2][2]


    ## Plotting WC parameters
    wcp.plot([str(ele1), str(ele2), str(ele3)])
    return()
   
calc_WC_parameter("mdmc-5000000.dump", "Cr", "Mn", "V", 2.8)