#from operator import index
import gurobipy as gb
#import pandas as pd
#import numpy as np
#import copy as cp

# Indexes 
MAINDATA = 0
NUMBER_OF_PICK_ORDERS_FOR_TRUCK = 1
PICK_ORDERS_FOR_TRUCK = range(2,32,1)
PICK_TIME = 32
AVAILABLE_PICKERS = 33
files = range(1,2,1)
a_ls = []
#https://stackoverflow.com/questions/21285684/how-to-read-numbers-in-text-file-using-python
for c in files:
    a_mainData = []
    a_numberOfPickOrdersForTruck = []
    a_pickOrdersForTruck = []
    a_pickTime = []
    a_availablePickers = []
    data = []
    with open('Instances/BaseCase/Input/Data' + str(c) + '.txt') as f:
        for line in f:
            if line != '\n':
                data.append([int(v) for v in line.split()])	

    a_mainData = data[MAINDATA]
    TOTAL_NUMBER_OF_PICK_ORDERS = a_mainData[0]
    TOTAL_NUMBER_OF_TRUCKS = a_mainData[1]
    TOTAL_NUMBER_OF_DOCKS = a_mainData[2]
    NUMBER_OF_TIME_SLOT = a_mainData[3]
    M = NUMBER_OF_TIME_SLOT
        
    # create array of NUMBER_OF_PICK_ORDERS_FOR_TRUCK + 1 zeros
    a_numberOfPickOrdersForTruck = [0] * (TOTAL_NUMBER_OF_TRUCKS)
    # copy dataset array shifted by 1
    ind = 0
    for e in data[NUMBER_OF_PICK_ORDERS_FOR_TRUCK]:
        a_numberOfPickOrdersForTruck[ind] = e
        ind = ind + 1
        
    # create base for multi array
    a_pickOrdersForTruck = []
    for po in PICK_ORDERS_FOR_TRUCK:
        # create array of zeros of number pick orders number for single truck
        a_pickOrdersForTruck_single = [0] * (len(data[po]))
        # copy dataset of number pick orders number for single truck shifted by 1
        ind = 0
        for e in data[po]:
            a_pickOrdersForTruck_single[ind] = e
            ind = ind + 1
        a_pickOrdersForTruck.append(a_pickOrdersForTruck_single)    
            #a_pickOrdersForTruck.append(data[i])
        
    # create array of PICK_TIME + 1 zeros
    a_pickTime = [0] * (TOTAL_NUMBER_OF_TRUCKS)
    # copy dataset array shifted by 1
    ind = 0
    for e in data[PICK_TIME]:
        a_pickTime[ind] = e
        ind = ind + 1
    #a_pickTime = data[PICK_TIME]
        
    a_availablePickers = [0] * (NUMBER_OF_TIME_SLOT)
    # copy dataset array shifted by 1
    ind = 0
    for e in data[AVAILABLE_PICKERS]:
        a_availablePickers[ind] = e
        ind = ind + 1
    #a_availablePickers = data[AVAILABLE_PICKERS]
        
    #a_timeSlot = [1] * NUMBER_OF_TIME_SLOT
    a_timeSlot = range(1,NUMBER_OF_TIME_SLOT + 1,1)
        
    #problem assignment
       
    p = gb.Model()
    p.ModelSense = gb.GRB.MINIMIZE 
        
    ls = p.addVars([i for i in range(1,TOTAL_NUMBER_OF_TRUCKS + 1, 1)],vtype=gb.GRB.INTEGER, name="ls")
    xot = p.addVars([(i,j) for i in range(1,TOTAL_NUMBER_OF_PICK_ORDERS + 1, 1) for j in range(1,NUMBER_OF_TIME_SLOT + 1, 1)],vtype=gb.GRB.BINARY, name="xot")
    #xot = p.addMVar((TOTAL_NUMBER_OF_PICK_ORDERS, NUMBER_OF_TIME_SLOT),vtype=gb.GRB.BINARY, name="xot")
    ys1 = p.addVars([i for i in range(1,TOTAL_NUMBER_OF_TRUCKS + 1, 1)],vtype=gb.GRB.INTEGER, name="ys1")
    ys = p.addVars([i for i in range(1,TOTAL_NUMBER_OF_TRUCKS + 1, 1)],vtype=gb.GRB.INTEGER, name="ys")
    qss1 = p.addVars([(i,j) for i in range(0,TOTAL_NUMBER_OF_TRUCKS + 2, 1) for j in range(0,TOTAL_NUMBER_OF_TRUCKS + 2, 1)],vtype=gb.GRB.BINARY, name="qss1")
    q0s = p.addVars([i for i in range(1,TOTAL_NUMBER_OF_TRUCKS + 1, 1)],vtype=gb.GRB.BINARY, name="q0s")
    qLasts = p.addVars([i for i in range(1,TOTAL_NUMBER_OF_TRUCKS + 1, 1)],vtype=gb.GRB.BINARY, name="qLasts")
        
    p.setObjective(gb.quicksum(ls[i] for i in range(1,TOTAL_NUMBER_OF_TRUCKS + 1, 1)))
        
    for t in range(1,NUMBER_OF_TIME_SLOT + 1, 1):
        p.addConstr(gb.quicksum(xot[o,t] for o in range(1, TOTAL_NUMBER_OF_PICK_ORDERS + 1, 1)) <= a_availablePickers[t-1])
      
    for s in range(1,TOTAL_NUMBER_OF_TRUCKS + 1, 1):
        p.addConstr(ls[s] >= (ys[s] - a_pickTime[s-1]))
    
    for s in range(1,TOTAL_NUMBER_OF_TRUCKS + 1, 1):
        for o_ind in a_pickOrdersForTruck:
            for o in o_ind:
                p.addConstr(gb.quicksum(t*xot[o,t] for t in a_timeSlot) <= ys1[s]) 

    for s1 in range(1,TOTAL_NUMBER_OF_TRUCKS + 1, 1):
        for s in range(1,TOTAL_NUMBER_OF_TRUCKS + 1, 1):
            p.addConstr((ys[s] - M*(1-qss1[s,s1]) + 1) <= ys1[s1])        
        
    for s in range(1,TOTAL_NUMBER_OF_TRUCKS + 1, 1):
        p.addConstr(ys[s] >= a_pickTime[s-1])
        
    for s in range(1,TOTAL_NUMBER_OF_TRUCKS + 1, 1):
        for o_ind in a_pickOrdersForTruck:
            for o in o_ind:
                p.addConstr(gb.quicksum(t*xot[o,t] for t in a_timeSlot) <= ys[s])

    for o in range(1, TOTAL_NUMBER_OF_PICK_ORDERS + 1, 1):
        p.addConstr(gb.quicksum(xot[o,t] for t in range(1, NUMBER_OF_TIME_SLOT + 1, 1))==1)

