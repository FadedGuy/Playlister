import os, sys, re, requests, json
from base64 import b64encode
from playlisterUtil.playlisterUtil import MongoDoc

regex_yt_url = r"^(?:https?:\/\/)?(?:www\.)?(?:youtube\.com\/(?:embed\/|v\/|watch\?v=|watch\?.+&v=)|youtu\.be\/)([-_a-zA-Z0-9]{11})"
regex_yt_index = r"&(index|start_radio)=(\d+)"
regex_yt_duration = r"^PT(?:([0-9]+)H)?(?:([0-9]+)M)?(?:([0-9]+)S)?"

yt_video_options = ["snippet", "contentDetails", "status", "topicDetails"]
yt_video_url_api = "https://www.googleapis.com/youtube/v3/videos"
yt_playlist_options = ["snippet", "contentDetails", "status", "localizations"]
yt_playlist_url_api = "https://youtube.googleapis.com/youtube/v3/playlists"

spotify_token_url = "https://accounts.spotify.com/api/token"
spotify_search_url_api = "https://api.spotify.com/v1/search"
spotify_track_url_api = "https://api.spotify.com/v1/tracks"

def get_spotify_token():
    res = requests.post(spotify_token_url, 
                        headers={
                            'Authorization': 'Basic ' + b64encode(f"{os.environ.get('SPOTIFY_CLIENT_ID')}:{os.environ.get('SPOTIFY_CLIENT_SECRET')}".encode()).decode(),
                            'Content-Type': 'application/x-www-form-urlencoded'  
                        },
                        data={
                            'grant_type': 'client_credentials'
                        })
    
    if res.status_code == 200: 
        data = json.loads(res.content)
        return data['access_token']
    
    print(f"Error requesting spotify token\n{res.content}", file=sys.stderr)
    return None

def parse_yt_duration(duration):
    if re.match(regex_yt_duration, duration):
        duration_match = re.match(regex_yt_duration, duration)
        hours = int(duration_match.group(1)) if duration_match.group(1) else 1
        minutes = int(duration_match.group(2)) if duration_match.group(2) else 1
        seconds = int(duration_match.group(3)) if duration_match.group(3) else 1

        return hours*3600 + minutes*60 + seconds 
    
    return -1

def parse_spotify_duration(duration):
    return duration/1000

'''
4 types of videos:
    1. Music video
        - Search the description of the video to see if it has a spotify link
        - Search by name and author if present on spotify
        - Search using external tools such as shazam  
    2. Collection of music videos
        Need to determine the songs present
            - Search if a Spotify playlist is provided
            - Search the description and top comments to find chapters or tracklist and do type 1 video
            - Go through the audio at intervals and use externals tools to recognize
    3. List of music videos
        - Requires lower and upper index of list to process, at each one do type 1 video
    4. Non-music video
        Throw error message 
'''
'''
Returns 4 values in a list in the following order
- Boolean indicating valid or unvalid URL
- None or str indicating video_id
- None or str indicating mix_id 
- None or number indicating the index of the mix
'''
def validate_yt_url(mongoDoc: MongoDoc, col, col_id):
    # Validate url
    url = mongoDoc.get_value('youtube.url')
    if re.match(regex_yt_url, url):
        split_url = re.split(regex_yt_url, url)
        
        video_id = split_url[1]
        mongoDoc['youtube.video_id'] = video_id

        # Only video_id
        if split_url[2] == '':
            return False

        # No list id
        list_id = split_url[2].strip('&list=').split('&')[0]
        if list_id == '':
            return False
        
        mongoDoc['youtube.mix_id'] = list_id
        
        # Search for the index of the song
        split_index = re.split(regex_yt_index, split_url[2])
        if len(split_index) == 4:
            try:
                mongoDoc['youtube.mix_index'] = int(split_index[2])
            except ValueError:
                print(f"Invalid value {split_index[2]}", file=sys.stderr)

    else:
        return True

    return False

