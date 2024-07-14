import requests
import re
import pathlib
import json

from .ammg_config import AmmgConfig

# Note:
#
# check_token_validaty()  depends on  api_work.py,
# the import is  not at the top  to avoid circular
# import.

CONFIG_FILE: pathlib.Path = AmmgConfig().config_file
APPLE_MUSIC_URL: str = 'https://music.apple.com'


class GetAppleMusicToken():
    def __init__(self,
                 check_token: bool = False):
        self.token: str = ''
        self.check_token: bool = check_token

        # Load local token
        if CONFIG_FILE.is_file():
            with open(CONFIG_FILE, 'r') as config_file:
                try:
                    content = json.load(
                        fp=config_file
                    )

                    self.token = content.get('token', '')
                except json.JSONDecodeError:
                    self.token = ''

    @staticmethod
    def _get_js_filename() -> str:
        """Returns the js file."""
        response = requests.get(APPLE_MUSIC_URL)

        content = response.text

        regex_pattern = re.compile('[^"]*index.[a-z0-9]*.js')

        match = re.findall(regex_pattern, content)

        return match[0]

    @staticmethod
    def _get_js_content() -> str:
        """Returns the js file content."""
        js_filename = GetAppleMusicToken._get_js_filename()
        response = requests.get(
            f'{APPLE_MUSIC_URL}{js_filename}'
        )

        return response.text

    @staticmethod
    def get_new_token() -> str:
        """Returns a new token and updates config."""
        jwt_regex_pattern = re.compile(
            'eyJhbGciOiJFUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6IldlYlBsYXlLaWQifQ'
            '[^"]+'
        )

        js_content = GetAppleMusicToken._get_js_content()
        jwt_match = re.findall(jwt_regex_pattern, js_content)

        token = jwt_match[0]

        # Update config file with new token
        with open(CONFIG_FILE, 'w') as config_file:
            json.dump(
                obj={'token': token},
                fp=config_file,
                indent=4
            )

        return token

    def get_token(self) -> str:
        """Returns the apple music JWT token."""
        if self.token == '':  # There's no token in config
            return self.get_new_token()

        if self.check_token:
            return (
                self.token
                if self.check_token_validity(self.token)
                else self.get_new_token()  # token in config is expired
            )

        # check_token is False
        return self.token

    @staticmethod
    def check_token_validity(token) -> bool:
        """Returns true if token is valid, otherwise false."""
        from .api_work import ApiMusicApple

        api = ApiMusicApple(
            token,
            '1681177202',
            clean_request=True,
        )

        if api.get_response_data().get('status') == 200:
            return True

        return False
