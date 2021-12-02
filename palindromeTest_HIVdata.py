#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Dec  2 12:01:54 2021

@author: shantellesmith
"""
#%%
# import packages
from datetime import datetime
import pandas as pd
from matplotlib import pyplot as plt
from geopy.geocoders import Nominatim
import mpl_toolkits.basemap
import numpy as np

#%%
now = datetime.now()
current_time = now.strftime("%H:%M:%S")
print("Current Time =", current_time) 
#session 1 #12:02:19 #12:17:28
#session 2 #12:20:31 #13:07:28 (essentials completed)
#session 3 #14:48:55 #16:40:41 (extra map)
# 15.15 + 46.95 + 111.767 = 173.867 minutes
#%% Question 1
# read in data
hivdata = pd.read_excel('/Users/shantellesmith/OneDrive/PVT/Palindrome test/pone.0212445.s004.xlsx',
                        skiprows=1, engine='openpyxl')
#%% Question 2
# total no. people living with HIV according to survey estimate
total_surveys = hivdata.loc[hivdata['Estimate']=='Survey','NoPLHIV'].sum() #6409903
# average of estimate for Xhariep
average_Xhariep = hivdata.loc[hivdata['District']=='Xhariep','NoPLHIV'].mean() #12247.5
# new column for no. people not living with HIV
hivdata['NoPNLHIV'] = hivdata['NoPLHIV']/hivdata['Prevalence_%']*(100-hivdata['Prevalence_%'])
# sum of number people with HIV in cities/metros
total_cities = hivdata.loc[hivdata['District'].str.contains('city|metro', case=False),'NoPLHIV'].sum() #2572733

#%% Question 3
# remove special chars from column headings
hivdata.columns = hivdata.columns.str.replace(r'[^a-zA-Z0-9]', r'', regex=True)
print(hivdata.columns)
# Index(['District', 'Code', 'Estimate', 'Prevalence', 'PrevalenceLCL',
#        'PrevalenceUCL', 'NoPLHIV', 'NoPLHIVLCL', 'NoPLHIVUCL', 'NoPNLHIV'],
#       dtype='object')

#%% Question 4
hivdata_districtsEndI = hivdata.loc[hivdata['District'].str.endswith('i')].reset_index()
hivdata_districtsEndI_FH = hivdata_districtsEndI.loc[hivdata_districtsEndI['Estimate']=='Fay-Heriott']
x = hivdata_districtsEndI_FH['District']
y = hivdata_districtsEndI_FH['Prevalence']

fig, ax = plt.subplots()
for lower,upper,z in zip(hivdata_districtsEndI_FH['PrevalenceLCL'],
                         hivdata_districtsEndI_FH['PrevalenceUCL'],range(len(hivdata_districtsEndI_FH))):
    plt.plot((lower,upper),(z,z),'ro-',color='purple')
ax.scatter(y,x, zorder=2, marker = 's', color='purple', s=100)
plt.yticks(range(len(hivdata_districtsEndI_FH)),list(x))
plt.xlabel('Prevalence of HIV (%)')
plt.ylabel('Districts')
plt.tight_layout()

plt.savefig('fig1.png')

#%% Extract latitude and longitude for cities
hivdata_survey = hivdata.loc[hivdata['Estimate']=='Survey']
# fixing names not found by geolocator
hivdata_survey.loc[hivdata_survey['District']=='Dr Ruth Segomotsi Mompati','District'] = 'Bophirima'
hivdata_survey.loc[hivdata_survey['District']=='Nelson Mandela Bay Metro','District'] = 'Nelson Mandela Bay'
hivdata_survey.loc[hivdata_survey['District']=='Dr Kenneth Kaunda','District'] = 'Kaunda'
hivdata_survey = hivdata_survey.reset_index()
for i, city in enumerate(hivdata_survey['District']):
    address = city + ',' + 'South Africa'
    geolocator = Nominatim(user_agent="Shantelle_Smith")
    location = geolocator.geocode(address)
    hivdata_survey.loc[i,'latitude'] = location.latitude
    hivdata_survey.loc[i,'longitude'] = location.longitude

#%% Plot NoPLHIV data on map
#Calculate cases per 1000 people
cases_per_1000 = hivdata_survey['NoPLHIV'].values/(hivdata_survey['NoPLHIV'].values/hivdata_survey['Prevalence'].values/10)
districts = pd.DataFrame((hivdata_survey['longitude'].values, hivdata_survey['latitude'].values, hivdata_survey['District'].values)).transpose()

fig = plt.figure()
# add subplot for city data
ax = fig.add_subplot(122)
m = mpl_toolkits.basemap.Basemap(projection='lcc', resolution='h',
            lat_0=-29.635962, lon_0=24.754182,
            width=1.56E6, height=1.2E6)
m.shadedrelief()
m.drawparallels(np.arange(-80.,81.,5.),labels=[False,False,False,True])
m.drawmeridians(np.arange(-180.,181.,5.),labels=[True,True,True,False])
m.drawmapboundary(fill_color='white')
m.readshapefile('/Users/shantellesmith/OneDrive/PVT/Palindrome test/zaf_adm_sadb_ocha_20201109_SHP/zaf_admbnda_adm1_sadb_ocha_20201109',
                'zaf_admbnda_adm1_sadb_ocha_20201109')

# scatter data, with color reflecting population and size reflecting area
m.scatter(hivdata_survey['longitude'].values, hivdata_survey['latitude'].values, latlon=True,
          c=hivdata_survey['Prevalence'].values, s=cases_per_1000,
          cmap='viridis', alpha=0.8)

# colorbar and legend
plt.colorbar(label=r'Prevalence (%)', fraction=0.036, pad=0.04)

# make legend with dummy points
for a in [50, 150, 250]:
    plt.scatter([], [], c='k', alpha=0.5, s=a,
                label=str(a) + '')
plt.legend(title = 'Cases per\n1000 people', scatterpoints=1, frameon=True, framealpha=0.9,
           labelspacing=1, loc='upper left', facecolor='white')

# add subplot for city names
ax = fig.add_subplot(121)

m = mpl_toolkits.basemap.Basemap(projection='lcc', resolution='h',
            lat_0=-29.635962, lon_0=24.754182,
            width=1.56E6, height=1.2E6)
m.shadedrelief()
m.drawparallels(np.arange(-80.,81.,5.),labels=[False,False,False,True])
m.drawmeridians(np.arange(-180.,181.,5.),labels=[True,True,True,False])
m.drawmapboundary(fill_color='white')
m.readshapefile('/Users/shantellesmith/OneDrive/PVT/Palindrome test/zaf_adm_sadb_ocha_20201109_SHP/zaf_admbnda_adm1_sadb_ocha_20201109',
                'zaf_admbnda_adm1_sadb_ocha_20201109')

x, y = m(districts.iloc[:,0].values,districts.iloc[:,1].values)
for j in range(len(districts)):
    plt.annotate(districts.iloc[j,2],xy=(x[j],y[j]),xytext=(x[j]+20000,y[j]+5000),
                 size=7, bbox=dict(boxstyle="round",fc="w"))
