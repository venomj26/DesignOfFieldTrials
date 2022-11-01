#%%
from cv2 import exp
import pandas as pd 
import numpy as np 
import os
import geopandas


#%%
# Function that returns the yaxes position and xaxes domain for subplots r=1, c > 1
def xaxes_dom_yaxes_pos(gap=0.1, rows=5):
    #gap is the horizontal spacing between plot windows

    if rows < 5:
        raise ValueError('This funtion works for subplots with 1 rows and cols>2')
    l_window=  (1-gap)/rows
    d = l_window*3/10/2
    
    w = np.zeros((cols,6))
    #xaxis{k} has the domain [w[k-1][2],w[k-1][-3], for k=1, cols
    #w[j][1], w[j][-2] give the left, resp right yaxis associated to the default yaxis of the plot window, j=0 , cols-1
    for k in range(cols):
        start = k*(l_window+gap)#start point in [0, 1] of the plot window (subplot cell)
        end = start+l_window #end point in [0, 1] of the plot window
        w[k]  =  [start, start+d, start+2*d, end-2*d, end-d, end]
    return w

# %%
rootFilePath="/Users/jhasneha/Library/CloudStorage/OneDrive-purdue.edu/spring2022/DOE/doe_weather/WHIN_Weather_Sample_Data"

list_df=[]
for files in sorted(os.listdir(rootFilePath)):
    print("filename", files)
    # fileNameList=files.partition(".")
    # fileName=fileNameList[0]
    df=pd.read_csv(rootFilePath+'/'+files)
    list_df.append(df)
df_weatherData=pd.concat(list_df)

    
# %%
df_weatherData.shape
# %%
df_weatherData.columns.to_list()
# %%
df_weatherData.describe()

#%%
df_weatherData.dtypes

#datetime index can be used directly for indexing the values just in case that is easier 
#%%
from datetime import datetime
df_weatherData["year"]=pd.DatetimeIndex(df_weatherData["observation_time"]).year
# df_weatherData["month"]=pd.DatetimeIndex(df_weatherData["observation_time"]).month
df_weatherData["date"]=pd.DatetimeIndex(df_weatherData["observation_time"]).month


# %%
import plotly.express as px
#factor="soil_temp_4"
def plot_yearly(df, filename, factor):
    # df_map=df_weatherData[["station_id","latitude","longitude","soil_temp_1","soil_temp_2","soil_temp_3","soil_temp_4","year"]].copy()
    df_map=df[["name","latitude","longitude"]].copy()

    gdf = geopandas.GeoDataFrame(
    df_map, geometry=geopandas.points_from_xy(df_map.longitude, df_map.latitude))
    geo_df = gdf
    #geo_df['YLD_VOL_DR']=geo_df['YLD_VOL_DR'].astype(float) 
    px.set_mapbox_access_token(open("mbtoken.mapbox_token").read())
    #px.set_mapbox_access_token("pk.eyJ1IjoidmVub21qIiwiYSI6ImNrY3Z0c3ZhYzA3cHYyeHFsZXk4cXQwMmIifQ.kYc2bb8QRPiZ1L9CBqgtLw")

    fig = px.scatter_mapbox(geo_df,lat=geo_df.geometry.y,lon=geo_df.geometry.x,
                        # hover_name="station_id",
                        hover_name="name",
                        #hover_data=["YLD_VOL_DR"],
                        mapbox_style="satellite-streets",
                        # color=geo_df[factor],
                        #animation_frame="year",
                        color_discrete_sequence=["fuchsia"],
                        zoom=8,
                        size_max=3,
                        height=500)

    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    fig.write_html(filename+".html")
    figure=fig.show()
    return(figure)

#%%
plot_yearly(df_weatherData,"stations","name")

# %%
df_weatherstation=pd.read_csv("/Users/jhasneha/Library/CloudStorage/OneDrive-purdue.edu/DOE_code/WHIN/location.csv")

# %%

#rootfilepath="/Users/jhasneha/Library/CloudStorage/OneDrive-purdue.edu/spring2022/DOE/doe_weather/ACRE_mesonetTablehrly.xlsx"
rootfilepath="/Users/jhasneha/Library/CloudStorage/OneDrive-purdue.edu/summer2022/DOE/weather/ACRE/mesonetAcre/1staugust2022/aug1(Hrly).xlsx"
df_acreWeather=pd.read_excel(rootfilepath, sheet_name='Sheet 1')
df_acreWeatherCopy=df_acreWeather.copy()

