# -*- coding: utf-8 -*-
"""
Data Manager for epidemic data
"""

import os
import sys
import requests
import urllib.request
import re
import urllib.parse
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import datetime

class HDXdata(object):
    def __init__(self, csvPaths=[]):
        if not csvPaths == []:
            self.csvNames = [os.path.basename(f) for f in csvPaths]
            self.csvPaths = csvPaths
        else:    
            self.csvNames = []
            self.csvPaths = []
        self.countriesNames = []
        self.countriesData = {}
        self.countriesDataParsed = {}
        
    def set_countries(self, countriesNames):
        self.countriesNames = countriesNames
        
    def get_csvNames(self):
        return self.csvNames
    
    def get_csvPaths(self):
        return self.csvPaths
    
    def get_countriesNames(self):
        return self.countriesNames
    
    def get_countriesData(self):
        return self.countriesData
    
    def get_countryData(self, countryName):
        if not len(self.countriesData) == 0:
            return self.countriesData[countryName]
        
    def get_countryDataParsed(self, countryName):
        if not len(self.countriesDataParsed) == 0:
            return self.countriesDataParsed[countryName]
        
    def get_country_confirmed(self, country=''):
        return self.get_country_category(country, 'confirmed')
        
    def get_country_recovered(self, country=''):
        return self.get_country_category(country, 'recovered')
        
    def get_country_deaths(self, country=''):
        return self.get_country_category(country, 'deaths')
    
    def get_country_category(self, country='', category=''):
        if country == '' or not country in self.countriesDataParsed.keys():
            print("ERROR: No valid specified country '" + country + "' !")
        else:
            if not category in ['confirmed', 'deaths', 'recovered']:
                print("ERROR: Specified category '" + category + "' for country '" + country + "' is invalid!")
            return self.countriesDataParsed[country].allData[category].drop(columns=['Province/State', 'Country/Region', 'Lat', 'Long']).iloc[0]
    
    def get_countries_confirmed(self):
        return self.get_countries_category('confirmed')
        
    def get_countries_recovered(self):
        return self.get_countries_category('recovered')
        
    def get_countries_deaths(self):
        return self.get_countries_category('deaths')
    
    def get_countries_category(self, category=''):
        countries_df = {}
        for country in self.countriesNames:
            countries_df.update({country : self.get_country_category(country, category)})
        return countries_df
    
    def add_countriesNames(self, *countriesNames):
        if countriesNames=="":
            print('No countriesNames to add...')
            pass
        for idxCountry, country in enumerate(countriesNames):
            if country not in self.countriesNames:
                self.countriesNames.append(country)
                
    def replace_countryData(self, countryName, countryData):
        if self.countriesData == {} or countryName not in self.countriesData.keys():
            self.countriesData.update({countryName : countryData})
        else:
            print("WARNING: Country '" + countryName + "' is present in data and will be replaced")
            self.countriesData[countryName] = countryData
    
    def download(self):
        # Fetching data
        url = "https://data.humdata.org/dataset/novel-coronavirus-2019-ncov-cases"
        print("Loading webpage from " + repr(url) + " ...")
        response = requests.get(url)
        if not response.ok :
            print("ERROR: Impossible to fetch data from the URL! The script will abort ...")
            sys.exit()
        print('Data has been correctly loaded.\n')
        
        # Parsing website's content by regex
        self.csvNames = re.findall(r'<span class="ga-download-resource-title" style="display: none">(.*)</span>', response.text)[0:3]
        print('The following data-sets have been found:\n' + '\n'.join(map(str, self.csvNames)) + '\n')
        
        csvLinks = list(map(urllib.parse.unquote, re.findall('<a href="\S+(?<=url=)(.*)"(?=\sclass)', response.text)[0:3] ))
        fixLink = lambda x: re.sub(r'&amp;.*', "", x)
        csvLinks = list(map(fixLink, csvLinks))
        
        # Downloading files from extracted URLs - To the actual directory
        os.chdir( os.getcwd() )
        def downloadFile(url, filename='None'):
            if filename=='None':
                filename = url.split('/')[-1]
            print("Downloading file " + filename + " at URL " + url + " ...")
            urllib.request.urlretrieve(url, filename)
            if os.path.isfile(filename):
                print("File " + filename + " has been successfuly downloaded and saved in " + os.getcwd() + ".")
            else:
                print("WARNING: Impossible to download file " + filename + "!")
            print('\n')

        for idxFile in range(len(csvLinks)):
            downloadFile(csvLinks[idxFile], self.csvNames[idxFile])
        
        self.csvPaths = [os.getcwd() + '\\' + s for s in self.csvNames]
        
    def load_country(self, country=None):
        if self.csvPaths==[]:
            print("No available data. Downloading them...")
            self.download()
        if country==None:
            print("WARNING: No country to load has been specified, no data will be returned")
            pass
        country_df = {}
        for idxSrc, csvAct in enumerate(self.csvPaths):
            df = pd.read_csv(csvAct)
            if df['Country/Region'].isin([country]).any():
                country_df.update({self.csvNames[idxSrc] : df[df['Country/Region'] == country]})
                self.add_countriesNames(country)
            else:
                print("WARNING: No country named '" + country + "' could be found in dataset named " + self.csvNames[idxSrc] )
        self.replace_countryData(country, country_df)
        return country_df
    
    def load_all_countries(self):
        if len(self.countriesNames)==0:
            print("ERROR: No countriesNames are defined!")
            pass
        for country in self.countriesNames:
            print("Loading data for country '" + country + "' ...")
            self.countriesData.update({country : self.load_country(country)})
            
    def parse_country(self, country):
        return ParsedDataCountry( self.get_countryData(country) )
            
    def parse_all_countries(self):
        if len(self.countriesNames)==0:
            print("ERROR: No countriesNames are defined!")
            pass
        for country in self.countriesNames:
            print("Parsing data for country '" + country + "' ...")
            self.countriesDataParsed.update({country : self.parse_country(country)})
            
    def load_parse_all_countries(self):
        self.load_all_countries()
        self.parse_all_countries()
        
    def refresh(self):
        print("Refreshing available data ...")
        self.download()
        self.load_parse_all_countries()

