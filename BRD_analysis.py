import numpy as np
from single_EV_problem import single_EV_water_filling, single_EV_linprogram, single_EV_MILP
import pandas as pd
import matplotlib.pyplot as plt
from C02_emissions import calculate_schedule_emissions
from data_extractor import data_extractor
from best_response import bestResponseDynamics

realVehicles = 1e7

aggregate_sizes = [1, 10, 100, 1000] #en millier de voitures

def get_performance(date, single_EV_method, aggregate_size) :
    J = aggregate_size # nombre de VE
    timeSlots = 48 # nombre de créneaux temporels
    initialProfile = np.random.rand(J, timeSlots) # profil initial aléatoire
    idList = np.random.randint(1, 10, size=J)  # liste des identifiants des VE
    eta = 1e-2
    K = 100

    powerMultiplicator = realVehicles/(aggregate_size*1000) # multiplicateur pour les besoins énergétiques des VE

    data = data_extractor(date, idList)
    data['energy_need'] = data['energy_need'] * powerMultiplicator

    profile = bestResponseDynamics(initialProfile, data, eta, K, single_EV_method=single_EV_method, powerMultiplicator=powerMultiplicator)
    total_emissions = calculate_schedule_emissions(data['fixedLoad'] + profile.sum(axis=0)) - calculate_schedule_emissions(data['fixedLoad']) # émissions totales avec les VE - émissions sans les VE
    return total_emissions, data['fixedLoad'] + profile.sum(axis=0), data['fixedLoad']


if __name__ == "__main__":
    from datetime import datetime
    date = datetime(2019, 6, 5).date() # date choisie
    emissions = np.zeros((len(aggregate_sizes), 3)) # to store emissions for each aggregate size and method
    methods = ['MILP', 'LP', 'WF']
    for i, method in enumerate(methods) :
        profiles = []
        for j, agg in enumerate(aggregate_sizes) :
            if agg > 100 and method == 'MILP' : # éviter de faire tourner le MILP pour les plus grandes tailles d'agrégats, pour des raisons de temps de calcul
                emissions[j,i] = np.nan
            else :
                emissions[j,i], profile , load= get_performance(date, method, agg)
                profiles.append(profile)
                plt.plot(load, label='Base Load (kW)')
        plt.plot(profiles[-1], label=method)
plt.legend()

plt.figure(figsize=(10, 6))
for i, method in enumerate(methods):
    plt.plot(aggregate_sizes, emissions[:, i], marker='o', label=method)

plt.xlabel('Aggregate Size (x1000 vehicles)')
plt.ylabel('Total Emissions (TCO2) above baseline')
plt.title('Emissions vs Aggregate Size by Method')
plt.legend()
plt.xscale('log')
plt.grid(True, alpha=0.3)
plt.show()