#%%
df_acreWeather.columns=df_acreWeather.columns.str.replace('"', 'in')
df_acreWeather.columns=df_acreWeather.columns.str.replace(' ', '_')
df_acreWeather.columns=df_acreWeather.columns.str.replace(' ', '_')


#%%
from datetime import datetime
df_acreWeather["year"]=pd.DatetimeIndex(df_acreWeather["Time_(LST)"]).year
df_acreWeather["month"]=pd.DatetimeIndex(df_acreWeather["Time_(LST)"]).month_name().str[:3]
df_acreWeather["time"]=pd.DatetimeIndex(df_acreWeather["Time_(LST)"]).time
df_acreWeather["date"]=pd.DatetimeIndex(df_acreWeather["Time_(LST)"]).date



"""  subset of the whole data sset wherre soil moisture has values
 """
#%%
df_acreWeather_test = df_acreWeather[df_acreWeather['20in_Soil_Temp_(°F)'].notna()]






#%%
df_acreWeather2021= df_acreWeather_test.loc[df_acreWeather['year'] >2020]
df_acreWeather2021["Time_(LST)"]=pd.to_datetime(df_acreWeather2021["Time_(LST)"])

#create an index column to have a unique id for plotting
df_acreWeather2021 = df_acreWeather2021.reset_index()
df_acreWeather2021= df_acreWeather2021.rename(columns={'index':'measurement_ID'})



""" precipitation event"""

#%%
g=df_acreWeather2021['Precipitation_(in)'].eq(0).shift().bfill().cumsum()
df_acreWeather2021["cont_rain"]=df_acreWeather2021.groupby(g)['Precipitation_(in)'].cumsum()




""" GDD calculation"""
#%%
Tbase=50
df_test=df_acreWeather2021[["Air_Temp_(°F)","date" ]].copy()
# from datetime import datetime
df_gdd=df_test.groupby("date").max()
df_gdd=df_gdd.rename(columns={"Air_Temp_(°F)":"max_temp"})
df_gdd["min_temp"]=df_test.groupby("date").min()
df_gdd["max_gdd_temp"]=df_gdd.apply(lambda x:  x["max_temp"] if  x["max_temp"]< 87 else 86, axis=1)
df_gdd["min_gdd_temp"]=df_gdd.apply(lambda x:  50 if  x["min_temp"]< 50 else x["min_temp"], axis=1)
df_gdd["gdd"]= ((df_gdd["max_gdd_temp"] + df_gdd["min_gdd_temp"])/2 )-Tbase
df_gdd["gdd_positive"]=df_gdd.apply(lambda x:  0 if  x["gdd"]< 0 else x["gdd"], axis=1)
df_gdd_cumulative=df_gdd.copy()
df_gdd_cumulative=df_gdd_cumulative.reset_index()
df_gdd_cumulative["year"]=pd.DatetimeIndex(df_gdd_cumulative["date"]).year
df_gdd_cumulative['Cumulative_gdd'] = df_gdd_cumulative.groupby(["year"])['gdd_positive'].cumsum() 


#df_gdd= df_gdd.groupby()



""" FAO penman-Monteith equation"""

#%%
df_acreWeather2021_FAO=df_acreWeather2021.copy()