class ParsedDataCountry(object):
    def __init__(self, countryData=0):
        if not len(countryData) == 0:
            self.confirmed = self.search_category(countryData, 'confirmed')
            self.deaths = self.search_category(countryData, 'deaths')
            self.recovered = self.search_category(countryData, 'recovered')
            self.allData = { 'confirmed' : self.confirmed , 'deaths' : self.deaths , 'recovered' : self.recovered }
            self.countryName = self.extract_countryName()
            self.timeData = self.extract_time()
        else:
            self.confirmed = []
            self.deaths = []
            self.recovered = []
            self.countryName = []
    
    def search_category(self, dictionary, search_key):
        return [val for key, val in dictionary.items() if search_key in key.lower()][0]

    def extract_countryName(self):
        for key, currentData in self.allData.items():
            if not len(currentData) == 0:
                return currentData["Country/Region"].to_string(index=False).strip()
            
    def extract_time(self):
        for key, currentData in self.allData.items():
            if not len(currentData) == 0:
                return currentData.columns[4:-1]
            
    def get_values_category(self, category):
        if category == '' or category not in self.allData.keys():
            print("ERROR: Specified category " + category + " is invalid or not present in data!")
        else:
            return self.allData[category][self.timeData].iloc[0]
            #return data.head(), data.iloc[0]
        
    def plot_values_category(self, category):
        if category == '' or category not in self.allData.keys():
            print("ERROR: Specified category '" + category + "' is invalid or not present in data!")
        else:
            data = self.get_values_category(category)
            fig = plt.figure()
            ax = plt.subplot(111)
            ax.plot(data.index, data.values, label=category)
            plt.xticks(rotation=90)
            plt.ylabel('Number of people')
            plt.xlabel('Days')
            ax.legend()
            ax.xaxis.set_major_locator(ticker.MultipleLocator(5))
            ax.xaxis.set_minor_locator(ticker.MultipleLocator(1))
            fig.set_dpi(300)
            return fig, ax
        
    def plot_values(self, dpi=300):
        categories = self.allData.keys()
        fig = plt.figure()
        ax = plt.subplot(111)
        for category in categories:
            data = self.get_values_category(category)
            ax.plot(data.index, data.values, label=category)
        plt.xticks(rotation=90)
        plt.ylabel('Number of people')
        plt.xlabel('Days')
        ax.legend()
        ax.xaxis.set_major_locator(ticker.MultipleLocator(5))
        ax.xaxis.set_minor_locator(ticker.MultipleLocator(1))
        plt.title(self.countryName)
        fig.set_dpi(dpi)

class POPdata(object):
    def __init__(self, force_update=False):
        url = 'https://population.un.org/wpp/Download/Files/1_Indicators%20(Standard)/CSV_FILES/WPP2019_TotalPopulationBySex.csv'
        filename = url.split('/')[-1]
        self.filepath = os.getcwd() + '\\' + filename
        if not os.path.isfile(filename) or force_update:
            print("Downloading populations' file " + filename + " at URL " + url + " ...")
            res = requests.get(url)
            with open(filename, 'wb') as outfile:
                outfile.write(res.content)
        else:
            print("Using already existing file " + self.filepath + " to extract the populations' data" + '\n')
        self.allPopData = self.parseData()

    def parseData(self):
        if not os.path.isfile(self.filepath):
            print("ERROR: Cannot find file " + self.path + " ! No data will be extracted.")
            return []
        df = pd.read_csv(self.filepath, usecols=["Location", "Time", "PopTotal"], index_col="Location")
        #cols = df.columns
        #colToRename = [el for idx, el in enumerate(cols) if 'Year_' in el]
        #df.rename(columns=lambda s: s.replace("Year_", ""), inplace=True)
        return df

    def get_pop_country(self, country='', year=datetime.datetime.now().year):
        if country == '':
            print("ERROR: No specified country to extract data from!")
            return []
        if self.allPopData.empty == True:
            print("ERROR: Invalid populations' data!")
            return []
        countryData = self.allPopData.loc[self.remap_country_name(country)].set_index("Time")
        return countryData.loc[year].iloc[0][0] * 1000
    
    def remap_country_name(self, country):
        switcher = {
            'US' : 'United States of America'
            }
        return switcher.get(country, country)

    def get_pop_countries(self, *countriesNames):
        if countriesNames=="":
            print('No countriesNames to get the popolation for...')
            pass
        pops = {}
        for country in countriesNames:
            pops.update({country : self.get_pop_country(country)})
        return pops