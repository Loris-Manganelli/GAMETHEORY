import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import linprog
import scipy.optimize
from C02_emissions import getCO2_em, grad_emissions, calculate_emissions, get_max_prod
import time

def single_EV_water_filling(load, arrival, departure, energy_need, max_power = 7, power_increment = 0.2) :
    time_slot_duration = 0.5 #hours

    charging_schedule = np.zeros(48)
    while charging_schedule.sum() < energy_need/time_slot_duration:  #while the total charging is not sufficient
        eligible_slots = np.where((charging_schedule < max_power) & ((np.arange(48) >= arrival) | (np.arange(48) < departure)))[0] #eligible slots for charging : betxeen arrival and departure, and max power not reached
        slots = np.array(np.argmin(load[eligible_slots] + charging_schedule[eligible_slots]))
        charging_schedule[eligible_slots[slots]] += power_increment #add some charging to all optimal slots
    return charging_schedule #array of size 48 containing charging power at each time slot

def single_EV_linprogram(load, arrival, departure, energy_need, max_power = 7) :
    bounds = [(0, max_power) if (i >= arrival or i < departure) else (0, 0) for i in range(48)] #bounds for each time slot
    c = [grad_emissions(load[i]) for i in range(48)] #cost function coefficients
    A_eq = [[1 if (i >= arrival or i < departure) else 0 for i in range(48)]] #equality constraint coefficients
    b_eq = [energy_need / 0.5] #total energy needed in k
    return linprog(c, A_eq=A_eq, b_eq=b_eq, bounds=bounds, method='highs')

#prepare data for MILP formulation
costs = dict(coal=86, gas=70, solar=0, wind=0, nuclear=30, hydro=0, fuel=162, bioen=0) #€/MWh
CO2_em = getCO2_em() #gCO2/kWh
max_prod = get_max_prod()
ordered_list = ['solar', 'wind', 'hydro', 'bioen', 'nuclear', 'gas', 'coal', 'fuel']

#cumulative poduction capacity of the i first technologies (merit order)
Pis = np.array([np.array([max_prod[tech] for tech in ordered_list[:i]]).sum() for i in range(len(ordered_list)+1)])

