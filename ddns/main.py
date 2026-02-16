import miniupnpc
from dotenv import dotenv_values,load_dotenv
from typing import Optional
import requests
import json
from os import getenv
import time
import logging
import sys
from pathlib import Path

class ExternalIP():

    def __init__(self):
        self.FALLBACK_PROVIDERS: dict[str, str | None] = dotenv_values("fallback_providers")

    def get_wan_ip_http(self, provider: str, timeout: float = 5.0) -> Optional[str]:
        """
        Get WAN IP address from an external provider.
        """
        url = self.FALLBACK_PROVIDERS.get(provider)
        if not url:
            log.error(f"Unknown provider '{provider}'")
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
            log.warning(f"WAN IP http fallback failed for provider '{provider}'")
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
            wan_ip = upnp.externalipaddress()
            log.info(f"WAN IP detected via UPnP: {wan_ip}")

            return wan_ip # Return WAN IP as a string

        except Exception:
            if fallback:
                log.warning("WAN IP detection via UPnP failed, trying http fallback")
                for provider in self.FALLBACK_PROVIDERS.keys():
                    ip: str | None = self.get_wan_ip_http(provider)
                    if ip:
                        log.info(f"WAN IP detected via http: {ip}")
                        return ip
                    else:
                        log.error("WAN IP detection via http fallback failed")


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
        api_url: str = f"{self.cf_api}/zones/{self.zone_id}/dns_records"

        try:
            resp = requests.get(
                url=api_url,
                headers = self.headers,
                params = {"type": "A", "name": self.record_name}
            )
            resp.raise_for_status()
            records = resp.json()["result"]

            if not records:
                raise ValueError(f"No A record found for {self.record_name}")

            log.info(f"record_id: {records[0]["id"]}")
            log.info(f"record_content: {records[0]["content"]}")

            return records[0]["id"], records[0]["content"]
        except requests.HTTPError:
            log.error(f"Failed to get Cloudflare A record at url: {api_url}")
            return "", "" # rework

    def get_ip(self):
        """Get the current IP address from the cache, or fetch if not cached."""
        if not self.cached_ip:
            self.record_id, self.cached_ip = self._get_record()
            log.info(f"Updated cached_ip: {self.cached_ip}")
            log.info(f"Updated record_id: {self.record_id}")

        return self.cached_ip

    def update_ip(self, new_ip: str) -> bool:
        """Update the A record and refresh the cache."""
        if self.record_id is None:
            self.record_id, self.cached_ip = self._get_record()
            log.info(f"Updated cached_ip: {self.cached_ip}")
            log.info(f"Updated record_id: {self.record_id}")

        # https://developers.cloudflare.com/api/resources/dns/subresources/records/methods/get/
        api_url = f"{self.cf_api}/zones/{self.zone_id}/dns_records/{self.record_id}"

        try:
            resp = requests.patch(
                url=api_url,
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
                log.info(f"Cloudflare A record change successful")
                return True
            return False
        except requests.HTTPError:
            log.error(f"Failed to update Cloudflare A record at url: {api_url}")
            return False


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        stream=sys.stdout,
    )
    log = logging.getLogger("ddns")
    load_dotenv(".env")

    cf = Cloudflare(
        api_token=str(getenv("CF_API_TOKEN")),
        zone_id=str(getenv("CF_ZONE_ID")),
        record_name=str(getenv("CF_RECORD_NAME"))
    )
    timeout = int(getenv("TIMEOUT")) if getenv("TIMEOUT") else 600
    EIP = ExternalIP()

    while True:
        wan_ip = EIP.get_wan_ip_upnp(fallback=True)
        dns_ip = cf.get_ip()

        if wan_ip != dns_ip:
            log.info(f"IP changed: {dns_ip} -> {wan_ip}, updating Cloudflare A record")
            cf.update_ip(str(wan_ip))
        Path("/tmp/ddns_healthy").touch()
        time.sleep(timeout)
