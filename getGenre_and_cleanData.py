import pandas as pd
import numpy as np
import requests

import cleanLibraryJson

# Define variables
# The path to your original Library JSON file
input_filename = './Data/YourLibrary.json'
# The path where you want to save the cleaned Library JSON
output_filename = './Data/CleanedYourLibrary.json'
# save your IDs from new project in Spotify Developer Dashboard
CLIENT_ID = 'insert_client_id'
CLIENT_SECRET = 'insert_client_token'
# base URL of all Spotify API endpoints
BASE_URL = 'https://api.spotify.com/v1/'

# read streaming history from the downloaded spotify Data in the Extended streaming history folder
df_stream0 = pd.read_json('./Data/Spotify Extended Streaming History/Streaming_History_Audio_2019-2021_0.json')
df_stream1 = pd.read_json('./Data/Spotify Extended Streaming History/Streaming_History_Audio_2021-2022_1.json')
df_stream2 = pd.read_json('./Data/Spotify Extended Streaming History/Streaming_History_Audio_2022-2024_2.json')

# merge streaming dataframes
df_streaming = pd.concat([df_stream0,df_stream1,df_stream2])

# print head
print(df_streaming.head())

# clean the library json and export it
cleanLibraryJson.cleanLibraryJson(input_filename, output_filename)
# read the new Library json
df_library = pd.read_json(output_filename)

# add UniqueID column (same as above) spotify:track:5DUDLaokWUsRbU8XLuQM2y
df_library['UniqueID'] = df_library['artist'] + ":" + df_library['track']

# add column with track URI stripped of 'spotify:track:'
new = df_library["uri"].str.split(":", expand=True)
df_library['track_uri'] = new[2]

print(df_library.head())

# create final dict as a copy df_stream
df_tableau = df_streaming.copy()

# add column checking if streamed song is in library
# not used in this project but could be helpful for cool visualizations
df_tableau['In Library'] = np.where(df_tableau['spotify_track_uri'].isin(df_library['uri'].tolist()),1,0)

# generate access token
# authentication URL
AUTH_URL = 'https://accounts.spotify.com/api/token'

# POST
auth_response = requests.post(AUTH_URL, {
    'grant_type': 'client_credentials',
    'client_id': CLIENT_ID,
    'client_secret': CLIENT_SECRET,
})

# convert the response to JSON
auth_response_data = auth_response.json()

# save the access token
access_token = auth_response_data['access_token']

# used for authenticating all API calls
headers = {'Authorization': 'Bearer {token}'.format(token=access_token)}

# create blank dictionary to store track URI, artist URI, and genres
dict_genre = {}

# convert track_uri column to an iterable list
track_uris = df_library['track_uri'].to_list()

# loop through track URIs and pull artist URI using the API,
# then use artist URI to pull genres associated with that artist
# store all these in a dictionary
for t_uri in track_uris:
    dict_genre[t_uri] = {'artist_uri': "", "genres": []}

    r = requests.get(BASE_URL + 'tracks/' + t_uri, headers=headers)
    r = r.json()
    a_uri = r['artists'][0]['uri'].split(':')[2]
    dict_genre[t_uri]['artist_uri'] = a_uri

    s = requests.get(BASE_URL + 'artists/' + a_uri, headers=headers)
    s = s.json()
    dict_genre[t_uri]['genres'] = s['genres']

# convert dictionary into dataframe with track_uri as the first column
df_genre = pd.DataFrame.from_dict(dict_genre, orient='index')
df_genre.insert(0, 'track_uri', df_genre.index)
df_genre.reset_index(inplace=True, drop=True)

df_genre_expanded = df_genre.explode('genres')

# save df_tableau and df_genre_expanded as csv files that we can load into Tableau
df_tableau.to_csv('./Data/MySpotifyDataTable.csv')
df_genre_expanded.to_csv('./Data/GenresExpandedTable.csv')

print('done')
