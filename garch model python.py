# -*- coding: utf-8 -*-
"""
Created on Tue Sep  6 12:50:18 2022

@author: x1diagar
"""

import requests
import datetime
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt  # from matplotlib import pyplot as plt
import scipy.optimize as spop
import seaborn
import math
from arch import arch_model
from scipy.stats import binom

plt.get_backend()

# INPUTS
Fecha_deseada = "2022-08-02"

variables = ["SOJ.ROS/MAY22", "SOJ.ROS/JUL22", "SOJ.ROS/NOV22", "SOJ.ROS/MAY23", "SOJ.ROS/JUL23", "MAI.ROS/JUL22", \
             "MAI.ROS/SEP22", "MAI.ROS/DIC22", "MAI.ROS/ABR23", "MAI.ROS/JUL23", "TRI.ROS/JUL22", "TRI.ROS/DIC22", \
             "TRI.ROS/ENE23", "SOJ.MAY/ABR23", "SOY.CME/ABR22", "SOY.CME/OCT22", "SOY.CME/JUN22", "MAI.ROS/AGO23", \
             "MAI.ROS/SEP23", "SOJ.ROS/ENE23", "SOJ.ROS/NOV23"]

# variables = ["SOJ.ROS/MAY22"]
fechaHistoricoDesde = "2015-05-21"

# CODIGO
retornos = []
retornos_log = []

cuerpo = {"instrumentos": []}
for i in range(len(variables)):
    cuerpo["instrumentos"].append(
        {
            "codigoInstrumento": variables[i],
            "codigoMercado": "XMTB",
            "fechaHistoricoDesde": fechaHistoricoDesde
        }
    )

# api_key = '5bc1e8bc228748f8b965a3c0d9679ccc'
api_key = SOMENTHING

headers = {'Ocp-Apim-Subscription-Key': '{key}'.format(key=api_key)}

# responses_API = requests.post('https://apim-integraciones-prd-001.azure-api.net/mercados/cotizaciones',\
#                                  headers=headers,json=cuerpo).json()
responses_API = requests.post(algo, \
                              headers=headers, json=cuerpo).json()

count = 0
for i in range(len(responses_API["data"])):
    count += 1
# print("Count = ",count)

Precios_df = pd.DataFrame()
listita = []
for j in range(count):
    Precios = pd.DataFrame()
    lista = responses_API["data"][j]["historicos"][:]
    for i in range(len(lista)):
        Precios.loc[i, "fecha"] = lista[i]["fecha"]
        nombre = responses_API['data'][j]['codigoInstrumento']
        Precios.loc[i, f'Precio {nombre}'] = lista[i]["valor"]
    listita.append(nombre)
    retornos.append(f"Ret_{nombre}")
    retornos_log.append(f"RetLog_{nombre}")
    if Precios_df.empty:
        Precios_df = Precios
    else:
        Precios_df = Precios_df.merge(Precios, how='outer', on='fecha')

set_difference = set(variables).symmetric_difference(set(listita))
list_difference = list(set_difference)

print("Los elementos que no fueron devueltos en las request fueron: ", list_difference)

Precios_df["fecha"] = pd.to_datetime(Precios_df["fecha"])

results_df = Precios_df
results_df[retornos] = results_df[results_df.columns[1:]].pct_change(fill_method='ffill')
results_df[retornos_log] = np.log(1 + results_df[retornos])

returns = Precios_df["RetLog_SOJ.ROS/MAY22"] * 100
prices = Precios_df["Precio SOJ.ROS/MAY22"]
mean = np.average(returns[1:])
var = np.std(returns) ** 2
print("valor de mu y var", mean, var)

arch_model_1 = arch_model(returns[1:])  # este *100 lo puse porque me lo sugirió python al correr el programa
result_arch_model = arch_model_1.fit(update_freq=1)
result_arch_model.summary()

gama = 1 - 0.2709 - 0.6709
Lon_Vol = (0.0936 / gama)
print("The long-run average variance per day implied by the model is:", round(Lon_Vol, 5) * 100, "%.",
      "This corresponds to a volatility of", round(math.sqrt(Lon_Vol), 3) * 100, "% per day")

fig = result_arch_model.plot(annualize="D")