import pathlib
import requests
import json
import sys

from .ammg_cache import AmmgCache


class ApiMusicApple():
    def __init__(self,
                 token,
                 album_id,
                 storefront: str = 'us',
                 clean_request: bool = False):
        self.api_url: str = 'http://api.music.apple.com/v1/catalog'
        self.storefront: str = storefront

        self.token: str = token
        self.album_id: str = album_id
        self.clean_request: str = clean_request

        self.headers: dict = {
            'Authorization': f'Bearer {self.token}',
            'Origin': 'https://music.apple.com',
        }

        self.cache_dir: pathlib.Path = AmmgCache().cache_dir

    def get_response_data(self) -> dict:
        """Returns a dict that contains the status and
        the json of the response.

        Returned Dictionary Keys:
            - status
            - json (if status is 200)
        """
        # Attempting to  read from cache  if cache
        # file exists for album_id
        cache_file = self.cache_dir.joinpath(f'{self.album_id}.json')

        if not self.clean_request and cache_file.is_file():
            with open(cache_file, 'r') as cf:
                data = json.load(cf)

                return data

        response_data: dict = {}

        api_url = f'{self.api_url}/{self.storefront}/albums/{self.album_id}'

        response = requests.get(
            api_url,
            headers=self.headers,
        )

        response_data['status'] = response.status_code

        if response.status_code != 200:
            return response_data

        response_data['json'] = response.json()

        # Writing cache
        with open(cache_file, 'w') as cf:
            json.dump(
                obj=response_data,
                fp=cf,
                indent=4,
            )

        return response_data

    def analyze_response_album(self, response_data) -> dict:
        """Returns a dictionary of the analyzed album.

        Dictionary keys:
            copyright:                      str
            album_release_date              str
            record_label:                   str
            track_count:                    int
            disc_count:                     int
            album_name:                     str
            album_artist_name:              str
            cover_url:                      str
            release_type: release_type,     str
            tracks: album_tracks,           list

            Each track contains:
                title:        str
                artist:       str
                date:         str
                composer:     str
                genre:        str
                isrc:         str
                media:        str
                duration:     int
                track_number: int
                discnumber:   int
                disctotal:    int
        """
        if response_data.get('status') != 200:
            print('Something went wrong while querying the metadata.')
            print()
            print('Maybe run with --clean-request.')

            sys.exit(1)

        json_data = response_data.get('json').get('data')[0]
        album_info = json_data.get('attributes')

        # Album Info
        copyright_: str = album_info.get('copyright').strip()
        record_label: str = album_info.get('recordLabel').strip()

        track_count: int = album_info.get('trackCount')

        album_name: str = album_info.get('name')
        album_artist_name: str = album_info.get('artistName')
        album_release_date: str = album_info.get('releaseDate').strip()

        cover_url: str = album_info.get('artwork').get('url')

        # Album or Single or EP
        release_type = album_info.get('playParams').get('kind')

        if release_type == 'album' and album_info.get('isSingle'):
            release_type = 'single'
        elif release_type == 'album' and '- EP' in album_name:
            release_type = 'ep'

        # Analyzing the tracks
        tracks = json_data.get('relationships').get('tracks').get('data')

        album_tracks: list[dict] = []
        disc_numbers: list[int] = []

        for track in tracks:
            info: dict = track.get('attributes')
            track_info: dict = {}

            track_info['title'] = info.get('name')
            track_info['artist'] = info.get('artistName')
            track_info['duration'] = info.get('durationInMillis')

            track_info['date'] = info.get('releaseDate')
            track_info['composer'] = info.get('composerName', '')
            track_info['genre'] = info.get('genreNames')[0]
            track_info['isrc'] = info.get('isrc')
            track_info['media'] = 'Digital Media'

            track_info['track_number'] = info.get('trackNumber')
            track_info['discnumber'] = info.get('discNumber')

            disc_numbers.append(int(info.get('discNumber')))

            album_tracks.append(track_info)

        final_album: dict = {
            'copyright': copyright_,
            'album_release_date': album_release_date,
            'record_label': record_label,
            'track_count': track_count,
            'disc_count': max(disc_numbers),
            'album_name': album_name,
            'album_artist_name': album_artist_name,
            'cover_url': cover_url,
            'release_type': release_type,
            'tracks': album_tracks,
        }

        return final_album
