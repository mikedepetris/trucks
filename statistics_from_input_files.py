import pandas as pd
import numpy as np

input_file_dir_path = ['Instances/BaseCase/Input/',
                       'Instances/Dock utilization/1 docks/Input/',
                       'Instances/Dock utilization/2 docks/Input/',
                       'Instances/Dock utilization/3 docks/Input/',
                       'Instances/Dock utilization/4 docks/Input/',
                       'Instances/Dock utilization/6 docks/Input/',
                       'Instances/Dock utilization/7 docks/Input/',
                       'Instances/Picker utilization/7 pickers/Input/',
                       'Instances/Picker utilization/9 pickers/Input/',
                       'Instances/Picker utilization/10 pickers/Input/',
                       'Instances/Picker utilization/11 pickers/Input/',
                       'Instances/Picker utilization/12 pickers/Input/']
# count  7200.000000
# mean      5.333333
# std       1.447704
# min       3.000000
# 25%       4.000000
# 50%       5.000000
# 75%       6.000000
# max      10.000000
# counts= [   0    0    0  564 1644 2052 1572  780  348  204   36]
# input_file_dir_path.append('Instances/Workload per truck/100 orders/Input/')
# input_file_dir_path.append('Instances/Workload per truck/130 orders/Input/')
# input_file_dir_path.append('Instances/Workload per truck/190 orders/Input/')
# input_file_dir_path.append('Instances/Workload per truck/220 orders/Input/')
files = range(1, 21, 1)  # c:\dev\python\trucks\Instances\BaseCase\Input\Data(1-20).txt
MAIN_DATA_FILE_LINE_INDEX = 0  # 0:    160	30	5	24
NUMBER_OF_ORDERS_FOR_TRUCK_FILE_LINE_INDEX = 1  # 1:    (30) 8	4	6	5	5	7	9	4	4	5	5	5	3	4	6	4	7	6	5	4	9	3	4	7	3	5	4	6	6	7
DUE_TIME_FOR_TRUCK_FILE_LINE_INDEX = 32
timeSlots = []
numberOfOrdersForTruck_TOTAL = []
us_dueTimeForTruck_TOTAL = []
us_dueTimeForTruck_RANDOM_TOTAL = []
for file_path in input_file_dir_path:
    file_index = 0
    for file_index in files:  # Data(1-20).txt
        # print('Reading data from file', file_path, 'file_index=', file_index)
        data = []  # store integer values read by lines skipping empty lines
        with open(file_path + 'Data' + str(file_index) + '.txt') as f:
            for line in f:
                if line != '\n':
                    if line == 'no\n':
                        data.append([])
                    else:
                        data.append([int(v) for v in line.split()])
        mainData_array = data[MAIN_DATA_FILE_LINE_INDEX]
        O_NUMBER_OF_ORDERS = mainData_array[0]
        S_NUMBER_OF_TRUCKS = mainData_array[1]
        T_NUMBER_OF_TIME_SLOTS = mainData_array[3]
        timeSlots = range(1, T_NUMBER_OF_TIME_SLOTS + 1, 1)
        # create array of NUMBER_OF_PICK_ORDERS_FOR_TRUCK + 1 zeros
        numberOfOrdersForTruck = [0] * S_NUMBER_OF_TRUCKS
        # copy dataset array shifted by 1
        ind = 0
        for e in data[NUMBER_OF_ORDERS_FOR_TRUCK_FILE_LINE_INDEX]:
            numberOfOrdersForTruck[ind] = e
            numberOfOrdersForTruck_TOTAL.append(e)
            ind = ind + 1

        # print('data[DUE_TIME_FOR_TRUCK_FILE_LINE_INDEX]=', data[DUE_TIME_FOR_TRUCK_FILE_LINE_INDEX])
        # print('data[DUE_TIME_FOR_TRUCK_FILE_LINE_INDEX] len=', len(data[DUE_TIME_FOR_TRUCK_FILE_LINE_INDEX]))
        us_dueTimeForTruck = [0] * S_NUMBER_OF_TRUCKS
        # copy dataset array shifted by 1
        ind = 0
        for e in data[DUE_TIME_FOR_TRUCK_FILE_LINE_INDEX]:
            us_dueTimeForTruck[ind] = e
            us_dueTimeForTruck_TOTAL.append(e)
            ind = ind + 1

        us_RANDOM = (np.random.choice(timeSlots, S_NUMBER_OF_TRUCKS, p=[
            0.25 / 6, 0.25 / 6, 0.25 / 6, 0.25 / 6, 0.25 / 6, 0.25 / 6,
            0.30 / 6, 0.30 / 6, 0.30 / 6, 0.30 / 6, 0.30 / 6, 0.30 / 6,
            0.40 / 6, 0.40 / 6, 0.40 / 6, 0.40 / 6, 0.40 / 6, 0.40 / 6,
            0.05 / 6, 0.05 / 6, 0.05 / 6, 0.05 / 6, 0.05 / 6, 0.05 / 6,
        ])).tolist()
        # print('us_RANDOM=', us_RANDOM)
        # print('us_RANDOM= len', len(us_RANDOM))
        ind = 0
        for e in us_RANDOM:
            us_dueTimeForTruck[ind] = e
            us_dueTimeForTruck_RANDOM_TOTAL.append(e)
            ind = ind + 1

