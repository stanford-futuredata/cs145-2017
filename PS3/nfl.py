# Utilities
import csv
import numpy as np
from collections import namedtuple
from collections import defaultdict
from collections import Counter

def loadData():
    PlayerTeam = namedtuple('PlayerTeam','teamname playername')
    PlayerCollege = namedtuple('PlayerCollege', 'playername collegename')
        
    teams = []
    for line in csv.reader(open("playerteam.csv", "rb"), delimiter='\t'):
        p = PlayerTeam._make(line)
        teams.append(p)

    colleges = []
    for line in csv.reader(open("playercollege.csv", "rb"), delimiter='\t'):
        p = PlayerCollege._make(line)
        colleges.append(p)
 
    return teams, colleges

def partitionTable(table, hashfunction,buckets):
    hRes = defaultdict(list)
    for b in range(buckets):
	hRes[b] = []
    attribute = 'playername'
    for s in table:
        hRes[hashfunction(getattr(s, attribute),buckets)].append(s)
    return hRes
