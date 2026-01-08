import os

from soulbrainarr.song import Song
from soulbrainarr.config_parser import get_config, CONFIG_DATA
from soulbrainarr.beets_api.duplicate_tools import get_database, BeetsSongDatabase

playlist_header: str = "#EXTM3U‍8"
SONG_DATABASE: BeetsSongDatabase = get_database()


def make_playlist_file(playlist_name: str, songs: list[Song]) -> None:
    '''
    Make an m3u8 playlist file from a list of songs that you pass in
    '''
    CONFIG: CONFIG_DATA = get_config()
    with open(os.path.join(CONFIG.NAVIDROME.NAVIDROME_MUSIC_PATH_PREFIX, f"{playlist_name}.m3u8"), 'w', encoding='utf-8') as file:
        file.write(f"{playlist_header}\n")
        for song in songs:
            # Some basic song info
            file.write(f"#EXTINF:-1,{song.artist} - {song.song_title}\n")

            # If the provided song doesn't have a filepath,
            # see if we can find a matchign song in our database with the file path
            if song.beets_file_path is None:
                matched_song = SONG_DATABASE.find_fuzzy_song(song)
                if matched_song is not None:
                    song = matched_song

            # Song path relative to where Navidrome will see it
            file.write(
                f"{os.path.join(CONFIG.NAVIDROME.NAVIDROME_MUSIC_PATH_PREFIX, song.beets_file_path)}\n")
