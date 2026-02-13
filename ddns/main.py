import miniupnpc
from typing import Optional

def get_wan_ip() -> Optional[str]:
    """
    Get WAN ip adress from router using uPnP
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

