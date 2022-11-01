#%%
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px

# %%
import geopandas

df_j4=pd.read_csv('/Users/jhasneha/Library/CloudStorage/OneDrive-purdue.edu/DOE_code/summer2021/DOE_ag/Soil data/SEPAC/J4/j4_2007_J4_nobuffer_harvest.csv')

#%%
rootfilepath='/Users/jhasneha/Library/CloudStorage/OneDrive-purdue.edu/DOE_code/summer2021/DOE_ag/Soil data/SEPAC/J4'
import os
import pathlib

#def create_df(rootfilepath):
root_files=os.listdir(rootfilepath)
df_yield_all=pd.DataFrame()

for entry in root_files:
    if not entry.startswith('.') and entry.endswith('.csv') :
        print (entry)
        df=pd.read_csv(rootfilepath+'/'+entry)
        df.columns=df.columns.str.replace(' ', '')
        df.columns=df.columns.str.replace(r'\([^)]*\)', '')
        df_yield_all=df_yield_all.append(df).fillna(0)





#df_j4=pd.read_csv('/Users/jhasneha/Documents/DOE/summer2021/Re__Ault_Harvest_Data/gott_east93_2012_harvest.csv',dtype="unicode", encoding= 'unicode_escape')
#%%
df_yield_all["XCoord"]=df_yield_all["XCoord"]+ df_yield_all["Longitude"]
df_yield_all["YCoord"]=df_yield_all["YCoord"]+ df_yield_all["Latitude"]

df_yield_all['DATE'] = pd.to_datetime(df_yield_all['DATE']).dt.normalize()

df_yield_all["DATE"]=pd.to_datetime(df_yield_all["DATE"],format='%Y-%m-%d')
df_yield_all["year"]=pd.DatetimeIndex(df_yield_all["DATE"]).year
df_yield_all=df_yield_all.sort_values(by=["year"],ascending=True)

#%%
df_corn=pd.DataFrame()
df_soybean=pd.DataFrame()
product=["CORN","CORN 2010", "CORN 2","15Corn-J4","Corn-F10"]
df_corn=df_yield_all[df_yield_all.PRODUCT.isin(product)]
df_corn=df_corn.sort_values(by=["year"],ascending=True)

product_=["SOYBEANS","Soybeans 2014"]
df_soybean=df_yield_all[df_yield_all.PRODUCT.isin(product_)]
df_soybean=df_soybean.sort_values(by=["year"],ascending=True)



#%%
import plotly.express as px
def plot_yearly(df, filename):
    dfj4_map=df[["YLD_VOL_DR","XCoord","YCoord","year","PRODUCT"]].copy()
    gdf_j4 = geopandas.GeoDataFrame(
    dfj4_map, geometry=geopandas.points_from_xy(dfj4_map.XCoord, dfj4_map.YCoord))
    geo_df = gdf_j4
    geo_df['YLD_VOL_DR']=geo_df['YLD_VOL_DR'].astype(float) 
    px.set_mapbox_access_token(open("/Users/jhasneha/Library/CloudStorage/OneDrive-purdue.edu/DOE_code/summer2021/DOE_ag/Weather/mbtoken.mapbox_token").read())
    #px.set_mapbox_access_token("pk.eyJ1IjoidmVub21qIiwiYSI6ImNrY3Z0c3ZhYzA3cHYyeHFsZXk4cXQwMmIifQ.kYc2bb8QRPiZ1L9CBqgtLw")
    
    fig = px.scatter_mapbox(geo_df,lat=geo_df.geometry.y,lon=geo_df.geometry.x,
                        hover_name="PRODUCT",
                        hover_data=["YLD_VOL_DR"],
                        mapbox_style="streets",
                        color=geo_df['YLD_VOL_DR'],
                        animation_frame="year",
                        zoom=8,
                        size_max=3,
                        height=900)

    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    # fig.write_html(filename+".html")
    figure=fig.show()
    return(figure)

#%%
plot_yearly(df_corn,"corn_j4")
plot_yearly(df_soybean,"soybean_j4")

#%%
df_stat_corn=df_corn[["YLD_VOL_DR","SPEED_MPH_","ELEVATION_","SWTH_WDTH_","MOISTURE__"]].copy()
df_stat_corn.describe()


#%%
df_corn["YLD_VOL_DR"]= df_corn["YLD_VOL_DR"].replace(0.0, np.nan)
df_corn= df_corn.dropna(axis=0,subset=['YLD_VOL_DR'])

df_soybean["YLD_VOL_DR"]= df_soybean["YLD_VOL_DR"].replace(0.0, np.nan)
df_soybean= df_soybean.dropna(axis=0,subset=['YLD_VOL_DR'])















"""#################################

bin analysis

###################################"""

#%%
# start=np.trunc(df_corn["YLD_VOL_DR"].min)
# stop=np.trunc(df)
# bins = np.arange(start=df_corn["YLD_"],stop=5.6, step=0.2)


df_corn["bin"]=(np.trunc(np.trunc(df_corn["YLD_VOL_DR"])/10))*10
dict_df=df_corn.groupby(["bin"]).mean().round(2).reset_index()
dict_gg=dict(zip(dict_df.bin,dict_df.YLD_VOL_DR))
df_corn['Mean_bin']=df_corn['bin'].map(dict_gg)












# %%
