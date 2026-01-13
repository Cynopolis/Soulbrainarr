from pathlib import Path
from typing import Optional
import os

import beets

from soulbrainarr.song import Song
from soulbrainarr.config_parser import CONFIG

from .beet_command_line import run_beet_command, parse_failed_imports_from_error_string

MINIMAL_BEETS_CONFIG = """\
directory: {music_path}
library: {library_path}

import:
  move: yes
  timid: no

paths:
  default: $artist/$album/$track - $title
"""


class BeetAPI:
    def __init__(self):
        self._do_initialization()

        self.beet_library = beets.library.Library(CONFIG.BEETS.BEETS_DATABASE)

    def _do_initialization(self):
        config_file_path = Path(CONFIG.BEETS.BEETS_DATABASE)
        if not config_file_path.exists():
            print(
                f"BEETS WARNING: Config file path {config_file_path} doesn't exist. Creating a basic config at this location.")
            config_file_path.parent.mkdir(parents=True, exist_ok=True)
            minimal_cfg = MINIMAL_BEETS_CONFIG.format(
                library_path=str(CONFIG.BEETS.BEETS_DATABASE),
                music_path=str(CONFIG.BEETS.BEETS_IMPORTED)
            )
            config_file_path.write_text(minimal_cfg, encoding="utf-8")

        db_file_path = Path(CONFIG.BEETS.BEETS_CONFIG)
        if not db_file_path.exists():
            print(
                f"BEETS WARNING: Database file path {db_file_path} doesn't exist. Creating an empty database at this location.")
            db_file_path.parent.mkdir(parents=True, exist_ok=True)

        beets_inbox_path = Path(CONFIG.BEETS.BEETS_INBOX)
        if not beets_inbox_path.exists():
            print(
                f"BEETS WARNING: Inbox file path {beets_inbox_path} doesn't exist. Creating an empty inbox at this location.")
            beets_inbox_path.mkdir(parents=True, exist_ok=True)

        beets_import_path = Path(CONFIG.BEETS.BEETS_IMPORTED)
        if not beets_import_path.exists():
            print(
                f"Warning, that path you provided for BEETS_IMPORTED ({beets_import_path}) doesn't exist. This probably means that your ocnfig is wrong.")
            print(
                f"Creating beets import folder at: {beets_import_path}")
            beets_import_path.mkdir(parents=True, exist_ok=True)

    def search_song(self, song: Song) -> Optional[Song]:
        '''
        Find the closest matching song in the beets database and return it. Returns None if there's no matching song.
        '''
        query = (
            f'artist:"{song.artist}" '
            f'title:"{song.song_title}"'
        )

        results = list(self.beet_library.items(query=query))

        if not results:
            return None

        # return the top result
        item = results[0]
        return Song(item.title, item.artist, album=item.album, beets_file_path=item.path)

    def import_folder(self, folder_path: str = CONFIG.BEETS.BEETS_INBOX):
        folder_path = Path(folder_path)
        if not folder_path.exists():
            raise FileNotFoundError(
                f"Cannot import songs from {folder_path} because it doesn't exist.")

        # Run an import that is going to search for full album matches
        _, error_output = run_beet_command(["import", str(folder_path)])

        failed_imports = parse_failed_imports_from_error_string(error_output)

        # Retry failed items with singleton import
        for song_path in failed_imports:
            if os.path.exists(song_path):
                _, error_output = run_beet_command(
                    ["import", "-s", str(folder_path)])
                failed_singleton_imports = parse_failed_imports_from_error_string(
                    error_output)
                if len(failed_singleton_imports) > 0:
                    print(
                        f"Failed to import the following songs:\n{failed_singleton_imports}")


ssBEET_API = BeetAPI()
