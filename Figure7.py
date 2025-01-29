import geopandas as gpd
import pandas as pd
import json
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.transforms import offset_copy
import matplotlib.ticker as tick
import cartopy.crs as ccrs
import cartopy.io.img_tiles as cimgt
from shapely.geometry import Point
import glob, warnings, os
from datetime import datetime, timedelta
warnings.filterwarnings('ignore')
from tqdm import tqdm

# Load Polygone
polygon = gpd.read_file('DBs/limits_IT_provinces.geojson')

# Load Biggest Cities
big_city = pd.read_csv('DBs/DCIS_POPRES1_11092023115658356.csv')
big_city = big_city.nlargest(n=10, columns=['Value'])
# Read Station Info
dpc_db = pd.read_csv('DBs/station_attributes.csv')
# Data Completeness
db_comp= pd.read_csv('DBs/completeness.csv')
long_stas = db_comp[(db_comp.CovidComp >= 50)&(db_comp.NoCovidComp >= 50)].Station.tolist()


# Opening JSON file
f = open('DBs/jsons/yearly_median_ext_covid_diff.json')
# returns JSON object as 
# a dictionary
data = json.load(f)
periods = ['0.0625', '0.0992', '0.125', '0.25', '0.5', '1.0']
fig= plt.figure(figsize=(16, 9),dpi=300)
ax = plt.gca()

# set colors and legends
from matplotlib.colors import ListedColormap, BoundaryNorm
N=[1,1,5,6,6,0,5,3,7,1]# number of colors  to extract from each cmap, sum(N)=len(classes)
base_cmaps = ['Purples','Greens','YlOrBr','PuRd','BrBG','BrBG','turbo','YlGn','Greys','Oranges']
stas = ['MODG',
'BGMO',
'BRSA','BNO','DSG','MLBT','SLOB',
'CAT','PTR','CLG1','BNT','CDI1','SVN',
'BAN','CML','NAP','POZS','BCLI','MPCD',
'TES','CTU','CFL','PNA','PLR',
'RMMM','RMVT','SBC',
'CMG','SNZ','BCN','SAR','SLC1','LVN1','CLM',
'TNO']
from matplotlib import cm

n_base = len(base_cmaps)
colors = np.concatenate([plt.get_cmap(name)(np.linspace(0.2,0.8,N[i])) for i,name in zip(range(n_base),base_cmaps)])
ax.set_prop_cycle(color=colors)

lines = []; cities = []; lgn_list = []; lgn_list2 = []
for city_index, city in enumerate(big_city.Territory.sort_values()):
	if True:
		city_poly = polygon[polygon.prov_name.values == city].geometry
		maxval = 0; minval = 0
		for sta in data[periods[0]]:
			st_inx = dpc_db[dpc_db['sta'] == sta].index.tolist()[0]
			stla = dpc_db['lat'][st_inx]
			stlo = dpc_db['lon'][st_inx]
			staP = Point(stlo,stla)
			
			if city_poly.contains(staP).tolist()[0] == True and sta in long_stas:
				if city not in cities:
					lgn_list.append(city)
					lgn_list2.append('')
					cities.append(city)
				syear = '2020'
				syear2 = '2022'
				DIR = 'DBs/sens_only/'
				
				npzs = glob.glob(os.path.join(DIR,syear) + '/**/' + sta + '.*')
				npzs2 = glob.glob(os.path.join(DIR,syear2) + '/**/' + sta + '.*')

				if sta == 'CLG1':
					#find indexes
					remove_idx = []
					for idx,file in enumerate(npzs2):
						day = int(file.split('/')[-2])
						if day >= 227 and day <= 319:
							remove_idx.append(idx)
					#convert list to numpy array
					arr = np.array(npzs2)
					#indices of elements to be removed
					#use numpy.delete() to remove elements
					new_arr = np.delete(arr, remove_idx)
					#convert numpy array back to list
					npzs2 = new_arr.tolist()

				res = np.load(npzs[0])
				org_keys = list(res.keys())
				org_freqs = res[org_keys[0]]
				# Exclude Pn key
				org_keys = org_keys[1:]
				# Periods up to 1 second
				freq_ints = org_freqs[:20]
				
				vals = np.empty([len(npzs),len(org_keys),len(freq_ints)])
				vals[:] = np.nan
				for npz in npzs:
					res = np.load(npz)
					keys = list(res.keys())
					for i,psd in enumerate(keys[1:]):
						idx = org_keys.index(psd)
						vals[i,idx,:] = res[psd][:20]

				# 2020
				for i, hour in enumerate(range(vals.shape[1])):
					avgs = []
					for freq in range(vals.shape[2]):
						avg = np.nanmedian(vals[:,hour,freq])
						avgs.append(avg)

				# 2022
				vals2 = np.empty([len(npzs2),len(org_keys),len(freq_ints)])
				vals2[:] = np.nan
				for npz in npzs2:
					res = np.load(npz)
					keys = list(res.keys())
					for i,psd in enumerate(keys[1:]):
						idx = org_keys.index(psd)
						vals2[i,idx,:] = res[psd][:20]
				for i, hour in enumerate(range(vals2.shape[1])):
					avgs2 = []
					for freq in range(vals2.shape[2]):
						avg = np.nanmedian(vals2[:,hour,freq])
						avgs2.append(avg)

				[line] = plt.plot(freq_ints,[a - b for a, b in zip(avgs2, avgs)],c=colors[stas.index(sta)]) #,label=sta  , cmap=cmap, vmin=0, vmax=N[city_index]
				lines.append(line)
				lgn_list.append(line)
				lgn_list2.append(sta)

import matplotlib.text as mtext
class LegendTitle(object):
	def __init__(self, text_props=None):
		self.text_props = text_props or {}
		super(LegendTitle, self).__init__()

	def legend_artist(self, legend, orig_handle, fontsize, handlebox):
		x0, y0 = handlebox.xdescent, handlebox.ydescent
		title = mtext.Text(x0, y0, r'\underline{' + orig_handle + '}', usetex=True, **self.text_props)
		handlebox.add_artist(title)
		return title

plt.legend(lgn_list, lgn_list2,handler_map={str: LegendTitle({'fontsize': 18})},ncol=2,loc='center left', bbox_to_anchor=(1, 0.5))
plt.xlim([0.02,1])
plt.xscale('log')
plt.xlabel('Period (s)')
plt.ylabel('Power Change (dB)\n>0: Noisier in 2022\n<0: Noisier in lockdown')
# plt.legend()
plt.tight_layout()
plt.grid(True, which="both", ls="--")
from matplotlib.ticker import FormatStrFormatter
ax.xaxis.set_minor_formatter(FormatStrFormatter("%.2f"))
plt.savefig('Figures/Fig7.png',dpi=300)
plt.savefig('Figures/Fig7.svg',dpi=300)
plt.close('all')
