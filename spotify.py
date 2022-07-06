import spotipy
import json
from spotipy.oauth2 import SpotifyOAuth


# Client information to establish the connection
client_id = "09005460146a4278928cca798bc1ef06"
client_secret = "a492c4196ba04d6bb4aece497b248d8c"

# Device information
id_phone = 'a2656dbf9d4631073b7708b293fd8adacc74dc34'
id_pc = 'da1095b9403dd603db94e8a3891459836e0d3765'

# The information that can be accessed
scope = [
    "ugc-image-upload",
    "user-modify-playback-state",
    "user-read-playback-state",
    "user-read-currently-playing",
    "user-follow-modify",
    "user-follow-read",
    "user-read-recently-played",
    "user-read-playback-position",
    "user-top-read",
    "playlist-read-collaborative",
    "playlist-modify-public",
    "playlist-read-private",
    "playlist-modify-private",
    "app-remote-control",
    "streaming",
    "user-read-email",
    "user-read-private",
    "user-library-modify",
    "user-library-read"
]


def export_to_json(file, name):
    with open(f'{name}.json', 'w') as outfile:
        json.dump(file, outfile)


class SpotifyPlayer:
    def __init__(self):

        # Initialize spotify
        spotipy.Spotify()
        self.spotify_connection = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id, client_secret, redirect_uri="http://localhost:8888/callback", scope=scope))

        # Information about the current track
        self.current_track_uri = ""  # track uri
        self.current_track_name = ""  # track name
        self.current_track_artists = []
        self.current_track_progress = 0  # in milliseconds
        self.current_track_length = 0  # in milliseconds
        self.current_track_playing_status = False
        self.audio_features = {}

        # Information about the previous track
        self.prev_track_uri = ""  # track ID
        self.prev_track_progress = 0  # in milliseconds

    def update(self):
        # Gets all the data about the current track
        self.get_track_data()

    def get_track_data(self):
        raw_current_track_data = self.spotify_connection.current_playback()
        if (raw_current_track_data is not None) and ((raw_current_track_data.get("item")) is not None):
            self.current_track_uri = raw_current_track_data['item']['uri']
            self.current_track_name = raw_current_track_data['item']['name']
            self.current_track_artists = [artist['name'] for artist in raw_current_track_data['item']['artists']]
            self.current_track_progress = raw_current_track_data['progress_ms']
            self.current_track_length = raw_current_track_data['item']['duration_ms']
            self.current_track_playing_status = raw_current_track_data.get("is_playing")

        else:
            pass  # TODO: reset all values

    def find_playlist_id(self, playlist_name):
        """
        Finds playlist_id given the playlist_name
        :param playlist_name: The name of the playlist of which the ID is wanted
        :return: The playlist_id
        """
        playlists = self.spotify_connection.current_user_playlists().get('items')
        playlist_table = []
        for playlist in playlists:
            playlist_table.append([playlist['name'], playlist['id']])

        return [i[1] for i in playlist_table if str(playlist_name) in i[0]][0]

    def get_playlist_statistics(self, playlist_name=None, limit=50):
        song_statistics = {'danceability': [], 'energy': [], 'loudness': [], 'speechiness': [], 'acousticness': [],
                           'instrumentalness': [], 'liveness': [], 'valence': [], 'tempo': []}

        # If the playlist ID cannot be found, the users saved tracks will be used instead
        if playlist_name is None:
            playlist_data = self.spotify_connection.current_user_saved_tracks(limit=limit).get('items')

        else:
            # TODO: add limit
            playlist_data = self.spotify_connection.playlist(self.find_playlist_id(playlist_name))['tracks'].get('items')

        for i, song in enumerate(playlist_data):
            for key in song_statistics:
                song_statistics[key].append(self.spotify_connection.audio_features(song['track']['id'])[0].get(key))

        for key in song_statistics:
            data = song_statistics[key]
            average_data = sum(data) / len(data)
            # TODO: add UI
            print(key, average_data)

    def get_current_track_statistics(self):
        # TODO: add UI
        print(self.spotify_connection.audio_features(self.spotify_connection.current_playback()['item']['id']))

    def start_pause(self):
        if self.current_track_playing_status:
            self.spotify_connection.pause_playback()
        else:
            self.spotify_connection.start_playback()
