import numpy as np
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
import glob, os

def plotBrune(ax):
	'''Plot Brune corner frequencies for mag/dist ranges of interest
	   (see esupp for details on calculation)'''
	# Read file containing list of corner frequencies
	dirname = os.path.dirname(__file__)
	brunecsv = os.path.join(dirname,'../DBs/brune-all.csv')
	df = pd.read_csv(brunecsv, names=['delta', 'mag', 'T', 'dB'], 
					 skiprows=1, sep=',')
	df = df[df['mag'] <= 4]

	# Plot grid of corner frequencies:
	# Draw lines connecting all magnitudes at a given distance,
	# then all distances at a given magnitude 
	gridcolor='#1f77b4' # darker blue
	linestyle={'color' : gridcolor,
			   'mfc' : gridcolor,
			   'linewidth' : 1,
			   'linestyle' : '--'}
	deltas = pd.unique(df['delta'])
	for delta in deltas:
		df_subset = df[df['delta'] == delta]
		if delta == 1:
			label=r'Brune f$_c$'
		else:
			label=''
		ax.plot(df_subset['T'], df_subset['dB'], marker='.', 
				**linestyle, label=label)
	mags = pd.unique(df['mag'])
	for mag in mags:
		df_subset = df[df['mag'] == mag]
		ax.plot(df_subset['T'], df_subset['dB'], marker='None', 
				**linestyle, label='')

	# Plot labels on grid for magnitudes and distances
	df_text = df[df['delta'] == 0.01]
	mags = np.arange(1,5)
	for mag in mags:
		df_plot = df_text[df_text['mag'] == mag]
		ax.text(df_plot['T'], df_plot['dB']+4, 
				"M{0}".format(mag), va='center', ha='center', 
				color=gridcolor)
	df_text = df[df['mag'] == 4]
	for delta in deltas:
		df_plot = df_text[df_text['delta'] == delta]
		ax.text(df_plot['T']+0.02, df_plot['dB']+2.5, 
				"{0:0d} km".format(int(delta*100)), va='center', 
				rotation=30, color=gridcolor)

def ALNM_P(P):
	Pl = [0.01, 1., 10., 150.,]
	lnm = [-135., -135., -130., -118.25,]
	if Pl[0]<=P<=Pl[-1]:
		lnm_P = np.interp(P, Pl, lnm)
		return lnm_P
	else:
		print(f'P={P} out of ALNM range.')
		return np.nan
def AHNM_P(P):
	Ph = [0.01, 0.1, 0.22, 0.32, 0.80, 3.8, 4.6, 6.3, 7.1, 150.,]
	hnm = [-91.5, -91.5, -97.41, -110.5, -120., -98., -96.5, -101., -105., -91.25]
	if Ph[0]<=P<=Ph[-1]:    
		hnm_P = np.interp(P, Ph, hnm)
		return hnm_P
	else:
		print(f'P={P} out of ALNM range.')
		return np.nan

# Fornasari et al. 2022 model
df = pd.read_csv('../DBs/italian_model.csv')
# 90+
ninety = pd.read_csv('../DBs/ninetyplus.csv')
long_stas = ninety.Station.tolist()

# Year 2022
import json
f = open('../DBs/jsons/yearly_median_all.json')
# returns JSON object as a dictionary
db_2022 = json.load(f)
# Lockdown
f = open('../DBs/jsons/yearly_median_all_covid.json')
# returns JSON object as a dictionary
db_covid = json.load(f)

# stas = ['BGMO','BRSA','BNO','DSG','MLBT','SLOB','CAT','PTR','CLG1','BNT','CDI1','SVN',
# 'BAN','CML','POZS','BCLI','MPCD','TES','CTU','CFL','PNA','PLR','RMMM','RMVT','SBC',
# 'SNZ','BCN','SAR','SLC1','LVN1','CLM','TNO',
# 'PTF','MLF','SPS','CES','CRTL','PNAL','SCO','ARR','NVR1','NCIA','BOJ',
# 'SLD','NCO']
stas = ['PTF']
for sta in stas:
	try:
		periods2022 = []
		vals = []
		for period in db_2022.keys():
			val = db_2022[period][sta]
			vals.append(val)
			periods2022.append(float(period))
		vals_covid = []
		periodscovid = []
		for period in db_covid.keys():
			val = db_covid[period][sta]
			vals_covid.append(val)
			periodscovid.append(float(period))

		mpl.rcParams.update({'font.size': 16})
		fig, ax = plt.subplots(figsize=(10,6))
		# Plot Model
		ax.plot(df.Period,df.Median, '--r', label='Median')
		ax.plot(df.Period,df.IALNM,'.--r')
		ax.plot(df.Period,df.IAHNM,'.--r',label='IAHNM - IALNM')
		ax.plot(periods2022,vals,'k',label=f'{sta} 2022')
		ax.plot(periodscovid,vals_covid,'y',label=f'{sta} Lockdown')
		ax.set_ylabel('Power (dB)')
		ax.set_xlabel('Period (s)')
		ax.semilogx()
		ax.set_xlim(0.01, 100)
		ax.set_ylim(-200, -50)
		# Plot Brune corner frequency grid
		plotBrune(ax)

		ax.legend(loc='lower right')
		plt.savefig(f'../Figures/NoiseModel/{sta}.png', dpi=300, bbox_inches='tight')
		plt.close(fig)
	except:
		print(f'Problem in station: {sta}')
		continue