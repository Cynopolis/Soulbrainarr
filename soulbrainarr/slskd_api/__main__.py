import asyncio
import json

from slskd_api.apis._types import SearchResponseItem
from .slskd_client import get_slskd_client


def _print_formatted_dict(dictionary: dict):
    print(json.dumps(dictionary, indent=2))


async def search_slskd(search_text: str) -> list[SearchResponseItem]:
    """
    Have a slskd instance search soulseek for something
    """
    slskd = get_slskd_client()
    # TODO: Check if we've done this search in the last day
    # searches = slskd.searches.get_all()

    # TODO: Do some search text validation
    test_search_id = slskd.searches.search_text(search_text)["id"]

    # Wait for the search to be done
    while not slskd.searches.state(test_search_id)["isComplete"]:
        await asyncio.sleep(1)

    search_responses = slskd.searches.search_responses(test_search_id)

    return search_responses
