# -*- coding: utf-8 -*-
"""
Library for SIR Model
- SIRmodel class is a generic SIR model, able to be simulated
- SIRmodelFIT class uses data of confirmed cases of a country and fits it
- SIRmodelFITset class is a set of fitting models of different countries
"""

import numpy as np
import scipy.integrate as integrate
import matplotlib.pyplot as plt
import datetime
from scipy.optimize import minimize
from scipy.optimize import curve_fit
import matplotlib.ticker as ticker

class SIRmodel(object):
    def __init__(self, N, beta, gamma):
        self.N = N
        self.beta = beta
        self.gamma = gamma
        self.t = []
        self.res = []
        self.name = 'None'
        self.y0 = []
        
    def set_name(self, name):
        self.name = name
        
    def set_pop(self, pop):
        if pop==0:
            print("ERROR: Population of model called '" + self.name + "' cannot be corresponding to zero!")
            pass
        self.N = pop
        
    def set_beta(self, beta):
        self.beta = beta
        
    def set_gamma(self, gamma):
        self.gamma = gamma
        
    def simulate(self, time_data, y0):
        def SIR_ODEs(t, y):
            S = y[0]
            I = y[1]
            R = y[2]
            return [-self.beta*S*I / self.N, self.beta*S*I / self.N - self.gamma*I, self.gamma*I]
        t0 = time_data[0]
        tf = time_data[-1]
        self.y0 = y0
        npoints = len(time_data)
        self.t = np.linspace(t0, tf, npoints)
        self.res = integrate.solve_ivp(SIR_ODEs, (t0, tf), y0, t_eval=self.t)
        return self.res
    
    def plotres(self, dpi=300, t=[]):
        if t==[] or self.y0==[]:
            if self.res==[]:
                print("ERROR: Result is empty! Impossible to plot data.")
                pass
            t = self.res.t
            S = self.res.y[0]
            I = self.res.y[1]
            R = self.res.y[2]
        else:
            if self.y0 == []:
                print("ERROR: Initial conditions are empty! No simulations will be performed.")
                pass
            res = self.simulate(t, self.y0)
            S, I, R = res.y[0], res.y[1], res.y[2]
        fig = plt.figure()
        ax = plt.subplot(111)
        ax.plot(t, S, label='S')
        ax.plot(t, I, label='I')
        ax.plot(t, R, label='R')
        plt.ylabel('Number of people')
        plt.xlabel('Days')
        ax.legend()
        if self.name != 'None':
            plt.title(self.name)
        fig.set_dpi(dpi)
        plt.grid()
        #plt.savefig(self.name + "_" + str(datetime.datetime.now().strftime("%Y%m%d_%H%M%S")) + ".png")
        return fig, ax

