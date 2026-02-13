import miniupnpc
from dotenv import dotenv_values
from typing import Optional
import requests
import json
import regex

FALLBACK_PROVIDERS: dict[str, str | None] = dotenv_values(".fallback_providers")
IP_REGEX: str = r"^[0-9]{1,3}.[0-9]{1,3}.[0-9]{1,3}.[0-9]{1,3}$"

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
        wan_ip: str = resp.text.strip()

        # check if the response was plain text or json
        if "json" in resp.headers.get("content-type", ""):
            for val in json.loads(wan_ip).values(): # iterate over values incase there are multiple
                if regex.match(IP_REGEX, val): # use regex to check if any values are IP addresses
                    wan_ip=val
                    break
                else:
                    wan_ip=""
            if not wan_ip:
                return None # if no values were IP's, return None to signify failure

        return wan_ip

    except requests.HTTPError:
        return None

def get_wan_ip_upnp(fallback: bool) -> Optional[str]:
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
        if fallback:
            for provider in FALLBACK_PROVIDERS.keys():
                ip: str | None = get_wan_ip_http(provider)
                if ip:
                    return ip




if __name__ == "__main__":
    print(get_wan_ip())

