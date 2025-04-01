import re
import libopensonic
import musicbrainzngs
from listenbrainz_playlist import ListenBrainz
from lidarr import Lidarr
import argparse
import configparser

class Playlist:
    def __init__(self, in_file_path = '', lb_user = '', pl_title = '', ss_host='', ss_user='', ss_password='', ss_port=443, lt='', lu='', lqp='', lrf='', lmp='', mb_email=''):
        self._in_file_path = in_file_path
        self._os_client = libopensonic.Connection(ss_host, ss_user, ss_password, port=ss_port)
        self._lb_client = ListenBrainz()
        self.lb_user = lb_user
        self.pl_title = pl_title
        self.lidarr_token = lt
        self.lidarr_url = lu
        self.quality_profile = lqp
        self.root_folder = lrf
        self.metadata_profile = lmp
        self._musicbrainz = musicbrainzngs
        self._musicbrainz.set_useragent("BrainzList", mb_email)

    def create(self):
        #Input is the jspf
        unadded_tracks = []
        for playlist in self.playlists():
            playlist.get()
            print(f'Processing playlist: {playlist.title}')
            for track in playlist.tracks:
                duration_fix = float(track.duration or '0') / 100
                duration_fix = duration_fix
                song = self.find_on_server(track.title, track.creator)
                if song:
                    os_playlist = self.os_playlist(playlist.title)
                    song_ids = []
                    if os_playlist:
                        song_ids = [song.id for song in os_playlist.songs]
                    else:
                        self._os_client.createPlaylist(name=playlist.title)
                        os_playlist = self.os_playlist(playlist.title)

                    if song.id not in song_ids:
                        self._os_client.updatePlaylist(os_playlist.id, name=playlist.title, comment=playlist.annotation, songIdsToAdd=[song.id])
                        print(f'Added track {track.creator} named {track.title}')
                    else:
                        print(f'Track by {track.creator} named {track.title} already added.')
                else:
                    print(f'Could not find track by {track.creator} named {track.title}')
                    print('Attempting To Fetch')
                    if not self.fetch_release_for_track(track):
                        unadded_tracks.append(track)

            print(f'Unable to grab tracks {[f'{track.creator} {track.title}' for track in unadded_tracks]}.')

    def lidarr_client(self):
        return Lidarr(self.lidarr_token, self.lidarr_url)

    def list_lidarr_albums(self, albums=[]):
        return self.lidarr_client().get_albums()

    def lookup_artists(self, name):
        return self.lidarr_client().lookup_artist(name)

    def lookup_albums(self, name, artist_name):
        return self.lidarr_client().lookup_album(name, artist_name)

    def create_artist(self, foreign_artist_id, quality_profile_id, metadata_profile_id, path, root_folder_path, artist_name):
        return self.lidarr_client().create_artist(foreign_artist_id=foreign_artist_id,
            quality_profile_id=quality_profile_id,
            metadata_profile_id=metadata_profile_id,
            path=path,
            root_folder_path=root_folder_path,
            artist_name=artist_name
        )

    def get_quality_profiles(self):
        return self.lidarr_client().get_quality_profiles()

    def get_metadata_profiles(self):
        return self.lidarr_client().get_metadata_profiles()

    def get_root_folders(self):
        return self.lidarr_client().get_root_folders()

    def get_info(self, mg_id):
        return self._musicbrainz.get_recording_by_id(mg_id, includes=['artists', 'release-group-rels'])

    def queue_grab(self, album_id):
        return self.lidarr_client().queue_grab(album_id)

    def get_releases(self, artist_id, album_id):
        return self.lidarr_client().get_releases(artist_id=artist_id, album_id=album_id)

    def fetch_release(self, release_data):
        return self.lidarr_client().fetch_release(release_data=release_data)

    def os_playlist(self, name):
        for playlist in self._os_client.getPlaylists():
            if name == playlist.name:
                return self._os_client.getPlaylist(playlist.id)

    def find_on_server(self, title, artist):
        search = self._os_client.search3(f'{title} {artist}')
        songs = search.get('songs')
        if songs:
            return songs[0]
        else:
            return False

    def playlists(self):
        pls = self._lb_client.get_playlists_created_for(self.lb_user)
        matched_pls = []
        for tmp_pl in pls:
            if self.pl_title in tmp_pl.title:
                matched_pls.append(tmp_pl)
        return matched_pls

    def fix_filename(self, name, ext):
        return f'{self.standard_string(name)}.{ext}'

    def standard_string(self, stri):
        fn = re.split(r'\W+', stri)
        fn = '_'.join(fn)
        return fn

    def fetch_release_for_track(self, track):
        artist_name = track.creator
        artist = playlist.lookup_artists(artist_name)[0]
        self.create_artist_if_not_exist(artist)
        album_title = track.album
        if not self.grab_add_release(artist_name, album_title):
            print(f"Couldn't find album for {artist_name} {album_title}")
            track_info = self.get_info(track.identifier)
            artist_name = track_info['recording']['artist-credit'][0]['artist']['name']
            print(f'Trying album for {artist_name} {album_title}')
            if not self.grab_add_release(artist_name, album_title):
                print(f"Couldn't grab {artist_name} {album_title}")
                return False
        return True


    def create_artist_if_not_exist(self, artist):
        if not artist.get('id', False):
            quality_profile_id = {profile['name']: profile['id'] for profile in self.get_quality_profiles()}[self.quality_profile]
            metadata_profile_id = {profile['name']: profile['id'] for profile in self.get_metadata_profiles()}[self.metadata_profile]
            root_folder_path = {profile['name']: profile['path'] for profile in self.get_root_folders()}[self.root_folder]

            self.create_artist(foreign_artist_id=artist['foreignArtistId'],
                quality_profile_id=quality_profile_id,
                metadata_profile_id=metadata_profile_id,
                root_folder_path=root_folder_path,
                path=f"{root_folder_path}/{artist['folder']}",
                artist_name=artist['artistName']
            )
        else:
            print(f'Artist {artist["artistName"]} Already Exists')


    def grab_add_release(self, artist_name, album_title):
        albums = self.lookup_albums(name=album_title, artist_name=artist_name)
        idx_albums = {}
        for album in albums:
            standard_title = self.standard_string(album['title'])
            if idx_albums.get(standard_title):
                idx_albums[standard_title].append(album)
            else:
                idx_albums[standard_title] = [album]
        standard_title = self.standard_string(album_title)
        if idx_albums.get(standard_title):
            for album in idx_albums[standard_title]:
                if album.get('id') and album.get('artist', {}).get('artistName') == artist_name:
                    releases = self.get_releases(artist_id=album['artistId'], album_id=album['id'])
                    for release in releases:
                        if release['downloadAllowed'] and not release['rejected']:
                            print(f'Fetching release for {artist_name}: {album_title}')
                            self.fetch_release(release)
                            return True
                            break
        else:
            # breakpoint()
            return False
        return True

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        prog='BrainzList',
        description='Pulls playlists from ListenBrainz and imports them in to a Subsonic server and grabs any missing tracks via Lidarr.'
    )
    parser.add_argument('-lbu', '--listenbrainz-user')
    parser.add_argument('-pl', '--listenbrainz-playlist')
    parser.add_argument('-ssu', '--subsonic-user')
    parser.add_argument('-ssp', '--subsonic-password')
    parser.add_argument('-ssh', '--subsonic-host')
    parser.add_argument('-sspt', '--subsonic-port')
    parser.add_argument('-lt', '--lidarr-token')
    parser.add_argument('-lu', '--lidarr-url')
    parser.add_argument('-lqp', '--lidarr-quality-profile')
    parser.add_argument('-lrf', '--lidarr-root-folder')
    parser.add_argument('-lmp', '--lidarr-metadata-profile')
    parser.add_argument('-mbe', '--musicbrainz-email')

    args = parser.parse_args()

    config = configparser.ConfigParser()
    config.read('config.ini')

    default_config = config['DEFAULT']
    lb_config = config['listenbrainz']
    ss_config = config['subsonic']
    ld_config = config['lidarr']
    mb_config = config['musicbrainz']

    #ListenBrainz
    lb_user = args.listenbrainz_user or lb_config.get('LBUser')
    pl_title = args.listenbrainz_playlist or lb_config.get('PlaylistMatch')
    #SubSonic
    ss_host = args.subsonic_host or ss_config.get('SSHost')
    ss_user = args.subsonic_user or ss_config.get('SSUser')
    ss_password = args.subsonic_password or ss_config.get('SSPassword')
    ss_port = args.subsonic_port or ss_config.get('SSPort')
    #Lidarr
    lt = args.lidarr_token or ld_config.get('Token')
    lu = args.lidarr_url or ld_config.get('URL')
    lqp = args.lidarr_quality_profile or ld_config.get('QualityProfile') or default_config.get('QualityProfile')
    lrf = args.lidarr_root_folder or ld_config.get('RootFolder') or default_config.get('RootFolder')
    lmp = args.lidarr_metadata_profile or ld_config.get('MetadataProfile') or default_config.get('MetadataProfile')
    #MusicBrainz
    mb_email = args.musicbrainz_email or mb_config.get('Email')

    playlist = Playlist(lb_user=lb_user, pl_title=pl_title, ss_host=ss_host, ss_user=ss_user, ss_password=ss_password,
                        ss_port=ss_port, lt=lt, lu=lu, lqp=lqp, lrf=lrf, lmp=lmp, mb_email=mb_email
    )
    playlist.create()