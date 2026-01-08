from typing import Optional

from beets.library import Library

from soulbrainarr.config_parser import get_config, CONFIG_DATA
from soulbrainarr.song import Song

CONFIG: CONFIG_DATA = get_config()


class BeetsSongDatabase:
    def __init__(self, lib_path: str):
        self.songs: list[Song] = []
        self.title_artist_index: dict[tuple[str, str], Song] = {}
        self.title_list: list[str] = []

        # Load songs from beets library
        lib = Library(lib_path)
        for item in lib.items():
            song = Song(
                item.title,
                item.artist,
                album=item.album,
                beets_file_path=str(item.path)
            )
            self.songs.append(song)

            # Exact-match index (lowercased)
            key = (song.song_title.lower(), song.artist.lower())
            self.title_artist_index[key] = song

            # Keep list of titles for fuzzy search
            self.title_list.append(song.song_title)
        print("Succesfully loaded beets library")

    def find_song(self, song: Song) -> Optional[Song]:
        matched_song = self.find_exact_song(song)
        if matched_song is None:
            matched_song = self.find_fuzzy_song(song)

        return matched_song

    def find_exact_song(self, song: Song) -> Optional[Song]:
        key = (song.song_title.lower(), song.artist.lower())
        has_song: bool = key in self.title_artist_index
        if has_song:
            print(f"Exact match found for song {song}")
            return self.title_artist_index[key]
        return None

    def find_fuzzy_song(self, song: Song) -> Optional[Song]:
        for other_song in self.songs:
            if song == other_song:
                print(f"Fuzzy Match for {song} found with song {other_song}")
                return other_song

        return None


def get_database() -> BeetsSongDatabase:
    return BeetsSongDatabase(
        CONFIG.BEETS.BEETS_DATABASE)


SONG_DATABASE: BeetsSongDatabase = get_database()


def skip_already_downloaded_songs(recommendations: list[Song]) -> list[Song]:
    new_recs: list[Song] = []

    for rec in recommendations:
        matched_song: Optional[Song] = SONG_DATABASE.find_song(rec)
        if matched_song is not None:
            new_recs.append(rec)

    return new_recs
