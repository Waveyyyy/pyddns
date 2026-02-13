import miniupnpc
from dotenv import dotenv_values
from typing import Optional
import requests

FALLBACK_PROVIDERS: dict[str, str | None] = dotenv_values(".fallback_providers")

def get_wan_ip_http(provider: str, timeout: float = 5.0) -> Optional[str]:
    """
    Get WAN IP address from an external provider.
    """
    url = FALLBACK_PROVIDERS.get(provider)
    if not url:
        raise ValueError(f"Unknown provider '{provider}'. Options\n{list(FALLBACK_PROVIDERS.keys())}")
    try:
        resp = requests.get(url=url, timeout=timeout)
        resp.raise_for_status()
        return resp.text.strip()
    except requests.HTTPError:
        return None

def get_wan_ip_upnp() -> Optional[str]:
    """
    Get WAN IP adress from router using uPnP.
    """
    try:
        upnp = miniupnpc.UPnP()
        upnp.discoverdelay = 200 # Discovery timeout (default: 2000)
        if not upnp.discover(): # Number of devices (0 is a failure state)
            return None

        upnp.selectigd() # Select Internet Gateway Device (router)
        return upnp.externalipaddress() # Return WAN IP as a string

    except Exception:
        return None


if __name__ == "__main__":
    print(get_wan_ip())

