#!/usr/bin/env python3
import requests
import externip as pub
from dotenv import dotenv_values


class Api:
    def __init__(self):
        self.info = {
            'zoneid': None,
            'userid': None,
            'old_ip': None,
            'new_ip': pub.getexternip(),
            'domain': None,
            # 'last_updated': update_time,

        }
        # headers used for api requests
        self.Headers = {
            'X-Auth-Email': dotenv_values(".env")["AUTH_EMAIL"],
            'X-Auth-Key': dotenv_values(".env")["API_TOKEN"],
            'Authorization': f'Bearer {dotenv_values(".env")["AUTHORIZATION"]}',
            'Content-Type': 'application/json',
        }

    def __buildurl(self, endpoint):
        """Creates the url from the base and the desired endpoint"""
        url_base = 'https://api.cloudflare.com/client/v4/'
        url = '/'.join([url_base, endpoint])
        return url

    def getzoneid(self):
        """Get the zone identifier, needed to make most requests"""
        # curl -X GET "https://api.cloudflare.com/client/v4/zones" \
        # -H "X-Auth-Email: user@example.com" \
        # -H "X-Auth-Key: c2547eb745079dac9320b638f5e225cf483cc5cfdda41" \
        # -H "Content-Type: application/json"
        with requests.Session() as session:
            pass
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

if __name__ == "__main__":
    a = Api()
    print(a.Headers)
