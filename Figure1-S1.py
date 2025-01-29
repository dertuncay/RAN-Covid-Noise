import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.transforms import offset_copy
import matplotlib.ticker as tick
import cartopy.crs as ccrs
import cartopy.io.img_tiles as cimgt
import glob, warnings, os
import string
from scipy.interpolate import interp1d

def draw_map(fig,ax,stname,stlos,stlas,data,vmin,vmax):
	# Limit the extent of the map to a small longitude/latitude range.
	ax.set_extent([6.90, 18.55, 36.5, 47], crs=ccrs.Geodetic())
	# Add the Stamen data at zoom level 8.
	# ax.add_image(stamen_terrain, 8)
	request = cimgt.GoogleTiles(style='satellite',)
	ax.add_image(request, 8, interpolation='bilinear')
	# Add data points
	day_map = ax.scatter(stlos, stlas, marker='^', c=data,
	 s=40, alpha=0.9, transform=ccrs.Geodetic(), 
	 cmap='jet',vmin=vmin,vmax=vmax)
	# Colorbar
	ticks = np.linspace(vmin, vmax, 10)#.astype(int)
	cbar = plt.colorbar(day_map, ax= ax, orientation='vertical',extend='both',ticks=ticks,format=tick.FormatStrFormatter('%.1f'))
	cbar.ax.tick_params(labelsize=6)
	cbar.set_label(r'Power (db rel. 1 (m/s$^{2}$)$^{2}$/Hz)', rotation=90, size=8)
	# Use the cartopy interface to create a matplotlib transform object
	# for the Geodetic coordinate system. We will use this along with
	# matplotlib's offset_copy function to define a coordinate system which
	# translates the text by 25 pixels to the left.
	geodetic_transform = ccrs.Geodetic()._as_mpl_transform(ax)
	text_transform = offset_copy(geodetic_transform, units='dots', x=-25)
	return fig, ax


# Opening JSON file
f = open('DBs/jsons/yearly_median_ext.json')
# returns JSON object as a dictionary
data = json.load(f)

# 90+
ninety = pd.read_csv('DBs/ninetyplus.csv')
long_stas = ninety.Station.tolist()

# Read Station Info
dpc_db = pd.read_csv('DBs/station_attributes.csv')

# Define Figure
# Create a Stamen terrain background instance.
stamen_terrain = cimgt.Stamen('terrain-background')
fig,ax = plt.subplots(4,2, figsize=(9, 15), facecolor='w', edgecolor='k',subplot_kw={'projection': stamen_terrain.crs}, gridspec_kw = {'wspace':0, 'hspace':0.1})

# Annotation
annotations = list(string.ascii_lowercase)

# Italian Background Noise Model
it_model = pd.read_csv('DBs/it_model.csv',sep=';')

f1_low = interp1d(it_model.Period, it_model.IALNM, kind='linear')
f1_high = interp1d(it_model.Period, it_model.IAHNM, kind='linear')


periods = ['0.0992','0.25','0.5','1.0']

vmins = [f1_low(period).tolist() for period in periods]
vmaxs = [f1_high(period).tolist() for period in periods]

vmins_std = []; vmaxs_std = []
for per_idx, (period, vmin, vmax) in enumerate(zip(periods,vmins,vmaxs)):
	print(period,vmin,vmax)
	stnames = []; stlos = []; stlas = []; dif = []; 
	for sta in data[period]:
		if sta in long_stas:
			val = data[period][sta]
			st_inx = dpc_db[dpc_db['sta'] == sta].index.tolist()[0]
			stla = dpc_db['lat'][st_inx]
			stlo = dpc_db['lon'][st_inx]
			stlas.append(stla)
			stlos.append(stlo)
			stnames.append(sta)
			dif.append(val)

	dif = np.array(dif)
	fig, ax[per_idx,0] = draw_map(fig,ax[per_idx,0],stnames,stlos,stlas,dif,vmin,vmax)
	# LAT-LON Grids
	import cartopy.mpl.ticker as cticker
	ax[per_idx,0].set_yticks(np.linspace(37,46,4), crs=ccrs.PlateCarree())
	ax[per_idx,0].set_yticklabels(np.linspace(37,46,4))
	ax[per_idx,0].yaxis.tick_left()
	ax[per_idx,0].set_xticks(np.linspace(7,17, 6), crs=ccrs.PlateCarree())
	ax[per_idx,0].set_xticklabels(np.linspace(7,17, 6))
	ax[per_idx,0].xaxis.set_tick_params(labelsize=8)
	ax[per_idx,0].yaxis.set_tick_params(labelsize=8)
	lon_formatter = cticker.LongitudeFormatter(direction_label=False)
	lat_formatter = cticker.LatitudeFormatter(direction_label=False)
	ax[per_idx,0].yaxis.set_major_formatter(lat_formatter)
	ax[per_idx,0].xaxis.set_major_formatter(lon_formatter)
	ax[per_idx,0].grid(linewidth=2, color='black', alpha=0.0, linestyle='--')


# Opening JSON file
f_covid = open('DBs/jsons/yearly_median_ext_covid.json')
# returns JSON object as a dictionary
data = json.load(f_covid)

for per_idx, (period, vmin, vmax) in enumerate(zip(periods,vmins,vmaxs)):
	print(period,vmin,vmax)
	stnames = []; stlos = []; stlas = []; dif = []; 
	for sta in data[period]:
		if sta in long_stas:
			val = data[period][sta]
			st_inx = dpc_db[dpc_db['sta'] == sta].index.tolist()[0]
			stla = dpc_db['lat'][st_inx]
			stlo = dpc_db['lon'][st_inx]
			stlas.append(stla)
			stlos.append(stlo)
			stnames.append(sta)
			dif.append(val)

	dif = np.array(dif)
	fig, ax[per_idx,1] = draw_map(fig,ax[per_idx,1],stnames,stlos,stlas,dif,vmin,vmax)
	# LAT-LON Grids
	import cartopy.mpl.ticker as cticker
	ax[per_idx,1].set_yticks(np.linspace(37,46,4), crs=ccrs.PlateCarree())
	ax[per_idx,1].set_yticklabels(np.linspace(37,46,4))
	ax[per_idx,1].yaxis.tick_left()
	ax[per_idx,1].set_xticks(np.linspace(7,17, 6), crs=ccrs.PlateCarree())
	ax[per_idx,1].set_xticklabels(np.linspace(7,17, 6))
	ax[per_idx,1].xaxis.set_tick_params(labelsize=8)
	ax[per_idx,1].yaxis.set_tick_params(labelsize=8)
	lon_formatter = cticker.LongitudeFormatter(direction_label=False)
	lat_formatter = cticker.LatitudeFormatter(direction_label=False)
	ax[per_idx,1].yaxis.set_major_formatter(lat_formatter)
	ax[per_idx,1].xaxis.set_major_formatter(lon_formatter)
	ax[per_idx,1].grid(linewidth=2, color='black', alpha=0.0, linestyle='--')


ax = ax.ravel()
for idx, axes in enumerate(ax):
	axes.text(-0.1, 1.02, annotations[idx] + ')', transform=axes.transAxes, size=12)


plt.savefig('Figures/Fig1.png',dpi=300, bbox_inches='tight')
plt.savefig('Figures/Fig1.svg',dpi=300, bbox_inches='tight')
