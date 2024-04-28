"""
Title: Amsterdam Meetbouten Scraper
Author: Valentijn Hoogeboom

Description:
This script creates a spreadsheet containing all data of all meetbouten in a street.

Dependencies:
Pandas
Numpy
Requests

"""
import os
import time
import numpy as np
import pandas as pd
import requests


def calculateSpeedDiff(frame):
    """
    Returns a newly calculated speed difference in comparison to the year before.
    :param frame: data frame to transform
    :return: the new column meant for "zakking"
    """
    speed_values = []

    frame['date'] = pd.to_datetime(frame['datum'])
    frame.sort_values(by=['adres', 'date'], inplace=True)

    for _, group in frame.groupby('adres'):
        group['prev_date'] = group['date'].shift(1)

        # Converts date difference to years
        group['date_diff'] = (group['date'] - group['prev_date']).dt.total_seconds() / (365.25 * 24 * 3600)

        for index, row in group.iterrows():
            if row["zakking"] == float('Inf'):
                continue
            date_diff = (row['date_diff']) if not np.isnan(row['date_diff']) else 0

            if date_diff > 0:
                speed = row['zakking'] / date_diff
            else:
                speed = None  # Avoid division by zero, set speed to None
            if speed is not None:
                speed_values.append(round(speed, 1))
            else:
                speed_values.append(0)

    return speed_values


def insertBlankRows(arr):
    """
    Inserts blank rows after each address.
    :param arr: the data frame    :return:  with blank rows
    """

    newArray = arr.copy()
    c = 0
    last_addr = ""

    for a, t in enumerate(arr):
        if last_addr == "":
            last_addr = t[2]
        if last_addr != t[2]:
            insert_index = a + c
            newArray = np.insert(newArray, insert_index, ["", "", "", "", "", "", "", "", "", ""], axis=0)
            last_addr = t[2]
            c += 1
    return newArray


def getAddresses(rows):
    """
    Returns all addresses from the data frame.
    :param rows: the data frame
    :return: the addresses in the data frame.
    """

    addresses = []
    for i in rows:
        if not i[0] in addresses:
            addresses.append(i[0])
    return addresses


def main():
    """
    Main function of this script. Handles input of the street, then transforms it to a dataframe.
    and saves it as output.csv. It uses the Amsterdam Data API to fetch 'meetbouten'. These are measurement
    devices that return the current NAP of a certain address.
    """
    straat = input("Voer straat naam in: ")
    straat = " ".join(
        map(lambda x: x[0].upper() + x[1:], straat.split(" ")))  # Makes every letter after a space uppercase.

    try:
        # Makes a request the Amsterdam Data API to fetch all meetbouten in the street.
        # Specifies page size in order to make sure all meetbouten are returned.

        data = requests.get(
            f'https://api.data.amsterdam.nl/v1/meetbouten/meetbouten/'
            f'?_pageSize=100&nabijNummeraanduiding[like]={straat}+*').json()
    except Exception as e:
        print(e)
        time.sleep(3)  # Makes sure the app doesn't immediately close upon erroring.
        return

    # Checks whether the API has returned any meetbouten.
    if not data or len(data["_embedded"]['meetbouten']) == 0:
        print("Straat niet gevonden (Controleer spaties)")
        time.sleep(3)  # Makes sure the app doesn't immediately close upon erroring.
        return

    rows = []

    for i in (data["_embedded"]['meetbouten']):
        print(i["nabijNummeraanduiding"])
        meetboutStatus = i["statusOmschrijving"]

        # Fetches all measurements for the given meetbout.
        d = requests.get(
            f"https://api.data.amsterdam.nl/v1/meetbouten/metingen/"
            f"?hoortBijMeetbout.identificatie={i["_links"]["self"]["title"]}", ).json()

        # Formats data for output dataframe.
        for r in d["_embedded"]["metingen"]:
            adres = i["nabijNummeraanduiding"]
            hoogteTovnap = round(r["hoogteTovNap"], 3)
            meetbout = i["_links"]["self"]["title"]
            zakking = round(r["zakking"], 2)
            zakkingSnelheid = round(r["zakkingssnelheid"], 1) if r["zakkingssnelheid"] else r["zakkingssnelheid"]
            zakkingCumulatief = round(r["zakkingCumulatief"], 1)

            datum = r["datum"]
            hoeveelsteMeting = r["hoeveelsteMeting"]

            rows.append(
                [adres, hoogteTovnap, meetbout, meetboutStatus, zakking, zakkingSnelheid, zakkingCumulatief, datum,
                 hoeveelsteMeting])

    arr = np.array(rows)
    frame = pd.DataFrame(arr,
                         columns=["adres", "hoogteTovNap", "meetbout", "meetboutStatus", "zakking", "zakkingssnelheid",
                                  "zakkingCumulatief", "datum",
                                  "hoeveelsteMeting"])

    # Adds additional relations based on other columns.
    frame["zakkingLaatstePeriode"] = calculateSpeedDiff(frame)

    frame = frame[
        ["meetbout", "meetboutStatus", "adres", "datum", "hoeveelsteMeting", "hoogteTovNap", "zakkingCumulatief",
         "zakking",
         "zakkingssnelheid", "zakkingLaatstePeriode"]]
    arr = frame.to_numpy()

    # Inserts blank rows after each address.
    arr2 = insertBlankRows(arr)

    frame = pd.DataFrame(arr2,
                         columns=["meetbout", "status", "adres", "datum", "hoeveelsteMeting", "hoogteTovNap",
                                  "zakkingCumulatief",
                                  "zakking", "zakkingssnelheid", "zakkingLaatstePeriode"])
    # The ';' seperator is used on order to support Excel formatting.
    dir_path = os.path.dirname(os.path.realpath(__file__))
    frame.to_csv(f"{dir_path}/output.csv", index=False, sep=';')


if __name__ == '__main__':
    main()
