#!/usr/bin/env python3
import requests
import externip as pub


class Api:
    def __init__(self):
        self.info = {
            'zoneid': None,
            'userid': None,
            'old_ip': None,
            'new_ip': pub.externip(),
            # 'last_updated': update_time,

        }

    def __buildrequest(self):
        """Builds the request with all of the required info"""
        pass

    def getzoneid(self):
        """Get the zone identifier, needed to make most requests"""
        # curl -X GET "https://api.cloudflare.com/client/v4/zones" \
        # -H "X-Auth-Email: user@example.com" \
        # -H "X-Auth-Key: c2547eb745079dac9320b638f5e225cf483cc5cfdda41" \
        # -H "Content-Type: application/json"
        pass

    def getuserid(self):
        """Get the user identifier, also needed to make most requests"""
        pass

    def getcurrentip(self):
        """Get the current IP from the DNS A record"""
        pass

    def updateip(self):
        """Update the DNS A record with the IP returned by pub.getexternip()"""
        pass

    def __verifyupdate(self):
        """Verify if the DNS A record was successfully updated"""
        pass
