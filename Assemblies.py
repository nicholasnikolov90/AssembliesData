import pandas as pd
import numpy as np
import re

#Author: Nick Nikolov

#INSTRUCTIONS
#1. Copy entire Code stress results grid into a .csv file
#2. Create a .csv file for all tee node numbers / any nodes you need results at.
#3. Results will be saved in the same folder in a .xlsx format.

#NOTES
#Only make modifications to this first code block. 

#*INPUTS* 
#Legend of variables
#code_stresses = code stress results grid, saved as a csv
#nodes = node numbers of elbows or tee connections. Input into the first column A. Start at Node A01. A00 should be "nodes"

#reads all the data from csv files
code_stresses = pd.read_csv('100Acs.csv', usecols = ['Point', 'Seg', 'Category', 'Stress', 'Allowable'], low_memory=False).tail(-1)
elbow_nodes = pd.read_csv("elbowNodes.csv")
header_nodes = pd.read_csv("teeNodes.csv", usecols = ['Nodes', 'Header'])
branch_nodes = pd.read_csv("teeNodes.csv", usecols = ['Nodes', 'Branch'])
print(header_nodes)
print(branch_nodes)

#Data clean up
#Removes all duplicates based on soil points and bend midpoints
code_stresses['Point'] = code_stresses['Point'].str.split('[ NFM]').str[0]

#Manually calculate 'ratio' column of the code stresses to get more significant digits than the code stress tab gives
code_stresses['Ratio'] = ((code_stresses['Stress'].astype(float) / code_stresses['Allowable'].astype(float))*100).round(2)
code_stresses = code_stresses.set_index(['Point', 'Category', 'Seg'])
code_stresses = code_stresses.groupby(level=['Point', 'Category', 'Seg']).max().sort_index()

header_results = code_stresses.loc[header_nodes['Nodes']].reset_index()

header_results = header_results.merge(header_nodes, left_on=['Point', 'Seg'], right_on=['Nodes', 'Header'], how='left')
header_results['Header/Branch'] = header_results.apply(lambda row: 'Header' if pd.notna(row['Nodes']) else 'Branch', axis=1)
header_results = header_results.drop(['Nodes', 'Header', 'Allowable', 'Seg', 'Stress'], axis = 1)

print(header_results)
header_results = header_results.pivot_table(index=['Point', 'Header/Branch'], columns='Category')

print(header_results)

#header_results = header_results.pivot_table(index=['Seg', 'Point'], columns='Category').drop(['Stress', 'Allowable'], axis = 1).sort_values(by='Point')
#header_results.to_excel("test.xlsx")  

#extract material allowables at each node (only for use in general stress array)
allowables = code_stresses.reset_index()
allowables = allowables.set_index(['Point', 'Category', 'Seg', 'Allowable'])
allowables = allowables.groupby(level=['Point', 'Allowable']).max().reset_index().drop(['Stress', 'Ratio'], axis = 1).set_index(['Point']).groupby(level='Point').max().sort_index()

#turn general stress and code stre  sses into pivot tables
code_stresses = pd.pivot_table(code_stresses, values = 'Ratio', index = ['Point'], columns = 'Category')

#Merge all results into one sheet
overall_results = code_stresses

#RESULTS. 
#Prints only the results for the nodes needed
elbow_results = overall_results.loc[elbow_nodes['Nodes']]

#OUTPUT RESULTS TO EXCEL
elbow_results.to_excel("output.xlsx")  