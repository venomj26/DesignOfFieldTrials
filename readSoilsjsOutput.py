#%%
import json
import pandas as pd
import matplotlib
import numpy as np

# %%
# with open("/Users/jhasneha/Library/CloudStorage/OneDrive-purdue.edu/summer2022/DOE/SSURGO/output-soils-aultfields.json", "r") as read_file:
with open("/Users/jhasneha/Library/CloudStorage/OneDrive-purdue.edu/summer2022/DOE/SSURGO/output-soils-aultfields-GOTT93_large.json","r") as read_file:
    aultfarm = json.load(read_file)
# %%
aultfarmFormatted = json.dumps(aultfarm, indent=4)
print(aultfarmFormatted)

#%%
ault_yld=pd.read_csv("/Users/jhasneha/Library/CloudStorage/OneDrive-purdue.edu/DOE_code/summer2021/Re__Ault_Harvest_Data/gott_east93_2013_harvest.csv",encoding= 'unicode_escape')


# %%
mupolygonT=pd.DataFrame.from_dict(aultfarm["mupolygon"])
mupolygon=mupolygonT.T

componentT=pd.DataFrame.from_dict(aultfarm["component"])
component=componentT.T

chorizonT=pd.DataFrame.from_dict(aultfarm["chorizon"])
chorizon=chorizonT.T

mapunitT=pd.DataFrame.from_dict(aultfarm["mapunit"])
mapunit=mapunitT.T


# %%
componentSelectedColumns=component[['comppct_r','compname','compkind','runoff','drainagecl','elev_l','elev_r','elev_h','hydgrp','taxclname','taxorder',
 'taxsuborder','taxgrtgroup','taxsubgrp','mukey','cokey','chorizon']].copy()
# %%
chorizonSelectedColumns=chorizon[['hzdept_r','ph01mcacl2_l','ph01mcacl2_r','ph01mcacl2_h','ptotal_l','ptotal_r','ptotal_h','cokey','chkey']].copy()

# %%
mapunitSelectedColumns=mapunit[['musym','muname','mukind','farmlndcl','muhelcl','invesintens','mukey']].copy()
# %%
soilS=mupolygon.join(mapunitSelectedColumns, lsuffix='_mupolygon', rsuffix='_mapunit')
soilSSURGO=soilS.join(componentSelectedColumns,lsuffix='',rsuffix='_component')

#%%
soilSSURGO=soilSSURGO.rename(columns={"mupolygongeo":"geometry"})
musymList=list(soilSSURGO["musym_mupolygon"].unique())
def convertLstToDict(lst):
    res_dct = {lst[i]: i+1 for i in range(0, len(lst), 1)}
    return res_dct
musymdict=convertLstToDict(musymList)
soilSSURGO["musymCodeForColor"]=soilSSURGO["musym_mupolygon"].map(musymdict)

# %%
import folium


m = folium.Map(location=[30.744821613020875, 79.49125440581872], zoom_start=13)
m


#%%




#%%
import utm
ault_yld["latUTM"]=np.nan
ault_yld["lonUTM"]=np.nan
ault_yld["zone"]=np.nan
for index in range(len(ault_yld["Latitude"])):
    x=utm.from_latlon(ault_yld["Latitude"][index],ault_yld["Longitude"][index])
    ault_yld["latUTM"][index]=x[0]
    ault_yld["lonUTM"][index]=x[1]
    ault_yld["zone"][index]=str(x[2])+x[3]



#%%
import geopandas as gpd
soilSSURGO['geometry'] = gpd.GeoSeries.from_wkt(soilSSURGO['geometry'])
soilSSURGOgeo = gpd.GeoDataFrame(soilSSURGO, geometry='geometry')
soilSSURGOgeo=soilSSURGOgeo.set_crs('epsg:4326')

