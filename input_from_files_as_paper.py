import gurobipy as gb

VERBOSE = 1  # 0 = disabled
MIPGAP = 0.15
TIMELIMIT = 3000.0  # seconds
input_file_dir_path = 'Instances/BaseCase/Input/'
# input_file_dir_path = 'Instances/UnluckyCase/'
COLLAB = 1
# c:\dev\python\trucks\Instances\BaseCase\Input\Data(1-20).txt
if COLLAB == 1:
    files = range(1, 21, 2)
else:
    files = range(1, 21, 1)
# input_file_dir_path = 'Instances/SimpleCase/Input/'
# files = range(2, 3, 1)  # Instances\SimpleCase\Input\Data1.txt

# Parameters of the base case instances.
# Parameter                           Notation  Value
# Total number of pick orders         |O|       160
# Total number of trucks              |S|       30
# Number of time slots                |T|       24
# Total number of docks               d         5
# Number of pickers at each time slot p         8

# 20 random instances with the given parameters as the base case instances
# and 240 ( 4 × 3 × 20 ) additional instances, leading to 260 instances in total.
# We use these instances for both collaborative and non-collaborative scenarios.
# We first solve every two instances separately (non-collaborative scenario)
# and then combine them into one joint in-stance. So, we have 10 joint instances
# and compare their results in the case of collaboration and non-collaboration.

# 'Number of pick orders: |O|' 'Number of trucks: |S|' 'Number of docks: |D|' 'Number of times lots: |T|'
# 'Number of orders in each truck: |O_s|'
# 'The orders in each truck: O_s'
# 'Due time of trucks: u_s'
# 'Number of pickers at each time slot: p'
# Indexes
MAIN_DATA_FILE_LINE_INDEX = 0  # 0:    160	30	5	24
NUMBER_OF_ORDERS_FOR_TRUCK_FILE_LINE_INDEX = 1  # 1:    (30) 8	4	6	5	5	7	9	...
ORDERS_FOR_TRUCK_FILE_LINE_INDEXES = range(2, 32, 1)  # 2-31: (30 rows) with 1..8 9..12 ...
DUE_TIME_FOR_TRUCK_FILE_LINE_INDEX = 32  # 32:   (30) 14	9	2	1	17	14	18	10	...
NUMBER_OF_PICKERS_FOR_TIME_SLOT_FILE_LINE_INDEX = 33  # 33:   (24) 8	8	8	8	8	...

# vars to accumulate optimal solutions values and objs
file_indexes = []
runtimes = []
statuses = []
optimal_obj_values_all_cases = []
optimal_ls_values_all_cases = []

