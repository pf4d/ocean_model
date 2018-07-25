"""
Create a whole-ocean mesh. The final product is a 2D mesh in North polar 
stereographic projection.

You may need to truncate the input data in order to scale the problem for your
particular amount of system memory.  The parameter ``n_skip`` can be changed 
to remove all but every ``n_skip`` elements from the data.  Using ``n_skip = 2`` requires about 20 GB of memory.  Island contours must contain at least five
nodes.

Using ``n_skip = 2`` and ``skip_pts = 1`` :
 
  Mesh statistics :

    number of islands     : 2517
    time to mesh 2D plane : 21.4 minutes
    total time to compute : 31.0 minutes
    number of elements    : 42,094,019
    number of vertices    : 20,964,839

Using ``n_skip = 2`` and ``skip_pts = 10`` :
 
  Mesh statistics :

    number of islands     : 420
    time to mesh 2D plane : 52.98 seconds
    total time to compute : 136.7 seconds
    number of elements    : 2,395,834
    number of vertices    : 1,184,363

  * test system consisted of a Xeon E5-1620 v4 clocked at 3.50GHz.
"""

from gmsh_meshgenerator import MeshGenerator, print_text
from pylab              import *
from netCDF4            import Dataset
from pyproj             import Proj, transform
from time               import time

t0 = time() # start the timer

# every other ``n_skip`` data points will be removed :
n_skip = 2

# get the data :
data = Dataset('../data/RTopo-2.0.1_1min_aux.nc', 'r')
mask = data['amask'][:]
lat  = data['lat'][:]
lon  = data['lon'][:]

# reduce the size of the dataset by 50% for easy plotting :
mask = np.delete(mask, list(range(0, mask.shape[0], n_skip)), axis=0)
mask = np.delete(mask, list(range(0, mask.shape[1], n_skip)), axis=1)

lon  = np.delete(lon,  list(range(0, len(lon), n_skip)))
lat  = np.delete(lat,  list(range(0, len(lat), n_skip)))

# create a grid of lon/lat coordinates :
LON, LAT = np.meshgrid(lon, lat)

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

msh_name = 'crude_mesh'      # name of all outputs
out_dir  = 'meshes/'         # directory for all outputs
S        = mask              # mathematical function to contour
S[S>0.1] = 1.0               # no shelves, etc.
skip_pts = 10                # number of contour points to skip

# the MeshGenerator instance initialized with the matrix coordinates,
# output file name, and output directory :
m = MeshGenerator(X, Y, msh_name, out_dir)

# create and add contours from S.  Parameter "skip_pts" are the number of 
# contour nodes to remove from the resulting contour, if a lower-resolution
# contour is desired.  Parameter "distance_check" is the distance from each node
# to check for edge intersections which may arise from removing points; 
# increase the distance if overlaps occur :
m.create_contour(S, zero_cntr=0.1, skip_pts=skip_pts,
                 distance_check=50, min_nodes=5)

# if points have been removed, land masses may overlap and therefore must be
# combined :
if skip_pts > 0:  m.unify_overlapping_contours()

# plot the resulting contours :
#m.plot_contour(legend=False)

# write the gmsh contour to the "msh_name".geo file with characteristic 
# cell diameter "lc".  If "boundary_extend"=True, the edge size of the contour 
# is extrapolated into the interior :
m.write_gmsh_contour(lc=10000000, boundary_extend=True)#False)

# get the number of contours for the mesh :
num_ctrs = m.num_contours()
#
## add identical edge attractors to all contours with sequential identifier.
## the parameter "NNodesByEdge" adds extra nodes to the edge for the purpose
## of refinement, increase this if your edges are much longer than your 
## cell refinement "lcMin" set by m.add_threshold() below :
#for i in range(num_ctrs):
#  m.add_edge_attractor(field=i, contour_index=i, NNodesByEdge=3)
#
## for each edge attractor, add a threshold for mesh refinement in the vicinity 
## of the edge :
#for i in range(num_ctrs):
#  # parameters are respectively: field, ifield, lcMin, lcMax, distMin, distMax
#  m.add_threshold(num_ctrs+i, i, 1000000, 10000000, 0, 20000000)

# finialize the creation of the "msh_name".geo file :
m.finish()

# instruct gmsh to create the mesh, saving to a "msh_name".msh 
# file in "out_dir" :
m.create_mesh()

# convert the "msh_name".msh file to a "msh_name".xml.gz file used by FEniCS :
#m.convert_msh_to_xml()

# display the total compute time :
print_text("total time to compute: %g seconds" % (time() - t0), 'red', 1)