#%%
from shapely.geometry import Point, Polygon
dict_pt={}
soilSSURGO["geometryProj"]=np.nan
for index, row in soilSSURGO.iterrows():
    list_pt=[]
    for pt in list(row['geometry'].exterior.coords): 
        ptRev=pt[::-1]
        print(ptRev)
        projectedpt=utm.from_latlon(ptRev[0],ptRev[1])
        projectedCoords=projectedpt[0],projectedpt[1]
        print(projectedCoords)
        list_pt.append(projectedCoords)
    dict_pt[index]=list_pt
    print ("the point in the for loop denotes",dict_pt.keys())
    print("polygon is", Polygon(dict_pt[str(index)]))
    soilSSURGO["geometryProj"][index]= Polygon(dict_pt[str(index)])


#%%
""" GOTT 93 shape polygon coordinates from kml file"""
# %%
-86.1780901507896 40.99603597096603, -86.1781863693512 40.99304515435004, -86.18257318138112 40.99301162127941, -86.18204209372472 40.99166942290629, -86.18094069981052 40.99165004818988, -86.18096731521683 40.98946383884736, -86.17349865825189 40.98952131878603, -86.17336774199779 40.99495737158855, -86.17446671331301 40.99498398925493, -86.17449790155415 40.99581764731506, -86.1745265808937 40.99596165839267, -86.17469548032307 40.9960063394718, -86.17488112848748 40.99600524727202, -86.1749690362592 40.99589905248019, -86.17503786040234 40.9955421670162, -86.17507249582104 40.99521062325751, -86.17560253436575 40.99519486418392, -86.17562190060717 40.9960415864886, -86.1780901507896 40.99603597096603

#%%
import plotly.express as px
import geopandas
def plotOnMap(df):
    
    dfmap=df[["Longitude","Latitude","Estimated Volume (Dry)(bu/ac)"]].copy()
    gdfGPR = geopandas.GeoDataFrame(
    df, geometry=geopandas.points_from_xy(df.Latitude, df.Longitude))
    geo_df = gdfGPR
    # geo_df['Altitude']=geo_df['Altitude'].astype(float) 
    px.set_mapbox_access_token(open("/Users/jhasneha/Library/CloudStorage/OneDrive-purdue.edu/DOE_code/summer2021/DOE_ag/Weather/mbtoken.mapbox_token").read())
    #px.set_mapbox_access_token("pk.eyJ1IjoidmVub21qIiwiYSI6ImNrY3Z0c3ZhYzA3cHYyeHFsZXk4cXQwMmIifQ.kYc2bb8QRPiZ1L9CBqgtLw")

    fig = px.scatter_mapbox(geo_df,lat=geo_df.geometry.x,lon=geo_df.geometry.y,
                        hover_name="Estimated Volume (Dry)(bu/ac)",
                        # hover_data=["YLD_VOL_DR"],
                        mapbox_style="streets",
                        color=geo_df["Estimated Volume (Dry)(bu/ac)"],
                        # animation_frame="year",
                        zoom=12,
                        size_max=3,
                        height=900)

    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    fig.write_html("ault_GOTT93_soil.html")
    figure=fig.show()
    return(figure)

#%%
plotOnMap(ault_yld)

# %%

xmin, ymin, xmax, ymax = soilSSURGOgeo.total_bounds

centroidx = np.mean([xmin, xmax])
centroidy = np.mean([ymin, ymax])

map1 = folium.Map(
    location=[centroidy, centroidx],
    tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
    zoom_start=6,
    attr= 'Tiles &copy; Esri &mdash; Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community'
)

cmap = matplotlib.cm.get_cmap('gnuplot2')

# vmin = soilSSURGOgeo["muname"].min()
# vmax = soilSSURGOgeo[colname].max()
# list_color=[1,2,3,4,5]

# norm = matplotlib.colors.SymLogNorm(vmin=vmin, vmax=vmax, linthresh=0.1)
norm = matplotlib.colors.SymLogNorm(vmin=1, vmax=5, linthresh=0.1)

def fetchHexFromValue(value):
  NormedValue = norm(value)
  RGBAValue = cmap(NormedValue)
  HEXValue = matplotlib.colors.to_hex(RGBAValue)
  return HEXValue



