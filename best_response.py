import numpy as np
from single_EV_problem import single_EV_water_filling, single_EV_linprogram, single_EV_MILP
import pandas as pd
import matplotlib.pyplot as plt
import time
from C02_emissions import calculate_emissions
from data_extractor import data_extractor

def bestResponseDynamics(initialProfile, data, eta, K, single_EV_method = 'WF', powerMultiplicator = 1):

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
                newProfile[j,:] = single_EV_MILP(load, arrival[j], departure[j], energy_need[j], max_power=7*powerMultiplicator)
                
                #stability check
                em = 0
                for i in range(48) :
                    em += calculate_emissions(load[i] + newProfile[j,i]) - calculate_emissions(load[i] + profile[j,i]) # émissions totales avec nouveau profil vs ancien profil
                if abs(em) < 0.001 : # tolérance pour éviter les oscillations dues à des différences d'émissions très faibles
                    newProfile[j,:] = profile[j,:] # on garde l'ancien profil si la différence d'émissions est négligeable
            elif single_EV_method == 'LP':
                newProfile[j,:] = single_EV_linprogram(load, arrival[j], departure[j], energy_need[j], max_power=7*powerMultiplicator).x
                
                #stability check
                em = 0
                for i in range(48) :
                    em += calculate_emissions(load[i] + newProfile[j,i]) - calculate_emissions(load[i] + profile[j,i]) # émissions totales avec nouveau profil vs ancien profil
                if abs(em) < 0.001 : # tolérance pour éviter les oscillations dues à des différences d'émissions très faibles
                    newProfile[j,:] = profile[j,:] # on garde l'ancien profil si la différence d'émissions est négligeable
            elif single_EV_method == 'WF':
                newProfile[j,:] = single_EV_water_filling(load, arrival[j], departure[j], energy_need[j], max_power=7*powerMultiplicator, power_increment=0.2*powerMultiplicator)
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
    J = 10 # nombre de VE
    timeSlots = 48 # nombre de créneaux temporels
    initialProfile = np.random.rand(J, timeSlots) # profil initial aléatoire
    idList = np.random.randint(1, 10, size=J)  # liste des identifiants des VE
    from datetime import datetime
    date = datetime(2019, 1, 1).date() # date choisie
    eta = 1e-2
    K = 100
    PLOT_RESULTS = True

    powerMultiplicator = 750 # multiplicateur pour les besoins énergétiques des VE, à ajuster pour tester différentes situations (ex: 10 pour simuler des camions électriques)

    data = data_extractor(date, idList)
    data['energy_need'] = data['energy_need'] * powerMultiplicator

    profile = bestResponseDynamics(initialProfile, data, eta, K, single_EV_method='WF', powerMultiplicator=powerMultiplicator)
    
    if PLOT_RESULTS :
        total_load = data['fixedLoad'] + profile.sum(axis=0)
        initial_load = data['fixedLoad']
        plt.plot(total_load, label='Total Load with EVs')
        plt.plot(initial_load, label='Initial Load without EVs')
        plt.xlabel('Time Slot (30 min each)')
        plt.ylabel('Power (kW)')
        plt.title('Total Load Profile with Best Response Dynamics (Method: {})'.format('WF'))
        plt.legend()
        plt.grid(True)
        plt.show()
        # fig, axes = plt.subplots(J, 1, figsize=(10, 12), sharex=True) 

        # for i in range(J):
        #     axes[i].plot(profile[i])
        #     axes[i].set_title(f'Véhicule n°{i+1}, ID {idList[i]}')
        #     axes[i].grid(True)

        # plt.xlabel('Time slots')
        # plt.ylabel('Charging Power (kW)')
        # plt.tight_layout()
        # # plt.savefig(f'files/best_response_dynamics_ev_charging_{J}_{date}.png')
        # plt.show()