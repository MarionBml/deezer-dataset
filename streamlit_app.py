import altair as alt
import pandas as pd
import streamlit as st

# Show the page title and description.
st.set_page_config(page_title="Deezer & Spotify data", page_icon="🎶")
st.title("🎶 Listening history dataset")
st.write(
    """
    This app visualizes data from Deezer & Spotify data export.
    It shows which songs performed best in Marion's heart since 2019. 
    Just click on the widgets below to explore!
    """
)

# We're caching this so it doesn't reload every time the app
# reruns (e.g. if the user interacts with the widgets).
@st.cache_data
def load_data_deezer():
    dee = pd.read_excel('data/deezer-data_2175171744.xlsx', sheet_name='10_listeningHistory')
    dee = dee.drop(columns=['Platform Name', 'Platform Model'])
    dee.Date = pd.to_datetime(dee.Date,format='%Y-%m-%d %H:%M:%S')
    dee = dee.rename(columns={"Listening Time" : "Listening Time (s)"})
    dee['conn_country']=dee['ISRC'].apply(lambda x: x[0:2])
    return dee

@st.cache_data
def load_data_spotify():
    spot = pd.read_json('data/Spotify_Audio_2013-2024_251124.json')
    spot['Listening Time (s)']=round(spot['ms_played']/1000,0)
    spot = spot.drop(columns=['platform', 'ms_played'])

    spot = spot.rename(columns={'ts': 'Date', 
                     'ip_addr':"IP Address",
                      'master_metadata_track_name': 'Song Title',
                      'master_metadata_album_artist_name' : 'Album Artist',
                      'master_metadata_album_album_name' : 'Album Title'})

    spot.Date = pd.to_datetime(spot.Date, format ="%Y-%m-%dT%H:%M:%SZ" )
    spot = spot.iloc[:,0:7]
    return spot

@st.cache_data
def load_data(dee,spot):
    data = pd.concat([dee,spot])
    data = data[data['Song Title'].isna()== False]
    data['Year'] = data['Date'].dt.year
    data = data[data.Year > 2018]
    data['spotify_track_uri'] = data['spotify_track_uri'].astype(str) 
    data['Platform']=data['spotify_track_uri'].apply(lambda x: "Deezer" if x == 'nan' else "Spotify")
    return data

dee = load_data_deezer()
spot = load_data_spotify()
data = load_data(dee,spot)

#Show a multiselect widget with the favorite artists using `st.multiselect`.
fav = st.multiselect(
    "Preferred artists",
    data.Artist.unique(),
    ["Alma","Anne-Marie","Ava Max", "Chilla","Dua Lipa","Ed Sheeran","Greyson Chance", "Hatik", "Justin Bieber", "Rihanna",
     "Lomepal","Robin Schulz", "Therapie TAXI", "Tove Lo" ],
)

# Show a slider widget with the years using `st.slider`.
data['Date'] = pd.to_datetime(data['Date'])
data['Year'] = data['Date'].dt.year
years = st.slider("Year", 2019, 2024, (2020, 2024))

# Filter the dataframe based on the widget input and reshape it.
data_filtered = data[(data["Artist"].isin(fav)) & (data["Year"].between(years[0], years[1]))]
#data_filtered = data[data["year"].between(years[0], years[1])]
data_reshaped = data_filtered.pivot_table(
    index="Year", columns="Artist", values="Listening Time", aggfunc="sum", fill_value=0
)
data_reshaped = data_reshaped.sort_values(by="Year", ascending=False)

# Display the data as a table using `st.dataframe`.
st.dataframe(
    data_reshaped,
    use_container_width=True,
    column_config={"Year": st.column_config.TextColumn("Year")},
)

#Display the data as an Altair chart using `st.altair_chart`.
data_chart = pd.melt(
    data_reshaped.reset_index(), id_vars="Year", var_name="Artist", value_name="Listening Time"
)
chart = (
    alt.Chart(data_chart)
    .mark_line()
    .encode(
        x=alt.X("Year:N", title="Year"),
        y=alt.Y("Listening Time:Q", title="Time listened (s)"),
        color="Artist:N",
    )
    .properties(height=320)
)
st.altair_chart(chart, use_container_width=True)