# for idx, r in soilSSURGOgeo.iterrows():

#     lat = r["geometry"].centroid.y
#     lon = r["geometry"].centroid.x
#     # folium.Marker(location=[lat, lon],
#     #             #   popup='idx:{0} <br> {1}: {2}'.format(idx,
#     #             #                                        "muname", 
#     #             #                                        r["muname"])
#     ).add_to(map1)

soilSSURGOgeo.explore("musymCodeForColor", cmap="gnuplot2", m=map1)

map1

# %%
#%%

import folium
latlon = [ (40.995976,-86.183812), (40.995956,-86.168347), (40.990035,-86.168654), ( 40.989495, -86.181206), (40.995976, -86.183812)]
# poly=Polygon(latlon) #creates square from the latlon points
for coord in latlon:
    folium.Marker( location=[ coord[0], coord[1] ], fill_color='#43d9de', radius=8 ).add_to( map1 )

# folium.GeoJson(data=)
map1






#%%

for poly in range(len(soilSSURGO["geometry"])):
    print(soilSSURGO["geometry"][poly])
    polygonCheck=soilSSURGO["geometry"][poly]


# %%
ault_yldSliced=ault_yld[:]
ault_yldSliced["mupolygonkey"]=np.nan
from shapely.geometry import Point, Polygon
for index in range(len(ault_yldSliced["latUTM"])):
    point=Point(ault_yldSliced["Longitude"][index],ault_yldSliced["Latitude"][index])
    # print("point being checked:         ",point) 
    for poly in range(len(soilSSURGO["geometry"])):
        # print("polygon checking:  ",soilSSURGO["geometryProj"][poly])
        polygonCheck=soilSSURGO["geometry"][poly]
        # print(polygonCheck.contains(point))
        if polygonCheck.contains(point) == True:
            print("Found in:    ",poly, soilSSURGO["mupolygonkey"][poly])
            ault_yldSliced["mupolygonkey"][index]=soilSSURGO["mupolygonkey"][poly]
        else:
            # print("Not FOUND in", poly)
            continue



# %%
# soilSSURGO=soilSSURGO.reset_index()
for colnames in soilSSURGO.columns.to_list():
    print(colnames)
    dict_col=dict(zip(soilSSURGO["mupolygonkey"],soilSSURGO[colnames]))
    ault_yldSliced[colnames]=ault_yldSliced["mupolygonkey"].map(dict_col)




#%%
import plotly.express as px
import geopandas
def plotOnMap(df):
    
    dfmap=df[["Longitude","Latitude","Estimated Volume (Dry)(bu/ac)","musym_mupolygon"]].copy()
    gdfGPR = geopandas.GeoDataFrame(
    df, geometry=geopandas.points_from_xy(df.Latitude, df.Longitude))
    geo_df = gdfGPR
    # geo_df['Altitude']=geo_df['Altitude'].astype(float) 
    px.set_mapbox_access_token(open("/Users/jhasneha/Library/CloudStorage/OneDrive-purdue.edu/DOE_code/summer2021/DOE_ag/Weather/mbtoken.mapbox_token").read())
    #px.set_mapbox_access_token("pk.eyJ1IjoidmVub21qIiwiYSI6ImNrY3Z0c3ZhYzA3cHYyeHFsZXk4cXQwMmIifQ.kYc2bb8QRPiZ1L9CBqgtLw")

    fig = px.scatter_mapbox(geo_df,lat=geo_df.geometry.x,lon=geo_df.geometry.y,
                        hover_name="Estimated Volume (Dry)(bu/ac)",
                        # hover_data=["YLD_VOL_DR"],
                        mapbox_style="streets",
                        color=geo_df["Estimated Volume (Dry)(bu/ac)"],
                        # animation_frame="year",
                        zoom=12,
                        size_max=3,
                        height=900)

    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    fig.write_html("ault_GOTT93_soil.html")
    figure=fig.show()
    return(figure)

#%%
plotOnMap(ault_yldSliced)


# %%
