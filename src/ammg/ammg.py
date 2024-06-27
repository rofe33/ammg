#!/usr/bin/env python3

# Author: Raphael Tannous
# Source: https://github.com/rofe33/ammg
# License: GPLv3

import argparse
import pathlib
import sys
import mutagen
import shutil
import requests
import math

from .embed_metadata_to_file import EmbedMetadataToFile
from .get_apple_music_token import GetAppleMusicToken
from .api_work import ApiMusicApple
from .ammg_cache import AmmgCache


def parse_arguments():
    epilog = 'All The Glory To Jesus God...'
    parser = argparse.ArgumentParser(
        prog='ammg',
        description=(
            'A tool for appending metadata to music files from Apple Music.'
        ),
        epilog=epilog,
        add_help=True,
        allow_abbrev=True,
        exit_on_error=True,
    )

    subparsers = parser.add_subparsers(
        title='Commamds',
        required=True,
    )

    # Main Program
    get_parser_help = 'Download music metadata and embed them into file.'
    get_parser = subparsers.add_parser(
        name='get',
        description=get_parser_help,
        epilog=epilog,
        help=get_parser_help,
        add_help=True,
        allow_abbrev=True,
        exit_on_error=True,
    )

    get_parser.add_argument(
        'directory',
        type=pathlib.Path,
        help=(
            'Path to the directory that contains the '
            'music downladed using yt-dlp'
        ),
        metavar='path/to/directory',
    )

    get_parser.add_argument(
        '-i',
        '--album-id',
        type=int,
        help='Album id from Apple Music',
        required=True,
    )

    get_parser.add_argument(
        '-o',
        '--output-directory',
        type=pathlib.Path,
        help='Output directory in which the music files will be moved',
        default=pathlib.Path('Music'),
        metavar='path/to/output_directory',
        required=True,
    )

    get_parser.add_argument(
        '-s',
        '--storefront',
        type=str,
        help='Storefront to be used when querying metadata',
        default='us',
    )

    get_parser.add_argument(
        '-t',
        '--tracks',
        nargs='+',
        help='Make metadata for just a bunch of tracks',
    )

    get_parser.add_argument(
        '-c',
        '--clean-request',
        action='store_true',
        default=False,
        help='Don\'t get cached requests',
    )

    get_parser.add_argument(
        '--cover-width',
        type=int,
        help='Cover width (default: 500)',
        default=500,

    )

    get_parser.add_argument(
        '--cover-height',
        type=int,
        help='Cover height (default: 500)',
        default=500,
    )

    get_parser.add_argument(
        '--do-not-check-token',
        action='store_true',
        default=False,
        help='Whether to not check token before using it',
    )

    get_parser.add_argument(
        '--duration-error',
        type=int,
        default=5,
        help='Duration error when attempting to look correct file music.',
    )

    get_parser.add_argument(
        '--create-lrc-file',
        action='store_true',
        default=False,
        help='Whether to create a .lrc file next to the opus file',
    )

    get_parser.add_argument(
        '--lrc-file-text',
        type=str,
        default='No Lyrics.',
        help='Text written in the .lrc file (default: No Lyrics.)',
    )

    get_parser.add_argument(
        '--create-txt-file',
        action='store_true',
        default=False,
        help='Whether to create a .txt file next to the opus file',
    )

    get_parser.add_argument(
        '--txt-file-text',
        type=str,
        default='No Lyrics.',
        help='Text written in the .txt file (default: No Lyrics.)',
    )

    # Cache Work
    cache_parser_help = 'Check and work with cache.'
    cache_parser = subparsers.add_parser(
        name='cache',
        description=cache_parser_help,
        epilog=epilog,
        help=cache_parser_help,
        add_help=True,
        allow_abbrev=True,
        exit_on_error=True,
    )

    cache_group = cache_parser.add_argument_group(
        title='Cache Work',
    )

    cache_group_exclusive = cache_group.add_mutually_exclusive_group(
        required=False,
    )

    cache_group.add_argument(
        '--dry-run',
        action='store_true',
        default=False,
        help='Can be used with --clean-cache, but not removing anything.'
    )

    cache_group_exclusive.add_argument(
        '--get-cache-size',
        action='store_true',
        default=False,
        help='Print the size of the cache in Megabytes.',
    )

    cache_group_exclusive.add_argument(
        '--clean-cache',
        action='store_true',
        default=False,
        help='Removes the cache folder from system.',
    )

    cache_group_exclusive.add_argument(
        '--get-cache-path',
        action='store_true',
        default=False,
        help='Print the path of the cache.',
    )

    get_parser.set_defaults(
        func=get_args,
    )

    cache_parser.set_defaults(
        func=cache_args,
    )

    args = parser.parse_args()

    args.func(args)

    return None


