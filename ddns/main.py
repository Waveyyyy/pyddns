import miniupnpc
from dotenv import dotenv_values
from typing import Optional
import requests
import json

class ExternalIP():

    def __init__(self):
        self.FALLBACK_PROVIDERS: dict[str, str | None] = dotenv_values(".fallback_providers")

    def get_wan_ip_http(self, provider: str, timeout: float = 5.0) -> Optional[str]:
        """
        Get WAN IP address from an external provider.
        """
        url = self.FALLBACK_PROVIDERS.get(provider)
        if not url:
            raise ValueError(f"Unknown provider '{provider}'. Options\n{list(self.FALLBACK_PROVIDERS.keys())}")

        try:
            resp = requests.get(url=url, timeout=timeout)
            resp.raise_for_status()
            wan_ip: str = resp.text.strip()

            # check if the response was plain text or json
            if "json" in resp.headers.get("content-type", ""):
                return json.loads(wan_ip.split(",")[0]).values()

            return wan_ip

        except requests.HTTPError:
            return None

    def get_wan_ip_upnp(self, fallback: bool) -> Optional[str]:
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
                for provider in self.FALLBACK_PROVIDERS.keys():
                    ip: str | None = self.get_wan_ip_http(provider)
                    if ip:
                        return ip


if __name__ == "__main__":
    print(ExternalIP().get_wan_ip_upnp(True))

