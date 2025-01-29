import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.transforms import offset_copy
import matplotlib.ticker as tick
import cartopy.crs as ccrs
import cartopy.io.img_tiles as cimgt
import glob, warnings, os
from datetime import datetime, timedelta
import string
warnings.filterwarnings("ignore")

def draw_map(fig,ax,stname,stlos,stlas,data,vmin,vmax):
	# Limit the extent of the map to a small longitude/latitude range.
	ax.set_extent([6.90, 18.55, 36.5, 47], crs=ccrs.Geodetic())
	# Add the Stamen data at zoom level 8.
	request = cimgt.GoogleTiles(style='satellite',)
	ax.add_image(request, 8, interpolation='bilinear')
	# Add data points
	day_map = ax.scatter(stlos, stlas, marker='^', c=data,
	 s=40, alpha=0.9, transform=ccrs.Geodetic(), 
	 cmap='seismic',vmin=vmin,vmax=vmax)
	# Colorbar
	ticks = np.linspace(vmin, vmax, 7)
	cbar = plt.colorbar(day_map, ax= ax, orientation='vertical',extend='both',ticks=ticks,format=tick.FormatStrFormatter('%.1f'))
	cbar.ax.tick_params(labelsize=12) 
	cbar.set_label(r'Power Change (dB)', rotation=90, size=16)
	# Use the cartopy interface to create a matplotlib transform object
	# for the Geodetic coordinate system. We will use this along with
	# matplotlib's offset_copy function to define a coordinate system which
	# translates the text by 25 pixels to the left.
	geodetic_transform = ccrs.Geodetic()._as_mpl_transform(ax)
	text_transform = offset_copy(geodetic_transform, units='dots', x=-25)
	# LAT-LON Grids
	import cartopy.mpl.ticker as cticker
	ax.set_yticks(np.linspace(37,46,4), crs=ccrs.PlateCarree())
	ax.set_yticklabels(np.linspace(37,46,4))
	ax.yaxis.tick_left()
	ax.set_xticks(np.linspace(7,17, 6), crs=ccrs.PlateCarree())
	ax.set_xticklabels(np.linspace(7,17, 6))
	ax.xaxis.set_tick_params(labelsize=12)
	ax.yaxis.set_tick_params(labelsize=12)
	lon_formatter = cticker.LongitudeFormatter(direction_label=False)
	lat_formatter = cticker.LatitudeFormatter(direction_label=False)
	ax.yaxis.set_major_formatter(lat_formatter)
	ax.xaxis.set_major_formatter(lon_formatter)
	ax.grid(linewidth=2, color='black', alpha=0.0, linestyle='--')
	return fig, ax


# Opening JSON file
f = open('DBs/jsons/yearly_median_ext_covid_diff.json')
# returns JSON object as 
# a dictionary
data = json.load(f)

# 90+
ninety = pd.read_csv('DBs/ninetyplus.csv')
long_stas = ninety.Station.tolist()

# Read Station Info
dpc_db = pd.read_csv('DBs/station_attributes.csv')

# Define Figure
# Create a Stamen terrain background instance.
stamen_terrain = cimgt.Stamen('terrain-background')
fig,axs = plt.subplots(2,2, figsize=(18, 17), facecolor='w', edgecolor='k',subplot_kw={'projection': stamen_terrain.crs}, gridspec_kw = {'wspace':0, 'hspace':0.1})
axs = axs.ravel()
# Annotation
annotations = list(string.ascii_lowercase)

periods = ['0.0992','0.25','0.5','1.0']

stas = []; difs = []; pers = [];
total_db = pd.DataFrame(columns=['Period', 'Station', 'Value'])
for per_idx, period in enumerate(periods):
	print(period)
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
			total_db = total_db._append(pd.Series([float(period),sta,val], index=['Period', 'Station', 'Value']), ignore_index=True) 
	dif = np.array(dif)

	abs_dif = np.absolute(dif)
	vmax = np.nanpercentile(abs_dif, 95)
	fig, ax = draw_map(fig,axs[per_idx],stnames,stlos,stlas,dif,-vmax,vmax)
	axs[per_idx].text(-0.05, 1.02, annotations[per_idx] + ')', transform=axs[per_idx].transAxes, size=15)

# periods = total_db.Period.unique()
# for period in periods:
# 	per_db = total_db[total_db.Period == period]
# 	per_db.to_csv('../DBs/CovidDif/' + str(period) + '.csv',index=False)

axs[-1].text(0.45, -0.05, 'Red = 2022 Noisier', transform=axs[per_idx].transAxes, size=8)
plt.savefig('Figures/Fig3.png',dpi=300, bbox_inches='tight')
plt.savefig('Figures/Fig3.svg',dpi=300, bbox_inches='tight')
