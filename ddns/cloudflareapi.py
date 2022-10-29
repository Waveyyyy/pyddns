#!/usr/bin/env python3
import requests
import externip as pub


class Api:
    def __init__(self):
        self.info = {
            'zoneid': self.getzoneid(),
            'userid': self.getuserid(),
            'old_ip': self.getcurrentip(),
            'new_ip': pub.externip(),
            # 'last_updated': update_time,

        }

    def __buildrequest(self):
        """Builds the request with all of the required info"""
        pass

    def getzoneid(self):
        """Get the zone identifier, needed to make most requests"""
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
