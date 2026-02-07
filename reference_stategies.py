import numpy as np

def standard_strategy(arrival, departure, energy_need, max_power=7):
    
    charging_schedule = np.zeros(48)
    time_slot_duration = 0.5  # hours
    remaining_energy = energy_need

    slotsRange = list(range(int(arrival)+1, 48)) + list(range(1, int(departure))) if arrival >= departure else list(range(int(arrival), int(departure)))
    
    # Charge at maximum power from arrival until energy need is fulfilled or departure
    for i in slotsRange:
        # Check if EV is connected (between arrival and departure)
        if remaining_energy > 0:
            # Charge at maximum power, or whatever is needed if less than max_power
            power_to_charge = min(max_power, remaining_energy / time_slot_duration)
            charging_schedule[i] = power_to_charge
            remaining_energy -= power_to_charge * time_slot_duration
        
        if remaining_energy <= 0:
            break
    
    return charging_schedule


def offpeak_strategy(arrival, departure, energy_need, max_power=7):

    charging_schedule = np.zeros(48)
    time_slot_duration = 0.5  # hours
    remaining_energy = energy_need

    startCharging = max(44, int(arrival)+1)

    slotsRange = list(range(startCharging, 48)) + list(range(1, int(departure))) if arrival >= departure else list(range(int(arrival), int(departure)))
    
    # Charge at maximum power from arrival until energy need is fulfilled or departure
    for i in slotsRange:
        # Check if EV is connected (between arrival and departure)
        if remaining_energy > 0:
            # Charge at maximum power, or whatever is needed if less than max_power
            power_to_charge = min(max_power, remaining_energy / time_slot_duration)
            charging_schedule[i] = power_to_charge
            remaining_energy -= power_to_charge * time_slot_duration
        
        if remaining_energy <= 0:
            break
    
    return charging_schedule



def standard_strategy_collective(data, max_power=7):

    arrival = data['arrival']
    departure = data['departure']
    energy_need = data['energy_need']

    charging_schedule = np.zeros((len(arrival), 48))
    
    for j in range(len(arrival)):
        charging_schedule[j] = standard_strategy(arrival[j], departure[j], energy_need[j], max_power)
    
    return charging_schedule

def offpeak_strategy_collective(data, max_power=7):

    arrival = data['arrival']
    departure = data['departure']
    energy_need = data['energy_need']

    charging_schedule = np.zeros((len(arrival), 48))
    
    for j in range(len(arrival)):
        charging_schedule[j] = offpeak_strategy(arrival[j], departure[j], energy_need[j], max_power)
    
    return charging_schedule

if __name__ == "__main__":
    # Example usage
    arrival = 36
    departure = 14
    energy_need = 80
    max_power = 7
    
    schedule = standard_strategy(arrival, departure, energy_need, max_power)
    print("Charging schedule:", schedule)
    print("Total energy charged (kWh):", schedule.sum() * 0.5)