def single_EV_MILP(load, arrival, departure, energy_need, max_power = 7):
    L = load[[i for i in range(48) if (i >= arrival or i < departure)]] #load at the eligible time slots
    J = len(L) #number of eligible time slots

    #seek the last technology activated by the current load for each time slot
    i0s = np.zeros(J)
    for k in range(J) :
        i0 = 0
        while i0 < len(Pis) and Pis[i0] < L[k] :
            i0 += 1
        i0s[k] = i0 
    
    #matrix of the reduced cumulative powers used for each time slot. size (J, I)
    usedPis = [[Pis[i] - L[k] if i >= i0s[k] else 0 for i in range(len(Pis))] for k in range(J)] 
    I = len(Pis) #number of steps in the merit order curve


    #equality constraints
    equality_constraints_block = np.block([[np.zeros(I), np.ones(I)],[np.ones(I), np.zeros(I)]]) #block of the equality constraints
    equality_constraints = np.block([[equality_constraints_block if j == k else np.zeros((2,2*I)) for j in range(J)] for k in range(J)]) #equality constraints for all time slots
    equality_constraints = np.block([[equality_constraints], [usedPis[i//(2*I)][i%(2*I) - I] if (i%(2*I) >= I) else 0 for i in range(2*I*J)]]) #block of all equality constraints (add constraint for total energy need)
    b_eq = np.ones(2*J + 1) #right-hand side of the equality constraints
    b_eq[-1] = energy_need / 0.5 #total energy need in kWh
    equ = scipy.optimize.LinearConstraint(equality_constraints, b_eq, b_eq)


    #inequality constraints
    #inequalities Yij <= lambdaij + lambda(i-1)j. size (I*J, 2*I*J) :
    ineq_constraints = np.zeros((I*J, 2*I*J)) #block of the inequality constraints
    for j in range(J):
        for i in range(I) :
            ineq_constraints[j*I + i][i + 2*I*j] = 1  #for Yij
            if i > 0 : #if i = 0, Yij = 0 in all cases
                ineq_constraints[j*I + i][I + i + 2*I*j] = -1 #for lambdaij
                ineq_constraints[j*I + i][I + i-1 + 2*I*j] = -1 #for lambdai-1j
    #inequalities limiting max power transfered. size (J, 2*I*J)
    ineq_constraints_power = np.block([[np.concatenate([np.zeros(I), usedPis[j]]) if j == k else np.zeros(2*I) for j in range(J)] for k in range(J)]) 
    ineq_constraints_total = np.block([[ineq_constraints], [ineq_constraints_power]]) #block of all inequality constraints
    b_ineq = np.concatenate([np.zeros(I*J), max_power*np.ones(J)]) #right-hand side of the inequality constraints.
    ineq = scipy.optimize.LinearConstraint(ineq_constraints_total, -np.inf, b_ineq)
    

    #cost, and assemble problem. bounds not specified : by default everything is >=0
    c = [calculate_emissions(usedPis[i//(2*I)][i%(2*I) - I] + L[i//(2*I)]) if (i%(2*I) >= I) else 0 for i in range(2*I*J) ]
    
    integrality = [1 if (i%(2*I) < I) else 0 for i in range(2*I*J)] #the (Yij) are binary, the others are continuous
    constraints = [equ, ineq]
    result = scipy.optimize.milp(c, constraints=constraints, integrality=integrality)
    
    #recompose the schedule
    schedule = np.zeros(J)
    if not result.success:
        print("Optimization failed:", result.message)
    else :
        for j in range(J) :
            schedule[j] = np.dot(result.x[j*2*I + I:(j+1)*2*I], usedPis[j]) #sum of lambdaij * Pi for i in range(I)
    #recompose real schedule by adding unplugged time slots
    final_schedule = np.zeros(48)
    final_schedule[[i for i in range(48) if (i >= arrival or i < departure)]] = schedule
    return final_schedule

if __name__ == "__main__":
    #Example of usage
    load = np.random.rand(48)*110000 #random load profile for testing, including peak hours
    arrival = 36
    departure = 14
    energy_need = 80000
    max_power = 10000


    
    t0 = time.time()
    charging_schedule_milp = single_EV_MILP(load, arrival, departure, energy_need, max_power)
    t1 = time.time()
    print("MILP computation time: ", t1 - t0, " seconds")
    charging_schedule_lp = single_EV_linprogram(load, arrival, departure, energy_need, max_power)
    t2 = time.time()
    print("LP computation time: ", t2 - t1, " seconds")
    charging_schedule_WF = single_EV_water_filling(load, arrival, departure, energy_need, max_power, max_power/100)
    t3 = time.time()
    print("Water-filling computation time: ", t3 - t2, " seconds")  
    
    #calcul des performances en terme de CO2 
    em_WF = 0
    em_LP = 0
    em_MILP = 0
    em_load = 0
    for i in range(48):
        em_WF += calculate_emissions(load[i] + charging_schedule_WF[i])
        em_LP += calculate_emissions(load[i] + charging_schedule_lp.x[i])
        em_MILP += calculate_emissions(load[i] + charging_schedule_milp[i])
        em_load += calculate_emissions(load[i])
    print("EV Emissions with Water-filling (TCO2): ", em_WF - em_load)
    print("EV Emissions with LP (TCO2): ", em_LP - em_load)  
    print("EV Emissions with MILP (TCO2): ", em_MILP - em_load)
    print("Total Emissions without EV (TCO2): ", em_load)

    #plotting
    plt.plot(load, label='Base Load (kW)')
    plt.plot(load+charging_schedule_lp.x, label='EV Charging (LP)')
    plt.plot(load+charging_schedule_milp, label='EV Charging (MILP)')
    plt.plot(load+charging_schedule_WF, label='EV Charging (WF)')
    plt.axvline(x=arrival, linestyle='--', label='Arrival Time', color='green')
    plt.axvline(x=departure, linestyle='--', label='Departure Time', color='red')
    plt.xlabel('Time Slot (30 min each)')   
    plt.ylabel('Power (kW)')
    plt.legend()
    plt.show()
