import pandas as pd
import streamlit as st

# We're caching this so it doesn't reload every time the app
# reruns (e.g. if the user interacts with the widgets).
@st.cache_data
def load_data_deezer(deezer):
    dee = pd.read_excel(deezer, sheet_name='10_listeningHistory')
    dee = dee.drop(columns=['Platform Name', 'Platform Model'])
    dee.Date = pd.to_datetime(dee.Date,format='%Y-%m-%d %H:%M:%S')
    dee = dee.rename(columns={"Listening Time" : "Listening Time (s)"})
    dee['conn_country']=dee['ISRC'].apply(lambda x: x[0:2])
    return dee

@st.cache_data
def load_data_spotify(spotify):
    spot = pd.read_json(spotify)
    spot = spot.iloc[:,0:9]
    spot['Listening Time (s)']=round(spot['ms_played']/1000,0)
    spot = spot.drop(columns=['platform', 'ms_played'])
    spot = spot.rename(columns={'ts': 'Date', 
                     'ip_addr':"IP Address",
                      'master_metadata_track_name': 'Song Title',
                      'master_metadata_album_artist_name' : 'Artist', # This is an approximation since Spotify doesn't take the song artist but the album artist
                      'master_metadata_album_album_name' : 'Album Title'})

    spot.Date = pd.to_datetime(spot.Date, format ="%Y-%m-%dT%H:%M:%SZ" )
    return spot

@st.cache_data
def load_data(dee,spot):
    data = pd.concat([dee,spot])
    data = data[data['Song Title'].isna()== False]
    data['Year'] = data['Date'].dt.year
    data['Month'] = data['Date'].dt.month
    data = data[data.Year > 2018]
    data['spotify_track_uri'] = data['spotify_track_uri'].astype(str) 
    data['Platform']=data['spotify_track_uri'].apply(lambda x: "Deezer" if x == 'nan' else "Spotify")
    return data