#    p.addConstr(gb.quicksum(q0s[s] for s in range(1,TOTAL_NUMBER_OF_TRUCKS + 1, 1)) <= TOTAL_NUMBER_OF_DOCKS)       
#    p.addConstr(gb.quicksum(qLasts[s] for s in range(1,TOTAL_NUMBER_OF_TRUCKS + 1, 1)) <= TOTAL_NUMBER_OF_DOCKS)       
    p.addConstr(gb.quicksum(qss1[0,s] for s in range(1,TOTAL_NUMBER_OF_TRUCKS + 1, 1)) <= TOTAL_NUMBER_OF_DOCKS)
    p.addConstr(gb.quicksum(qss1[s, TOTAL_NUMBER_OF_TRUCKS + 1] for s in range(1,TOTAL_NUMBER_OF_TRUCKS + 1, 1)) <= TOTAL_NUMBER_OF_DOCKS)

#    for d in range(1,TOTAL_NUMBER_OF_DOCKS + 1,1):    
#        for s in range(1,TOTAL_NUMBER_OF_TRUCKS + 1,1):
#            p.addConstr(gb.quicksum(qss1[s1 - 1,s] for s1 in range(1,TOTAL_NUMBER_OF_TRUCKS + 1,1) if s1 != s) == 1)

    #for d in range(1,TOTAL_NUMBER_OF_DOCKS + 1,1):    
    #for s in range(1,TOTAL_NUMBER_OF_TRUCKS + 1,1):
    #    p.addConstr(qss1[s - 1,s] == 1)

    #for d in range(1,TOTAL_NUMBER_OF_DOCKS + 1,1):    
    #for s in range(1,TOTAL_NUMBER_OF_TRUCKS + 1,1):
    #    p.addConstr(qss1[s, s +1] == 1)

    for s in range(1,TOTAL_NUMBER_OF_TRUCKS + 1,1):
        p.addConstr(gb.quicksum(qss1[s1,s] for s1 in range(0,TOTAL_NUMBER_OF_TRUCKS + 1, 1) if s1 != s) == 1)
        
    for s in range(1,TOTAL_NUMBER_OF_TRUCKS + 1,1):
        p.addConstr(gb.quicksum(qss1[s,s1] for s1 in range(1,TOTAL_NUMBER_OF_TRUCKS + 2,1) if s1 != s) == 1)

    #for s in range(1,TOTAL_NUMBER_OF_TRUCKS + 1,1):
    #    p.addConstr(qLasts[s] +  gb.quicksum(qss1[s,s1] for s1 in range(1,TOTAL_NUMBER_OF_TRUCKS + 2,1) if s1 != s) == 1)

    p.optimize()

    # Display optimal values of decision variables
    print("Display optimal values of decision variables")
    for v in p.getVars():
        if (p.Status != 3):
            if v.x > 1e-6:
                print(v.varName, v.x)

    # Display optimal total matching score
    if (p.Status != 3):
        print('Total matching score: ', p.objVal)

    ls1 = []
    if (p.Status != 3):
        for z in ls:
            ls1.append(ls[z].X)
    else:
         ls1 = []                         
        
    a_ls.append(ls1)
print(a_ls.__len__())