#%%
import math
from datetime import timedelta
g=0.66 #psychometric constant from annex table 2.2 for altitude 200m
GSC=0.0820 #MJ m(-2)min(-1)
latRad=40.470233 *math.pi/180 #latitudee of Acre in decimal degrees is 40.470233
lz=75 #eastern time zone constant
long= 86.991811 #longitude of Acre
t1=1 # 1 for hourly and 0.5 for half hourly
z=200 #elevation of acre field in meters
a=0.23 #albedo or canopy reflectioncoefficient, 0.23 is albedo for hypothetical grass reference crop [dimensionless]
s=2.043*pow(10,-10) #stefan-boltzman constant in MJ m(-2) hour(-1). It is different for daily and hourly calculation.
df_acreWeather2021_FAO["Rs_MJ"]=(df_acreWeather2021_FAO["Solar_Radiation_(kW/m²)"]*0.36)
df_acreWeather2021_FAO["Air_Temp_degC"]=(df_acreWeather2021_FAO["Air_Temp_(°F)"]- 32) * (5 / 9)
df_acreWeather2021_FAO["D_mid"]=(df_acreWeather2021_FAO["Air_Temp_degC"]*17.27)/(df_acreWeather2021_FAO["Air_Temp_degC"]+237.3)
df_acreWeather2021_FAO["D"]=4098*(0.6108* np.exp(df_acreWeather2021_FAO["D_mid"]))/((df_acreWeather2021_FAO["Air_Temp_degC"]+237.3)**2)
df_acreWeather2021_FAO["eDegT"]=0.6108* pow(2.7183,(df_acreWeather2021_FAO["D_mid"])) #np.exp and pow(2.7183,power) both methods are same
df_acreWeather2021_FAO["eA"]= df_acreWeather2021_FAO["eDegT"]*(df_acreWeather2021_FAO["Relative_Humidity_(%)"]/100)
df_acreWeather2021_FAO["dayOfYear"]=pd.DatetimeIndex(df_acreWeather2021_FAO["date"]).dayofyear
df_acreWeather2021_FAO["inverseRelativeDistanceEarthSun"]=1+ 0.033* np.cos(2* math.pi*df_acreWeather2021_FAO["dayOfYear"]/365)
df_acreWeather2021_FAO["solar_declination"]=0.409* np.sin(2* math.pi *df_acreWeather2021_FAO["dayOfYear"]/365 -1.39)
df_acreWeather2021_FAO["seasonalCorrection"]= 0.1645 *np.sin(2* (2*math.pi*(df_acreWeather2021_FAO["dayOfYear"]-81)/364))-0.1255*np.cos((2*math.pi*(df_acreWeather2021_FAO["dayOfYear"]-81)/364)) -0.025*np.sin((2*math.pi*(df_acreWeather2021_FAO["dayOfYear"]-81)/364))

df_acreWeather2021_FAO["midHourObject"]=df_acreWeather2021_FAO["Time_(LST)"].dt.strftime("%H%M")
df_acreWeather2021_FAO["midHour"]=(df_acreWeather2021_FAO["midHourObject"].astype(float)/100)-0.5
df_acreWeather2021_FAO["solarTimeAngleMidHour"]=(math.pi/12)*((df_acreWeather2021_FAO["midHour"]+0.6667*(lz-long)+df_acreWeather2021_FAO["seasonalCorrection"])-12)
df_acreWeather2021_FAO["solarTimeAngleStart"]=df_acreWeather2021_FAO["solarTimeAngleMidHour"]-math.pi*t1/24
df_acreWeather2021_FAO["solarTimeAngleEnd"]=df_acreWeather2021_FAO["solarTimeAngleMidHour"]+math.pi*t1/24


df_acreWeather2021_FAO["Ra"]=(12*60/math.pi)*GSC*df_acreWeather2021_FAO["inverseRelativeDistanceEarthSun"]*((df_acreWeather2021_FAO["solarTimeAngleEnd"]-df_acreWeather2021_FAO["solarTimeAngleStart"])* math.sin(latRad)*np.sin(df_acreWeather2021_FAO["solar_declination"]) + math.cos(latRad)*np.cos(df_acreWeather2021_FAO["solar_declination"])*(np.sin(df_acreWeather2021_FAO["solarTimeAngleEnd"])- np.sin(df_acreWeather2021_FAO["solarTimeAngleStart"])) )
df_acreWeather2021_FAO["Rso"]= (0.75+ 2* pow(10,-5)*z) * df_acreWeather2021_FAO["Ra"]
df_acreWeather2021_FAO["Rns"]=(1-a)*df_acreWeather2021_FAO["Rs_MJ"]
df_acreWeather2021_FAO["cloudCover"]=df_acreWeather2021_FAO["Rs_MJ"]/df_acreWeather2021_FAO["Rso"]
df_acreWeather2021_FAO["Rnl"]=df_acreWeather2021_FAO["Air_Temp_degC"]*s*(0.34-0.14*np.sqrt(df_acreWeather2021_FAO["eA"]))*(1.35*df_acreWeather2021_FAO["cloudCover"]-0.35)
df_acreWeather2021_FAO["Rn"]=df_acreWeather2021_FAO["Rns"]-df_acreWeather2021_FAO["Rnl"]

