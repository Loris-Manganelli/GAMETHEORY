import numpy as np
from single_EV_problem import single_EV_water_filling
import pandas as pd

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
    timeSlots = initialProfile.shape[1] # nombre de créneaux temporels

# Récupération de la charge fixe
    month = date.month
    year = str(date.year)
    season = 'summer' if month==6 else 'winter'
    df = pd.read_csv('data/eCO2mix_RTE_Annuel-Definitif_' + year + '_' + season + '.csv') # vecteur de taille timeSlots, se déduit de la date 
    df["date"] = pd.to_datetime(df["date"])
    dailyDf = df[df["date"].dt.date == pd.to_datetime(date).date()]
    fixedLoad = dailyDf["consumption"].values

    while not converged and k<=K:
        k = k+1
        for j in range(J):
            load = fixedLoad + profile.sum(axis=0) - profile[j,:]
            profile[j,:] = single_EV_water_filling(load, date, eta, idList[j])
