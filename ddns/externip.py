#!/usr/bin/env python3
import miniupnpc


def getexternip():
    """Query router for external ip address"""

    # create upnp object and set discover delay
    pnp = miniupnpc.UPnP()
    pnp.discoverdelay = 200

    # discover devices, select a valid upnp igd
    pnp.discover()
    pnp.selectigd()

    # return the external ip address
    return pnp.externalipaddress()


if __name__ == "__main__":
    print('external IP: {}'.format(getexternip()))