df_acreWeather2021_FAO["Ghr"]= df_acreWeather2021_FAO.apply (lambda x: 0.5* x["Rn"] if x["Rs_MJ"]==0.0 else 0.1*x["Rn"],axis=1 )

df_middleterm1=0.408* df_acreWeather2021_FAO["D"]*(df_acreWeather2021_FAO["Rn"]-df_acreWeather2021_FAO["Ghr"])
#1 mph = 0.44704 m/s
df_middleterm1_2= g*df_acreWeather2021_FAO["Wind_Speed_(mph)"]*0.44704*(df_acreWeather2021_FAO["eDegT"]-df_acreWeather2021_FAO["eA"])*(37/(273+df_acreWeather2021_FAO["Air_Temp_degC"]))
df_middleterm1_3=df_acreWeather2021_FAO["D"]+g*(1+ (0.34*df_acreWeather2021_FAO["Wind_Speed_(mph)"]*0.44704))

df_acreWeather2021_FAO["ET0_(mm/hr)"]=(df_middleterm1+df_middleterm1_2)/df_middleterm1_3




#%%




# %%
import plotly.graph_objects as go
from matplotlib.colors import colorConverter

fc=30
pwp=15
mad=0.55
# w = xaxes_dom_yaxes_pos()


# Create figure
fig = go.Figure()

fc_r = colorConverter.to_rgba('red', alpha=0.4)



# Add traces
fig.add_trace(go.Scatter(
    x=df_acreWeather2021["Time_(LST)"],
    y=df_acreWeather2021['20in_Soil_Temp_(°F)'],
    name="20in_ST",
    text=df_acreWeather2021['20in_Soil_Temp_(°F)'],
    line=dict(
        color='chocolate'
                    ),
    yaxis="y10",
))

fig.add_trace(go.Scatter(
    x=df_acreWeather2021["Time_(LST)"],  
    y=df_acreWeather2021['20in_Soil_Water_Content_(%)'],
    name="20in_WC",
    text=df_acreWeather2021['20in_Soil_Water_Content_(%)'],
    line=dict(
        color='deepskyblue'
                    ),
    yaxis="y4",
))

fig.add_trace(go.Scatter(
    x=df_acreWeather2021["Time_(LST)"],
    y=df_acreWeather2021['4in_Soil_Temp_(°F)'],
    name="4in_ST",
    text=df_acreWeather2021['4in_Soil_Temp_(°F)'],
    line=dict(
        color='salmon'
                    ),
    yaxis="y10",
))

fig.add_trace(go.Scatter(
    x=df_acreWeather2021["Time_(LST)"],
    y=df_acreWeather2021['4in_Soil_Water_Content_(%)'],
    name="4in_WC",
    text=df_acreWeather2021['4in_Soil_Water_Content_(%)'],
    line=dict(
        color='royalblue'
                    ),
    yaxis="y4",
))
fig.add_trace(go.Scatter(
    x=df_acreWeather2021["Time_(LST)"],
    y=df_acreWeather2021['Air_Temp_(°F)'],
    name="Air_Temp_",
    text=df_acreWeather2021['Air_Temp_(°F)'],
    line=dict(
        color='red'
                    ),
    yaxis="y3",
))
fig.add_trace(go.Scatter(
    x=df_acreWeather2021["Time_(LST)"],
    y=df_acreWeather2021['Relative_Humidity_(%)'],
    name="Relative_Humidity",
    text=df_acreWeather2021['Relative_Humidity_(%)'],
    line=dict(
        color='orchid'
                    ),
    yaxis="y7",
))

fig.add_trace(go.Scatter(
    x=df_acreWeather2021["Time_(LST)"],
    y=df_acreWeather2021['Wind_Speed_(mph)'],
    name="wind_speed",
    text=df_acreWeather2021['Wind_Speed_(mph)'],
    line=dict(
        color='grey'
                    ),
    yaxis="y",
))
fig.add_trace(go.Scatter(
    x=df_acreWeather2021["Time_(LST)"],
    y=df_acreWeather2021["Precipitation_(in)"],
    name="Rain",
    fill="tozeroy",
    text=df_acreWeather2021["Precipitation_(in)"],
    line=dict(
        color='darkblue'
                    ),
    yaxis="y2",
))

