import os

from soulbrainarr.song import Song
from soulbrainarr.config_parser import get_config, CONFIG_DATA

playlist_header: str = "#EXTM3U‍8"


def make_playlist_file(playlist_name: str, songs: list[Song]) -> None:
    CONFIG: CONFIG_DATA = get_config()
    with open(os.path.join(CONFIG.NAVIDROME.NAVIDROME_MUSIC_PATH_PREFIX, f"{playlist_name}.m3u8"), 'w', encoding='utf-8') as file:
        file.write(f"{playlist_header}\n")
        for song in songs:
            # Some basic song info
            file.write(f"#EXTINF:-1,{song.artist} - {song.song_title}\n")
            # Song path relative to where Navidrome will see it
            file.write(f"{song.beets_file_path}\n")
