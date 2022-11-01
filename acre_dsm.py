#%%
from osgeo import gdal
dataset = gdal.Open(r'/Users/jhasneha/Library/CloudStorage/OneDrive-purdue.edu/Fall2022/DOE/lidar/in2017_01702115_12_dsm.tiff')
band1 = dataset.GetRasterBand(1).ReadAsArray()

# %%
import numpy as np
import rasterio as rio
from rasterio.plot import show
import matplotlib.pyplot as plt
from pyproj import Proj, transform
dem = rio.open("/Users/jhasneha/Library/CloudStorage/OneDrive-purdue.edu/Fall2022/DOE/lidar/in2017_01702115_12_dsm.tiff")
dem_array = dem.read(1).astype('float64')

# %%
fig, ax = plt.subplots(1)
show(dem_array, cmap="Greys_r", ax=ax)
#show(dem_array, contour=True, ax=ax, linewidths=0.7)

plt.axis('off')
plt.show()
# %%
import richdem as rd
dem_richdem = rd.rdarray(dem_array, no_data=-9999)
# %%
fig = rd.rdShow(dem_richdem, axes=False, cmap="bone");
fig
# %%
import matplotlib as mpl
mpl.rcParams['figure.dpi'] =600
dem_slope = rd.TerrainAttribute(dem_richdem, attrib="aspect")
fig=rd.rdShow(dem_slope, axes=False, cmap="jet", figsize=(20,20));
fig
# %%
import rioxarray
beck=rioxarray.open_rasterio("/Users/jhasneha/Documents/spring2022/DOE/SSURGO/lidar/beck_whole.tiff")



# %%
from pyproj import CRS
epsg = beck.rio.crs.to_epsg()
#%%
crs = CRS(epsg)
crs

# %%
from pyproj import CRS
crs=CRS.from_epsg(9003)


# %%
crss=crs.to_epsg()

# %%
from zipfile import ZipFile
 
kmz = ZipFile("/Users/jhasneha/Downloads/home128_rx_Target Rate (Count).kmz", 'r')
kml = kmz.open('doc.kml', 'r').read()
# %%
from osgeo import gdal
import numpy as np
dataset = gdal.Open("/Users/jhasneha/Library/CloudStorage/OneDrive-purdue.edu/spring2022/DOE/AGMRI/3_default_farm_07_27_2021_veg.tiff")
channel = np.array(dataset.GetRasterBand(1).ReadAsArray())
# %%
print("Driver: {}/{}".format(dataset.GetDriver().ShortName,
                            dataset.GetDriver().LongName))
#%%                          
print("Size is {} x {} x {}".format(dataset.RasterXSize,
                                    dataset.RasterYSize,
                                    dataset.RasterCount))
#%%
print("Projection is {}".format(dataset.GetProjection()))
geotransform = dataset.GetGeoTransform()
if geotransform:
    print("Origin = ({}, {})".format(geotransform[0], geotransform[3]))
    print("Pixel Size = ({}, {})".format(geotransform[1], geotransform[5]))





"""At this time access to raster data via GDAL is done one band at a time. Also, there is metadata, block sizes, 
color tables, and various other information available on a band by band basis. The following codes fetches a GDALRasterBand object 
from the dataset (numbered 1 through GDALRasterBand::GetRasterCount()) and displays a little information about it."""

# %%
band = dataset.GetRasterBand(1)
print("Band Type={}".format(gdal.GetDataTypeName(band.DataType)))

min = band.GetMinimum()
max = band.GetMaximum()
if not min or not max:
    (min,max) = band.ComputeRasterMinMax(True)
print("Min={:.3f}, Max={:.3f}".format(min,max))

if band.GetOverviewCount() > 0:
    print("Band has {} overviews".format(band.GetOverviewCount()))

if band.GetRasterColorTable():
    print("Band has a color table with {} entries".format(band.GetRasterColorTable().GetCount()))



"""There are a few ways to read raster data, 
but the most common is via the GDALRasterBand::RasterIO() method. 
This method will automatically take care of data type conversion, up/down sampling and windowing. 
The following code will read the first scanline of data into a similarly sized buffer, 
converting it to floating point as part of the operation."""
# %%
scanline = band.ReadRaster(xoff=0, yoff=0,
                        xsize=band.XSize, ysize=1,
                        buf_xsize=band.XSize, buf_ysize=1,
                        buf_type=gdal.GDT_Float32)
"""Note that the returned scanline is of type string, and contains xsize*4 bytes of raw binary floating point data. 
This can be converted to Python values using the struct module from the standard library:"""
# %%
import struct
tuple_of_floats = struct.unpack('f' * band.XSize, scanline)

# %%
