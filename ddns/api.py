#!/usr/bin/env python3
import requests
import externip as eip
from dotenv import dotenv_values
import json
from pprint import pprint


class Api:
    def __init__(self):
        self.info = {
            'zoneid': dotenv_values(".env")["ZONEID"],
            'userid': dotenv_values(".env")["USERID"],
            'old_ip': None,
            'new_ip': eip.getexternip(),
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

    def getARecordIP(self):
        """Get the current IP from the DNS A record

        - Checks all DNS records of a domain
        - Checks each record looking for the A record
        - Success -- returns IP address as a string
        - Failure -- returns None
        """
        # query for all DNS records for a domain
        response = requests.get(self.__buildurl(
            f'zones/{self.info["zoneid"]}/dns_records/'),
            headers=self.Headers)
        # TODO: Add error handling / logging

        # create list containing the results(records) from the
        # initial response
        records = json.loads(response.text)["result"]
        for record in records:
            # check if the record is type A (only one per domain) this contains
            # the current IP cloudflare expects the domain to be at
            if record["type"] == "A":
                return record["content"]
            else:
                # TODO: Add logging for when A record is missing
                return None

    def updateip(self):
        """Update the DNS A record with the IP returned by pub.getexternip()"""
        pass

    def __updateInfo(self):
        """Update the self.info dictionary with new information"""
        pass


if __name__ == "__main__":
    a = Api()
    pprint(a.Headers)
    a.getARecordIP()
    pprint(a.info)