fig.add_trace(go.Scatter(
    x=df_gdd_cumulative["date"],
    y=df_gdd_cumulative["Cumulative_gdd"],
    name="GDD",
    fill="tozeroy",
    text=df_gdd_cumulative["Cumulative_gdd"],
    line=dict(
        color='lime',
                    ),
    yaxis="y8",
))
fig.add_trace(go.Scatter(
    x=df_acreWeather2021_FAO["Time_(LST)"],
    y=df_acreWeather2021_FAO["ET0_(mm/hr)"],
    name="ET0",
    #fill="tozeroy",
    text=df_acreWeather2021_FAO["ET0_(mm/hr)"],
    line=dict(
        color='orangered',
                    ),
    yaxis="y9",
))
fig.add_trace(go.Scatter(
    x=df_acreWeather2021_FAO["Time_(LST)"],
    y=df_acreWeather2021_FAO["Solar_Radiation_(kW/m²)"],
    name="Solar Radiation",
    #fill="tozeroy",
    text=df_acreWeather2021["Solar_Radiation_(kW/m²)"],
    line=dict(
        color='gold',
                    ),
    yaxis="y5",
))
#there is some problem in this styling traces part of the code
# style all the traces
# fig.update_traces(
#     hoverinfo="name+x+text",
#     line={"width": 0.5},
#     marker={"size": 8},
#     mode="lines+markers",
#     showlegend=False
# )

# Add annotations
fig.update_layout(
    annotations=[
        dict(
            x="0.1",
            showarrow=False,
            y=fc+2,
            text="FC%",
            xref="paper",
            yref="y4"
        ),
        dict(
            x="0.1",
            showarrow=False,
            y=pwp+2,
            text="PWP%",
            xref="paper",
            yref="y4"
        ),
        dict(
            x="0.1",
            showarrow=False,
            y=pwp+2,
            text="PWP%",
            xref="paper",
            yref="y4"
        ),
        dict(
            x="0.1",
            showarrow=False,
            y=fc+2,
            text="FC%",
            xref="paper",
            yref="y4"
        ),
        dict(
            x="0.8",
            showarrow=False,
            y=pwp+4,
            align="right",
            text="MAD",
            xref="paper",
            yref="y4"
        ),
        dict(
            x="0.8",
            showarrow=False,
            y=pwp+4,
            text="MAD",
            xref="paper",
            yref="y4"
        ),
        dict(
            x="0.1",
            showarrow=False,
            y=0.2,
            text="heavyRain",
            xref="paper",
            yref="y2"
        ),
        dict(
            x="0.1",
            showarrow=False,
            y=0.5,
            text="veryHeavyRain",
            xref="paper",
            yref="y2"
        ),
        # dict(
        #     x="0.1",
        #     showarrow=False,
        #     y=0.5,
        #     text="Total cloud cover",
        #     xref="paper",
        #     yref="y10"
        # )
    ],
)

#Add shapes
fig.update_layout(
    shapes=[
        dict(
            line={"width": 1, "color":"green"},
            type="line",
            x0=0,
            x1=0.85,
            name="FC%",
            xref="paper",
            y0=fc,
            y1=fc,
            yref="y4"
        ),
    
        dict(
            line={"width": 1, "color":"red"},
            type="line",
            x0=0,
            x1=0.85,
            name="PWP%",
            xref="paper",
            y0=pwp,
            y1=pwp,
            yref="y4"
        ),
    
        dict(
            fillcolor="orange",
            opacity=0.2,
            line={"width": 1, "color":"orange"},
            type="rect",
            x0=0,
            x1=0.85,
            name="MAD",
            xref="paper",
            y0=pwp,
            y1=pwp+((fc-pwp)*mad),
            yref="y4"
        ),
        dict(
            # fillcolor="orange",
            # opacity=0.2,
            line={"width": 1, "color":"orange"},
            type="line",
            x0=0,
            x1=0.85,
            name="heavyRain",
            xref="paper",
            y0=0.15748,
            y1=0.15748,
            yref="y2"
        ),
        dict(
            # fillcolor="orange",
            # opacity=0.2,
            line={"width": 1, "color":"red"},
            type="line",
            x0=0,
            x1=0.85,
            name="VeryHeavyRain",
            xref="paper",
            y0=0.314961,
            y1=0.314961,
            yref="y2"
        ),
        dict(
            # fillcolor="orange",
            # opacity=0.2,
            line={"width": 1, "color":"green"},
            type="line",
            x0=0,
            x1=0.85,
            xref="paper",
            y0=0,
            y1=0,
            yref="y8"
        ),
        # dict(
        #     # fillcolor="orange",
        #     # opacity=0.2,
        #     line={"width": 1, "color":"grey"},
        #     type="line",
        #     x0=0,
        #     x1=0.85,
        #     xref="paper",
        #     y0=0.3,
        #     y1=0.3,
        #     yref="y10"
        # ),
        
    ]
)

