#!/usr/bin/env python3
"""GBIF occurrence search for crocodilian specimens. Usage: gbif.py "<extra params>" """
import sys, requests
extra = sys.argv[1]
url = "https://api.gbif.org/v1/occurrence/search?taxonKey=11493978&limit=300&" + extra
d = requests.get(url, timeout=60).json()
print("URL:", url, "COUNT:", d.get("count"))
for o in d.get("results", []):
    print("-", o.get("publishingCountry"), "|", o.get("institutionCode"), "|", o.get("catalogNumber"), "|", o.get("scientificName"), "|", o.get("country"), "|", o.get("locality"), "|", (o.get("occurrenceRemarks") or "")[:80], "|", o.get("preparations"), "| key", o.get("key"))
