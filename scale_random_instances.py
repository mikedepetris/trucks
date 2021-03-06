import gurobipy as gb
import numpy as np

VERBOSE = 0  # 0 = disabled
MIPGAP = 0.15
TIMELIMIT = 6000.0  # seconds
NUMBER_OF_CASES = 20

# Parameters of the base case instances.
# Notation  Value Parameter
# |O|       160   Total number of pick orders
# |S|       30    Total number of trucks
# |T|       24    Number of time slots
# d         5     Total number of docks
# p         8     Number of pickers at each time slot
#
# O     S   d   p
# 64    12  2   3.2
# 80    15  2.5 4
# 160   30  5   8
# 320   60  10  16
# 640  120  20  32
# 1280 240  40  64
# 2560 480  80 128
O_NUMBER_OF_ORDERS = 2560
S_NUMBER_OF_TRUCKS = 480
D_NUMBER_OF_DOCKS = 80
NUMBER_OF_PICKERS = 128
T_NUMBER_OF_TIME_SLOTS = 24
M = T_NUMBER_OF_TIME_SLOTS  # for constr (5)
NUMBER_OF_ORDERS_PROBABILITY_DISTRIBUTION = \
    [0, 0, 564 / 7200, 1644 / 7200, 2052 / 7200, 1572 / 7200, 780 / 7200, 348 / 7200, 204 / 7200, 36 / 7200]
print('Number of orders: |O|', O_NUMBER_OF_ORDERS,
      'Number of trucks: |S|', S_NUMBER_OF_TRUCKS,
      'Number of docks: |D|', D_NUMBER_OF_DOCKS,
      'Number of time slots: |T|', T_NUMBER_OF_TIME_SLOTS)

timeSlots = range(1, T_NUMBER_OF_TIME_SLOTS + 1, 1)
Os_ORDER_CODES = range(1, O_NUMBER_OF_ORDERS + 1, 1)
O_orders = range(1, O_NUMBER_OF_ORDERS + 1)

# vars to accumulate optimal solutions values and objs
case_indexes = []
runtimes = []
statuses = []
optimal_obj_values_all_cases = []
optimal_ls_values_all_cases = []


def generate_fixed_sum_random_vector(fixed_sum_of_vector, max_element_value, number_of_elements_to_generate,
                                     max_tries=500):
    print('generate_fixed_sum_random_vector(fixed_sum_of_vector=', fixed_sum_of_vector,
          'max_element_value=', max_element_value, 'number_of_elements_to_generate=', number_of_elements_to_generate,
          'max_tries=', max_tries, ')')
    # uniform distribution range: 1-max
    # generated_vector = np.random.randint(1, max_element_value,
    #                                      number_of_elements_to_generate)
    generated_vector = np.random.choice(np.arange(1, 11), number_of_elements_to_generate,
                                        p=NUMBER_OF_ORDERS_PROBABILITY_DISTRIBUTION) + 1
    generated_vector_sum = sum(generated_vector)
    if np.sum(np.round(generated_vector / generated_vector_sum * fixed_sum_of_vector)) == fixed_sum_of_vector:
        return np.round(generated_vector / generated_vector_sum * fixed_sum_of_vector)
    elif np.sum(np.floor(generated_vector / generated_vector_sum * fixed_sum_of_vector)) == fixed_sum_of_vector:
        return np.floor(generated_vector / generated_vector_sum * fixed_sum_of_vector)
    elif np.sum(np.ceil(generated_vector / generated_vector_sum * fixed_sum_of_vector)) == fixed_sum_of_vector:
        return np.ceil(generated_vector / generated_vector_sum * fixed_sum_of_vector)
    else:
        if max_tries > 0:
            return generate_fixed_sum_random_vector(fixed_sum_of_vector, max_element_value,
                                                    number_of_elements_to_generate, max_tries - 1)
        else:
            print('Limit reached: maxTries=', max_tries)
            return [-1]


