# Import Libraries for Spotify API
import spotipy
import pandas as pd
from spotipy.oauth2 import SpotifyClientCredentials
import time
import json

# client id and secret
CLIENT_ID = 'insert_clientid'
CLIENT_SECRET = 'insert_clientsecret'

client_credentials_manager = SpotifyClientCredentials(client_id=CLIENT_ID, client_secret=CLIENT_SECRET)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)


def get_features_for_tracks(track_ids):
    """
    Fetches audio features for provided track IDs.

    :param track_ids: List of Spotify track IDs.
    :return: List of dictionaries containing track features.
    """
    features_list = []
    # Spotify limits batch requests to 100 IDs per request
    batch_size = 100

    for i in range(0, len(track_ids), batch_size):
        batch = track_ids[i:i + batch_size]
        batch = [t for t in batch if isinstance(t, str)]
        features_results = sp.audio_features(tracks=batch)
        features_list.extend(features_results)
        time.sleep(1)  # Sleep to avoid hitting rate limits
    return features_list


def save_features_to_csv(features, filename="track_features.csv"):
    """
    Saves the track features to a CSV file.

    :param features: List of dictionaries containing track features.
    :param filename: Name of the file to save.
    """
    df = pd.read_json(features)
    df.to_csv(filename, index=False)
    print(f"Saved track features to {filename}")


def extract_track_ids_from_csv(file_path, uri_column='spotify_track_uri'):
    """
    Extracts track IDs from the Spotify URI column in a CSV file.

    :param file_path: Path to the CSV file.
    :param uri_column: Column name where Spotify URIs are stored.
    :return: A list of extracted track IDs.
    """
    df = pd.read_csv(file_path)
    # Extract the track ID part from the URI
    new = df[uri_column].str.split(":", expand=True)
    return new[2]


csv_file_path = './Data/MySpotifyDataTable.csv'  # Update with the path to your CSV file
track_ids = extract_track_ids_from_csv(csv_file_path)
features = get_features_for_tracks(track_ids)
save_features_to_csv(features)