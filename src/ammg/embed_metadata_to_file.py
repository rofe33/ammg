import mutagen
import pathlib
import base64

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
        self.music_file = music_file
        self.music = mutagen.File(self.music_file)

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

    def save_music(self):
        """Save new metadata to file."""

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