file_index = 0
for file_index in files:  # Data(1-20).txt
    print('Starting model preparation for file_index=', file_index)

    mainData_array = []
    numberOfOrdersForTruck = []
    us_dueTimeForTruck = []
    p_numberOfPickersForTimeSlot = []
    data = []  # store integer values read by lines skipping empty lines
    with open(input_file_dir_path + 'Data' + str(file_index) + '.txt') as f:
        for line in f:
            if line != '\n' and not line.startswith('Total_matching_score:_'):
                if line == 'no\n':
                    data.append([])
                else:
                    data.append([int(v) for v in line.split()])

    # 0:    160	30	5	24
    mainData_array = data[MAIN_DATA_FILE_LINE_INDEX]
    O_NUMBER_OF_ORDERS = mainData_array[0]
    S_NUMBER_OF_TRUCKS = mainData_array[1]
    D_NUMBER_OF_DOCKS = mainData_array[2]
    T_NUMBER_OF_TIME_SLOTS = mainData_array[3]
    timeSlots = range(1, T_NUMBER_OF_TIME_SLOTS + 1, 1)
    M = T_NUMBER_OF_TIME_SLOTS  # for constr (5)

    # vars to elaborate data to evaluate collab impact
    data2 = []  # set of data from second file to create joint case
    HALF_NUMBER_OF_ORDERS = O_NUMBER_OF_ORDERS / 2
    if COLLAB == 1:
        with open(input_file_dir_path + 'Data' + str(file_index + 1) + '.txt') as f:
            for line in f:
                if line != '\n' and not line.startswith('Total_matching_score:_'):
                    if line == 'no\n':
                        data2.append([])
                    else:
                        data2.append([int(v) for v in line.split()])
        HALF_NUMBER_OF_ORDERS = O_NUMBER_OF_ORDERS
        O_NUMBER_OF_ORDERS = O_NUMBER_OF_ORDERS * 2
        S_NUMBER_OF_TRUCKS = S_NUMBER_OF_TRUCKS * 2
        D_NUMBER_OF_DOCKS = D_NUMBER_OF_DOCKS * 2

    numberOfOrdersForTruck = [0] * S_NUMBER_OF_TRUCKS
    number_of_orders_for_truck_file_line_index = 0
    for number_of_orders_for_truck_file_line in data[NUMBER_OF_ORDERS_FOR_TRUCK_FILE_LINE_INDEX]:
        numberOfOrdersForTruck[number_of_orders_for_truck_file_line_index] = number_of_orders_for_truck_file_line
        number_of_orders_for_truck_file_line_index = number_of_orders_for_truck_file_line_index + 1
    if COLLAB == 1:
        for number_of_orders_for_truck_file_line in data2[NUMBER_OF_ORDERS_FOR_TRUCK_FILE_LINE_INDEX]:
            numberOfOrdersForTruck[number_of_orders_for_truck_file_line_index] = number_of_orders_for_truck_file_line
            number_of_orders_for_truck_file_line_index = number_of_orders_for_truck_file_line_index + 1

    # create base for multi array
    Os_ordersForTruck = []
    for ii in ORDERS_FOR_TRUCK_FILE_LINE_INDEXES:
        # create array of zeros of number of orders for single truck
        ordersForTruck_single = [0] * (len(data[ii]))
        # copy dataset of number of orders for single truck shifted by 1
        number_of_orders_for_truck_file_line_index = 0
        for number_of_orders_for_truck_file_line in data[ii]:
            ordersForTruck_single[number_of_orders_for_truck_file_line_index] = number_of_orders_for_truck_file_line
            number_of_orders_for_truck_file_line_index = number_of_orders_for_truck_file_line_index + 1
        if ordersForTruck_single:
            Os_ordersForTruck.append(ordersForTruck_single)
    if COLLAB == 1:
        for ii in ORDERS_FOR_TRUCK_FILE_LINE_INDEXES:
            # create array of zeros of number of orders for single truck
            ordersForTruck_single = [0] * (len(data2[ii]))
            # copy dataset of orders number for single truck shifted by 1
            number_of_orders_for_truck_file_line_index = 0
            for number_of_orders_for_truck_file_line in data2[ii]:
                ordersForTruck_single[number_of_orders_for_truck_file_line_index] = \
                    number_of_orders_for_truck_file_line + HALF_NUMBER_OF_ORDERS
                number_of_orders_for_truck_file_line_index = number_of_orders_for_truck_file_line_index + 1
            if ordersForTruck_single:
                Os_ordersForTruck.append(ordersForTruck_single)

    us_dueTimeForTruck = [0] * S_NUMBER_OF_TRUCKS
    # copy dataset array shifted by 1
    number_of_orders_for_truck_file_line_index = 0
    for number_of_orders_for_truck_file_line in data[DUE_TIME_FOR_TRUCK_FILE_LINE_INDEX]:
        us_dueTimeForTruck[number_of_orders_for_truck_file_line_index] = number_of_orders_for_truck_file_line
        number_of_orders_for_truck_file_line_index = number_of_orders_for_truck_file_line_index + 1
    if COLLAB == 1:
        for number_of_orders_for_truck_file_line in data2[DUE_TIME_FOR_TRUCK_FILE_LINE_INDEX]:
            us_dueTimeForTruck[number_of_orders_for_truck_file_line_index] = number_of_orders_for_truck_file_line
            number_of_orders_for_truck_file_line_index = number_of_orders_for_truck_file_line_index + 1

    p_numberOfPickersForTimeSlot = [0] * T_NUMBER_OF_TIME_SLOTS
    # copy dataset array shifted by 1
    number_of_pickers_for_time_slot_file_line_index = 0
    for number_of_pickers_for_time_slot_file_line in data[NUMBER_OF_PICKERS_FOR_TIME_SLOT_FILE_LINE_INDEX]:
        p_numberOfPickersForTimeSlot[number_of_pickers_for_time_slot_file_line_index] = \
            number_of_pickers_for_time_slot_file_line
        number_of_pickers_for_time_slot_file_line_index = number_of_pickers_for_time_slot_file_line_index + 1
    if COLLAB == 1:
        number_of_pickers_for_time_slot_file_line_index = 0
        for number_of_pickers_for_time_slot_file_line in data2[NUMBER_OF_PICKERS_FOR_TIME_SLOT_FILE_LINE_INDEX]:
            p_numberOfPickersForTimeSlot[number_of_pickers_for_time_slot_file_line_index] += \
                number_of_pickers_for_time_slot_file_line
            number_of_pickers_for_time_slot_file_line_index = number_of_pickers_for_time_slot_file_line_index + 1

    if COLLAB == 1:
        print('COLLABORATION OF TWO COMPANIES')
    print('Number of orders: |O|', O_NUMBER_OF_ORDERS,
          'Number of trucks: |S|', S_NUMBER_OF_TRUCKS,
          'Number of docks: |D|', D_NUMBER_OF_DOCKS,
          'Number of time slots: |T|', T_NUMBER_OF_TIME_SLOTS)
    print('Number of orders in each truck: |O_s|', numberOfOrdersForTruck)
    print('The orders in each truck: O_s', Os_ordersForTruck)
    print('Due time of trucks: u_s', us_dueTimeForTruck)
    print('Number of pickers at each time slot: p', p_numberOfPickersForTimeSlot)
    print()

    # problem assignment
    p = gb.Model()
    p.ModelSense = gb.GRB.MINIMIZE

    # Decision variables
    xot = p.addVars(
        # [(i, j) for i in range(1, O_NUMBER_OF_PICK_ORDERS + 1, 1) for j in range(1, T_NUMBER_OF_TIME_SLOTS + 1, 1)],
        range(1, O_NUMBER_OF_ORDERS + 1, 1),
        range(1, T_NUMBER_OF_TIME_SLOTS + 1, 1),
        vtype=gb.GRB.BINARY, name='xot')
    ys1 = p.addVars([i for i in range(1, S_NUMBER_OF_TRUCKS + 1, 1)], vtype=gb.GRB.INTEGER, name='ys1')
    ys = p.addVars([i for i in range(1, S_NUMBER_OF_TRUCKS + 1, 1)], vtype=gb.GRB.INTEGER, name='ys')
    ls = p.addVars([i for i in range(1, S_NUMBER_OF_TRUCKS + 1, 1)], vtype=gb.GRB.INTEGER, name='ls')
    qss1 = p.addVars(
        # [(i, j) for i in range(1, TOTAL_NUMBER_OF_TRUCKS + 1, 1) for j in range(1, TOTAL_NUMBER_OF_TRUCKS + 1, 1)],
        range(1, S_NUMBER_OF_TRUCKS + 1, 1),
        range(1, S_NUMBER_OF_TRUCKS + 1, 1),
        vtype=gb.GRB.BINARY, name='qss1')
    q0s = p.addVars(range(1, S_NUMBER_OF_TRUCKS + 1, 1), vtype=gb.GRB.BINARY, name='q0s')
    qslast = p.addVars(range(1, S_NUMBER_OF_TRUCKS + 1, 1), vtype=gb.GRB.BINARY, name='qslast')

    # (1) The objective function represents the minimization of the # total tardiness of the shipping trucks
    p.setObjective(gb.quicksum(ls[i] for i in range(1, S_NUMBER_OF_TRUCKS + 1, 1)))

    # (2) Constraints ensure that the total number of pick orders picked at each time slot does not exceed the number of
    # available pickers.
    for t in range(1, T_NUMBER_OF_TIME_SLOTS + 1, 1):
        p.addConstr(gb.quicksum(xot[o, t] for o in range(1, O_NUMBER_OF_ORDERS + 1, 1)) <=
                    p_numberOfPickersForTimeSlot[t - 1], 'two')

    # (3) Constraints determine the tardiness of trucks, which takes a positive value if the departure time of a
    # truck is greater than its due time.
    for s in range(1, S_NUMBER_OF_TRUCKS + 1, 1):
        p.addConstr(ls[s] >= (ys[s] - us_dueTimeForTruck[s - 1]), 'three')

    # (4) Constraints define the start time of picking the orders assigned to each truck.
    for s in range(1, S_NUMBER_OF_TRUCKS + 1, 1):
        for o in Os_ordersForTruck[s - 1]:
            p.addConstr(ys1[s] <= gb.quicksum(t * xot[o, t] for t in range(1, T_NUMBER_OF_TIME_SLOTS + 1, 1)), 'four')

    # (5) Constraints guarantee that when two trucks are assigned to the same dock door, the successor can only start
    # loading once the predecessor has departed. The reason is that the pick orders of a truck are put in the
    # corresponding dock lane after being picked, therefore, there must be a free dock lane for each truck,
    # when its corresponding orders are being picked. In this constraint, M denotes a sufficiently large number. In the
    # case where q ss ′ = 1 , we have y s ≤ y ′ s ′ + M − 1 . Since y s always takes a value between 1 and | T | ,
    # M must be at least equal to | T | . Therefore, we set this parameter equal to | T | .
    for s in range(1, S_NUMBER_OF_TRUCKS + 1, 1):
        for s1 in range(1, S_NUMBER_OF_TRUCKS + 1, 1):
            if s != s1:
                p.addConstr((ys[s] - (M * (1 - qss1[s, s1])) + 1) <= ys1[s1], 'five')

    # (6) Constraints define the departure time of each truck. The departure of the truck must be after its due time
    for s in range(1, S_NUMBER_OF_TRUCKS + 1, 1):
        p.addConstr(ys[s] >= us_dueTimeForTruck[s - 1], 'six')

    # (7) Constraints define the departure time of each truck. The departure of the truck must be also after all its
    # orders are picked and loaded.
    for s in range(1, S_NUMBER_OF_TRUCKS + 1, 1):
        for o in Os_ordersForTruck[s - 1]:
            p.addConstr(ys[s] >= gb.quicksum(t * xot[o, t] for t in range(1, T_NUMBER_OF_TIME_SLOTS + 1, 1)), 'seven')

    # (8) Constraints guarantees that all the orders are picked in the planning horizon.
    for o in range(1, O_NUMBER_OF_ORDERS + 1, 1):
        p.addConstr((gb.quicksum(xot[o, t] for t in range(1, T_NUMBER_OF_TIME_SLOTS + 1, 1))) == 1, 'eight')

    # (9) Constraints ensures that at most d docks may be used in total.
    p.addConstr(gb.quicksum(q0s[s] for s in range(1, S_NUMBER_OF_TRUCKS + 1, 1)) <= D_NUMBER_OF_DOCKS, 'nine')

    # (10) Constraints (10) and (11) define the sequence of trucks at each dock door,
    # so that each truck has one immediate successor and one immediate predecessor.
    for s in range(1, S_NUMBER_OF_TRUCKS + 1, 1):
        p.addConstr((q0s[s] + gb.quicksum(qss1[s1, s] for s1 in range(1, S_NUMBER_OF_TRUCKS + 1) if s1 != s)) == 1,
                    'ten')

    # (11)
    for s in range(1, S_NUMBER_OF_TRUCKS + 1, 1):
        p.addConstr(qslast[s] + gb.quicksum(qss1[s, s1] for s1 in range(1, S_NUMBER_OF_TRUCKS + 1) if s1 != s) == 1,
                    'eleven')

    p.params.TimeLimit = TIMELIMIT
    p.params.MIPGap = MIPGAP
    p.optimize()

    # Model statuses:
    #  1    LOADED
    #  2    OPTIMAL
    #  3    INFEASIBLE
    #  4    INF_OR_UNBD
    #  5    UNBOUNDED
    #  6    CUTOFF
    #  7    ITERATION_LIMIT
    #  8    NODE_LIMIT
    #  9    TIME_LIMIT
    # 10    SOLUTION_LIMIT
    # 11    INTERRUPTED
    # 12    NUMERIC
    # 13    SUBOPTIMAL
    # 14    INPROGRESS
    # 15    USER_OBJ_LIMIT
    # 16    WORK_LIMIT

    # Display optimal total matching score
    print()
    print('Status: ', p.status)
    if p.Status == 3:
        print('INFEASIBLE')
    else:
        print('Total matching score: ', p.objVal)
    print()

    optimal_ls_values = []
    if p.Status not in [3, 9]:
        for z in ls:
            optimal_ls_values.append(ls[z].X)
    else:
        optimal_ls_values = []

    file_indexes.append(file_index)
    statuses.append(p.status)
    runtimes.append(p.Runtime)
    if p.Status == 3:
        optimal_obj_values_all_cases.append(-1)
    else:
        optimal_obj_values_all_cases.append(p.objVal)
    optimal_ls_values_all_cases.append(optimal_ls_values)

    if VERBOSE > 0 and p.Status not in [3, 9]:
        # Display optimal values of decision variables
        print('Display optimal values of decision variables')
        for v in p.getVars():
            if v.X > 1e-6:
                print(v.varName, v.X)

        print()
        print('(2) Constraints ensure that the total number of pick orders picked at each time slot does not exceed '
              'the number of available pickers.')
        for t in range(1, T_NUMBER_OF_TIME_SLOTS + 1, 1):
            sum_for_time_slot = sum(xot[o, t].X for o in range(1, O_NUMBER_OF_ORDERS + 1, 1))
            print('t=', t, 'p_pickers=', p_numberOfPickersForTimeSlot[t - 1], 'sum_for_time_slot', sum_for_time_slot)
            for o in range(1, O_NUMBER_OF_ORDERS + 1, 1):
                if xot[o, t].X == 1.0:
                    print('    ', xot[o, t])

        print()
        print('(3) Constraints determine the tardiness of trucks, which takes a positive value if the departure time '
              'of a truck is greater than its due time.')
        for s in range(1, S_NUMBER_OF_TRUCKS + 1, 1):
            if ls[s].X == ys[s].X - us_dueTimeForTruck[s - 1]:
                print(ls[s].X == ys[s].X - us_dueTimeForTruck[s - 1],
                      ls[s],
                      'ys-us=', ys[s].X - us_dueTimeForTruck[s - 1],
                      ys[s],
                      'us=', us_dueTimeForTruck[s - 1])
            else:
                print(ls[s].X == ys[s].X - us_dueTimeForTruck[s - 1],
                      ls[s].X,
                      ys[s].X - us_dueTimeForTruck[s - 1],
                      ys[s].X,
                      us_dueTimeForTruck[s - 1],
                      '<-----------')

        print()
        print('(4) Constraints define the start time of picking the orders assigned to each truck.')
        for s in range(1, S_NUMBER_OF_TRUCKS + 1, 1):
            for o in Os_ordersForTruck[s - 1]:
                if ys1[s].X > 0:
                    print('s=', s, 'o=', o, ys1[s], '<--------------')
                    for t in range(1, T_NUMBER_OF_TIME_SLOTS + 1, 1):
                        if xot[o, t].X == 1.0:
                            print('    ', xot[o, t])
                else:
                    print(o, ys1[s])

        print()
        print('(5) Constraints guarantee that when two trucks are assigned to the same dock door, the successor can '
              'only start loading once the predecessor has departed. The reason is that the pick orders of a truck '
              'are put in the corresponding dock lane after being picked, therefore, there must be a free dock lane '
              'for each truck, when its corresponding orders are being picked. In this constraint, M denotes a '
              'sufficiently large number. In the case where q ss ′ = 1 , we have y s ≤ y ′ s ′ + M − 1 . Since y s '
              'always takes a value between 1 and | T | , M must be at least equal to | T | . Therefore, we set this '
              'parameter equal to | T | .')
        for s in range(1, S_NUMBER_OF_TRUCKS + 1, 1):
            print('Truck s=', s)
            for s1 in range(1, S_NUMBER_OF_TRUCKS + 1, 1):
                if s != s1:
                    if qss1[s, s1].X > 0:
                        print('    ',
                              (ys[s].X - M * (1 - qss1[s, s1].X) + 1), ' <= ', ys1[s1].X, ys[s],
                              'M=', M,
                              qss1[s, s1],
                              ys1[s1])

        print()
        print('(6) Constraints define the departure time of each truck. The departure of the truck must be after its '
              'due time')
        for s in range(1, S_NUMBER_OF_TRUCKS + 1, 1):
            print('Truck s=', s, ys[s], ' >= ', us_dueTimeForTruck[s - 1])

        print()
        print('(7) Constraints define the departure time of each truck. The departure of the truck must be also after '
              'all its orders are picked and loaded.')
        for s in range(1, S_NUMBER_OF_TRUCKS + 1, 1):
            for o in range(1, O_NUMBER_OF_ORDERS + 1, 1):
                if ys[s].X > 0:
                    print('Truck s=', s, 'o=', o, ys[s], '<--------------')
                    for t in range(1, T_NUMBER_OF_TIME_SLOTS + 1, 1):
                        if xot[o, t].X == 1.0:
                            print('    ', xot[o, t], 't * xot[o, t].X=', t * xot[o, t].X)
                else:
                    print(o, ys[s])

        print()
        print('(8) Constraints guarantees that all the orders are picked in the planning horizon.')
        for o in range(1, O_NUMBER_OF_ORDERS + 1, 1):
            print('order o=', o, 'T_NUMBER_OF_TIME_SLOTS=', T_NUMBER_OF_TIME_SLOTS)
            for t in range(1, T_NUMBER_OF_TIME_SLOTS + 1, 1):
                if xot[o, t].X == 1.0:
                    print('    ', xot[o, t])

        print()
        print('(9) Constraints ensures that at most d docks may be used in total.')
        for s in range(1, S_NUMBER_OF_TRUCKS + 1, 1):
            # print(q0s[s], TOTAL_NUMBER_OF_DOCKS)
            if q0s[s].X == 1:
                print(q0s[s], 'FIRST TRUCK with d=', D_NUMBER_OF_DOCKS, '<----------------')
            else:
                print(q0s[s], 'not first truck with d=', D_NUMBER_OF_DOCKS)

        print()
        print('(10) Constraints (10) and (11) define the sequence of trucks at each dock door, so that each truck has '
              'one immediate successor and one immediate predecessor.')
        for s in range(1, S_NUMBER_OF_TRUCKS + 1, 1):
            print(q0s[s])
            for s1 in range(1, S_NUMBER_OF_TRUCKS + 1):
                if qss1[s1, s].X == 1:
                    print('    ', qss1[s1, s])

        print()
        print('(11) Constraints (10) and (11) define the sequence of trucks at each dock door, so that each truck has '
              'one immediate successor and one immediate predecessor.')
        for s in range(1, S_NUMBER_OF_TRUCKS + 1, 1):
            print(qslast[s])
            for s1 in range(1, S_NUMBER_OF_TRUCKS + 1):
                if qss1[s, s1].X == 1:
                    print('    ', qss1[s, s1])
        print('********************************************')
        print()

# Display all results
print()
print('Number of cases: ', file_index)
print('Files parsed: ', file_indexes)
print('Run times: ', runtimes)
print('Statuses: ', statuses)
print('Number of solutions: ', optimal_obj_values_all_cases.__len__())
print('Obj solutions values: ', optimal_obj_values_all_cases)
print('Total tardiness: ', sum(optimal_obj_values_all_cases))
print('Number of solutions ls values: ', optimal_ls_values_all_cases.__len__())
print('Solutions ls values: ', optimal_ls_values_all_cases)
print('--------------------------------------------------------------------------------------------------------------')
print()
