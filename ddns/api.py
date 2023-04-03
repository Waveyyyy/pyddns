#!/usr/bin/env python3
import requests
import externip as eip
from dotenv import dotenv_values
import json
from pprint import pprint
import logging as log


class Api:
    def __init__(self):
        self.info = {
            'zoneid': dotenv_values(".env")["ZONEID"],
            'userid': dotenv_values(".env")["USERID"],
            'old_ip': None,
            'new_ip': eip.getexternip(),
            'domain': None,
            'identifier': None,
            'proxied': None,
            'ttl': None
            # 'last_updated': update_time,
        }
        # headers used for api requests
        self.Headers = {
            'X-Auth-Email': dotenv_values(".env")["AUTH_EMAIL"],
            'Authorization': f'Bearer {dotenv_values(".env")["AUTHORIZATION"]}',
            'Content-Type': 'application/json',
        }

        # initialise logging options
        log.basicConfig(filename='ddns.log', filemode='w',
                        format='%(name)s - [%(levelname)s] %(message)s',
                        level=log.DEBUG)

    def __buildurl(self, endpoint):
        """Create the url from the base and the desired endpoint

        Parameters:
        - endpoint -- endpoint separated by forward slashes

        - Success -- return url
        - Failure -- exit with TypeError
        """
        url_base = 'https://api.cloudflare.com/client/v4/'
        try:
            log.debug(f'__buildurl: endpoint = {endpoint}')
            url = '/'.join([url_base, endpoint])
        except TypeError:
            log.critical('__buildurl: URL failed to build - TypeError')
            log.info('Exiting...')
            exit(TypeError)
        else:
            return url

    def getARecord(self):
        """Get the current DNS A record

        Check all DNS records of a domain looking for the A record

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
                self.record = record
                return record
            else:
                # TODO: Add logging for when A record is missing
                return None

    def __getARecordIP(self):
        """Retrieve the current IP used in the DNS A Record"""
        return self.record["content"]

    def __getZoneName(self):
        """Retrieve the zone name from the DNS A Record"""
        return self.record["name"]

    def __getIdentifier(self):
        """Retrieve the identifier from the DNS A Record"""
        return self.record["id"]

    def __getProxyStatus(self):
        """Retrieve the proxy status from the DNS A Record"""
        return self.record["proxied"]

    def __getTTL(self):
        """Retrieve the TTL value from the DNS A Record"""
        return self.record["ttl"]

    def updateInfo(self):
        """Update the self.info dictionary

        - Will only update info when required
        """
        # instead of making an API request for each case,
        # make a single API request at the start
        self.getARecord()
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
                case "identifier":
                    id = self.__getIdentifier()
                    if not id or (value != id):
                        self.info[key] = id
                case "proxied":
                    proxy = self.__getProxyStatus()
                    if not value or (value != proxy):
                        self.info[key] = proxy
                case "ttl":
                    ttl = self.__getTTL()
                    if not value or (value != ttl):
                        self.info[key] = ttl

    def updateARecord(self):
        """Update the DNS A record with new IP address

        - Success -- return Status Code (not final behaviour)
        - Failure -- return None (not final behaviour)
        """
        self.updateInfo()
        if self.info["new_ip"] == self.info["old_ip"]:
            return None
        body = {
            "content": self.info['new_ip'],
            "name": self.info['domain'],
            "type": "A",
            "proxied": self.info['proxied'],
            "ttl": self.info['ttl'],
        }
        res = json.loads(requests.put(self.__buildurl(
            f'zones/{self.info["zoneid"]}/dns_records/{self.info["identifier"]}'),
            headers=self.Headers, json=body).text)
        pprint(res)
        if res["success"]:
            return res
        else:
            return res


if __name__ == "__main__":
    a = Api()
    pprint(a.Headers)
    pprint(a.getARecord())
    pprint(a.info)
