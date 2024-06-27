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


class GetAppleMusicToken():
    def __init__(self,
                 token: str = '',
                 no_check: bool = False):
        self.apple_music_url: str = 'https://music.apple.com'

        self.token: str = token
        self.no_check: bool = no_check

        self.config_file: pathlib.Path = AmmgConfig().config_file

        # Load local token
        if self.config_file.is_file():
            with open(self.config_file, 'r') as config_file:
                try:
                    content = json.load(
                        fp=config_file
                    )

                    self.token = content.get('token', '')
                except json.JSONDecodeError:
                    self.token = ''

    def _get_js_filename(self) -> str:
        """Returns the js file."""
        response = requests.get(self.apple_music_url)

        content = response.text

        regex_pattern = re.compile('[^"]*index.[a-z0-9]*.js')

        match = re.findall(regex_pattern, content)

        return match[0]

    def _get_js_content(self) -> str:
        """Returns the js file content."""
        js_filename = self._get_js_filename()
        response = requests.get(
            f'{self.apple_music_url}{js_filename}'
        )

        return response.text

    def get_token(self) -> str:
        """Returns the apple music JWT token."""
        # If no_check, return stored token if stored
        if self.no_check and self.token != '':
            return self.token

        # Check for stored token validity if it's expired
        if self.check_token_validity():
            return self.token

        jwt_regex_pattern = re.compile(
            'eyJhbGciOiJFUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6IldlYlBsYXlLaWQifQ'
            '[^"]+'
        )

        js_content = self._get_js_content()
        jwt_match = re.findall(jwt_regex_pattern, js_content)

        self.token = jwt_match[0]

        # Update config file with new token
        with open(self.config_file, 'w') as config_file:
            json.dump(
                obj={'token': self.token},
                fp=config_file,
                indent=4
            )

        return self.token

    def check_token_validity(self) -> bool:
        """Returns true if token is valid, otherwise false."""
        from .api_work import ApiMusicApple

        api = ApiMusicApple(
            self.token,
            '1681177202',
            clean_request=True,
        )

        if api.get_response_data().get('status') == 200:
            return True

        return False
