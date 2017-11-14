# copy and paste your answers into each of the below variables 
# NOTE: do NOT rename variables
# Modify the return statements to return the relevant values
# Include 1-2 sentences (as a python comment) above each answer explaining your reasoning.

import math

#Q1ai 
io_split_sort = 

#Q1aii
merge_arity =

#Q1aiii 
merge_passes = 

#Q1aiv 
merge_pass_1 = 

#Q1av
total_io =

#Q1bi 
def cost_initial_runs(B, N, P):
    # BEGIN YOUR CODE 
    return 0
    # END YOUR CODE 

#Q1bii 
def cost_per_pass(B, N, P):
    # BEGIN YOUR CODE 
    return 0
    #END YOUR CODE

#Q1biii
def num_passes(B, N, P):
    # BEGIN YOUR CODE 
    return 0
    # END YOUR CODE

#Q1c 
# Save the optimal value here
P =

# Save a list of tuples of (P, io_cost) here, for all feasible P's
points = 

#Q2a 
IO_Cost_HJ_1 =
IO_Cost_HJ_2 = 
IO_Cost_SMJ_1 = 
IO_Cost_SMJ_2 =
IO_Cost_BNLJ_1 = 
IO_Cost_BNLJ_2 = 

#Q2b 
P_R = 
P_S = 
P_T = 
P_RS = 
P_RST =
B =

HJ_IO_Cost_join1 = 
SMJ_IO_Cost_join2 =

SMJ_IO_Cost_join1 = 
HJ_IO_Cost_join2 =

#Q3ai
def lru_cost(N, M, B):
    # BEGIN YOUR CODE 
    return 0
    #END YOUR CODE

#Q3aii 
def mru_cost(N, M, B):
    #BEGIN YOUR CODE 
    return 0
    #END YOUR CODE

#Q3aiii
# Provide a list of tuple (m, difference between LRU and MRU in terms of IO cost) here:
p3_lru_points = 

#Q3bi 
def clock_cost(N, M, B):
    #BEGIN YOUR CODE
    return 0
    #END YOUR CODE

#Q3bii 
# Provide a list of tuple (m vs the absolute value of the difference between LRU and CLOCK in terms of IO cost) here:
p3_clock_points = 

'''
Explanation here:
'''

#Q4ai
def hashJoin(table1, table2, hashfunction,buckets):
    # Parition phase 
    t1Partition = partitionTable(table1,hashfunction,buckets)
    t2Partition = partitionTable(table2,hashfunction,buckets)
    # Merge phase
    result = []
    
    # ANSWER GOES HERE
    
    # To populate your output you should use the following code(t1Entry and t2Entry are possible var names for tuples)
    # result.append((t1Entry.teamname, t1Entry.playername, t2Entry.collegename))
    return result

#Q4aii
'''
Explanation here:
'''

#Q4bi 
# partition- a table partition as returned by method partitionTable
# return value - a float representing the skew of hash function (i.e. stdev of chefs assigned to each restaurant)
def calculateSkew(partition):
    # ANSWER STARTS HERE
    skew = 
    # ANSWER ENDS HERE
    return skew

#Q4bii 
# Design a better hash function and print the skew difference for 
def hBetter(x,buckets):
    rawKey = #ANSWER GOES HERE
    return rawKey % buckets

#Q4biii 
res1 = # ENTER CODE HERE

#speedup here =

#Q4c
flocco_elite = 
