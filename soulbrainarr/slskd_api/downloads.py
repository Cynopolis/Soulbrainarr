from slskd_api.apis._types import SearchResponseItem, Transfer
from requests.exceptions import HTTPError
from .log_parser import parse_log_to_exception
from .slskd_client import get_slskd_client
from time import time
import asyncio


def attempt_download(search_response: SearchResponseItem) -> bool:
    '''
    This will attempt to enqueue all of the search response items given to it
    '''
    slskd = get_slskd_client()

    username = search_response["username"]
    files = search_response["files"]
    success: bool = False

    try:
        if slskd.transfers.enqueue(username, files):
            success = True
    except HTTPError as e:
        print(e)

    # Check the download result
    log = slskd.logs.get()[-1]
    error = parse_log_to_exception(log)
    if error is not None:
        print(error)
        success = False
    return success


def attempt_downloads(search_responses: list[SearchResponseItem]) -> bool:
    '''
    This will individually attempt to download each of the given search response items until one succeeds
    '''
    success: bool = False
    for response in search_responses:
        if attempt_download(response):
            success = True
            break

    return success


def is_download_in_progress(download: Transfer) -> bool:
    # If any file is incomplete return false
    for directory in download["directories"]:
        for file in directory["files"]:
            # TODO: We should check file["state"] to handle errored downloads
            if file["percentComplete"] < 100:
                return True

    return False


def are_downloads_in_progress(downloads: list[Transfer]) -> bool:
    for download in downloads:
        if is_download_in_progress(download):
            return True
    return False


async def wait_for_downloads_to_complete(timeout_minutes: float = 10) -> bool:
    slskd = get_slskd_client()

    all_downloads_completed_before_timeout: bool = False

    # Clear all completed downloads
    slskd.transfers.remove_completed_downloads()

    # monitor for any in-progress downloads and return when there are none
    start_monitoring_time = time()
    while time() - start_monitoring_time < timeout_minutes*60:
        # Break out of waiting if all downloads are complete
        if not are_downloads_in_progress(slskd.transfers.get_all_downloads()):
            all_downloads_completed_before_timeout = False
            break
        await asyncio.sleep(5)

    return all_downloads_completed_before_timeout
