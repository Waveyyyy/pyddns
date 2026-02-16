import miniupnpc
from dotenv import dotenv_values
from typing import Optional
import requests
import json
from os import getenv

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


class Cloudflare():
    """Manages a single Cloudflare DNS A record with local caching."""

    def __init__(self, api_token: str, zone_id: str, record_name: str):
        self.headers = {
            "Authorization": f"Bearer {api_token}",
            "Content-Type": "application/json"
        }
        self.zone_id = zone_id
        self.record_name = record_name
        self.cf_api = "https://api.cloudflare.com/client/v4"
        self.record_id: str | None = None
        self.cached_ip: str | None = None

    def _get_record(self) -> tuple[str, str]:
        """Fetch record ID and current IP from Cloudflare. Called once on startup."""
        resp = requests.get(
            f"{self.cf_api}/zones/{self.zone_id}/dns_records",
            headers = self.headers,
            params = {"type": "A", "name": self.record_name}
        )
        resp.raise_for_status()
        records = resp.json()["result"]

        if not records:
            raise ValueError(f"No A record found for {self.record_name}")

        return records[0]["id"], records[0]["content"]

    def get_ip(self):
        """Get the current IP address from the cache, or fetch if not cached."""
        if not self.cached_ip:
            self.record_id, self.cached_ip = self._get_record()

        return self.cached_ip

    def update_ip(self, new_ip: str) -> bool:
        """Update the A record and refresh the cache."""
        if self.record_id is None:
            self.record_id, self.cached_ip = self._get_record()

        # https://developers.cloudflare.com/api/resources/dns/subresources/records/methods/get/
        resp = requests.patch(
            f"{self.cf_api}/zones/{self.zone_id}/dns_records/{self.record_id}",
            headers=self.headers,
            json={
                "type": "A",
                "name": self.record_name,
                "content": new_ip,
                "ttl": 1,
                "proxied": False
            }
        )
        resp.raise_for_status()

        if resp.json()["success"]:
            self.cached_ip = new_ip
            return True
        return False


if __name__ == "__main__":
    cloudflare_data: dict[str, str | None] = dotenv_values(".cloudflare")
    cf = Cloudflare(
        api_token=cloudflare_data["CF_API_TOKEN"] if cloudflare_data["CF_API_TOKEN"] else str(getenv("CF_API_TOKEN")),
        zone_id=cloudflare_data["CF_ZONE_ID"] if cloudflare_data["CF_ZONE_ID"] else str(getenv("CF_ZONE_ID")),
        record_name=cloudflare_data["CF_RECORD_NAME"] if cloudflare_data["CF_RECORD_NAME"] else str(getenv("CF_RECORD_NAME"))
    )

    print(cf.get_ip())

    print(ExternalIP().get_wan_ip_upnp(True))

