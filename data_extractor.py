import pandas as pd
import numpy as np
from datetime import datetime

def data_extractor(date, idList) :

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

    return dict(fixedLoad=fixedLoad, arrival=arrival, departure=departure, energy_need=energy_need)
    