import os, sys, re, requests

regex_yt_url = r"^(?:https?:\/\/)?(?:www\.)?(?:youtube\.com\/(?:embed\/|v\/|watch\?v=|watch\?.+&v=)|youtu\.be\/)([-_a-zA-Z0-9]{11})"
regex_yt_mix = r"^&list=[A-Za-z0-9]{13}"
regex_yt_index_mix = r"^&(index|start_radio)=\d+"
yt_api_part = ["snippet", "contentDetails", "status", "topicDetails"]

yt_video_url_api = "https://www.googleapis.com/youtube/v3/videos"

def get_mongo_uri() -> str :
    return f"mongodb://{os.environ.get('MONGO_USER')}:{os.environ.get('MONGO_PASS')}@{os.environ.get('MONGO_SVC_ADDRESS')}/{os.environ.get('MONGO_DB')}" 

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
def validate_yt_url(url):
    print(url, file=sys.stderr)
    # Validate url
    if re.match(regex_yt_url, url):
        split_url = re.split(regex_yt_url, url)
        video_id = split_url[1]
        
        # Only video or mix
        if len(split_url) == 3 and re.match(regex_yt_mix, split_url[2]):
            split_mix = re.split(regex_yt_mix, split_url[2])
            list_id = split_url[2].strip("&list=").split('&')[0]
            # With or without index of mix
            if len(split_mix) == 2 and re.match(regex_yt_index_mix, split_mix[1]):
                index_id = split_mix[1].strip("&").strip("index=").strip("start_radio=")
                return True, video_id, list_id, index_id
            else:
                return True, video_id, list_id, None
        return True, video_id, None, None

    return False, None, None, None

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
# Tries to find a match according to type 1 music video
def process_yt_id(video_id):
    url = yt_video_url_api + f"?id={video_id}&part={','.join(yt_api_part)}&key={os.environ.get('YT_API_KEY')}"
    response = requests.get(url)

    # Depending on status code ie 2xx ack | 4xx nack | 5xx nack 
    if response.status_code == 200:
        video_data = response.json()
        if len(video_data['items']) == 0:
            return False
        
        print(video_data, file=sys.stderr)
        return True
    
    return False    