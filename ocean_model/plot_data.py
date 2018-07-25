from netCDF4              import Dataset
from mpl_toolkits.basemap import Basemap
from pyproj               import Proj, transform
import numpy                  as np
import matplotlib.pyplot      as plt

# NOTE: you'll have to download the data from :
#       http://hs.pangaea.de/Maps/RTopo-2.0.1/RTopo-2.0.1_1min_aux.nc
#       and put it in the ``../data`` directory.

# get the data :
data = Dataset('../data/RTopo-2.0.1_1min_aux.nc', 'r')
mask = data['amask'][:]
lat  = data['lat'][:]
lon  = data['lon'][:]

# reduce the size of the dataset for easy plotting :
mask = np.delete(mask, list(range(0, mask.shape[0], 2)), axis=0)
mask = np.delete(mask, list(range(0, mask.shape[1], 2)), axis=1)

lon  = np.delete(lon,  list(range(0, len(lon), 2)))
lat  = np.delete(lat,  list(range(0, len(lat), 2)))

# create a grid of lon/lat coordinates :
LON, LAT = np.meshgrid(lon, lat)
    
## plot the data with basemap :
#m = Basemap(projection='npstere', ellps='WGS84',
#            boundinglat=-88, lon_0=270, resolution='h')
#
## convert to projection coordinates :
#X,Y = m(LON, LAT)

#projection info :
proj   = 'stere'
lat_0  = '90'
lat_ts = '90'
lon_0  = '270'

# create projection :
txt  =   " +proj="   + proj \
       + " +lat_0="  + lat_0 \
       + " +lat_ts=" + lat_ts \
       + " +lon_0="  + lon_0 \
       + " +k=1 +x_0=0 +y_0=0 +no_defs +a=6378137 +rf=298.257223563" \
       + " +towgs84=0.000,0.000,0.000 +to_meter=1"
p    = Proj(txt)
    
# convert to projection coordinates :
X,Y = p(LON, LAT)

# plot :
#m.drawcoastlines()

fig  = plt.figure()
ax   = fig.add_subplot(111)
cs   = ax.contourf(X, Y, mask)
cbar = fig.colorbar(cs) 

ax.set_aspect('equal')
plt.tight_layout()
plt.show()



