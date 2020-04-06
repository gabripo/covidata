# -*- coding: utf-8 -*-
"""
Fitting of data with infection models

Data is downloaded:
    - By scraping the page https://data.humdata.org/dataset/novel-coronavirus-2019-ncov-cases for infected, recovered and dead people
    - By direct downloading the file https://population.un.org/wpp/Download/Files/1_Indicators%20(Standard)/CSV_FILES/WPP2019_TotalPopulationBySex.csv for the number of people in populations

An alternative way to load data offline is possible:
    - By providing full paths of csv files as an argument of HDXdata()
    - By placing the file WPP2019_TotalPopulationBySex.csv in the working directory

Data is managed with the module data_manager, then analyzed with the module lib_sir_model
"""

import os
os.chdir( os.getcwd() )
import data_manager as dtmg
import lib_sir_model as sir

# Loading data
data = dtmg.HDXdata()
popData = dtmg.POPdata()

# Interesting countries (It is possible to add others to the list)
ita = 'Italy'
deu = 'Germany'
usa = 'US'
eng = 'United Kingdom'
esp = 'Spain'
ned = 'Netherlands'
fra = 'France'

# Ordering countries' data
data.add_countriesNames(ita, deu, usa, eng, esp, ned, fra)
data.load_parse_all_countries()

# Getting data
pops = popData.get_pop_countries(ita, deu, usa, eng, esp, ned, fra)
confirmed = data.get_countries_confirmed()  # Corresponding to Infected
#recovered = data.get_countries_recovered()  # Corresponding to Recovered

# Fitting models
IC = (0, 0)
setSIRmodels = sir.SIRmodelFITset(confirmed, pops, IC)
setSIRmodels.opt_curve_fit()

# Plotting results for N days
dpi = 600
N = 20
#setSIRmodels.plot_compare_reference(dpi)
setSIRmodels.plot_prediction(dpi, N)
#setSIRmodels.plotres(dpi)
setSIRmodels.plotres_predicted(dpi, N)