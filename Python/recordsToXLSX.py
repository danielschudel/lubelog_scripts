#!/usr/bin/python

import requests
import json
import sys
import xlsxwriter
import datetime
from datetime import datetime


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
            current['cost']     = float(r['cost'])

            if current['notes'] == None:
                current['notes'] = ""

            combined.append(current)

    # sorted_list = sorted(my_list, key=lambda x: x['age'])
    filename="{}.xlsx".format(identifier)

    # Create a workbook and add a worksheet.
    workbook = xlsxwriter.Workbook(filename)
    formatCost     = workbook.add_format({'num_format': '$#,##0', 'align': 'right'})
    formatOdometer = workbook.add_format({'num_format':  '#,##0', 'align': 'right'})
    formatDate     = workbook.add_format({'num_format': 'mm-dd-yyyy', 'align': 'right'})
    formatBold     = workbook.add_format({'bold': True})
    formatWrap     = workbook.add_format({'text_wrap': True})
    formatTop      = workbook.add_format({'valign': 'top'})


    worksheet = workbook.add_worksheet()

    row=0
    col=0
    for key in [ "Date", "Odometer", "Description", "Notes", "Cost" ]:
        worksheet.write(row, col, key, formatBold)
        col+=1

    for r in sorted(combined, key=lambda x: x['odometer']):
        row+=1
        worksheet.write_datetime(row, 0, datetime.strptime(r['date'], "%m/%d/%Y"))
        worksheet.write_number(row, 1, r["odometer"])
        worksheet.write_string(row, 2, r["description"])
        worksheet.write_string(row, 3, r["notes"])
        if r['cost'] == 0:
            worksheet.write_blank(row, 4, None)
        else:
            worksheet.write_number(row, 4, r["cost"])

    worksheet.set_column('A:A', 12, formatDate)
    worksheet.set_column('B:B', 10, formatOdometer)
    worksheet.set_column('C:C', 25)
    worksheet.set_column('D:D', 35, formatWrap)
    worksheet.set_column('E:E', 10, formatCost)
    workbook.close()
    print("             Saved: {}".format(filename))
