import altair as alt
import pandas as pd
import streamlit as st
from modules.datasets import load_data_deezer, load_data_spotify, load_data

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

#Load the datasets
DEEZER_PATH = 'data/deezer-data_2175171744.xlsx'
SPOTIFY_PATH = 'data/Spotify_Audio_2013-2024_251124.json'

dee = load_data_deezer(DEEZER_PATH)
spot = load_data_spotify(SPOTIFY_PATH)
data = load_data(dee,spot)

# Show a slider widget with the years using `st.slider`.
years = st.slider("Year", 2019, 2024, (2020, 2024))
data_year = data[data["Year"].between(years[0], years[1])]

# Display the platform usage during these years
st.header("Listening time per platform - " + str(years[0]) + " to "+ str(years[1]))
data_platform = data_year.pivot_table(
    index="Year", columns="Platform", values="Listening Time (s)", aggfunc="sum", fill_value=0
)
#data_platform = data_platform.sort_values(by="Year", ascending=False)
data_platform = round(data_platform/3600)

platform_chart = pd.melt(
    data_platform.reset_index(), id_vars="Year", var_name="Platform", value_name="Listening Time"
)
chart = (
    alt.Chart(platform_chart)
    .mark_bar()
    .encode(
        x=alt.X("Year:N", title="Year"),
        y=alt.Y("Listening Time:Q", title="Time listened (hours)"),
        color=alt.Color("Platform:N",  
                        scale=alt.Scale(domain=['Deezer', 'Spotify'],  
                                        range=['#a100ff', '#1db954']))
    )
    .properties(height=320)
)
st.altair_chart(chart, use_container_width=True)

# Display the platform usage depending on the month
st.header("Listening time per month \n " + str(years[0]) + " to "+ str(years[1]))
data_month = data_year.pivot_table(
    index="Year", columns="Month", values="Listening Time (s)", aggfunc="sum", fill_value=0
)
#data_month = data_month.sort_values(by="Year", ascending=False)
data_month = round(data_month/3600)

month_chart = pd.melt(
    data_month.reset_index(), id_vars="Year", var_name="Month", value_name="Listening Time"
)
chart = (
    alt.Chart(month_chart)
    .mark_line()
    .encode(
        x=alt.X("Month:N", title="Year"),
        y=alt.Y("Listening Time:Q", title="Time listened (hours)"),
        color=alt.Color("Year:N")
    )
    .properties(height=320)
)
st.altair_chart(chart, use_container_width=True)

#Show the top 10 artists and songs on the selected period
col1, col2 = st.columns(2)

with col1:
    st.header("Top 10 artists \n " + str(years[0]) + " to "+ str(years[1]))
    data_artists = data_year.explode('Artist')  # Dans le cas où 2 artistes ont contribué à une chanson, on duplique le temps d'écoute pour avoir chacun le temps d'écoute de la chanson

    top_artists = data_artists.pivot_table(
    index="Artist", columns="Year", values="Listening Time (s)", aggfunc="sum", fill_value=0
    )
    top_artists=top_artists.astype(float)
    top_artists['Total']=top_artists.sum(axis=1)
    top_artists = top_artists.sort_values(by="Total", ascending=False).head(10)
    top_artists = round(top_artists/60)
    top_artists = top_artists.drop('Total', axis=1)

    artists_chart = pd.melt(
    top_artists.reset_index(), id_vars="Artist", var_name="Year", value_name="Listening Time"
    )
    chart = (
    alt.Chart(artists_chart)
    .mark_bar()
    .encode(
        x=alt.X("Listening Time:Q", title="Time listened (min)"),
        y=alt.Y("Artist:N", title="Artist"),
        color=alt.Color("Year:N")
    )
    .properties(height=320)
    )
    st.altair_chart(chart, use_container_width=True)

with col2:
    st.header("Top 10 songs \n " + str(years[0]) + " to "+ str(years[1]))

    top_songs = data_year.pivot_table(
    index="Song Title", columns="Year", values="Listening Time (s)", aggfunc="sum", fill_value=0
    )
    top_songs=top_songs.astype(float)
    top_songs['Total']=top_songs.sum(axis=1)
    top_songs = top_songs.sort_values(by="Total", ascending=False).head(10)
    top_songs = round(top_songs/60)
    top_songs = top_songs.drop('Total', axis=1)

    songs_chart = pd.melt(
    top_songs.reset_index(), id_vars="Song Title", var_name="Year", value_name="Listening Time"
    )
    chart = (
    alt.Chart(songs_chart)
    .mark_bar()
    .encode(
        x=alt.X("Listening Time:Q", title="Time listened (min)"),
        y=alt.Y("Song Title:N", title="Song"),
        color=alt.Color("Year:N")
    )
    .properties(height=320)
    )
    st.altair_chart(chart, use_container_width=True)

#Show a multiselect widget with the favorite artists using `st.multiselect`.
artists = data_artists['Artist'].(str.split(',').explode().str.strip().dropna().unique()

fav = st.multiselect(
    "Preferred artists",
    sorted(artists),
    ["Alma","Ava Max", "Chilla","Dua Lipa","Ed Sheeran","Greyson Chance", "Hatik",  "Rihanna",
     "Lomepal", "Therapie TAXI", "Tove Lo" ],
)

# Filter the dataframe based on the widget input and reshape it.
data_filtered = data_artists[data_artists["Artist"].isin(fav)]
#En utilisant data_artists, on fait quelques approximations : si on prenait le temps total de tous les artistes, on aurait un total bien supérieur à la réalité puisqu'une chanson
#avec plusieurs artistes est comptée autant de fois qu'il y'a d'artistes 

#data_final=pd.DataFrame(columns = data.columns) # On construit un DataFrame dans lequel ne sont conservés que les noms d'artistes contenant les noms sélectionnés
#for index, row in data_artists.iterrows():
    #for artist in fav :
        #if artist in row["Artist"] :
            #data_final.loc[len(data_final)] = row 
    


data_reshaped = data_filtered.pivot_table(
    index="Year", columns="Artist", values="Listening Time (s)", aggfunc="sum", fill_value=0
)
data_reshaped = data_reshaped.sort_values(by="Year", ascending=False)
data_reshaped = round(data_reshaped/60) # Transforming into minutes 

st.text("Listening time per artist on the selected period")
# Display the data as a table using `st.dataframe`.
with st.expander("See values"):
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
        y=alt.Y("Listening Time:Q", title="Time listened (min)"),
        color="Artist:N",
    )
    .properties(height=320)
)
st.altair_chart(chart, use_container_width=True)
