import numpy as np
from single_EV_problem import single_EV_water_filling, single_EV_linprogram, single_EV_MILP
import pandas as pd
import matplotlib.pyplot as plt
import time
from C02_emissions import calculate_emissions
from data_extractor import data_extractor

def bestResponseDynamics(initialProfile, data, eta, K, single_EV_method = 'WF') :

    '''
    initialProfile : matrice de taille (nombre de VE) x (nombre de créneaux temporels)
    eta : paramètre du critère d'arrêt
    K : nombre maximum d'itérations
    '''
    print("Starting best response dynamics with method: ", single_EV_method)
    t0 = time.time()
# Initialisation
    k=0
    profile = initialProfile.copy()
    converged = False
    J = initialProfile.shape[0] # nombre de VE
    fixedLoad = data['fixedLoad']
    arrival = data['arrival']
    departure = data['departure']
    energy_need = data['energy_need']

    while not converged and k<=K:
        k = k+1
        newProfile = profile.copy()
        for j in range(J):
            load = fixedLoad + newProfile.sum(axis=0) - newProfile[j,:] # calcul de la charge totale 
            if single_EV_method == 'MILP':
                newProfile[j,:] = single_EV_MILP(load, arrival[j], departure[j], energy_need[j])
            elif single_EV_method == 'LP':
                newProfile[j,:] = single_EV_linprogram(load, arrival[j], departure[j], energy_need[j]).x
            elif single_EV_method == 'WF':
                newProfile[j,:] = single_EV_water_filling(load, arrival[j], departure[j], energy_need[j])
            else :
                raise ValueError("Invalid method for single EV optimization. Choose 'MILP', 'LP' or 'WF'.")

        totalVariation = ((newProfile - profile)**2).sum()
        if totalVariation < eta:
            converged = True
        profile = newProfile

        print("Iteration {}: total variation = {}".format(k, totalVariation))

    print("Converged in {} iterations".format(k))
    t1 = time.time()
    print("Best response dynamics computation time: ", t1 - t0, " seconds")

    # calul des émissions dues aux VE
    total_emissions_EV = 0
    for i in range(48) :
        total_emissions_EV += calculate_emissions(fixedLoad[i] + profile[:,i].sum()) - calculate_emissions(fixedLoad[i]) # émissions totales avec les VE - émissions sans les VE
    print("Total emissions due to EVs with best response dynamics (TCO2): ", total_emissions_EV)

    return profile

if __name__ == "__main__":
    # Exemple d'utilisation
    np.random.seed(0)
    J = 5 # nombre de VE
    timeSlots = 48 # nombre de créneaux temporels
    initialProfile = np.random.rand(J, timeSlots) # profil initial aléatoire
    idList = np.random.randint(1, 10, size=J)  # liste des identifiants des VE
    from datetime import datetime
    date = datetime(2019, 1, 1).date() # date choisie
    eta = 1e-2
    K = 100
    PLOT_RESULTS = True

    data = data_extractor(date, idList)

    profile = bestResponseDynamics(initialProfile, data, eta, K, single_EV_method='WF')
    
    if PLOT_RESULTS :
        fig, axes = plt.subplots(J, 1, figsize=(10, 12), sharex=True) 

        for i in range(J):
            axes[i].plot(profile[i])
            axes[i].set_title(f'Véhicule n°{i+1}, ID {idList[i]}')
            axes[i].grid(True)

        plt.xlabel('Time slots')
        plt.ylabel('Charging Power (kW)')
        plt.tight_layout()
        # plt.savefig(f'files/best_response_dynamics_ev_charging_{J}_{date}.png')
        plt.show()