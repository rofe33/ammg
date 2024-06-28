import mutagen
import pathlib
import base64
import sys

from mutagen.flac import Picture


class EmbedMetadataToFile():
    def __init__(self,
                 music_file: pathlib.Path,
                 title: str,
                 artist: str,
                 album: str,
                 album_artist: str,
                 date: str,
                 composer: str,
                 genre: str,
                 discnumber: str,
                 disctotal: str,
                 tracknumber: str,
                 tracktotal: str,
                 media: str,
                 releasetype: str,
                 isrc: str,
                 copyright_: str,
                 label: str,
                 cover: pathlib.Path,
                 cover_info: dict):
        self.music_file: pathlib.Path = music_file
        self.music: mutagen.File = mutagen.File(self.music_file)

        # Which metadata format to use
        # Not checking the file extension.
        if isinstance(self.music.info, mutagen.mp4.MP4Info):
            self.music_file_type = 'm4a'
        elif isinstance(self.music.info, mutagen.oggopus.OggOpusInfo):
            self.music_file_type = 'opus'
        else:
            print('File Type Not Supported.')

            sys.exit(2)

        self.title = title
        self.artist = artist
        self.album = album
        self.album_artist = album_artist
        self.tracknumber = tracknumber
        self.date = date
        self.composer = composer
        self.discnumber = discnumber
        self.genre = genre
        self.disctotal = disctotal
        self.tracktotal = tracktotal
        self.isrc = isrc
        self.copyright = copyright_
        self.releasetype = releasetype
        self.media = media
        self.label = label

        self.cover = cover
        self.cover_info = cover_info

    def _process_image(self) -> str:
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
        - [x] tracknumber   -> trkn[0]
        - [x] tracktotal    -> trkn[1]
        - [x] discnumber    -> disk[0]
        - [x] disctotal     -> disk[1]
        - [x] isrc          -> Freeform (ISRC)
        - [x] media         -> Freeform (MEDIA)
        - [x] label         -> Freeform (LABEL)

        - [ ] releasetype   -> There is no releasetype.
        """

        self.music['\xa9nam'] = self.title

        self.music['\xa9ART'] = self.artist
        self.music['\xa9alb'] = self.album
        self.music['aART'] = self.album_artist

        self.music['\xa9day'] = self.date

        self.music['\xa9wrt'] = self.composer
        self.music['\xa9gen'] = self.genre

        self.music['cprt'] = self.copyright
        self.music['stik'] = [1]

        self.music['disk'] = [
            (
                int(self.discnumber),
                int(self.disctotal)
            )
        ]

        self.music['trkn'] = [
            (
                int(self.tracknumber),
                int(self.tracktotal)
            )
        ]

        # Freeform
        self.music['----:com.apple.iTunes:ISRC'] = [
            mutagen.mp4.MP4FreeForm(
                data=self.isrc.encode(),
                dataformat=mutagen.mp4.AtomDataType.UTF8
            )
        ]

        self.music['----:com.apple.iTunes:LABEL'] = [
            mutagen.mp4.MP4FreeForm(
                data=self.isrc.encode(),
                dataformat=mutagen.mp4.AtomDataType.UTF8
            )
        ]

        self.music['----:com.apple.iTunes:MEDIA'] = [
            mutagen.mp4.MP4FreeForm(
                data=self.media.encode(),
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
        - [x] tracknumber   -> tracknumber
        - [x] tracktotal    -> tracktotal
        - [x] discnumber    -> discnumber
        - [x] disctotal     -> disctotal
        - [x] isrc          -> isrc
        - [x] media         -> media
        - [x] label         -> label
        - [x] releasetype   -> releasetype
        """

        self.music['title'] = self.title
        self.music['artist'] = self.artist
        self.music['album'] = self.album
        self.music['albumartist'] = self.album_artist
        self.music['tracknumber'] = str(self.tracknumber)
        self.music['date'] = self.date
        self.music['composer'] = self.composer
        self.music['discnumber'] = str(self.discnumber)
        self.music['genre'] = self.genre
        self.music['disctotal'] = self.disctotal
        self.music['totaldiscs'] = self.disctotal
        self.music['tracktotal'] = self.tracktotal
        self.music['totaltracks'] = self.tracktotal
        self.music['isrc'] = self.isrc
        self.music['copyright'] = self.copyright
        self.music['releasetype'] = self.releasetype
        self.music['media'] = self.media
        self.music['label'] = self.label
        self.music['metadata_block_picture'] = [self._process_image()]

        self.music.save()

    def save_music(self):
        """Save new metadata."""

        if self.music_file_type == 'opus':
            self._save_opus_music()
        else:
            self._save_m4a_music()
