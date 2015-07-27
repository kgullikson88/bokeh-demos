import random
import requests
from requests.exceptions import ConnectionError

import pandas as pd
import utils
import ui


airports = utils.airports.copy()
airport = utils.get_airport_data('3682', airports)


def do_update(newid):
    url = "http://127.0.0.1:5050/data/update/%s" % newid
    try:
        res = requests.get(url, timeout=2)

    except ConnectionError:
        print ("CONNECTION ERROR!", url)

def select_new():
    if len(airport['connections'].dest_ap_id):
        ind = random.randrange(0, len(airport['connections'].dest_ap_id)-1)
        newid = airport['connections'].dest_ap_id.values[ind]
    else:
        newid = 3682

    do_update(newid)
    return newid


import time
if __name__ == "__main__":
    while True:
        new_id = select_new(airport)

        try:
            airport = utils.get_airport_data(str(new_id), airports)
        except ValueError:
            print("ERROR?", new_id)

        time.sleep(2)


