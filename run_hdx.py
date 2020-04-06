# -*- coding: utf-8 -*-
"""
Test of execution for HDX loader library
"""

import os
#import glob
os.chdir( os.getcwd() )

import data_manager as dtmg

#csvPaths = [os.getcwd() + "\\" + s for s in glob.glob('*.csv')]
csvPaths = []

data = dtmg.HDXdata(csvPaths)
data.load_country('Italy')
data.load_country('Germany')

itaData = dtmg.ParsedDataCountry( data.get_countryData("Italy") )
gerData = dtmg.ParsedDataCountry( data.get_countryData("Germany") )

itaData.plot_values(600)

popData = dtmg.POPdata()

itaPop = popData.get_pop_country("Italy")
gerPop = popData.get_pop_country("Germany")