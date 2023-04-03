#!/usr/bin/env python3
import requests
import externip as eip
from dotenv import dotenv_values
import json
from pprint import pprint
import logging as log


class APIFailure(Exception):
    """Exception raised when an API request fails"""
    pass


class RecordMissing(Exception):
    """Exception raised when a DNS record is missing"""
    pass


class Api(object):
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
            log.debug(f'__buildurl: url = {url}')
            log.critical('__buildurl: URL failed to build - TypeError')
            log.info('__buildurl: Exiting...')
            exit(TypeError)
        else:
            log.debug(f'__buildurl: url = {url}')
            return url

    def getARecord(self):
        """Get the current DNS A record

        Check all DNS records of a domain looking for the A record

        - Success -- returns A record as a dictionary
        - Failure -- returns None
        """
        try:
            # request all DNS records for given zoneid
            response = requests.get(self.__buildurl(
                f'zones/{self.info["zoneid"]}/dns_records/'),
                headers=self.Headers)
            log.debug(f'getARecord: Headers - {self.Headers}')
            # check if the API request was successful
            if not json.loads(response.text)["success"]:
                raise APIFailure
        except APIFailure:
            log.warning('getARecord: API Request Failed')
            log.info(f'getARecord: Status Code = {response.status_code}')
            # add sleep loop here aswell
            # see final else block of function
            return APIFailure
        else:
            # create list containing the results(records) from the
            # initial response
            records = json.loads(response.text)["result"]
            for record in records:
                # check if the record is type A (one per domain) this contains
                # the current IP cloudflare expects the domain to be at and
                # other info such as the domain name(zone name)
                if record["type"] == "A":
                    log.debug(f'getARecord: {record}')
                    self.record = record
                    return record
                else:
                    log.critical('getARecord: No DNS A Record Present')
                    # add sleep loop here, possibly create a new file for sleep
                    # functionality
                    exit(RecordMissing)

    def __getARecordIP(self):
        """Retrieve the current IP used in the DNS A Record"""
        content = self.record["content"]
        log.debug(f'__getARecordIP: DNS A Record IP - {content}')
        return content

    def __getZoneName(self):
        """Retrieve the zone name from the DNS A Record"""
        name = self.record["name"]
        log.debug(f'__getZoneName: Zone(Domain) Name - {name}')
        return name

    def __getIdentifier(self):
        """Retrieve the identifier from the DNS A Record"""
        id = self.record["id"]
        log.debug(f'__getIdentifier: Zone Identifier - {id}')
        return id

    def __getProxyStatus(self):
        """Retrieve the proxy status from the DNS A Record"""
        proxied = self.record["proxied"]
        log.debug(f'__getProxyStatus: Proxied via cloudflare - {proxied}')
        return proxied

    def __getTTL(self):
        """Retrieve the TTL value from the DNS A Record"""
        ttl = self.record["ttl"]
        log.debug(f'__getTTL: TTL of DNS Record - {ttl}')
        return ttl

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
                    if not value or (value != extern):
                        log.info(f'updateInfo: Updated self.info["{key}"]')
                        self.info[key] == extern
                case "old_ip":
                    recordIP = self.__getARecordIP()
                    if value != recordIP:
                        log.info(f'updateInfo: Updated self.info["{key}"]')
                        self.info[key] = recordIP
                case "domain":
                    name = self.__getZoneName()
                    if not value or (value != name):
                        log.info(f'updateInfo: Updated self.info["{key}"]')
                        self.info[key] = name
                case "identifier":
                    id = self.__getIdentifier()
                    if not value or (value != id):
                        log.info(f'updateInfo: Updated self.info["{key}"]')
                        self.info[key] = id
                case "proxied":
                    proxy = self.__getProxyStatus()
                    if not value or (value != proxy):
                        log.info(f'updateInfo: Updated self.info["{key}"]')
                        self.info[key] = proxy
                case "ttl":
                    ttl = self.__getTTL()
                    if not value or (value != ttl):
                        log.info(f'updateInfo: Updated self.info["{key}"]')
                        self.info[key] = ttl

    def updateARecord(self):
        """Update the DNS A record with new IP address

        - Success -- return Status Code (not final behaviour)
        - Failure -- return None (not final behaviour)
        """
        # update self.info before checking if the new and old ip match
        self.updateInfo()
        if self.info["new_ip"] == self.info["old_ip"]:
            return None

        # so much needed as it seems to overwrite these values completely
        # if not sent with the update request
        body = {
            "content": self.info['new_ip'],
            "name": self.info['domain'],
            "type": "A",
            "proxied": self.info['proxied'],
            "ttl": self.info['ttl'],
        }
        try:
            log.debug(f'updateARecord: Headers {self.Headers}')
            log.debug(f'updateARecord: json body {body}')

            # update DNS A record wit new ip address
            res = requests.put(self.__buildurl(
                "/".join(['zones', self.info["zoneid"],
                          '/dns_records/', self.info["identifier"]])),
                headers=self.Headers, json=body)

            res_json = json.loads(res.text)
            if not res_json["success"]:
                raise APIFailure
        except APIFailure:
            log.warning('updateARecord: API Request Failed')
            log.info(f'updateARecord: Status Code = {res.status_code}')
            # add sleep loop here aswell
            # see final else block of function
            return APIFailure
        else:
            # return result json
            return res_json


if __name__ == "__main__":
    a = Api()
    pprint(a.Headers)
    pprint(a.updateARecord())
    pprint(a.info)
