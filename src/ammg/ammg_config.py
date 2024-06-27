import pathlib
import platform


class AmmgConfig():
    """Handles Config."""

    def __init__(self):
        system_os = platform.system()

        if system_os == 'Linux':
            # ~/.config/ammg
            self.config_dir = pathlib.Path.home().joinpath(
                '.config', 'ammg'
            )
        elif system_os == 'Darwin':
            # ~/Library/Preferences/ammg
            self.config_dir = pathlib.Path.home().joinpath(
                'Library', 'Preferences', 'ammg'
            )
        elif system_os == 'Windows':
            # ~\AppData\Roaming\ammg
            self.config_dir = pathlib.Path.home().joinpath(
                'AppData', 'Roaming', 'ammg'
            )
        else:
            # If     unknown     system     create
            # ammg_config folder  for config, in
            # the current working directory.
            self.config_dir = pathlib.Path().cwd().joinpath(
                'ammg_config'
            )

        # Create directory if it doesn't exists
        if not self.config_dir.is_dir():
            self.config_dir.mkdir(parents=True)

        self.config_file = self.config_dir.joinpath(
            'ammg_config.json'
        )
