import miniupnpc

def get_wan_ip() -> str:
    """
    Get WAN ip adress from router using uPnP
    """
    upnp = miniupnpc.UPnP()
    upnp.discoverdelay = 200
    upnp.discover()
    upnp.selectigd()
    return upnp.externalipaddress()

if __name__ == "__main__":
    print(get_wan_ip())

