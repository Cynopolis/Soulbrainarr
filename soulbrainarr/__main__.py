import asyncio
from time import sleep

from soulbrainarr.song import Song

from .config_parser import get_config, CONFIG_DATA
from .listen_brainz_api import get_recommendation_list
from .slskd_api import search_slskd, attempt_downloads, wait_for_downloads_to_complete
from .beets_api import BEET_API
from .playlist_maker import make_playlist_file

CONFIG: CONFIG_DATA = get_config()


def remove_preexisting_songs(songs: list[Song]):
    new_songs: list[Song] = []
    for song in songs:
        if BEET_API.search_song(song) is None:
            new_songs.append(song)

    return new_songs


async def search_and_download(rec: Song):
    search_term: str = f"{rec.artist} {rec.song_title}"
    print(f"Searching for: {search_term}")
    search_responses = await search_slskd(search_term)

    if attempt_downloads(search_responses):
        print(f"Download for {search_term} queued succesfully")
    else:
        print(f"Download for {search_term} failed to queue")


async def search_and_download_recommendations(recs: list[Song]):
    # search recommendations in slskd_api
    await asyncio.gather(*[search_and_download(rec) for rec in recs])


async def main(song_batch_size: int, song_rec_offset: int):
    print("================================")

    # Get recommendations from listen brainz
    print(
        f"Getting {song_batch_size} recommendations with offset {song_rec_offset}:")
    recommendations: list[Song] = get_recommendation_list(
        CONFIG.LISTEN_BRAINZ.USERNAME,
        CONFIG.LISTEN_BRAINZ.EMAIL,
        song_batch_size,
        recommendation_offset=song_rec_offset
    )

    # List all of the recommendations in the logs
    for recommendation in recommendations:
        print(recommendation)

    # Skip any already downloaded songs
    print("Skipping already downloaded songs")
    songs_to_download = remove_preexisting_songs(recommendations)

    # Download all of the songs in the recommendations list
    if len(songs_to_download) > 0:
        print("Queueing Downloads")
        await search_and_download_recommendations(songs_to_download)
    else:
        print("No Downloads to Queue.")

    # Wait for the downloads to complete
    print("Waiting for all downloads to complete")
    await wait_for_downloads_to_complete()

    print("Importing downloaded songs into beets")
    BEET_API.import_folder(CONFIG.SLSKD.SLSKD_DOWNLOADS)

    print("Making playlist file")
    make_playlist_file("Discover Weekly", recommendations)
    print("================================")


async def looper():
    # Make sure beets will be initialized correctly
    run_interval_seconds: int = CONFIG.SOULBRAINARR.RUN_INTERVAL_MINUTES * 60
    song_offset: int = 0
    while True:
        await main(CONFIG.SOULBRAINARR.SONG_BATCH_SIZE, song_offset)
        song_offset += CONFIG.SOULBRAINARR.SONG_BATCH_SIZE
        print(
            f"Sleeping for {CONFIG.SOULBRAINARR.RUN_INTERVAL_MINUTES} minutes")
        sleep(run_interval_seconds)

if __name__ == "__main__":
    asyncio.run(looper())
