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

def draw_map(fig,ax,stname,stlos,stlas,data,vmin,vmax):
	# Limit the extent of the map to a small longitude/latitude range.
	ax.set_extent([6.90, 18.55, 36.5, 47], crs=ccrs.Geodetic())
	# Add the Stamen data at zoom level 8.
	# request = cimgt.OSM()
	request = cimgt.GoogleTiles(style='satellite',)
	ax.add_image(request, 8, interpolation='bilinear')
	# Add data points
	day_map = ax.scatter(stlos, stlas, marker='^', c=data,
	 s=20, alpha=0.7, transform=ccrs.Geodetic(), 
	 cmap='seismic', vmin=vmin, vmax=vmax)
	# Colorbar
	ticks = np.linspace(vmin, vmax, 7)
	cbar = plt.colorbar(day_map, ax= ax, orientation='vertical',extend='both',ticks=ticks,format=tick.FormatStrFormatter('%.1f'))
	cbar.ax.tick_params(labelsize=6) 
	cbar.set_label('Power Change (dB)', rotation=90,size=8)
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
	ax.xaxis.set_tick_params(labelsize=8)
	ax.yaxis.set_tick_params(labelsize=8)
	lon_formatter = cticker.LongitudeFormatter(direction_label=False)
	lat_formatter = cticker.LatitudeFormatter(direction_label=False)
	ax.yaxis.set_major_formatter(lat_formatter)
	ax.xaxis.set_major_formatter(lon_formatter)
	ax.grid(linewidth=2, color='black', alpha=0.0, linestyle='--')

	return fig, ax


# Opening Day JSON file
f = open('DBs/jsons/day_ext.json')
# returns JSON object as 
# a dictionary
day = json.load(f)

# Opening Day Covid JSON file
f = open('DBs/jsons/day_ext_covid.json')
# returns JSON object as 
# a dictionary
dayc = json.load(f)

# Opening Night JSON file
f = open('DBs/jsons/night_ext.json')
# returns JSON object as 
# a dictionary
night = json.load(f)

# Opening Night Covid JSON file
f = open('DBs/jsons/night_ext_covid.json')
# returns JSON object as 
# a dictionary
nightc = json.load(f)

# Read Station Info
dpc_db = pd.read_csv('DBs/station_attributes.csv')

# 90+
ninety = pd.read_csv('DBs/ninetyplus.csv')
long_stas = ninety.Station.tolist()

# Define Figure
# Create a Stamen terrain background instance.
stamen_terrain = cimgt.Stamen('terrain-background')

fig,axs = plt.subplots(4,2, figsize=(9,15), facecolor='w', edgecolor='k',subplot_kw={'projection': stamen_terrain.crs}, gridspec_kw = {'wspace':0, 'hspace':0.1})
axs = axs.ravel()
# Annotation
annotations = list(string.ascii_lowercase)

periods = ['0.0992','0.25','0.5','1.0']

# Find common stations
day_stas = []; dayc_stas = []; night_stas = []; nightc_stas = [];
for period in periods:
	for sta in day[period]:
		if sta not in day_stas:
			day_stas.append(sta)
	for sta in dayc[period]:
		if sta not in dayc_stas:
			dayc_stas.append(sta)
	for sta in night[period]:
		if sta not in night_stas:
			night_stas.append(sta)
	for sta in nightc[period]:
		if sta not in nightc_stas:
			nightc_stas.append(sta)
total_stas = [day_stas, dayc_stas, night_stas, nightc_stas]
common_stas = list(set(total_stas[0]).intersection(*total_stas))

increment = 0
for per_idx, period in enumerate(periods):
	stnames = []; stlos = []; stlas = []; difd = []; difn = []; 
	for sta in common_stas:
		if sta in long_stas:
			# No Covid
			no_covid = np.median(day[period][sta])
			no_covidn = np.median(night[period][sta])
			# Covid
			covid = np.median(dayc[period][sta])
			covidn = np.median(nightc[period][sta])
			vald = no_covid - covid
			valn = no_covidn - covidn
			st_inx = dpc_db[dpc_db['sta'] == sta].index.tolist()[0]
			stla = dpc_db['lat'][st_inx]
			stlo = dpc_db['lon'][st_inx]
			stlas.append(stla)
			stlos.append(stlo)
			stnames.append(sta)
			difd.append(vald)
			difn.append(valn)

	# Day vmax
	difd = np.array(difd)
	abs_dif = np.absolute(difd)
	vmaxd = np.nanpercentile(abs_dif, 95)
	# Night vmax
	difn = np.array(difn)
	abs_dif = np.absolute(difn)
	vmaxn = np.nanpercentile(abs_dif, 95)

	if per_idx == 0:
		increment += 1
		# Day Covid Dif
		fig, ax = draw_map(fig,axs[per_idx],stnames,stlos,stlas,difd,-vmaxd,vmaxd)
		axs[per_idx].text(-0.10, 1.02, annotations[per_idx] + ')', transform=axs[per_idx].transAxes, size=15)
		# Night Covid Dif
		fig, ax = draw_map(fig,axs[per_idx+1],stnames,stlos,stlas,difn,-vmaxn,vmaxn)
		axs[per_idx+1].text(-0.10, 1.02, annotations[per_idx+1] + ')', transform=axs[per_idx+1].transAxes, size=15)
	elif per_idx == 1:
		increment += 1
		# Day Covid Dif
		fig, ax = draw_map(fig,axs[increment],stnames,stlos,stlas,difd,-vmaxd,vmaxd)
		axs[increment].text(-0.10, 1.02, annotations[increment] + ')', transform=axs[increment].transAxes, size=15)
		# Night Covid Dif
		fig, ax = draw_map(fig,axs[increment+1],stnames,stlos,stlas,difn,-vmaxn,vmaxn)
		axs[increment+1].text(-0.10, 1.02, annotations[increment+1] + ')', transform=axs[increment+1].transAxes, size=15)
	elif per_idx > 1:
		increment += 2
		# Day Covid Dif
		fig, ax = draw_map(fig,axs[increment],stnames,stlos,stlas,difd,-vmaxd,vmaxd)
		axs[increment].text(-0.10, 1.02, annotations[increment] + ')', transform=axs[increment].transAxes, size=15)
		# Night Covid Dif
		fig, ax = draw_map(fig,axs[increment+1],stnames,stlos,stlas,difn,-vmaxn,vmaxn)
		axs[increment+1].text(-0.10, 1.02, annotations[increment+1] + ')', transform=axs[increment+1].transAxes, size=15)

axs[increment+1].text(0.30, -0.10, 'Red = 2022 Noisier', transform=axs[increment+1].transAxes, size=8)
plt.savefig('Figures/Fig4.png',dpi=300, bbox_inches='tight')
plt.savefig('Figures/Fig4.svg',dpi=300, bbox_inches='tight')
