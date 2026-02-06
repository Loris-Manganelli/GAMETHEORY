import numpy as np

def standard_strategy(data, max_power=7):
    
    arrival = data['arrival']
    departure = data['departure']
    energy_need = data['energy_need']

    charging_schedule = np.zeros(48)
    time_slot_duration = 0.5  # hours
    remaining_energy = energy_need
    
    # Charge at maximum power from arrival until energy need is fulfilled or departure
    for i in range(48):
        # Check if EV is connected (between arrival and departure)
        if (i >= arrival or i < departure) and remaining_energy > 0:
            # Charge at maximum power, or whatever is needed if less than max_power
            power_to_charge = min(max_power, remaining_energy / time_slot_duration)
            charging_schedule[i] = power_to_charge
            remaining_energy -= power_to_charge * time_slot_duration
        
        if remaining_energy <= 0:
            break
    
    return charging_schedule


def offpeak_strategy(data, max_power=7):

    arrival = data['arrival']
    departure = data['departure']
    energy_need = data['energy_need']

    charging_schedule = np.zeros(48)
    time_slot_duration = 0.5  # hours
    remaining_energy = energy_need
    offpeak_start = 40  # 10 PM (20:00 in 24h format = slot 40 in 48-slot day)
    
    # Charge at maximum power during off-peak hours only
    for i in range(48):
        # Check if EV is connected and in off-peak hours
        if (i >= arrival or i < departure) and i >= offpeak_start and remaining_energy > 0:
            power_to_charge = min(max_power, remaining_energy / time_slot_duration)
            charging_schedule[i] = power_to_charge
            remaining_energy -= power_to_charge * time_slot_duration
        
        if remaining_energy <= 0:
            break
    
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