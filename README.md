# BrainzList

## How To Use
- Rename the config.ini.example to config.ini
- Change values to apply to you, change the musicbrainz email as well to comply with their TOS.
- Install Python, the Pipfile has 3.13 but anything 3+ should work, you just might have to change the version to get the pipenv install to work.
- Install the python package dependencies with `pipenv install`
- Run the script with `pipenv run create_playlist`

## Options Breakdown
- You can overwrite the config.ini options at runtime with command line options.
- Run `pipenv run create_playlist --help` for the help text.
### Lidarr Options
- `Token`/`-lt`/`--lidarr-token` is the API Key in Lidarr in the Settings -> General -> Security section.
- `URL`/`-lu`/`--lidarr-url` is the full URL to your Lidarr installation.
- `QualityProfile`/`-lqp`/`--lidarr-quality-profile` is the quality profile that should be used when downloading albums to Lidarr
- `RootFolder`/`-lrf`/`--lidarr-root-folder` is the folder that should be used when downloading albums to Lidarr
- `MetadataProfile`/`-lmp`/`--lidarr-metadata-profile` is the metadata profile that should be used when downloading albums to Lidarr.
### Subsonic Options
- `SSUser`/`-ssu`/`--subsonic-user` is the username for the Subsonic user you want to add these playlists to.
- `SSHost`/`-ssh`/`--subsonic-host` is the URL to your Subsonic server.
- `SSPassword`/`-ssp`/`--subsonic-password` is the password to your Subsonic user.
- `SSPort`/`-sspt`/`--subsonic-port` is the port for your Subsonic server.
### MusicBrainz Options
- `Email`/`-mbe`/`--musicbrainz-email` is the email address for accessing the MusicBrainz API. You don't have to sign up, but setting it will let them send you notifications if you're exceeding rate limits.
### ListenBrainz Options
- `LBUser`/`-lbu`/`--listenbrainz-user` is the user you want to fetch playlists from.
- `PlaylistMatch`/`-lbp`/`--listenbrainz-playlist` is the string to try to match for fetching playlists. It will pull multiple playlists if they all match, so if you want to download all of the auto-generated "Exploration" playlists you would run `pipenv run create_playlist --listenbrainz-playlist=Exploration`

- While you can mix/match options and the command line options will take precedence to what is in the config file, the option that makes the most sense to use this way is `--lbp`/`--listenbrainz-playlist`. So if you want to fetch all of the auto-generated "Jams" and "Exploration" playlists, running `pipenv run create_playlist --listenbrainz-playlist=Jams` and then running `pipenv run create_playlist --listenbrainz-playlist=Exploration`

## Limitations
- At the moment it will not wait for the albums to download before trying to add the track to the playlist. So if there are quite a few missing, just wait a bit and run it later when you think the albums have downloaded.
- Sometimes it cannot find an album's information in MusicBrainz as it has to search for the album via the song provided in the playlist. If you want to look at how this is done and figure out if you can make it work better, look in the `grab_add_release` and `lookup_albums` functions in `create_playlist.py` and the `lookup_album` function in `lidarr.py`.

## Contributions
- Just submit a PR, this is a pretty POC level project at the moment. If you find it useful and want to improve its limitations, or just make it a more mature project it would be appreciated.
- Working on improving on the limitations listed above, adding tests, or an executable would all be welcome additions.
