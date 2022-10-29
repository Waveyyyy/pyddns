#!/usr/bin/env python3
import requests
import externip as pub


def getcurrentip():
    """Get the current IP from the DNS A record"""
    pass


def updateip():
    """Update the DNS A record with the IP returned by pub.getexternip()"""
    pass


# might be an unnecessary function, evaluate usefulness
def verifyupdate(getcurrentip):
    """Verify if the DNS A record was successfully updated"""
