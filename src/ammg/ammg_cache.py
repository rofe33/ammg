import pathlib
import platform


class AmmgCache():
    """Handles cache work."""

    def __init__(self):
        system_os = platform.system()

        if system_os == 'Linux':
            # ~/.cache/ammg
            self.cache_dir = pathlib.Path.home().joinpath(
                '.cache', 'ammg'
            )
        elif system_os == 'Darwin':
            # ~/Library/Caches/ammg
            self.cache_dir = pathlib.Path.home().joinpath(
                'Library', 'Caches', 'ammg'
            )
        elif system_os == 'Windows':
            # ~\AppData\Local\ammg
            self.cache_dir = pathlib.Path.home().joinpath(
                'AppData', 'Local', 'ammg'
            )
        else:
            # If     unknown     system     create
            # ammg_cache  folder  for cache,  in
            # the current working directory.
            self.cache_dir = pathlib.Path().cwd().joinpath(
                'ammg_cache'
            )

        # Create directory if it doesn't exists
        if not self.cache_dir.is_dir():
            self.cache_dir.mkdir(parents=True)

    def clean_cache(self,
                    dry_run: bool = True):
        """Clean the cache from system."""
        files: list[pathlib.Path] = [
            *[
                x for x in self.cache_dir.glob('*.json')
            ],
            *[
                x for x in self.cache_dir.glob('*.jpg')
            ]
        ]

        total_size = sum(
            x.stat().st_size for x in files
        )

        for file in files:
            print(f'deleting {file.absolute()}')

            if not dry_run:
                file.unlink(
                    missing_ok=True,
                )

        if len(files) > 0:
            print()

        print(
            f'total cleaned size is {total_size} bytes'
            f' ({total_size / (1024 ** 2):.2f} Megabytes)',
            end=''
        )

        if dry_run:
            print(' (DRY RUN)')
        else:
            print()

    def get_cache_size(self) -> int:
        """Returns the ammg cache size in bytes.

        Note:
            It  returns  the  size  based  on  the
            actual file  size, not the  disk space
            consumed of each file.

            It returns the size  of the json & jpg
            files generated  by ammg,  any other
            files added  by the  user will  not be
            added.
        """
        return sum([
            *[
                x.stat().st_size for x in self.cache_dir.glob('*.json')
            ],
            *[
                x.stat().st_size for x in self.cache_dir.glob('*.jpg')
            ]
        ])
