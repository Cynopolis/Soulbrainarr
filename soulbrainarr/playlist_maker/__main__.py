from soulbrainarr.song import Song
from os.path import join

playlist_header: str = "#EXTM3U‍8"


def to_playlist(playlist_name: str, playlist_folder_path: str, songs: list[Song]) -> None:
    with open(join(playlist_folder_path, playlist_name, ".m3u8"), 'w', encoding='utf-8') as file:
        file.write(f"{playlist_header}\n")
        for song in songs:
            # Some basic song info
            file.write(f"#EXTINF:-1,{song.artist} - {song.song_title}")
            # Song path relative to where Navidrome will see it
            file.write(f"{song.beets_file_path}\n")