# Update axes
fig.update_layout(
    xaxis=dict(
        domain=[0,0.85],
        range=[df_acreWeather2021["Time_(LST)"].min(), df_acreWeather2021["Time_(LST)"].max()],
        rangeslider=dict(
            autorange=True,
            range=[df_acreWeather2021["Time_(LST)"].min(), df_acreWeather2021["Time_(LST)"].max()],
        ),
        type="date"
    ),
    yaxis5=dict(
        title='S_Rad (kW/m²)',
        titlefont=dict(
            color='peru'
        ),
        range=[df_acreWeather2021['Solar_Radiation_(kW/m²)'].min(),df_acreWeather2021['Solar_Radiation_(kW/m²)'].max()],
        autorange=True,
        domain=[0.2,0.4],
        tickfont=dict(
            color='peru'
        ),
        tickmode="auto",
        ticks="",
        showline=True,
        linecolor='peru',
        anchor="x",
        side='left',
        type="linear",
        position=0.9
    ),
    
    yaxis10=dict(
        
        autorange=True,
        domain=[0.2,0.4],
        linecolor="orangered",
        mirror=True,
        range=[df_acreWeather2021['4in_Bare_Soil_Temp_(°F)'].min(),df_acreWeather2021['4in_Bare_Soil_Temp_(°F)'].max()],
        showline=True,
        tickfont={"color": "orangered"},
        tickmode="auto",
        ticks="",
        overlaying='y5',
        title="Soil Temp(°F)",
        titlefont={"color": "orangered"},
        anchor='free',
        side='right',
        type="linear",
        position=0.9    
        ),


    yaxis4=dict(
        anchor="x",
        autorange=True,
        domain=[0.6, 0.8],
        linecolor="blue",
        mirror=True,
        range=[df_acreWeather2021['20in_Soil_Water_Content_(%)'].min(),df_acreWeather2021['20in_Soil_Water_Content_(%)'].max()],
        showline=True,
        side="left",
        tickfont={"color": "blue"},
        tickmode="auto",
        ticks="",
        title="Water Content(%)",
        titlefont={"color": "blue"},
        type="linear",
        zeroline=False
    ),
    
    yaxis3=dict(
        anchor="x",
        autorange=True,
        domain=[0.4, 0.6],
        linecolor="red",
        mirror=True,
        range=[df_acreWeather2021["Air_Temp_(°F)"].min(),df_acreWeather2021['Air_Temp_(°F)'].max()],
        showline=True,
        side="left",
        tickfont={"color": "red"},
        tickmode="auto",
        ticks="",
        title="Air_Temp(°F)",
        titlefont={"color": "red"},
        type="linear",
        zeroline=False
    ),
    
    yaxis2=dict(
        anchor="x",
        autorange=True,
        domain=[0.8,1],
        linecolor="darkblue",
        mirror=True,
        range=[df_acreWeather2021['Precipitation_(in)'].min(),df_acreWeather2021['Precipitation_(in)'].max()],
        showline=True,
        side="left",
        tickfont={"color": "darkblue"},
        tickmode="auto",
        ticks="",
        title="Rain(in)",
        titlefont={"color": "darkblue"},
        type="linear",
        zeroline=False
    ),
    yaxis=dict(
        title='wind(mph)',
        titlefont=dict(
            color='black'
        ),
        range=[(df_acreWeather2021['Wind_Speed_(mph)']).min(),(df_acreWeather2021['Wind_Speed_(mph)']).max()],
        autorange=True,
        domain=[0, 0.2],
        tickfont=dict(
            color='black'
        ),
        tickmode="auto",
        ticks="",
        showline=True,
        linecolor='black',
        anchor="x",
        side='left',
        type="linear",
    ),
    yaxis8=dict(
        title='GDU',
        titlefont=dict(
            color='darkgreen'
        ),
        range=[df_gdd_cumulative['Cumulative_gdd'].min(),df_gdd_cumulative['Cumulative_gdd'].max()],
        autorange=True,
        domain=[0.4, 0.6],
        tickfont=dict(
            color='green'
        ),
        tickmode="auto",
        ticks="",
        showline=True,
        linecolor='green',
        anchor='free',
        overlaying='y3',
        side='right',
        type="linear",
        position=0.85
    ),
    yaxis9=dict(
        title='Et0(mm/hr)',
        titlefont=dict(
            color='orangered'
        ),
        range=[df_acreWeather2021_FAO['ET0_(mm/hr)'].min(),df_acreWeather2021_FAO['ET0_(mm/hr)'].max()],
        autorange=True,
        domain=[0,0.2],
        tickfont=dict(
            color='orangered'
        ),
        tickmode="auto",
        ticks="",
        showline=True,
        linecolor='orangered',
        anchor='free',
        overlaying='y',
        side='right',
        type="linear",
        position=0.85
    ),
    
    yaxis7=dict(
        autorange=True,
        domain=[0.8, 1],
        linecolor="magenta",
        mirror=True,
        range=[df_acreWeather2021['Relative_Humidity_(%)'].min(),df_acreWeather2021['Relative_Humidity_(%)'].max()],
        showline=True,
        side="right",
        anchor="free",
        overlaying='y2',
        tickfont={"color": "magenta"},
        tickmode="auto",
        ticks="",
        title="Relative Humidity(%)",
        titlefont={"color": "magenta"},
        type="linear",
        position=0.9

    )
    
)
# fig.update_layout(legend=dict(
#     yanchor="bottom",
#     y=0.1,
#     xanchor="right",
#     x=0.99
# ))

