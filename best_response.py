import numpy as np
from single_EV_problem import single_EV_water_filling, single_EV_linprogram, single_EV_MILP
import pandas as pd
import matplotlib.pyplot as plt
import time
from C02_emissions import calculate_emissions

def bestResponseDynamics(initialProfile, idList, date, eta, K, single_EV_method = 'MILP') :

    '''
    initialProfile : matrice de taille (nombre de VE) x (nombre de créneaux temporels)
    idList : liste des identifiants des VE, de taille nombre de VE
    eta : paramètre du critère d'arrêt
    K : nombre maximum d'itérations
    '''
    print("Starting best response dynamics with method: ", single_EV_method)
    t0 = time.time()
# Initialisation
    k=0
    profile = initialProfile.copy()
    converged = False
    J = len(idList) # nombre de VE

# Récupération de la charge fixe
    month = date.month
    year = str(date.year)
    season = 'summer' if month==6 else 'winter'
    df = pd.read_csv('data/eCO2mix_RTE_Annuel-Definitif_' + year + '_' + season + '.csv', sep=';') # vecteur de taille timeSlots, se déduit de la date 
    df["date"] = pd.to_datetime(df["date"])
    dailyDf = df[df["date"].dt.date == pd.to_datetime(date).date()]
    fixedLoad = dailyDf["consumption"].values #liste de la charge fixe à chaque créneau temporel, de taille NtimeSlots

# Récupération des heures d'arrivée et de départ des VE
    df = pd.read_csv('data/ev_scenarios.csv', sep=';')
    df['day'] = pd.to_datetime(df['day'], format='%d/%m/%Y')
    df_selection = df[df['day'].dt.date == date]

    arrival = np.zeros(J)
    departure = np.zeros(J)
    energy_need = np.zeros(J)

    for j in range(J):
        thisType = df_selection[df_selection['ev_id'] == idList[j]]
        
        arrival[j] = int(thisType['time_slot_arr'].values[0])
        departure[j] = int(thisType['time_slot_dep'].values[0])
        energy_need[j] = float(thisType['energy_need (kWh)'].values[0])


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
    J = 50 # nombre de VE
    timeSlots = 48 # nombre de créneaux temporels
    initialProfile = np.random.rand(J, timeSlots) # profil initial aléatoire
    idList = np.random.randint(1, 10, size=J)  # liste des identifiants des VE
    from datetime import datetime
    date = datetime(2019, 1, 1).date() # date choisie
    eta = 700
    K = 100
    PLOT_RESULTS = False

    profile = bestResponseDynamics(initialProfile, idList, date, eta, K, single_EV_method='MILP')
    
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