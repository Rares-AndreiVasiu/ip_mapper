import csv
import os
import socket
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urlparse
from pathlib import Path

import ipinfo
import matplotlib.pyplot as plt
import mpl_toolkits
from dotenv import load_dotenv
from mpl_toolkits.basemap import Basemap


def get_access_token():
    return os.getenv("access_token")


def get_urls(file):
    data = []

    with open(file) as f:
        data = f.readlines()

    return data


def get_details(ip_address):
    try:
        details = handler.getDetails(ip_address)

        return details.all
    except:
        return


def get_hostname(domain_names):
    ip_set = set()

    for domain in domain_names:
        try:
            ip_addr = socket.gethostbyname(domain)

            ip_set.add(ip_addr)
        except:
            print(domain)

    return ip_set


def get_domain_names(data):
    domain_names = set()

    for url in data:
        final_url = urlparse(url).netloc

        final_url = final_url.split(":")[0]

        domain_names.add(final_url)

    return domain_names


def plot_map(lon, lat):
        
    plt.figure(figsize=(12, 8))

    m = Basemap(
            projection='merc',
            llcrnrlat=-60,
            urcrnrlat=80,
            llcrnrlon=-180,
            urcrnrlon=180,
            resolution='l'
            )

    m.drawcoastlines()

    m.drawcountries()

    m.fillcontinents(color='#2d2d2d', lake_color='#000000')

    m.drawmapboundary(fill_color='#000000')

    x, y = m(lon, lat)

    m.scatter(x, y, marker='o', s=20, color='blue')

    plt.title("IP Geolocation Map")
    
    plt.show()


def check_handler_details(handler, ip_addr):
    print(handler.getDetails(ip_addr).city)


def get_ip_set(file_name):
    history_file = data_dir / file_name

    return  get_hostname(get_domain_names(get_urls(history_file)))



def get_latitude_longitude(ip_set):
    complete_details = []

    with ThreadPoolExecutor(max_workers=10) as e:
        for ip_address in list(ip_set):
            complete_details.append(e.submit(get_details, ip_address))

    for loc in as_completed(complete_details):
        result = loc.result()

        if not result:
            continue
        
        la = result.get("latitude")

        lo = result.get("longitude")

        if la is None or lo is None:
            continue
    
        try:
            lat.append(float(la))
            lon.append(float(lo))
        except:
            continue

    return [lat, lon]



if __name__ == "__main__":
    load_dotenv()

    handler = ipinfo.getHandler(get_access_token())

    # check_handler_details(handler,"216.239.36.21")

    project_root = Path(__file__).parent.parent.parent

    data_dir = project_root / "data"

    lat = []
    lon = []
    
    #ip_set = get_ip_set("history.txt")
    #
    #lat, lon = get_latitude_longitude(ip_set)
    
    ip_file = data_dir / "ip.csv"

    with open(ip_file, "r", newline="") as csvfile:
        reader = csv.DictReader(csvfile)

        for row in reader:
            lat.append(float(row["latitude"]))
            lon.append(float(row["longitude"]))  

    plot_map(lon, lat)

    

