import altair as alt
import pandas as pd
import streamlit as st

# Show the page title and description.
st.set_page_config(page_title="Deezer data", page_icon="🎶")
st.title("🎶 Listening history dataset")
st.write(
    """
    This app visualizes data from Deezer data export.
    It shows which songs performed best in Marion's heart over the years. 
    Just click on the widgets below to explore!
    """
)

# Load the data from a CSV. We're caching this so it doesn't reload every time the app
# reruns (e.g. if the user interacts with the widgets).
@st.cache_data
def load_data_deezer():
    dee = pd.read_excel('data/deezer-data_2175171744.xlsx', sheet_name='10_listeningHistory', )
    return dee

@st.cache_data
def load_data_spotify():
    spot = pd.read_json('data/spotify_data_251124.json')
    return spot

dee = load_data_deezer()
spot = load_data_spotify()





#Show a multiselect widget with the favorite artists using `st.multiselect`.
fav = st.multiselect(
    "Preferred artists",
    df.Artist.unique(),
    ["Alma","Anne-Marie","Ava Max", "Chilla","Dua Lipa","Ed Sheeran","Greyson Chance", "Hatik", "Justin Bieber", "Rihanna",
     "Lomepal","Robin Schulz", "Therapie TAXI", "Tove Lo" ],
)

# Show a slider widget with the years using `st.slider`.
df['Date'] = pd.to_datetime(df['Date'])
df['Year'] = df['Date'].dt.year
years = st.slider("Year", 2019, 2024, (2020, 2024))

# Filter the dataframe based on the widget input and reshape it.
df_filtered = df[(df["Artist"].isin(fav)) & (df["Year"].between(years[0], years[1]))]
#df_filtered = df[df["year"].between(years[0], years[1])]
df_reshaped = df_filtered.pivot_table(
    index="Year", columns="Artist", values="Listening Time", aggfunc="sum", fill_value=0
)
df_reshaped = df_reshaped.sort_values(by="Year", ascending=False)

# Display the data as a table using `st.dataframe`.
st.dataframe(
    df_reshaped,
    use_container_width=True,
    column_config={"Year": st.column_config.TextColumn("Year")},
)

#Display the data as an Altair chart using `st.altair_chart`.
df_chart = pd.melt(
    df_reshaped.reset_index(), id_vars="Year", var_name="Artist", value_name="Listening Time"
)
chart = (
    alt.Chart(df_chart)
    .mark_line()
    .encode(
        x=alt.X("Year:N", title="Year"),
        y=alt.Y("Listening Time:Q", title="Time listened (s)"),
        color="Artist:N",
    )
    .properties(height=320)
)
st.altair_chart(chart, use_container_width=True)