'''
snippet
    title
    tags
        additional search params
    categoryId 
        10 = music
        https://mixedanalytics.com/blog/list-of-youtube-video-category-ids/
    description
        parse and search for spotify url 
        additional search params
contentDetails
    duration
        determine if one of multiple songs
status
    embeddable
        can use for streaming audio without needing to download video
topicDetails
    additional search params
'''
# Acaso es un bug lo que me esta mandando informacion extra para los available markets?
# Tries to find a match according to type 1 music video with spotify api
# Picks the first match that it encounters for the moment
def process_yt_id(mongoDoc: MongoDoc):
    video_id = mongoDoc.get_value('youtube.video_id')
    url = yt_video_url_api + f"?id={video_id}&part={','.join(yt_video_options)}&key={os.environ.get('YT_API_KEY')}"
    response = requests.get(url)

    # Depending on status code ie 2xx ack | 4xx nack | 5xx nack 
    if response.status_code == 200:
        video_data = response.json()
        if len(video_data['items']) == 0:
            return False
        
        snippet = video_data['items'][0]['snippet']
        contentDetails = video_data['items'][0]['contentDetails']
        status = video_data['items'][0]['status']

        mongoDoc['youtube.title'] = snippet['title'] 
        mongoDoc['youtube.channel_name'] = snippet['channelTitle'] 
        mongoDoc['youtube.duration'] = parse_yt_duration(contentDetails['duration'])
        mongoDoc['youtube.license'] = status['license']
        mongoDoc['youtube.embeddable'] = status['embeddable']


        if mongoDoc.get_value('youtube.mix_id') != '':
            # Is playlist or mix
            playlist_url = yt_playlist_url_api + f"?id={mongoDoc.get_value('youtube.mix_id')}&part={','.join(yt_playlist_options)}&key={os.environ.get('YT_API_KEY')}"
            playlist_res = requests.get(playlist_url)

            if playlist_res.status_code == 200:
                playlist_data = playlist_res.json()
                
                if len(playlist_data['items']) == 0:
                    return True
                
                snippet = playlist_data['items'][0]['snippet']
                contentDetails = playlist_data['items'][0]['contentDetails']
                status = playlist_data['items'][0]['status']

                mongoDoc['youtube.mix_name'] = snippet['title'] 
                mongoDoc['youtube.channel_name'] = snippet['channelTitle'] 
                mongoDoc['youtube.mix_num_songs'] = contentDetails['itemCount']

                # It is a mix
                if snippet['publishedAt'] == '1970-01-01T00:00:00Z' and snippet['channelTitle'] == 'YouTube':
                    mongoDoc['youtube.mix_type'] = 'mix'
                else:
                    mongoDoc['youtube.mix_type'] = 'playlist'

                # Calling for single video? Do one video and then the rest? How to handle mix spotify
                return False
            else:
                return True

        # Is just video
        # Duration greater than 15minutes
        if mongoDoc.get_value('youtube.duration') >= 900:
            mongoDoc['youtube.is_multiple_songs'] = True
    
        spotify_token = get_spotify_token()
        res = requests.get(spotify_search_url_api, headers={'Authorization': f"Bearer {spotify_token}"},
                        params={'q':mongoDoc.get_value('youtube.title'),
                                'type': 'track',
                                'limit': 2})

        if res.status_code == 200:
            spotify_data = res.json()
            song_data = spotify_data['tracks']['items'][0]

            mongoDoc['spotify.song.name'] = song_data['name']
            mongoDoc['spotify.song.open_url'] = song_data['external_urls']['spotify']
            mongoDoc['spotify.song.preview_url'] = song_data['preview_url']
            mongoDoc['spotify.song.api_url'] = song_data['href']
            mongoDoc['spotify.song.duration'] = parse_spotify_duration(song_data['duration_ms'])

            mongoDoc['spotify.artist.name'] = song_data['artists'][0]['name']
            mongoDoc['spotify.artist.open_url'] = song_data['artists'][0]['external_urls']['spotify']
            mongoDoc['spotify.artist.api_url'] = song_data['artists'][0]['href']

            mongoDoc['spotify.album.name'] = song_data['album']['name']
            mongoDoc['spotify.album.image_url'] = song_data['album']['images'][0]['url']
            mongoDoc['spotify.album.open_url'] = song_data['album']['external_urls']['spotify']
            mongoDoc['spotify.album.api_url'] = song_data['album']['href']
            # Can calculate duration by calling album api and adding all track durations
            mongoDoc['spotify.album.duration'] = 0

        else:
            print("An error occurred", file=sys.stderr)
            return True

        return False
    else:
        return True  
    