#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Dec  2 11:02:27 2022

@author: Gaurav Arora, Ph.D Email:gauravarora.1100@gmail.com
"""

"""
This code takes any POSCAR and randomize it based on the user input (filename and number_of_elements). User has to input exact number of atoms
of different types as an input. 
"""
def randomizing_POSCAR(filename, number_of_elements):
    import numpy as np
    import random
    import os
    #Reading POSCAR file
    file = open(str(filename), 'r')
    
    #readin each line of the POSCAR file
    system_info = file.readline()
    _ = file.readline()
    #reading and storing box dimensions
    x_dims = file.readline().strip().split()
    y_dims = file.readline().strip().split()
    z_dims = file.readline().strip().split()
    types = file.readline().strip().split()
    types_of_atoms = len(types)
    num_of_atoms = file.readline().strip().split()
    
    #Extracting number of atoms of each type and also the total number of atoms
    num_of_atoms_for_each_element = []
    for i in range (0,len(num_of_atoms)):
        _ = int(num_of_atoms[i])
        num_of_atoms_for_each_element.append(_)
    total_num_of_atoms = sum(num_of_atoms_for_each_element)
    
    coordinates_type = file.readline()
    
    #reading and storing coordinates of the atoms
    x_coordinates, y_coordinates, z_coordinates = [], [], []
    for i in range (0,total_num_of_atoms):
        _ = file.readline().strip().split()
        x_coordinates.append(float(_[0]))
        y_coordinates.append(float(_[1]))
        z_coordinates.append(float(_[2]))
        
    file.close()
    
    #Make a list of random numbers based on the composition
    if number_of_elements == 2:
        comp1 = int(input('Enter the number of atoms of type 1: '))
        comp2 = int(input('Enter the number of atoms of type 2: '))
        total_atoms = comp1 + comp2
        atom_type = str(comp1) + ' ' + str(comp2)
        if total_atoms == total_num_of_atoms:
            array = [1] * comp1 + [2] * comp2
            random.shuffle(array)
        else:
            print('Total number of atoms do not match with the number of atoms in the POSCAR')
    
    if number_of_elements == 3:
        comp1 = 18
        comp2 = 9
        comp3 = 9
        #comp1 = int(input('Enter the number of atoms of type 1: '))
        #comp2 = int(input('Enter the number of atoms of type 2: '))
        #comp3 = int(input('Enter the number of atoms of type 3: '))
        total_atoms = comp1 + comp2 + comp3
        atom_type = str(comp1) + ' ' + str(comp2) + ' ' + str(comp3)
        if total_atoms == total_num_of_atoms:
            array = [1] * comp1 + [2] * comp2 + [3] * comp3
            random.shuffle(array)
        else:
            print('Total number of atoms do not match with the number of atoms in the POSCAR')
    
    if number_of_elements == 4:
        comp1 = int(input('Enter the number of atoms of type 1: '))
        comp2 = int(input('Enter the number of atoms of type 2: '))
        comp3 = int(input('Enter the number of atoms of type 3: '))
        comp4 = int(input('Enter the number of atoms of type 4: '))
        total_atoms = comp1 + comp2 + comp3 + comp4
        atom_type = str(comp1) + ' ' + str(comp2) + ' ' + str(comp3) + ' ' + str(comp4)
        if total_atoms == total_num_of_atoms:
            array = [1] * comp1 + [2] * comp2 + [3] * comp3 + [4] * comp4
            random.shuffle(array)
        else:
            print('Total number of atoms do not match with the number of atoms in the POSCAR')
    
    if number_of_elements == 5:
        comp1 = int(input('Enter the number of atoms of type 1: '))
        comp2 = int(input('Enter the number of atoms of type 2: '))
        comp3 = int(input('Enter the number of atoms of type 3: '))
        comp4 = int(input('Enter the number of atoms of type 4: '))
        comp5 = int(input('Enter the number of atoms of type 5: '))
        total_atoms = comp1 + comp2 + comp3 + comp4 + comp5
        atom_type = str(comp1) + ' ' + str(comp2) + ' ' + str(comp3) + ' ' + str(comp4) + ' ' + str(comp5)
        if total_atoms == total_num_of_atoms:
            array = [1] * comp1 + [2] * comp2 + [3] * comp3 + [4] * comp4 + [5] * comp5
            random.shuffle(array)
        else:
            print('Total number of atoms do not match with the number of atoms in the POSCAR')
            
    if number_of_elements == 6:
        comp1 = int(input('Enter the number of atoms of type 1: '))
        comp2 = int(input('Enter the number of atoms of type 2: '))
        comp3 = int(input('Enter the number of atoms of type 3: '))
        comp4 = int(input('Enter the number of atoms of type 4: '))
        comp5 = int(input('Enter the number of atoms of type 5: '))
        comp6 = int(input('Enter the number of atoms of type 6: '))
        total_atoms = comp1 + comp2 + comp3 + comp4 + comp5 + comp6
        atom_type = str(comp1) + ' ' + str(comp2) + ' ' + str(comp3) + ' ' + str(comp4) + ' ' + str(comp5) + ' ' + str(comp6)
        if total_atoms == total_num_of_atoms:
            array = [1] * comp1 + [2] * comp2 + [3] * comp3 + [4] * comp4 + [5] * comp5 + [6] * comp6
            random.shuffle(array)
        else:
            print('Total number of atoms do not match with the number of atoms in the POSCAR')
    
    #Randomzing the coordinates
    coordinates_with_randomized_atom_type = (np.vstack((array, x_coordinates, y_coordinates, z_coordinates))).transpose()
    _ = coordinates_with_randomized_atom_type
    sorted_atoms = _[_[:, 0].argsort(kind='mergesort')] #Sorting based on first column
    
    
    #writing the randomized POSCAR
    file = open('randomized-' + str(filename), 'w')
    file.writelines('Randomized POSCAR \n')
    file.writelines('1 \n')
    #Writing box dimensions read earlier
    file.writelines(str(float(x_dims[0])) + ' ' + str(float(x_dims[1])) 
                 + ' ' + str(float(x_dims[2])) + '\n')
    file.writelines(str(float(y_dims[0])) + ' ' + str(float(y_dims[1])) 
                 + ' ' + str(float(y_dims[2])) + '\n')
    file.writelines(str(float(z_dims[0])) + ' ' + str(float(z_dims[1])) 
                 + ' ' + str(float(z_dims[2])) + '\n')
    
    #writing the types of atoms with spaces
    for i in range (0,number_of_elements):
        file.writelines('type' + str(i+1) + ' ')

    #writing the exact number of elements
    file.writelines('\n' + atom_type)
        
    file.writelines('\n' + str(coordinates_type))
    
    #writing the sorted coordinates
    for i in range (0,total_num_of_atoms):
        file.writelines(str(sorted_atoms[i,1]) + ' ' + str(sorted_atoms[i,2]) + ' ' + str(sorted_atoms[i,3]) + '\n')
    
    return(types)
import os
for i in range (0,250):
	randomizing_POSCAR('POSCAR',3 )
	os.rename('randomized-POSCAR', 'POSCAR-' + str(i))
    
