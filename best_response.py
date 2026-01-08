import numpy as np
from single_EV_problem import single_EV_water_filling
import pandas as pd
import matplotlib.pyplot as plt

def bestResponseDynamics(initialProfile, idList, date, eta, K):

    '''
    initialProfile : matrice de taille (nombre de VE) x (nombre de créneaux temporels)
    idList : liste des identifiants des VE, de taille nombre de VE
    eta : paramètre du critère d'arrêt
    K : nombre maximum d'itérations
    '''

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
    fixedLoad = dailyDf["consumption"].values

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
            load = fixedLoad + newProfile.sum(axis=0) - newProfile[j,:]
            newProfile[j,:] = single_EV_water_filling(load, arrival[j], departure[j], energy_need[j])

        totalVariation = ((newProfile - profile)**2).sum()
        if totalVariation < eta:
            converged = True
        profile = newProfile

        print("Iteration {}: total variation = {}".format(k, totalVariation))

    print("Converged in {} iterations".format(k))
    print("Final charging profiles (kW) at each time slot for each EV:")
    print(profile.shape)
    return profile

if __name__ == "__main__":
    # Exemple d'utilisation
    np.random.seed(0)
    J = 5 # nombre de VE
    timeSlots = 48 # nombre de créneaux temporels
    initialProfile = np.random.rand(J, timeSlots)*3 # profil initial aléatoire
    idList = [1, 1, 3, 5, 10]
    from datetime import datetime
    date = datetime(2019, 1, 1).date() # date choisie
    eta = 1e-3
    K = 100

    profile = bestResponseDynamics(initialProfile, idList, date, eta, K)

    fig, axes = plt.subplots(5, 1, figsize=(10, 12), sharex=True)  # sharex si tu veux le même axe x

    for i in range(J):
        axes[i].plot(profile[i])
        axes[i].set_title(f'Véhicule n°{i+1}')
        axes[i].grid(True)

    plt.xlabel('Time slots')
    plt.ylabel('Charging Power (kW)')
    plt.tight_layout()
    plt.savefig('files/best_response_dynamics_ev_charging.png')