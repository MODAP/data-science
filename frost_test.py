# Resolve the latest GFS dataset
import metpy
from siphon.catalog import TDSCatalog
import sys
import numpy as np
import matplotlib
matplotlib.use('Agg')	#Avoid the need for X11 forwarding

#------------------------
# Set up access via NCSS.
#------------------------
# We can plot just about anything from https://thredds.ucar.edu/thredds/catalog.html
# Use this to plot GFS output
#catalog = ('http://thredds.ucar.edu/thredds/catalog/grib/NCEP/GFS/'
#               'Global_0p5deg/catalog.xml?dataset=grib/NCEP/GFS/Global_0p5deg/Best')
#
# Here, let's plot the latest HRRR model analysis
catalog = ('https://thredds.ucar.edu/thredds/catalog/grib/NCEP/HRRR/CONUS_2p5km_ANA/catalog.xml')

# This works, but...
#cat = TDSCatalog(catalog)
#ncss = cat.datasets[0].subset()

# ...this is faster
from siphon.catalog import get_latest_access_url
from siphon.ncss import NCSS
latest = get_latest_access_url(catalog,"NetcdfSubset")
ncss = NCSS(latest)

# We can see what variables are available from ncss
print(ncss.variables)

# From here, we can build a query to ask for the data we want from the server
from datetime import datetime, timedelta

# Create a new NCSS query
query = ncss.query()

# Request data in netCDF format
query.accept('netcdf')

# Ask for a specific variable (or variables with a comma-delimited set of strings)
query.variables('Temperature_isobaric', 'Geopotential_height_isobaric')

# Ask for the 850 hPa surface. Native units are pascals.
#query.vertical_level(85000)	#This works for a single variable, but not for two or more because
								#the number and values of levels might be different. Handle this later.

# Set the time range of the data we want
now = datetime.utcnow()	#This grabs the current system time and saves it as a datetime object
#query.time_range(now, now + timedelta(days=1))	#This sets a range from now to a day from now (use this for forecasts)
query.time_range(now - timedelta(hours=3), now)	#For the latest HRRR data, we want to find data within the last 3 hours. THREDDS can be slow (adjust as needed).

# Set the spatial limits. If this is left out, we plot the whole domain.
#query.lonlat_box(west=-110, east=-45, north=50, south=10)

# Get the data
data = ncss.get_data(query)

########################
# Making sense of netCDF
########################

#View the properties of our data
print(type(data))

#We can use a library called XArray to make working with this a little simpler
from xarray.backends import NetCDF4DataStore
import xarray as xr

# Use NetCDFDataStore to open and read the existing netCDF dataset we downloaded
ds = xr.open_dataset(NetCDF4DataStore(data))

# Grab a specific dataset
temp_var = ds.metpy.parse_cf('Temperature_isobaric')
print(temp_var)
z_var = ds.metpy.parse_cf('Geopotential_height_isobaric')
print(z_var)

# XArray handles parsing things like dates, times, latitude, and longitude for us. This is so much easier than it used to be!
latitude = temp_var.metpy.y
longitude = temp_var.metpy.x

#-------
# Levels
#-------
# Select a level to plot. We can even choose different levels for each variable!
level = 85000
temp_var = temp_var.metpy.sel(vertical=level)
z_var = z_var.metpy.sel(vertical=level)

# Explore the available levels here if you want
#temp_levels = temp_var['isobaric']
#print("Temperature levels:",temp_levels)
#z_levels = z_var['isobaric1']
#print("Height levels:",z_levels)
#-------

####################
# Visualize the grid
####################

import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib.pyplot as plt

# The GFS uses a lon/lat grid
#data_projection = ccrs.PlateCarree()

# The HRRR uses a specific Lambert Conformal grid called the AWIPS 184 grid. See the parameters here: https://www.nco.ncep.noaa.gov/pmb/docs/on388/tableb.html#GRID184
# You can specify the parameters of your projection: https://scitools.org.uk/cartopy/docs/latest/crs/projections.html
# Set the map projection with the specific grid parameters (note that the grid parameters are also embedded within the data)
data_projection = ccrs.LambertConformal(central_longitude=-95.000,central_latitude=25.000)

# Make it easy to change what time step we look at
t_step = 0

#-------------
# Color tables
#-------------
# Look at the documentation for metpy.plots.colortables (https://unidata.github.io/MetPy/latest/api/generated/metpy.plots.ctables.ColortableRegistry.html)
# or choose one from here: https://matplotlib.org/examples/color/colormaps_reference.html
# Here are the custom color tables that MetPy supports: https://unidata.github.io/MetPy/latest/api/generated/metpy.plots.ctables.html
# Put '_r' at the end of any colormap name to reverse it.

# Import for colortables
from metpy.plots import colortables
colormap=colortables.get_colortable('ir_rgbv')	#Use this only for the MetPy-specific color tables. Otherwise, comment out this line and put your Matplotlib color selection below
#colormap='rainbow'
#-------------

#-------------
# Create a figure and plot the data
#-------------
fig = plt.figure(figsize=(12, 8))
ax = fig.add_subplot(1, 1, 1, projection=ccrs.LambertConformal())
#ax = fig.add_subplot(1, 1, 1, projection=ccrs.PlateCarree())	#You can use a different projection if you like
mesh = ax.pcolormesh(longitude, latitude, temp_var[t_step].squeeze(),
                     transform=data_projection, zorder=0, cmap=colormap)

# Add contours of 850-mb geopotential height
contours = np.arange(1140, 1620, 30)
ax.contour(longitude, latitude, z_var[t_step].squeeze(), contours, colors='k',
           transform=data_projection, linewidths=0.75, zorder=1)

# Add some common geographic features
ax.add_feature(cfeature.COASTLINE.with_scale('50m'))
ax.add_feature(cfeature.STATES.with_scale('50m'), edgecolor='black')
ax.add_feature(cfeature.BORDERS.with_scale('50m'))

# Add some lat/lon gridlines
ax.gridlines()

# Add a colorbar
cax = fig.colorbar(mesh)
cax.set_label(temp_var.attrs['units'])

# Get a sensible datetime format
vtime = ds.time.data[0].astype('datetime64[ms]').astype('O')

# Add a title
ax.set_title(temp_var.metpy.time[t_step].values)

#plt.show()							#View the plot via a GUI window. Remove matplotlib.use('Agg') above. I suggest saving it instead (see the next line).
plt.savefig("outofthebox.png")		#Just reload this image in your browser for fast viewing
plt.close()

#-------------------------------------------------------------------------------------------------
##################################################################################################
##################################################################################################
# Create the following plots:
# 1) 850-mb temperature as a colored contour, along with geopotential heights and associated wind barbs
# 2) 500-mb divergence as a colored contour, along with geopotential heights and associated wind barbs
# 3) 500-mb vorticity as a colored contour, along with geopotential heights and associated wind barbs
# 4) 500-mb isotachs (colored, starting at 20 knots), along with geopotential heights and associated wind barbs

# NOTE: You are welcome to zoom in on a region of interest in each plot.

# Add a title to each plot. Post your code and all four maps on your password-protected webpage.
##################################################################################################
##################################################################################################
#-------------------------------------------------------------------------------------------------