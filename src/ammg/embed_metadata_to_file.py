import mutagen
import pathlib
import base64
import sys

from mutagen.flac import Picture
from mutagen.mp4 import MP4Info
from mutagen.oggopus import OggOpusInfo


class EmbedMetadataToFile():
    def __init__(self,
                 music_file: pathlib.Path,
                 music_info: dict,
                 cover: pathlib.Path,
                 cover_info: dict):
        self.music_file: pathlib.Path = music_file
        self.music_info: dict = music_info

        self.music = mutagen.File(self.music_file)

        # Which metadata format to use
        # Not checking the file extension.
        if isinstance(self.music.info, MP4Info):
            self.music_file_type = 'm4a'
        elif isinstance(self.music.info, OggOpusInfo):
            self.music_file_type = 'opus'
        else:
            print('File Type Not Supported.')

            sys.exit(2)

        self.cover: pathlib.Path = cover
        self.cover_info: dict = cover_info

    def _process_image(self) -> str | bytes:
        """Process the picture."""
        with open(self.cover, 'rb') as pic:
            cover_data = pic.read()

        if self.music_file_type == 'm4a':
            return cover_data

        picture = Picture()
        picture.data = cover_data
        picture.type = self.cover_info.get('type', 3)
        picture.mime = self.cover_info.get('mime', 'image/jpeg')
        picture.width = self.cover_info.get('width', 500)
        picture.height = self.cover_info.get('height', 500)
        picture.depth = self.cover_info.get('depth', 8)

        picture_data = picture.write()
        encoded_data = base64.b64encode(picture_data)
        vcomment_value = encoded_data.decode('ascii')

        return vcomment_value

    def _save_m4a_music(self):
        """Save new metadata to m4a file.

        - [x] title         -> \xa9num
        - [x] artist        -> \xa9ART
        - [x] album         -> \xa9alb
        - [x] albumartist   -> aART
        - [x] date          -> \xa9day
        - [x] composer      -> \xa9wrt
        - [x] genre         -> \xa9gen
        - [x] cover         -> covr
        - [x] copyright     -> cprt
        - [x] track_number  -> trkn[0]
        - [x] tracktotal    -> trkn[1]
        - [x] discnumber    -> disk[0]
        - [x] disctotal     -> disk[1]
        - [x] isrc          -> Freeform (ISRC)
        - [x] media         -> Freeform (MEDIA)
        - [x] label         -> Freeform (LABEL)

        - [ ] releasetype   -> There is no releasetype.
        """

        self.music['\xa9nam'] = self.music_info.get('title')

        self.music['\xa9ART'] = self.music_info.get('artist')
        self.music['\xa9alb'] = self.music_info.get('album')
        self.music['aART'] = self.music_info.get('album_artist')

        self.music['\xa9day'] = self.music_info.get('date')

        self.music['\xa9wrt'] = self.music_info.get('composer')
        self.music['\xa9gen'] = self.music_info.get('genre')

        self.music['cprt'] = self.music_info.get('copyright')
        self.music['stik'] = [1]

        self.music['disk'] = [
            (
                int(self.music_info.get('discnumber')),
                int(self.music_info.get('disctotal'))
            )
        ]

        self.music['trkn'] = [
            (
                int(self.music_info.get('track_number')),
                int(self.music_info.get('tracktotal'))
            )
        ]

        # Freeform
        self.music['----:com.apple.iTunes:ISRC'] = [
            mutagen.mp4.MP4FreeForm(
                data=self.music_info.get('isrc').encode(),
                dataformat=mutagen.mp4.AtomDataType.UTF8
            )
        ]

        self.music['----:com.apple.iTunes:LABEL'] = [
            mutagen.mp4.MP4FreeForm(
                data=self.music_info.get('label').encode(),
                dataformat=mutagen.mp4.AtomDataType.UTF8
            )
        ]

        self.music['----:com.apple.iTunes:MEDIA'] = [
            mutagen.mp4.MP4FreeForm(
                data=self.music_info.get('media').encode(),
                dataformat=mutagen.mp4.AtomDataType.UTF8
            )
        ]

        self.music['covr'] = [self._process_image()]

        self.music.save()

    def _save_opus_music(self):
        """Save new metadata to opus file.

        - [x] title         -> title
        - [x] artist        -> artist
        - [x] album         -> album
        - [x] albumartist   -> albumartist
        - [x] date          -> date
        - [x] composer      -> composer
        - [x] genre         -> genre
        - [x] cover         -> metadata_block_picture
        - [x] copyright     -> copyright
        - [x] track_number  -> tracknumber
        - [x] tracktotal    -> tracktotal
        - [x] discnumber    -> discnumber
        - [x] disctotal     -> disctotal
        - [x] isrc          -> isrc
        - [x] media         -> media
        - [x] label         -> label
        - [x] releasetype   -> releasetype
        """

        self.music['title'] = self.music_info.get('title')
        self.music['artist'] = self.music_info.get('artist')
        self.music['album'] = self.music_info.get('album')
        self.music['albumartist'] = self.music_info.get('album_artist')
        self.music['tracknumber'] = str(self.music_info.get('track_number'))
        self.music['date'] = self.music_info.get('date')
        self.music['composer'] = self.music_info.get('composer', '')
        self.music['discnumber'] = str(self.music_info.get('discnumber'))
        self.music['genre'] = self.music_info.get('genre')
        self.music['disctotal'] = str(self.music_info.get('disctotal'))
        self.music['totaldiscs'] = str(self.music_info.get('disctotal'))
        self.music['tracktotal'] = str(self.music_info.get('tracktotal'))
        self.music['totaltracks'] = str(self.music_info.get('tracktotal'))
        self.music['isrc'] = self.music_info.get('isrc')
        self.music['copyright'] = self.music_info.get('copyright')
        self.music['releasetype'] = self.music_info.get('releasetype')
        self.music['media'] = self.music_info.get('media')
        self.music['label'] = self.music_info.get('label')
        self.music['metadata_block_picture'] = [self._process_image()]

        self.music.save()

    def save_music(self):
        """Save new metadata."""

        if self.music_file_type == 'opus':
            self._save_opus_music()
        else:
            self._save_m4a_music()
