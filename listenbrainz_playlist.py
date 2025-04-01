from liblistenbrainz import ListenBrainz

def get_created_playlists(self, user):
    return self._get(f'/1/user/{user}/playlists')

def get_playlists_created_for(self, user):
    playlists = self._get(f'/1/user/{user}/playlists/createdfor')
    return [ListenBrainzPlaylist(**playlist['playlist']) for playlist in playlists['playlists']]

def get_playlist(self, playlist_mbid):
    return self._get(f'/1/playlist/{playlist_mbid}')

ListenBrainz.get_created_playlists = get_created_playlists
ListenBrainz.get_playlists_created_for = get_playlists_created_for
ListenBrainz.get_playlist = get_playlist

class ListenBrainzPlaylist():
    def __init__(self, annotation, creator, date, extension, identifier, title, track):
        self.annotation = annotation
        self.creator = creator
        self.date = date
        self.extension = extension
        self.identifier = identifier.replace('https://listenbrainz.org/playlist/', '')
        self.title = title
        self.tracks = self.set_tracks(track)

    def set_tracks(self, tracks):
        self.tracks = [ListenBrainzTrack(**track) for track in tracks]

    def get(self):
        pl = ListenBrainz().get_playlist(self.identifier)
        try:
            self.set_tracks(pl['playlist']['track'])
        except TypeError:
            breakpoint()
        return pl

class ListenBrainzTrack():
    def __init__(self, album='', creator='', duration='', extension='', identifier='', title=''):
        self.album = album
        self.creator = creator
        self.duration = duration
        self.extension = extension
        self.identifier = identifier[0].replace('https://musicbrainz.org/recording/','')
        self.title = title