def get_args(args):
    """Work with the get command."""
    token = GetAppleMusicToken(
        no_check=args.do_not_check_token,
    ).get_token()

    api = ApiMusicApple(
        token=token,
        album_id=args.album_id,
        storefront=args.storefront,
        clean_request=args.clean_request,
    )

    # Requesting album info and analyzing int
    response = api.get_response_data()
    album_info = api.analyze_response_album(response)

    # Downloading Cover to cache
    cover_path = api.cache_dir.joinpath(f'{args.album_id}.jpg')
    cover_info = {}
    cover_url = album_info.get('cover_url')
    cover_url = cover_url.replace(
        '{w}',
        str(args.cover_width),
    ).replace(
        '{h}',
        str(args.cover_height),
    )

    # If clean request re-download the cover
    if args.clean_request or not cover_path.is_file():
        response = requests.get(cover_url, stream=True)

        with open(cover_path, 'wb') as cf:
            shutil.copyfileobj(response.raw, cf)

    # Output directory work
    output_directory: pathlib.Path = args.output_directory

    alphabet_directory: pathlib.Path = output_directory.joinpath(
        album_info.get('album_artist_name')[0].upper()
    )

    artist_directory: pathlib.Path = alphabet_directory.joinpath(
        album_info.get('album_artist_name')
    )

    album_directory = artist_directory.joinpath(
        album_info.get('album_name')
    )

    if not album_directory.is_dir():
        album_directory.mkdir(parents=True)

    for track in album_info.get('tracks', []):
        track_number = track.get('track_number')

        if (args.tracks is not None
                and track_number not in args.tracks):
            continue

        print(f'Looking for {track.get('title')} in {args.directory}.')

        # Valid file for tags, is based on:
        #   - Youtube title found in apple title
        #   - Duration error is under 5 seconds (Default)
        directory: pathlib.Path = args.directory
        apple_duration = track.get('duration') // 1000
        apple_title = track.get('title').lower()

        directory_files = [x for x in directory.iterdir() if x.is_file()]

        music_file = None
        for file in directory_files:
            file_duration = math.floor(mutagen.File(file).info.length)
            file_title = file.stem.lower()

            # Error for duration difference
            error = math.fabs(apple_duration - file_duration)

            # 5 seconds difference (Default)
            if error <= args.duration_error and file_title in apple_title:
                music_file = file

        if music_file is None:
            print('\tNo music found.')
            continue

        new_music_file = album_directory.joinpath(
            f'{track.get("track_number"):#02} {track.get("title")}'
            f'{music_file.suffix}'
        )
        new_txt_file = album_directory.joinpath(
            f'{track.get("track_number"):#02} {track.get("title")}'
            f'.txt'
        )
        new_lrc_file = album_directory.joinpath(
            f'{track.get("track_number"):#02} {track.get("title")}'
            f'.lrc'
        )

        # If  there's more  than one  disc create  a
        # Disc ## folder for each disc.
        if album_info.get('disc_count') >= 2:
            disc_dir = album_directory.joinpath(
                f'Disc {track.get("discnumber"):#02}'
            )

            new_music_file = disc_dir.joinpath(
                f'{track.get("track_number"):#02} {track.get("title")}'
                f'{music_file.suffix}'
            )
            new_txt_file = disc_dir.joinpath(
                f'{track.get("track_number"):#02} {track.get("title")}'
                f'.txt'
            )
            new_lrc_file = disc_dir.joinpath(
                f'{track.get("track_number"):#02} {track.get("title")}'
                f'.lrc'
            )

            if not disc_dir.is_dir():
                disc_dir.mkdir()

        if music_file.is_file():
            print(f'\tFound {music_file}')
            print('\tEmbeding Metadata ', end='')

            embed_data = EmbedMetadataToFile(
                music_file=music_file,
                title=track.get('title'),
                artist=track.get('artist'),
                album=album_info.get('album_name'),
                album_artist=album_info.get('album_artist_name'),
                date=album_info.get('album_release_date'),  # You can also have track.date
                composer=track.get('composer', ''),
                genre=track.get('genre'),
                discnumber=str(track.get('discnumber')),
                disctotal=str(album_info.get('disc_count')),
                tracknumber=str(track.get('track_number')),
                tracktotal=str(album_info.get('track_count')),
                media=track.get('media'),
                releasetype=album_info.get('release_type'),
                isrc=track.get('isrc'),
                copyright_=album_info.get('copyright'),
                label=album_info.get('record_label'),
                cover=cover_path,
                cover_info=cover_info,
            )

            embed_data.save_music()
            print('(done).')

            print(f'\tMoving to {new_music_file}.')

            music_file.rename(new_music_file)

            if args.create_lrc_file:
                new_lrc_file.write_text('No Lyrics.')
                print('\tCreating lrc file.')

            if args.create_txt_file:
                new_txt_file.write_text('No Lyrics.')
                print('\tCreating txt file.')

    sys.exit(0)


def cache_args(args):
    """Work with the cache command."""
    cache = AmmgCache()

    if args.get_cache_size:
        cache_size = cache.get_cache_size()

        print(
            f'Actual file size: {cache_size} bytes'
            f' ({cache_size / (1024 ** 2):.2f} Megabytes).'
        )

        sys.exit(0)

    if args.get_cache_path:
        print(cache.cache_dir.absolute())

        sys.exit(0)

    if args.clean_cache:
        cache.clean_cache(args.dry_run)

        sys.exit(0)

    if args.dry_run:
        print('You should use --dry-run with --clean-cache.')

        sys.exit(0)


def main():
    parse_arguments()

    sys.exit(0)
