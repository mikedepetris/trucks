# import random
import numpy as np

# r = random.randint(0,5)
# print(r)
# RANDOM_RANGE = 10
#
# acc = []
# random.seed(0)
# for i in range(1, 100001, 1):
#     r = random.randint(1, RANDOM_RANGE)
#     # print(i, r)
#     acc.append(r)
#
# print('-------------------------')
# for i in range(1, RANDOM_RANGE + 1, 1):
#     print(i, acc.count(i))

# Notation  Value Parameter
# |O|       160   Total number of pick orders
# |S|       30    Total number of trucks
# |T|       24    Number of time slots
# d         5     Total number of docks
# p         8     Number of pickers at each time slot
#
# O S d p
# 160 30 5 8
# 320 60 10 16

O_NUMBER_OF_ORDERS = 160
S_NUMBER_OF_TRUCKS = 30
D_NUMBER_OF_DOCKS = 5
T_NUMBER_OF_TIME_SLOTS = 24
timeSlots = range(1, T_NUMBER_OF_TIME_SLOTS + 1, 1)

# T: 4*6=24 us: T1-6 25%, T7-12 30%, T13-18 40%, and T19-24 5%
us_dueTimeForTruck = [0] * S_NUMBER_OF_TRUCKS
# https://numpy.org/doc/stable/reference/random/generated/numpy.random.choice.html
us_dueTimeForTruck = np.random.choice(timeSlots, S_NUMBER_OF_TRUCKS, p=[
    0.25/6, 0.25/6, 0.25/6, 0.25/6, 0.25/6, 0.25/6,
    0.30/6, 0.30/6, 0.30/6, 0.30/6, 0.30/6, 0.30/6,
    0.40/6, 0.40/6, 0.40/6, 0.40/6, 0.40/6, 0.40/6,
    0.05/6, 0.05/6, 0.05/6, 0.05/6, 0.05/6, 0.05/6,
])
print(us_dueTimeForTruck)


NUMBER_OF_ELEMENTS = 10
NUMBER_OF_PARTITIONS = 5
elements = range(1, NUMBER_OF_ELEMENTS + 1)
print('elements=', elements)
split_points = np.random.choice(elements, NUMBER_OF_PARTITIONS - 1, replace=False) + 1
print('split_points=', split_points)
split_points.sort()
print('sorted split_points=', split_points)
print(np.split(elements, split_points))
