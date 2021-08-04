from bs4 import BeautifulSoup
import requests
import json
from datetime import date
from tokens import spotify_user_id, refresh_token, access_token


# Variables
header = ""
song_array = []
artist_array = []
wanted_artists = ["Lil Uzi Vert", "The Kid LAROI", "Jack Harlow", "Kendrick Lamar", "Logic", "Lil Tjay", "Drake", "Lil Tecca", "Pop Smoke",
                    "Juice Wrld", "Lil Baby", "Lil Nas X", "Walker Hayes", "Post Malone"]
wanted_artist_array = []
wanted_song_array = []
song_info = {}


# Constructor
def __init__(self):
    self.spotify_user_id = spotify_user_id
    self.spotify_token = spotify_token
    self.spotify_token = ""


# Gets the Header Used in the Spotify API
def get_header():
    header = {"Content-Type": "application/json", "Authorization": "Bearer {}".format(spotify_token)}
    return header


# Creates a Playlist on Spotify
def create_playlist():

    date_today = date.today().strftime("%m/%d/%Y")

    if (date_today[0] == '0'):
        date_today = date_today[1:]

    request_body = json.dumps({ "name": "Tops Songs From " + date_today, "description": "Tops Songs from Rolling Loud", "public": False })
    
    query = "https://api.spotify.com/v1/users/{}/playlists".format(spotify_user_id)
    
    response = requests.post(query, data=request_body, headers=get_header())
    
    response_json = response.json()

    return response_json["id"]

   
# Gets the Spotify ID For Each Song Given the Song Name & Artist
def get_song_id(song_name, artist):
    
    query = "https://api.spotify.com/v1/search?query=track%3A{}+artist%3A{}&type=track&offset=0&limit=20".format(song_name, artist)

    response = requests.get(query, headers=get_header())

    response_json = response.json()

    songs = response_json["tracks"]["items"]

    uri = songs[0]["uri"]

    return uri


# Adds Songs to the Created Playlist
def add_songs_to_playlist():

    all_song_uri = [information["Spotify URI"] for song, information in song_info.items()]

    playlist_id = create_playlist()

    request_data = json.dumps(all_song_uri)
   
    query = "https://api.spotify.com/v1/playlists/{}/tracks".format(playlist_id)

    response = requests.post(query, data=request_data, headers=get_header())

    response_json = response.json()

    return response_json


# Returns a new Spotify Access Token
def refresh():

    query = "https://accounts.spotify.com/api/token"

    response = requests.post(query, data={"grant_type": "refresh_token", "refresh_token": refresh_token}, headers={"Authorization": "Basic " + access_token})

    response_json = response.json()

    return response_json["access_token"]

# Main Logic
# Scrapes Rolling Stones to get the top songs of the week
url = 'https://www.rollingstone.com/charts/songs/'

spotify_token = refresh()
        
try:
    data = requests.get(url).text
    soup = BeautifulSoup(data, 'lxml')

    top_song = soup.find_all('div', class_= 'c-chart__table--title')
    main_artist = soup.find_all('div', class_ = 'c-chart__table--caption')

except:
    print("Unable to Parse HTML")
    raise


for song in top_song:
    song_array.append(song.p.text)


for artist in main_artist:

    first_artist = "" 

    if artist.text.find(',') != -1:
        index = artist.text.index(",")
        first_artist = artist.text[:index]
        artist_array.append(first_artist)

    elif artist.text.find("feat") != -1:
        index = artist.text.index("feat")
        first_artist = artist.text[:index - 1]
        artist_array.append(first_artist)
    else:
        artist_array.append(artist.text)


for each_artist in artist_array:
    if each_artist in wanted_artists:
        index = artist_array.index(each_artist)
        wanted_artist_array.append(artist_array[index])
        wanted_song_array.append(song_array[index])


for song in wanted_song_array:
    for artist in wanted_artist_array:

        song_info[song] = {
        "Song Name": song,
        "Artist": artist,
        "Spotify URI": get_song_id(song, artist)
        }

        wanted_artist_array.remove(artist)
        break


add_songs_to_playlist()