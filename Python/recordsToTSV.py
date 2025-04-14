#!/usr/bin/python

import requests
import json
import sys

urlBase = sys.argv[1]
urlUpgrades = urlBase + "/api/vehicle/upgraderecords" + "?vehicleId="
urlService  = urlBase + "/api/vehicle/servicerecords" + "?vehicleId="
urlRepair   = urlBase + "/api/vehicle/repairrecords"  + "?vehicleId="
urlVehicles = urlBase + "/api/vehicles"

def odometerSort(e):
    return e['odometer']

vehicles = requests.get(urlVehicles)
vehicles = json.loads(vehicles.content)
for v in vehicles:
    identifier="{}-{}-{}-{}-{}".format(v['id'], v['year'], v['make'], v['model'], v['licensePlate'])
    identifier=identifier.replace(" ", "_")
    print("Processing vehicle: {}".format(identifier))

    combined = list()

    for url in [urlUpgrades, urlService, urlRepair]:
        records = requests.get("{}{}".format(url,v['id']))
        records = json.loads(records.content)
        for r in records:
            current = dict()
            for key in ["date", "description", "notes"]:
                current[key] = r[key]

            current['odometer'] = int(r['odometer'])
            if r['cost'] != '0':
                current['cost']     = "${:.02f}".format(float(r['cost']))
            else:
                current['cost']     = ""

            if current['notes'] == None:
                current['notes'] = ""

            combined.append(current)

    # sorted_list = sorted(my_list, key=lambda x: x['age'])
    filename="{}.tsv".format(identifier)
    print("             Saved: {}".format(filename))
    with open("{}.tsv".format(identifier), "w") as f:
        f.write("Date\tOdometer\tDescription\tNotes\tCost\n")
        for r in sorted(combined, key=lambda x: x['odometer']):
            f.write('{}\t'.format(r['date']))
            f.write('"{:,}"\t'.format(r['odometer']))
            f.write('"{}"\t'.format(r['description']))
            f.write('"{}"\t'.format(r['notes']))
            f.write('{}\n'.format(r['cost']))
