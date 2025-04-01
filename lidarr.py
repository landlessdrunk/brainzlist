import requests
from urllib.parse import urlunparse, urlparse, urlencode

class Lidarr:
    def __init__(self, api_key, url):
        self.api_key = api_key
        self.url = urlparse(url)
        self._api_base = '/api/v1'

    def get_albums(self, ids=[]):
        return self.get('album')

    #Will actually search the same way as the UI
    def lookup_artist(self, name):
        return self.get('artist/lookup', query={'term': name})

    def lookup_album(self, name, artist_name=''):
        return self.get('album/lookup', query={'term': f'{name} {artist_name}'})

    def get_quality_profiles(self):
        return self.get('qualityprofile')

    def get_metadata_profiles(self):
        return self.get('metadataprofile')

    def get_root_folders(self):
        return self.get('rootfolder')

    def monitor_albums(self, album_ids):
        return self.put('album/monitor', {'albumIds': album_ids})

    #wtf is this for? What ID does it take?
    #Still don't know, but it isn't an album id.
    def queue_grab(self, album_id):
        return self.post(f'queue/grab/{album_id}')

    def get_releases(self, artist_id, album_id):
        return self.get('release', query={'albumId': album_id, 'artistId': artist_id})

    def fetch_release(self, release_data):
        return self.post('release', release_data)

    def create_artist(self, foreign_artist_id, quality_profile_id, metadata_profile_id, path, root_folder_path, artist_name):
        return self.post('artist', params={
            'foreignArtistId': foreign_artist_id,
            'qualityProfileId': quality_profile_id,
            'metadataProfileId': metadata_profile_id,
            'rootFolderPath': root_folder_path,
            'path': path,
            'artistName': artist_name
        })

    def get(self, path, query={}):
        request_url = self.url._replace(path=f'{self._api_base}/{path}', query=urlencode(query))
        r = requests.get(urlunparse(request_url), headers=self.headers)
        try:
            result = r.json()
        except requests.exceptions.RequestException:
            breakpoint()
        return result

    def post(self, path, params={}):
        request_url = self.url._replace(path=f'{self._api_base}/{path}')
        req = requests.post(urlunparse(request_url), json=params, headers=self.headers)
        try:
            result = req.json()
        except requests.exceptions.RequestException:
            breakpoint()
        return result

    def put(self, path, params={}):
        request_url = self.url._replace(path=f'{self._api_base}/{path}')
        req = requests.put(urlunparse(request_url), json=params, headers=self.headers)
        try:
            result = req.json()
        except requests.exceptions.RequestException:
            breakpoint()
        return result

    @property
    def headers(self):
        return {
            'X-Api-Key': self.api_key,
            'Content-Type': 'application/json'
        }
