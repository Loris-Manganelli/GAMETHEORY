import numpy as np
import matplotlib.pyplot as plt
from C02_emissions import calculate_emissions
from best_response import bestResponseDynamics
from data_extractor import data_extractor
from reference_stategies import standard_strategy_collective, offpeak_strategy_collective
from datetime import datetime

# Parameters
num_ves_list = list(range(5, 40, 1)) 
powerMultiplicator = 750
date = datetime(2019, 1, 1).date()
standard_emissions_list = []
offpeak_emissions_list = []
best_response_emissions_list = []

for nVES in num_ves_list:

    idList = np.random.randint(1, 10, size=nVES)  # Randomly select VE IDs
    data = data_extractor(date, idList)
    data['energy_need'] = data['energy_need'] * powerMultiplicator

    # Run Best Response Dynamics
    initialProfile = np.random.rand(nVES, 48)  # Random initial profile
    best_response_profile = bestResponseDynamics(initialProfile, data, eta=1e-2, K=100, single_EV_method='WF', powerMultiplicator=powerMultiplicator)
    best_response_emissions = sum(calculate_emissions(data['fixedLoad'][i] + best_response_profile[:,i].sum()) for i in range(48))
    best_response_emissions_list.append(best_response_emissions)
    
    # Run Standard Strategy
    standard_profile = standard_strategy_collective(data, max_power=7*powerMultiplicator)
    standard_emissions = sum(calculate_emissions(data['fixedLoad'][i] + standard_profile[:,i].sum()) for i in range(48))
    standard_emissions_list.append(standard_emissions)

    # Run OffPeak Strategy
    offpeak_profile = offpeak_strategy_collective(data, max_power=7*powerMultiplicator)
    offpeak_emissions = sum(calculate_emissions(data['fixedLoad'][i] + offpeak_profile[:,i].sum()) for i in range(48))
    offpeak_emissions_list.append(offpeak_emissions)

plt.plot(num_ves_list, standard_emissions_list, label='Standard Strategy', marker='o')
plt.plot(num_ves_list, offpeak_emissions_list, label='OffPeak Strategy', marker='s')
plt.plot(num_ves_list, best_response_emissions_list, label='Best Response Strategy', marker='^')
plt.xlabel('Number of Electric Vehicles')
plt.ylabel('Total CO2 Emissions due to EVs (TCO2)')
plt.title('CO2 Emissions Comparison of Charging Strategies')
plt.legend()
plt.grid(True)
plt.show()