print()
print('stats for Os - number of orders for truck')
print('-----------------------------------------')
print('numberOfOrdersForTruck_TOTAL len=', len(numberOfOrdersForTruck_TOTAL))
# print('numberOfOrdersForTruck_TOTAL=', numberOfOrdersForTruck_TOTAL)

df_describe = pd.DataFrame(numberOfOrdersForTruck_TOTAL)
print('DataFrame describe:', df_describe.describe())

counts = np.bincount(numberOfOrdersForTruck_TOTAL)
print('MIN=', min(numberOfOrdersForTruck_TOTAL))
numberOfOrdersForTruck_max = max(numberOfOrdersForTruck_TOTAL)
print('MAX=', numberOfOrdersForTruck_max)
print('counts len=', len(counts))
print('counts sum=', sum(counts))
print('counts=', counts)
print('Table to show the ratio of the orders assigned to each truck ')
print('truck - ratio - orders count')
for i in range(1, numberOfOrdersForTruck_max + 1):
    print(i, "{:.2f}".format(counts[i] / len(numberOfOrdersForTruck_TOTAL)), counts[i])

print()
print('stats for us - due times for trucks')
print('-----------------------------------')
us_distribution_as_paper = [
    0.25 / 6, 0.25 / 6, 0.25 / 6, 0.25 / 6, 0.25 / 6, 0.25 / 6,
    0.30 / 6, 0.30 / 6, 0.30 / 6, 0.30 / 6, 0.30 / 6, 0.30 / 6,
    0.40 / 6, 0.40 / 6, 0.40 / 6, 0.40 / 6, 0.40 / 6, 0.40 / 6,
    0.05 / 6, 0.05 / 6, 0.05 / 6, 0.05 / 6, 0.05 / 6, 0.05 / 6,
]

print('us_dueTimeForTruck_TOTAL len=', len(us_dueTimeForTruck_TOTAL))
# print('us_dueTimeForTruck_TOTAL=', us_dueTimeForTruck_TOTAL)

df_describe = pd.DataFrame(us_dueTimeForTruck_TOTAL)
print('DataFrame describe:', df_describe.describe())

counts = np.bincount(us_dueTimeForTruck_TOTAL)
print('MIN=', min(us_dueTimeForTruck_TOTAL))
us_dueTimeForTruck_max = max(us_dueTimeForTruck_TOTAL)
print('MAX=', us_dueTimeForTruck_max)
print('counts len=', len(counts))
print('counts sum=', sum(counts))
print('counts=', counts)

print()
print('us_dueTimeForTruck_RANDOM_TOTAL len=', len(us_dueTimeForTruck_RANDOM_TOTAL))
# print('us_dueTimeForTruck_RANDOM_TOTAL=', us_dueTimeForTruck_RANDOM_TOTAL)

df_describe = pd.DataFrame(us_dueTimeForTruck_RANDOM_TOTAL)
print('DataFrame describe:', df_describe.describe())

counts_random = np.bincount(us_dueTimeForTruck_RANDOM_TOTAL)
print('MIN=', min(us_dueTimeForTruck_RANDOM_TOTAL))
us_dueTimeForTruck_max = max(us_dueTimeForTruck_RANDOM_TOTAL)
print('MAX=', us_dueTimeForTruck_max)
print('counts_random len=', len(counts_random))
print('counts_random sum=', sum(counts_random))
print('counts_random=', counts_random)

us_distribution_as_inputFiles = []
us_distribution_random = []
for i in timeSlots:
    us_ratio = counts[i] / len(us_dueTimeForTruck_TOTAL)
    us_distribution_as_inputFiles.append(us_ratio)
    # print(i, "{:.2f}".format(us_distribution_as_paper[i - 1]),
    #       "{:.2f}".format(us_ratio), counts[i])
    us_ratio_random = counts_random[i] / len(us_dueTimeForTruck_RANDOM_TOTAL)
    us_distribution_random.append(us_ratio_random)

print('Table to show the frequency ratio of the due times for each time slot')
print('comparing distribution as given by paper, those present in input files, and the random generated values')
print('time slots / paper / input file / random')
print('Group1',
      '/',
      "{:.2f}".format(sum(us_distribution_as_paper[0:6])),
      '/',
      "{:.2f}".format(sum(us_distribution_as_inputFiles[0:6])),
      '/',
      "{:.2f}".format(sum(us_distribution_random[0:6]))
      )
print('Group2',
      '/',
      "{:.2f}".format(sum(us_distribution_as_paper[6:12])),
      '/',
      "{:.2f}".format(sum(us_distribution_as_inputFiles[6:12])),
      '/',
      "{:.2f}".format(sum(us_distribution_random[6:12]))
      )
print('Group3',
      '/',
      "{:.2f}".format(sum(us_distribution_as_paper[12:18])),
      '/',
      "{:.2f}".format(sum(us_distribution_as_inputFiles[12:18])),
      '/',
      "{:.2f}".format(sum(us_distribution_random[12:18]))
      )
print('Group4',
      '/',
      "{:.2f}".format(sum(us_distribution_as_paper[18:24])),
      '/',
      "{:.2f}".format(sum(us_distribution_as_inputFiles[18:24])),
      '/',
      "{:.2f}".format(sum(us_distribution_random[18:24]))
      )
