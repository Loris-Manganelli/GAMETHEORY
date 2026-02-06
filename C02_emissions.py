import numpy as np
import matplotlib.pyplot as plt

costs = dict(coal=86, gas=70, solar=0, wind=0, nuclear=30, hydro=0, fuel=162, bioen=0) #€/MWh
CO2_em = dict(coal=986, gas=429, solar=0.1, wind=0.2, nuclear=0.3, hydro=0.4, fuel=777, bioen=494) #gCO2/kWh
max_prod = dict(coal=1818, gas=12752, solar=2600, wind=6000, nuclear=61370, hydro=25504, fuel=3000, bioen=2234) #MW (adjusted for capacity)
ordered_list = ['solar', 'wind', 'hydro', 'bioen', 'nuclear', 'gas', 'coal', 'fuel']

def solve_UC(load, ordered_list, max_prod):
    production = dict((tech, 0) for tech in ordered_list)
    remaining_load = load
    for tech in ordered_list:
        if remaining_load <= 0:
            break
        prod = min(max_prod[tech], remaining_load)
        production[tech] = prod
        remaining_load -= prod
    return production

def calculate_emissions(load):  # note : here the load corresponds to total load, including all flexible and non flexible
    #data
    #costs = dict(coal=86, gas=70, solar=0, wind=0, nuclear=30, hydro=0, fuel=162, bioen=0) #€/MWh
    CO2_em = dict(coal=986, gas=429, solar=0.1, wind=0.2, nuclear=0.3, hydro=0.4, fuel=777, bioen=494) #gCO2/kWh
    max_prod = dict(coal=1818, gas=12752, solar=2600, wind=6000, nuclear=61370, hydro=25504, fuel=3000, bioen=2234) #MW (adjusted for capacity)
    ordered_list = ['solar', 'wind', 'hydro', 'bioen', 'nuclear', 'gas', 'coal', 'fuel']

    #solve simplified UC
    production = dict((tech, 0) for tech in ordered_list)
    remaining_load = load
    for tech in ordered_list:
        if remaining_load <= 0:
            break
        prod = min(max_prod[tech], remaining_load)
        production[tech] = prod
        remaining_load -= prod

    #calculate emissions
    total_emissions = 0
    for tech, prod in production.items():
        total_emissions += prod * CO2_em[tech]  # gCO2
    return total_emissions / 1000000  # Convert to TCO2

def grad_emissions(load):
    CO2_em = dict(coal=986, gas=429, solar=0.1, wind=0.2, nuclear=0.3, hydro=0.4, fuel=777, bioen=494) #gCO2/kWh
    max_prod = dict(coal=1818, gas=12752, solar=2600, wind=6000, nuclear=61370, hydro=25504, fuel=3000, bioen=2234) #MW (adjusted for capacity)
    ordered_list = ['solar', 'wind', 'hydro', 'bioen', 'nuclear', 'gas', 'coal', 'fuel']

    #solve simplified UC to obtain last tech used
    remaining_load = load
    last_tech = None
    for tech in ordered_list:
        if remaining_load <= 0:
            break
        last_tech = tech
        prod = min(max_prod[tech], remaining_load)
        remaining_load -= prod
    return CO2_em[last_tech]  # gCO2/kWh

if __name__ == "__main__":
    max_total_prod = sum(max_prod.values())
    loads = range(10000, max_total_prod, 100)  # Example loads from 10,000 MW to 80,000 MW
    emissions = np.array([calculate_emissions(load) for load in loads])
    plt.plot(loads, emissions)
    plt.xlabel('Load (MW)')
    plt.ylabel('CO2 Emissions (TCO2)')  
    plt.show()