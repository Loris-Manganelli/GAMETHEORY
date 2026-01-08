import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import linprog
from C02_emissions import grad_emissions

def single_EV_water_filling(load, arrival, departure, energy_need) :
    max_power = 7 #kW
    power_increment = 0.2 #kW
    time_slot_duration = 0.5 #hours

    charging_schedule = np.zeros(48)
    while charging_schedule.sum() < energy_need/time_slot_duration:  #while the total charging is not sufficient
        eligible_slots = np.where((charging_schedule < max_power) & ((np.arange(48) >= arrival) | (np.arange(48) < departure)))[0] #eligible slots for charging : betxeen arrival and departure, and max power not reached
        slots = np.array(np.argmin(load[eligible_slots] + charging_schedule[eligible_slots]))
        charging_schedule[eligible_slots[slots]] += power_increment #add some charging to all optimal slots
    return charging_schedule #array of size 48 containing charging power at each time slot

def single_EV_linprogram(load, arrival, departure, energy_need):
    bounds = [(0, 7) if (i >= arrival or i < departure) else (0, 0) for i in range(48)] #bounds for each time slot
    c = [grad_emissions(load) for _ in range(48)] #cost function coefficients
    A_eq = np.diag([1 if (i >= arrival or i < departure) else 0 for i in range(48)]) #equality constraint coefficients
    b_eq = [energy_need / 0.5] #total energy needed in k
    return linprog(c, A_eq=A_eq, b_eq=b_eq, bounds=bounds, method='highs')

if __name__ == "__main__":
    #Example of usage
    load = np.random.rand(48)*50 #random load profile for testing
    arrival = 36
    departure = 14
    energy_need = 20
    charging_schedule = single_EV_water_filling(load, arrival, departure, energy_need)
    print("Charging schedule (kW) at each time slot:")
    print(charging_schedule)
    plt.plot(load, label='Base Load (kW)')
    plt.plot(load + charging_schedule, label='Load with EV Charging (kW)')
    plt.xlabel('Time Slot (30 min each)')   
    plt.ylabel('Power (kW)')
    plt.legend()
    plt.show()