import gzip
import os
import requests
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
from nsdotpy.session import NSSession

# Set up parameters I want everywhere
version = 0.1
keybind = 'enter'

# Should delete any existing nations.xml
if os.path.exists("nations.xml"):
    os.remove("nations.xml")

# Prompt the user for the nation and region names

nation = input("Enter the tarting nation name: ")
nation2 = nation.lower().replace(" ", "_")
password = input("Enter the nation's password: ")

# Set up our API work
headers = {
    "User-Agent": f"Tart Script/{version} (developer: https://github.com/Thorn1000 ; user:{nation};)"
}
# I got really annoyed entering my region when this works just as good
url = f"https://www.nationstates.net/cgi-bin/api.cgi?nation={nation}&q=region"

response = requests.get(url, headers=headers)
data = response.text

# Parse the XML response
soup = BeautifulSoup(data, "xml")  # Did I seriously change libraries because ET wouldnt work? Yes. Im so tired of XML

region = soup.find("REGION").text

# Print the extracted region
print("Region:", region)
region2 = region.lower().replace(" ", "_")

# makes a request to the NS API for the most recent region daily dump
# Thanks UPC for the legwork here!
print("Downloading Zip")  # Status messages baby
nations_daily_dump_url = "https://www.nationstates.net/pages/nations.xml.gz"
nations_download_request = requests.get(url=nations_daily_dump_url, headers=headers, allow_redirects=True)

# # writes that dump to an xml.gz file, will be unzipped into xml in the next step
with open("nations.xml.gz", "wb") as w:
    w.write(nations_download_request.content)

# # unzips gzip to xml
print("Unzipping file")
with gzip.open("nations.xml.gz", "rb") as r:
    with open("nations.xml", "wb") as w:
        w.write(r.read())

# Deletes the zipped file
print("Deleting zip")
os.remove("nations.xml.gz")

# Set up the xml processing
print("Processing...")
filename = "nations.xml"

nation_names = []
for event, elem in ET.iterparse(filename, events=("end",)):
    if elem.tag == "NATION":
        name_elem = elem.find("NAME")
        region_elem = elem.find("REGION")
        unstatus_elem = elem.find("UNSTATUS")
        endorsements_elem = elem.find("ENDORSEMENTS")

        endorsements = endorsements_elem.text.split(",") if endorsements_elem.text else []
        # And we thank UPC for unfucking this code too
        if region_elem.text.lower().replace(" ",
                                            "_") == region2 and unstatus_elem.text != "Non-member" and name_elem.text != nation and name_elem.text != nation2 and nation2 not in endorsements:
            nation_names.append(name_elem.text)

        elem.clear()

print("Ready!")

# Set up our NSDotPy session for HTML side
session = NSSession("Endotart script", "0.1", "Thorn1000", nation, keybind)
if session.login(nation, password):
    for names in nation_names:
        session.endorse(names)
