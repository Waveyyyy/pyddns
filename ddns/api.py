#!/usr/bin/env python3
import requests
import externip as pub
from dotenv import dotenv_values


class Api:
    def __init__(self):
        self.info = {
            'zoneid': dotenv_values(".env")["ZONEID"],
            'userid': dotenv_values(".env")["USERID"],
            'old_ip': None,
            'new_ip': pub.getexternip(),
            'domain': None,
            # 'last_updated': update_time,
        }
        # headers used for api requests
        self.Headers = {
            'X-Auth-Email': dotenv_values(".env")["AUTH_EMAIL"],
            'Authorization': f'Bearer {dotenv_values(".env")["AUTHORIZATION"]}',
            'Content-Type': 'application/json',
        }

    def __buildurl(self, endpoint):
        """Creates the url from the base and the desired endpoint"""
        url_base = 'https://api.cloudflare.com/client/v4/'
        url = '/'.join([url_base, endpoint])
        return url

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
    print(a.info)