# Update layout
# fig.update_layout(
#     dragmode="zoom",
#     hovermode="x",
#     legend=dict(traceorder="reversed"),
#     height=600,
#     template="plotly_white",
#     margin=dict(
#         t=100,
#         b=100
#     ),
# )
# fig.update_layout(
#     width=500,
#     height=500,
#     margin=dict(l=20, r=20, t=20, b=20),
#     paper_bgcolor="LightSteelBlue",
# )

fig.write_html("ET_august1st22_acre_hourly_20in4incomparison2021_test.html")
fig.show()




# %%
import numpy as np
import pandas as pd
 
import matplotlib.pyplot as plt
from scipy import stats
measured_param='4in_Soil_Water_Content_(%)'
calculated_param='4in_Soil_Temp_(°F)'
x=df_acreWeather2021_FAO[measured_param] 
y=df_acreWeather2021_FAO[calculated_param]

ax=plt.subplot()

#create scatterplot
plt.scatter(x, y)
result_regress= stats.linregress(x,y)

line = result_regress.slope*x+result_regress.intercept
print("p-value for a hypothesis test whose null hypothesis is that the slope is zero: ",result_regress.pvalue)
print("Slope and Standard error of the estimated slope (gradient), under the assumption of residual normality: ", result_regress.slope, result_regress.stderr)
print("Intercept and Standard error of the estimated intercept, under the assumption of residual normality: ", result_regress.intercept,  result_regress.intercept_stderr)
plt.plot(x, line, 'black', label="R-square value = "+ str(round((result_regress.rvalue**2),2)))
plt.title(measured_param+' vs. '+calculated_param)
plt.xlabel(measured_param)
plt.ylabel(calculated_param)
plt.legend()
plt.show()



# %%
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from scipy.interpolate import UnivariateSpline

func = UnivariateSpline(x, y)

measured_param='4in_Soil_Water_Content_(%)'
calculated_param='4in_Soil_Temp_(°F)'
x=df_acreWeather2021_FAO[measured_param] 
y=df_acreWeather2021_FAO[calculated_param]


popt, pcov = curve_fit(func, x, y)
print(popt)
# plt.plot(x, func(xdata, *popt), 'r-',
#          label='fit: a=%5.3f, b=%5.3f, c=%5.3f' % tuple(popt))

# # popt, pcov = curve_fit(func, xdata, ydata, bounds=(0, [3., 1., 0.5]))
# # plt.plot(xdata, func(xdata, *popt), 'g--',
# #          label='fit: a=%5.3f, b=%5.3f, c=%5.3f' % tuple(popt))

# plt.xlabel('x')
# plt.ylabel('y')
# plt.legend()
# plt.show()

# %%
