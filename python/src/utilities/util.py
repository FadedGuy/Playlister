import os

def get_mongo_uri() -> str :
    return f"mongodb://{os.environ.get('MONGO_USER')}:{os.environ.get('MONGO_PASS')}@{os.environ.get('MONGO_SVC_ADDRESS')}/{os.environ.get('MONGO_DB')}" 

class MongoDoc:
    def __init__(self):
        self.data = {
            'youtube': {
                'url': '',
                'title': '',
                'video_id': '',
                'mix_id': '',
                'mix_index': '',
                'duration': '',
                'license': '',
                'embeddable': False,
                # Determined by duration > 30min and youtube tags
                'is_multiple_songs': False, 
                'is_mix': False,
            },
            'spotify': {
                'api_href': '',
                'song': {
                    'name': '',
                    'open_url': '',
                    'preview_url': '',
                    'api_url': '',
                    'duration': 0,
                },
                'artist': {
                    'open_url': '',
                    'api_url': '',
                    'name': '',
                },
                'album': {
                    'name': '',
                    'image_url': '',
                    'open_url': '',
                    'api_url': '',
                    'duration': 0
                }

            },
            'createdAt': "",
            'startedProcessing': "",
            'finishedProcessing': "",
            'id': 0,
            # 0 not processed, 1 in process, 2 processed
            'processed': 0,
            # 0 didn't succeed, 1 succeed
            'success': 0,
            'retries': 0
        }

    def get_value(self, key, default=None):
        keys = key.split('.')
        value = self.data
        for k in keys:
            value = value.get(k)
            if value is None:
                return default
        
        return value
    
    def set_value(self, key, value):
        keys = key.split('.')
        cur_dict = self.data
        for k in keys[:-1]:
            if k not in cur_dict or not isinstance(cur_dict[k], dict):
                raise KeyError("Cannot add new key-value pair")
            cur_dict = cur_dict[k]
        
        last_key = keys[-1]
        if last_key in cur_dict:
            cur_dict[last_key] = value
        else:
            raise KeyError("Cannot add new key-value pair")
        
    def __setitem__(self, key, value):
        self.set_value(key, value)

    def __delitem__(self, key):
        raise KeyError("Cannot delete key-value pairs")

    def get_keys(self):
        def _recursive_keys(dictionary, parent_key=''):
            keys = []
            for key, value in dictionary.items():
                current_key = f'{parent_key}.{key}' if parent_key else key
                if isinstance(value, dict):
                    keys.extend(_recursive_keys(value, current_key))
                else:
                    keys.append(current_key)
            return keys

        all_keys = _recursive_keys(self.data)
        return all_keys

    def get_filtered_dict(self):
        keys_to_filter = ['youtube.license', 'spotify.api_href', 'spotify.song.api_url', 
                          'spotify.artist.api_url', 'spotify.album.api_url', 'createdAt',
                          'startedProcessing', 'finishedProcessing', 'retries']
        
        def _recursive_filter(dictionary, parent_key=''):
            filtered_dict = {}
            for key, value in dictionary.items():
                nested_key = f"{parent_key}.{key}" if parent_key else key
                if isinstance(value, dict):
                    filtered_value = _recursive_filter(value, parent_key=nested_key)
                    if filtered_value:
                        filtered_dict[key] = filtered_value
                elif nested_key not in keys_to_filter:
                    filtered_dict[key] = value
            return filtered_dict

        stripped = _recursive_filter(self.data.copy())
        return stripped
