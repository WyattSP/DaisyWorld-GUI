#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Sep 10 20:29:08 2023

@author: wyattpetryshen
"""

#Constants
S = 917
sig = 5.670374419*(10**-8)
q = 20
Ag = 0.4

#Functions for DaisyWorld
import random
import pandas as pd
def init_species(n_species, step_size, run_time, random_albedo = True, albedo = None):
    rows = int(round(run_time/step_size,1))
    #Create dataframe to store population
    spec_P = pd.DataFrame(columns=range(n_species),index=range(rows))
    for i in range(n_species):
        spec_P = spec_P.rename(columns={i:'%s%i'%('Species_',1+i)})

    if random_albedo == True:
        #Create dataframe to store species albedo (static)
        spec_A = [random.uniform(0,1) for i in range(n_species)]
    else:
        spec_A = albedo
    #Create dataframe to store Tc
    spec_Tc = pd.DataFrame(columns=range(n_species),index=range(rows))
    for i in range(n_species):
        spec_Tc = spec_Tc.rename(columns={i:'%s%i'%('Species_',1+i)})
    return spec_P, spec_A, spec_Tc

def eff_temp(S,L,A,sig):
    Tc = (((S*L*(1-A))/sig)**0.25)-273
    return Tc

def growth_rate(Ti):
    Bi = (1 - 0.00326*(22.5 - Ti)**2)
    return Bi

def planet_albedo_pl(x,spec_P,spec_A):
    a = spec_P
    b = spec_A
    f = lambda a,b: a*b
    d_cov = sum([f(a[i],b[i]) for i in range(len(a))])
    AgN = ((1 - (sum(a)))*Ag) + d_cov
    return AgN

def pop_cover_pl(species_frame):
    x = 1 - sum(species_frame)
    return x

def eff_coverage_pl(x,Ag,spec_P,spec_A):
    a = spec_P
    b = spec_A
    f = lambda a,b: a*b
    d_cov = sum([f(a[i],b[i]) for i in range(len(a))])
    A = x*Ag+d_cov
    return A

def temp_change_pl(Ai,Tc,x,spec_P,spec_A):
    Ti = q*(planet_albedo_pl(x,spec_P,spec_A) - Ai) + Tc
    return Ti

def pop_increase_pl(aia,species_frame,Ti,y):
    dadt = aia*((pop_cover_pl(species_frame)*growth_rate(Ti)) - y)
    return dadt

def lum_change(rate,max_time):
    L = 0.6+(rate*(1.2/max_time))
    #This is a good place to insert stochastic perturbation
    return round(float(L),3)

def new_pop(old_pop,pop_change):
    new_pop = old_pop + pop_change
    if new_pop < 0:
        return 0
    else:
        return new_pop

#####Daisyworld_V2
def make_daisy_v2(species_number, step_size, run_time, albedo=None, lumosity=None, Death_rate=None, Initial_populations=None):
    #Start parameters
    #Constant parameters
    #Input variables to usable values
    species_number = int(species_number)
    step_size = int(step_size)
    run_time = int(run_time)
    #albedo
    if albedo == "None" or albedo == "" or albedo == None:
        albedo = None
    else:
        albedo = [float(i) for i in albedo.split(",")]
    #lumosity
    if lumosity == "None" or lumosity == "" or lumosity == None:
         lumosity = None
    else:
         lumosity = float(lumosity)
    #Death Rate
    if Death_rate == "None" or Death_rate == "" or Death_rate == None:
         Death_rate = None
    elif Death_rate == "random":
        Death_rate = "random"
    else:
         Death_rate = [float(i) for i in Death_rate.split(",")]
    #Inital populations
    if Initial_populations == "None" or Initial_populations == "" or Initial_populations == None:
        Initial_populations = None
    else:
        Initial_populations = [float(i) for i in Initial_populations.split(",")]

    #Global Death Rate
    if Death_rate is None:
        spec_y = [0.3] * species_number
    elif Death_rate == "random":
        spec_y = [random.uniform(0.01,0.99) for i in range(species_number)]
    else:
        if species_number == len(Death_rate):
            spec_y = Death_rate
        else:
            raise ValueError('Death rate should be same length as species')

    #Initial species tables
    if albedo is None:
        spec_P, spec_A, spec_Tc = init_species(species_number,step_size,run_time,True)
    else:
        if species_number == len(albedo):
            spec_P, spec_A, spec_Tc = init_species(species_number,step_size,run_time,False,albedo)
        else:
            raise ValueError('Albedo should be same length as species')
    #
    if lumosity is None:
        #Starting lumosity
        #Add a starting lumosity for next parameter
        L = 0.6
    else:
        L = lumosity
    #Inital Population abundances
    #Eventually make editable boundary condition
    if Initial_populations is None:
        Apop_int = [0] * species_number
    else:
        if species_number == len(Initial_populations):
            Apop_int = Initial_populations
        else:
            raise ValueError('Initial populations should be same length as species')
    #Calcualte initial population cover
    x = pop_cover_pl(Apop_int)
    #Calcualute initial effective coverage
    A = eff_coverage_pl(x,planet_albedo_pl(x,Apop_int,spec_A),Apop_int,spec_A)
    #Calculate TC
    Tc = eff_temp(S,L,A,sig)
    #Inital population increase
    for i in range(0,len(spec_A)):
        #Calculate new temperature
        T_Temp = temp_change_pl(spec_A[i],Tc,x,Apop_int,spec_A)
        spec_Tc.iloc[0,i] = T_Temp
        #Calculate population increase
        Apop_incr= pop_increase_pl(Apop_int[i],Apop_int,T_Temp,spec_y[i])+0.001
        #Calculate new population
        Apop = new_pop(Apop_int[i],Apop_incr)
        spec_P.iloc[0,i] = Apop

    L_Lum = []
    L_Tc = []
    Time = []

    L_Lum.append(L)
    L_Tc.append(Tc)

    n_time = 0
    Time.append(n_time)
    for i in range(1,run_time):
        if lumosity is None:
            L = lum_change(n_time,run_time)
        else:
            L = lumosity
        n_time = n_time + step_size
        Time.append(n_time)
        L_Lum.append(L)
        #Recalculate pop_cover
        x = pop_cover_pl(spec_P.iloc[n_time-1])
        #Recalculate effective coverage
        A = eff_coverage_pl(x,planet_albedo_pl(x,spec_P.iloc[n_time-1],spec_A),spec_P.iloc[n_time-1],spec_A)
        #Recalculate Temp
        Tc = eff_temp(S,L,A,sig)
        L_Tc.append(Tc)
        ###New Populations for n-species
        for i in range(0,len(spec_A)):
            #Calculate new temperature
            T_Temp = temp_change_pl(spec_A[i],Tc,x,spec_P.iloc[n_time-1],spec_A)
            #spec_Tc.iloc[n_time,i] = T_Temp
            #Calculate population increase
            Apop_incr= pop_increase_pl(spec_P.iloc[n_time-1,i],spec_P.iloc[n_time-1],T_Temp,spec_y[i])+0.001
            #Calculate new population
            Apop = new_pop(spec_P.iloc[n_time-1,i],Apop_incr)
            spec_P.iloc[n_time,i] = Apop
    return spec_P, L_Lum, L_Tc, spec_A, spec_y, Time

#Plot
def plot_results(spec_A,Time,spec_P):
    fig, ax1 = plt.subplots()
    for i in range(0,len(spec_A)):
        ax1.plot(Time, spec_P.iloc[:,i].to_numpy())
    ax1.tick_params(axis='y', labelcolor='black')
    ax2 = ax1.twinx()
    ax2.plot(Time, L_Tc, color='tab:red',linestyle='--')
    ax2.tick_params(axis='y', labelcolor='tab:red')
    fig.tight_layout()
    return fig

#Pysimplegui implementation
from matplotlib.ticker import NullFormatter  # useful for `logit` scale
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import PySimpleGUI as sg
import matplotlib
matplotlib.use('TkAgg')

sg.theme('DarkAmber')

def draw_figure(canvas, figure):
    figure_canvas_agg = FigureCanvasTkAgg(figure, canvas)
    figure_canvas_agg.draw()
    figure_canvas_agg.get_tk_widget().pack(side='top', fill='both', expand=1)
    return figure_canvas_agg

def delete_figure_agg(figure_agg):
    figure_agg.get_tk_widget().forget()
    plt.close('all')

# All the stuff inside your window.
layout = [[sg.T("Species",size=(10, 1)),sg.In("2",size=(10, 1),key="species")],
          [sg.T("Step Size",size=(10, 1)),sg.In("1",size=(10, 1),key="step")],
          [sg.T("Run Time",size=(10, 1)),sg.In("100",size=(10, 1),key="run_time")],
          [sg.T("Albedo",size=(10, 1)),sg.In("None",size=(20, 1),key="albedo")],
          [sg.T("Lumosity",size=(10, 1)),sg.In("None",size=(20, 1),key="lumosity")],
          [sg.T("Death_rate",size=(10, 1)),sg.In("None",size=(20, 1),key="death_rate")],
          [sg.T("Initial_populations",size=(10, 1)),sg.In("None",size=(20, 1),key="initial_populations")],
          [sg.Button('Run'), sg.Button('Clear')],
          [sg.Canvas(size=(640, 480),key='-CANVAS-')],
          [sg.Text("", size=(0, 1), key='OUTPUT')]
          ]

# Create the Window
window = sg.Window('Window Title', layout, finalize=True, element_justification='center', font='Helvetica 18')
fig = plt.figure()
fig_canvas_agg = draw_figure(window['-CANVAS-'].TKCanvas, fig)
# Event Loop to process "events" and get the "values" of the inputs
while True:
    event, values = window.read()
    if event == sg.WIN_CLOSED:
        break
    #Enter parameters
    if event == "Run":
        species_number = values["species"]
        step_size = values["step"]
        run_time = values["run_time"]
        albedo = values["albedo"]
        lumosity = values["lumosity"]
        Death_rate =values["death_rate"]
        Initial_populations = values["initial_populations"]

        #Run daisyworld
        spec_P, L_Lum, L_Tc, spec_A, spec_y, Time= make_daisy_v2(species_number,
                                                                 step_size,
                                                                 run_time,
                                                             albedo=albedo,
                                                             lumosity=lumosity,
                                                             Death_rate=Death_rate,
                                                             Initial_populations = Initial_populations)
        #Plot results
        fig = plt.figure()
        delete_figure_agg(fig_canvas_agg)
        fig_canvas_agg = draw_figure(window['-CANVAS-'].TKCanvas, plot_results(spec_A,Time,spec_P))
        #window['OUTPUT'].update(value=L_Lum)
    if event == "Clear":
        delete_figure_agg(fig_canvas_agg)
        fig = plt.figure()
        fig_canvas_agg = draw_figure(window['-CANVAS-'].TKCanvas, fig)

window.close()
