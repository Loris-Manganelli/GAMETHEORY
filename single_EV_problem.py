import numpy as np

def single_EV_water_filling(load, day, month, ev_id) :
    #data = np.loadtxt('data/ev_scenarios.csv', delimiter = ';', skiprows = 1)
    #print(data)
    arrival = 36 #time slot (= 18h)
    departure = 14 #time slot (= 7h)
    energy_need = 8 #kWh
    max_power = 7 #kW
    power_increment = 0.2 #kW
    time_slot_duration = 0.5 #hours

    charging_schedule = np.zeros(48)
    while charging_schedule.sum() < energy_need/time_slot_duration:  #while the total charging is not sufficient
        eligible_slots = np.where((charging_schedule < max_power)&np.arange(48) >= arrival & np.arange(48) < departure) #eligible slots for charging : betxeen arrival and departure, and max power not reached
        slots = np.argmin(load[eligible_slots] + charging_schedule[eligible_slots])
        for s in slots :
            charging_schedule[s] += power_increment #add some charging to all optimal slots
    return charging_schedule #array of size 48 containing charging power at each time slot
