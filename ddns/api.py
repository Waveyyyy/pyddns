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

    def getARecord(self):
        """Get the current DNS A record

        - Checks all DNS records of a domain
        - Checks each record looking for the A record
        - Success -- returns A record as a dictionary
        - Failure -- returns None
        """
        # request all DNS records for given zoneid
        response = requests.get(self.__buildurl(
            f'zones/{self.info["zoneid"]}/dns_records/'),
            headers=self.Headers)
        # TODO: Add error handling / logging

        # create list containing the results(records) from the
        # initial response
        records = json.loads(response.text)["result"]
        for record in records:
            # check if the record is type A (only one per domain) this contains
            # the current IP cloudflare expects the domain to be at and
            # other info such as the domain name(zone name)
            if record["type"] == "A":
                return record
            else:
                # TODO: Add logging for when A record is missing
                return None

    def __getARecordIP(self):
        record = self.getARecord()
        return record["content"]

    def __getZoneName(self):
        record = self.getARecord()
        return record["name"]

    def updateip(self):
        """Update the DNS A record with the IP returned by pub.getexternip()"""
        pass

    def updateInfo(self):
        """Update the self.info dictionary

        - Updates info only when necessary
        """
        # loop over key, value pair of the self.info dictionary
        # TODO: Log when each item is updated
        for key, value in self.info.items():
            match key:
                case "new_ip":
                    extern = eip.getexternip()
                    if value != extern:
                        self.info[key] == extern
                case "old_ip":
                    recordIP = self.__getARecordIP()
                    if value != recordIP:
                        self.info[key] = recordIP
                case "domain":
                    name = self.__getZoneName()
                    if not value or (value != name):
                        self.info[key] = name


if __name__ == "__main__":
    a = Api()
    pprint(a.Headers)
    pprint(a.getARecord()["name"])
    pprint(f'Original:\n{a.info}')
    a.updateInfo()
    pprint(f'Updated:\n{a.info}')