cases_index = 0
for cases_index in range(1, NUMBER_OF_CASES + 1):
    print('Starting model preparation for case index=', cases_index)
    # 'Number of pick orders: |O|' 'Number of trucks: |S|' 'Number of docks: |D|' 'Number of times lots: |T|'
    # 'Number of orders in each truck: |O_s|'
    # 'The orders in each truck: O_s'
    # 'Due time of trucks: u_s'
    # 'Number of pickers at each time slot: p'

    # numberOfOrdersForTruck = []
    # ordersForTruckSplitIndex = np.random.choice(O_orders, S_NUMBER_OF_TRUCKS - 1, replace=False) + 1
    # print('ordersForTruckSplitIndex=', ordersForTruckSplitIndex)
    # ordersForTruckSplitIndex.sort()
    # Os_ordersForTruck = np.split(O_orders, ordersForTruckSplitIndex)
    # for s in range(1, S_NUMBER_OF_TRUCKS + 1, 1):
    #     numberOfOrdersForTruck.append(len(Os_ordersForTruck[s - 1]))
    numberOfOrdersForTruck = generate_fixed_sum_random_vector(O_NUMBER_OF_ORDERS, 10, S_NUMBER_OF_TRUCKS)
    # print('Number of orders: |O|', O_NUMBER_OF_ORDERS,
    #       'Number of trucks: |S|', S_NUMBER_OF_TRUCKS,
    #       'Number of docks: |D|', D_NUMBER_OF_DOCKS,
    #       'Number of time slots: |T|', T_NUMBER_OF_TIME_SLOTS)
    print('random numberOfOrdersForTruck=', numberOfOrdersForTruck, 'len=', len(numberOfOrdersForTruck), 'sum=',
          sum(numberOfOrdersForTruck))
    if len(numberOfOrdersForTruck) < 2:  # and numberOfOrdersForTruck[0] == [-1]:
        print('random numberOfOrdersForTruck=', numberOfOrdersForTruck, 'unable to generate random set, skipping')
    else:
        numberOfOrdersForTruck = numberOfOrdersForTruck.astype(int).tolist()
        # print('random as int numberOfOrdersForTruck=', numberOfOrdersForTruck, sum(numberOfOrdersForTruck))
        Os_ordersForTruck = []
        counter = 1
        for s in range(1, S_NUMBER_OF_TRUCKS + 1, 1):
            # print('for s in range(1, S_NUMBER_OF_TRUCKS + 1, 1): s=', s, 'counter=', counter)
            Os_ordersForTruck.append(np.arange(counter, counter + numberOfOrdersForTruck[s - 1]))
            counter = counter + numberOfOrdersForTruck[s - 1]
        # print('Os_ordersForTruck=', Os_ordersForTruck)

        # In the original dataset, 25%, 30%, 40%, and 5% of trucks depart in the first to fourth period, respectively.
        # T: 4*6=24 us: T1-6 25%, T7-12 30%, T13-18 40%, and T19-24 5%
        # https://numpy.org/doc/stable/reference/random/generated/numpy.random.choice.html
        us_dueTimeForTruck = (np.random.choice(timeSlots, S_NUMBER_OF_TRUCKS, p=[
            0.25 / 6, 0.25 / 6, 0.25 / 6, 0.25 / 6, 0.25 / 6, 0.25 / 6,
            0.30 / 6, 0.30 / 6, 0.30 / 6, 0.30 / 6, 0.30 / 6, 0.30 / 6,
            0.40 / 6, 0.40 / 6, 0.40 / 6, 0.40 / 6, 0.40 / 6, 0.40 / 6,
            0.05 / 6, 0.05 / 6, 0.05 / 6, 0.05 / 6, 0.05 / 6, 0.05 / 6,
        ])).tolist()
        # print('RANDOM Due time of trucks: u_s', us_dueTimeForTruck)

        p_numberOfPickersForTimeSlot = [NUMBER_OF_PICKERS] * T_NUMBER_OF_TIME_SLOTS

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

        #
        # Decision variables
        #
        # xot Binary decision variable which equals 1 if and only if pick order o is picked at time t
        xot = p.addVars(
            range(1, O_NUMBER_OF_ORDERS + 1, 1),
            range(1, T_NUMBER_OF_TIME_SLOTS + 1, 1),
            vtype=gb.GRB.BINARY, name='xot')

        # y???s The picking time of the first pick order which is assigned to truck s
        ys1 = p.addVars([i for i in range(1, S_NUMBER_OF_TRUCKS + 1, 1)], vtype=gb.GRB.INTEGER, name='ys1')

        # ys Departure time of truck s
        ys = p.addVars([i for i in range(1, S_NUMBER_OF_TRUCKS + 1, 1)], vtype=gb.GRB.INTEGER, name='ys')

        # ls Tardiness of truck s
        ls = p.addVars([i for i in range(1, S_NUMBER_OF_TRUCKS + 1, 1)], vtype=gb.GRB.INTEGER, name='ls')

        # qss??? Binary decision variable which equals 1 if and only if truck s??? is scheduled to depart immediately
        # after truck s at one of the docks
        qss1 = p.addVars(
            # [(i, j) for i in range(1, TOTAL_NUMBER_OF_TRUCKS + 1, 1) for j in range(1, TOTAL_NUMBER_OF_TRUCKS+1, 1)],
            range(1, S_NUMBER_OF_TRUCKS + 1, 1),
            range(1, S_NUMBER_OF_TRUCKS + 1, 1),
            vtype=gb.GRB.BINARY, name='qss1')

        # q0s (qs,|S|+1) Binary variable which equals 1 when truck s is the first (last) truck assigned to a dock,
        # respectively
        q0s = p.addVars(range(1, S_NUMBER_OF_TRUCKS + 1, 1), vtype=gb.GRB.BINARY, name='q0s')
        qslast = p.addVars(range(1, S_NUMBER_OF_TRUCKS + 1, 1), vtype=gb.GRB.BINARY, name='qslast')

        # (1) The objective function represents the minimization of the # total tardiness of the shipping trucks
        p.setObjective(gb.quicksum(ls[i] for i in range(1, S_NUMBER_OF_TRUCKS + 1, 1)))

        # (2) Constraints ensure that the total number of pick orders picked at each time slot does not exceed the
        # number of available pickers.
        for t in range(1, T_NUMBER_OF_TIME_SLOTS + 1, 1):
            p.addConstr(
                gb.quicksum(xot[o, t] for o in range(1, O_NUMBER_OF_ORDERS + 1, 1))
                <= p_numberOfPickersForTimeSlot[t - 1],
                'two')

        # (3) Constraints determine the tardiness of trucks, which takes a positive value if the departure time of a
        # truck is greater than its due time.
        for s in range(1, S_NUMBER_OF_TRUCKS + 1, 1):
            p.addConstr(ls[s] >= (ys[s] - us_dueTimeForTruck[s - 1]), 'three')

        # (4) Constraints define the start time of picking the orders assigned to each truck.
        for s in range(1, S_NUMBER_OF_TRUCKS + 1, 1):
            for o in Os_ordersForTruck[s - 1]:
                p.addConstr(ys1[s] <= gb.quicksum(t * xot[o, t] for t in range(1, T_NUMBER_OF_TIME_SLOTS + 1, 1)),
                            'four')

        # (5) Constraints guarantee that when two trucks are assigned to the same dock door, the successor can only
        # start loading once the predecessor has departed. The reason is that the pick orders of a truck are put in
        # the corresponding dock lane after being picked, therefore, there must be a free dock lane for each truck,
        # when its corresponding orders are being picked. In this constraint, M denotes a sufficiently large number.
        # In the case where q ss ??? = 1 , we have y s ??? y ??? s ??? + M ??? 1 . Since y s always takes a value between 1 and
        # | T | , M must be at least equal to | T | . Therefore, we set this parameter equal to | T | .
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
                p.addConstr(ys[s] >= gb.quicksum(t * xot[o, t] for t in range(1, T_NUMBER_OF_TIME_SLOTS + 1, 1)),
                            'seven')

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

        case_indexes.append(cases_index)
        statuses.append(p.status)
        runtimes.append(p.Runtime)
        if p.Status == 3:
            optimal_obj_values_all_cases.append(-1)
        else:
            optimal_obj_values_all_cases.append(p.objVal)
        optimal_ls_values_all_cases.append(optimal_ls_values)

        if p.Status not in [3, 9]:
            print('Display optimal values of decision variables')
            for v in p.getVars():
                if v.X > 1e-6:
                    print(v.varName, v.X)
            print()

        if VERBOSE > 0 and p.Status not in [3, 9]:
            print()
            print(
                '(2) Constraints ensure that the total number of pick orders picked at each time slot does not exceed '
                'the number of available pickers.')
            for t in range(1, T_NUMBER_OF_TIME_SLOTS + 1, 1):
                sum_for_time_slot = sum(xot[o, t].X for o in range(1, O_NUMBER_OF_ORDERS + 1, 1))
                print('t=', t, 'p_pickers=', p_numberOfPickersForTimeSlot[t - 1], 'sum_for_time_slot',
                      sum_for_time_slot)
                for o in range(1, O_NUMBER_OF_ORDERS + 1, 1):
                    if xot[o, t].X == 1.0:
                        print('    ', xot[o, t])

            print()
            print(
                '(3) Constraints determine the tardiness of trucks, which takes a positive value if the departure time '
                'of a truck is greater than its due time.')
            for s in range(1, S_NUMBER_OF_TRUCKS + 1, 1):
                if ls[s].X == ys[s].X - us_dueTimeForTruck[s - 1]:
                    print(ls[s].X == ys[s].X - us_dueTimeForTruck[s - 1],
                          ls[s],
                          'ys-us=', ys[s].X - us_dueTimeForTruck[s - 1],
                          ys[s],
                          'us=', us_dueTimeForTruck[s - 1])
                else:
                    print(ls[s].X == ys[s].X - us_dueTimeForTruck[s - 1], ls[s].X, ys[s].X - us_dueTimeForTruck[s - 1],
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
            print(
                '(5) Constraints guarantee that when two trucks are assigned to the same dock door, the successor can '
                'only start loading once the predecessor has departed. The reason is that the pick orders of a truck '
                'are put in the corresponding dock lane after being picked, therefore, there must be a free dock lane '
                'for each truck, when its corresponding orders are being picked. In this constraint, M denotes a '
                'sufficiently large number. In the case where q ss ??? = 1 , we have y s ??? y ??? s ??? + M ??? 1 . Since y s '
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
            print(
                '(6) Constraints define the departure time of each truck. The departure of the truck must be after its '
                'due time')
            for s in range(1, S_NUMBER_OF_TRUCKS + 1, 1):
                print('Truck s=', s, ys[s], ' >= ', us_dueTimeForTruck[s - 1])

            print()
            print('(7) Constraints define the departure time of each truck. The departure of the truck must be also '
                  'after all its orders are picked and loaded.')
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
            print('(10) Constraints (10) and (11) define the sequence of trucks at each dock door, so that each truck '
                  'has one immediate successor and one immediate predecessor.')
            for s in range(1, S_NUMBER_OF_TRUCKS + 1, 1):
                print(q0s[s])
                for s1 in range(1, S_NUMBER_OF_TRUCKS + 1):
                    if qss1[s1, s].X == 1:
                        print('    ', qss1[s1, s])

            print()
            print('(11) Constraints (10) and (11) define the sequence of trucks at each dock door, so that each truck '
                  'has one immediate successor and one immediate predecessor.')
            for s in range(1, S_NUMBER_OF_TRUCKS + 1, 1):
                print(qslast[s])
                for s1 in range(1, S_NUMBER_OF_TRUCKS + 1):
                    if qss1[s, s1].X == 1:
                        print('    ', qss1[s, s1])
            print('********************************************')
            print()

# Display all results
print()
print('--------------------------------------------------------------------------------------------------------------')
print('Number of orders: |O|', O_NUMBER_OF_ORDERS,
      'Number of trucks: |S|', S_NUMBER_OF_TRUCKS,
      'Number of docks: |D|', D_NUMBER_OF_DOCKS,
      'Number of time slots: |T|', T_NUMBER_OF_TIME_SLOTS)
print('Number of cases: ', cases_index)
print('Number of solutions: ', optimal_obj_values_all_cases.__len__())
print('Indexes of cases: ', case_indexes)
print('Statuses: ', statuses)
print('Run times: ', runtimes)
print('Run times rounded: ', np.rint(runtimes))
print('Obj solutions values: ', optimal_obj_values_all_cases)
print('Total tardiness: ', sum(optimal_obj_values_all_cases))
print('Number of solutions ls values: ', optimal_ls_values_all_cases.__len__())
print('Solutions ls values: ', optimal_ls_values_all_cases)
print('--------------------------------------------------------------------------------------------------------------')
print()