class SIRmodelFIT(object):
    def __init__(self, countriesDataConfirmed, countryPops=[], country=''):
        if country=='' or not country in countriesDataConfirmed.keys():
            print("ERROR: Country '" + country + "' is either invalid or could not be found in the provided data!")
            pass
        if countryPops==[] or not country in countryPops.keys():
            print("ERROR: Country population cannot be corresponding to zero!")
            pass
        self.country = country
        self.pop = countryPops[country]
        self.SIRmodel = SIRmodel(self.pop, 0, 0)
        self.SIRmodel.set_name(country)
        countryDataConfirmed = countriesDataConfirmed[country]
        self.data = np.array(countryDataConfirmed.to_list())
        self.tDate = self.reformat_date(countryDataConfirmed.index)
        self.tDays = self.dates_to_days(self.tDate)
        
    def reformat_date(self, dateStr):
        dates_formatted = [datetime.datetime.strptime(date, '%m/%d/%y').date() for date in dateStr]
        return [day.strftime('%d/%m/%y') for day in dates_formatted]
        
    def dates_to_days(self, dates):
        return np.linspace(1, len(dates), len(dates))
        
    def loss_fun_rmse(self, params):
        print("Evaluation of RMSE loss function with parameters: " + ' '.join('{}'.format(k) for k in params))
        self.SIRmodel.set_beta(params[0])
        self.SIRmodel.set_gamma(params[1])
        res = self.SIRmodel.simulate(self.tDays, [self.SIRmodel.N, 1, 0])
        return np.sqrt(np.mean(res.y[1] - self.data)**2)
    
    def opt_minrmse(self, IC, bnds=None, tolerance=None):
        print('\n' + "Starting fitting with minimization of RMSE for country " + self.country)
        return minimize(self.loss_fun_rmse, IC, bounds=bnds, tol=tolerance)
    
    def fun_curvefit(self, t, beta, gamma):
        print("Evaluation of fitting function with parameters: %f %f" % (beta, gamma)) #+ ' '.join('{}'.format(k) for k in params))
        self.SIRmodel.set_beta(beta)
        self.SIRmodel.set_gamma(gamma)
        res = self.SIRmodel.simulate(t, [self.SIRmodel.N, 1, 0])
        return res.y[1]
    
    def opt_curvefit(self, IC):
        print('\n' + "Starting fitting with non-linear LSQR method for country " + self.country)
        return curve_fit(self.fun_curvefit, self.tDays, self.data, IC)[0]
    
    def plot_compare_reference(self, dpi=300, dates=None):
        if dates == None:
            dates = self.tDate
        fig = plt.figure()
        ax = plt.subplot(111)
        ax.plot(self.tDate, self.data, label='Reference')
        plt.xticks(rotation=90)
        actModel = self.SIRmodel
        ax.plot(dates, self.simulate_model(dates), label='Fit')
        plt.xticks(rotation=90)
        plt.ylabel('Number of infected people')
        plt.xlabel('Days')
        plt.grid()
        ax.legend()
        if actModel.name != None:
            plt.title(actModel.name)
        ax.xaxis.set_major_locator(ticker.MultipleLocator(5))
        ax.xaxis.set_minor_locator(ticker.MultipleLocator(1))
        fig.set_dpi(dpi)
        return fig, ax
    
    def extend_date(self, dates, nDays):
        dates_formatted = [datetime.datetime.strptime(date, '%d/%m/%y') for date in dates]
        dates_toadd = [dates_formatted[-1] + datetime.timedelta(days=add) for add in range(1, nDays)]
        return [day.strftime('%d/%m/%y') for day in dates_formatted + dates_toadd]
    
    def simulate_model(self, dates=None):
        if dates == None:
            dates = self.tDate
        actModel = self.SIRmodel
        return actModel.simulate(self.dates_to_days(dates), [actModel.N, 1, 0]).y[1]
    
    def predict_days(self, nDays):
        return self.simulate_model(self.extend_date(self.tDate, nDays))
    
    def plot_prediction(self, nDays=0, dpi=300):
        fig, ax = self.plot_compare_reference(dpi, self.extend_date(self.tDate, nDays))
        return fig, ax
        
    def plotres(self, dpi=300, dates=[]):
        if dates==[]:
            dates = self.tDate
        fig, ax = self.SIRmodel.plotres(dpi, dates)
        return fig, ax
    
    def plotres_predicted(self, dpi=300, nDays=0):
        fig, ax = self.plotres(dpi, self.dates_to_days(self.extend_date(self.tDate, nDays)))

class SIRmodelFITset(object):
    def __init__(self, countriesDataConfirmed, countryPops, IC=None):
        if countryPops==[]:
            print("ERROR: Numbers of populations cannot be corresponding to zero!")
            pass
        if IC==None:
            print("ERROR: Invalid Initial Conditions!")
            pass
        self.IC = IC
        self.modelsSet = {}
        for country in countriesDataConfirmed.keys():
            self.modelsSet.update({country : SIRmodelFIT(countriesDataConfirmed, countryPops, country)})
    
    def opt_curve_fit(self):
        for country in self.modelsSet.keys():
            self.modelsSet[country].opt_curvefit(self.IC)
    
    def plot_compare_reference(self, dpi=300):
        for country in self.modelsSet.keys():
            self.modelsSet[country].plot_compare_reference(dpi)
            
    def plot_prediction(self, dpi=300, nDays=0):
        if nDays==0:
            print("WARNING: Number of days to predict either not specified or zero! No days will be predicted")
        for country in self.modelsSet.keys():
            self.modelsSet[country].plot_prediction(nDays, dpi)
            
    def plotres(self, dpi=300):
        for country in self.modelsSet.keys():
            self.modelsSet[country].plotres(dpi)
            
    def plotres_predicted(self, dpi=300, nDays=0):
        if nDays==0:
            print("WARNING: Number of days to predict either not specified or zero! No days will be predicted")
        for country in self.modelsSet.keys():
            self.modelsSet[country].plotres_predicted(dpi, nDays)