import pathlib
import platform
import sys


class AmmgConfig():
    """Handles Config."""

    def __init__(self) -> None:
        self.__config_dir: pathlib.Path

        system_os = platform.system()

        if system_os == 'Linux':
            # ~/.config/ammg
            self.__config_dir = pathlib.Path.home().joinpath(
                '.config', 'ammg'
            )
        elif system_os == 'Darwin':
            # ~/Library/Preferences/ammg
            self.__config_dir = pathlib.Path.home().joinpath(
                'Library', 'Preferences', 'ammg'
            )
        elif system_os == 'Windows':
            # ~\AppData\Roaming\ammg
            self.__config_dir = pathlib.Path.home().joinpath(
                'AppData', 'Roaming', 'ammg'
            )
        else:
            # If     unknown     system     create
            # ammg_config folder  for config, in
            # the current working directory.
            self.__config_dir = pathlib.Path().cwd().joinpath(
                'ammg_config'
            )

        self.__config_file = self.__config_dir.joinpath(
            'ammg_config.json'
        )

    @property
    def config_dir(self):
        """The config_dir property."""
        # Create directory if it doesn't exists
        if not self.__config_dir.is_dir():
            self.__config_dir.mkdir(parents=True)

        return self.__config_dir

    @config_dir.setter
    def config_dir(self, dir: pathlib.Path):
        if isinstance(dir, pathlib.Path):
            self.__config_dir = dir
        else:
            print('dir should be a pathlib.Path object.')

            sys.exit(1)

    @property
    def config_file(self):
        """The config_file property."""
        return self.__config_file

    @config_file.setter
    def config_file(self, file: pathlib.Path):
        if isinstance(file, pathlib.Path) and not file.is_dir():
            self.__config_file = file
        else:
            print('file should be a pathlib.Path object.')

            sys.exit(1)
