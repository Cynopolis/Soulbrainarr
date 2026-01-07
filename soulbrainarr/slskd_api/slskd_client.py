import slskd_api

from soulbrainarr.config_parser import get_config, CONFIG_DATA


CONFIG: CONFIG_DATA = get_config()


def get_slskd_client():
    SLSKD = slskd_api.SlskdClient(
        host=CONFIG.SLSKD.HOST,
        api_key=CONFIG.SLSKD.API_KEY
    )
    return SLSKD
