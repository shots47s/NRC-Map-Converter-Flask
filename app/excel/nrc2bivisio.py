from __future__ import print_function
import sys
import argparse
import csv
import copy
import pyexcel as p
from collections import OrderedDict
import googlemaps
import time

nrc2bivisio_map_dict = OrderedDict([
        ('ID','Id company'),
        ('Main Site','Id Branch'),
        ('Parent','Main Site'),
        ('company.name','company.name'),
        ('Website','Website'),
        ('NAICS','Categories'),
        ('address_line_1','address_line_1'),
        ('city','city'),
        ('state','state'),
        ('Prov_Original','Provinces'),
        ('country','country'),
        ('postal_code','postal_code'),
        ('Influence','Influences'),
        ('Type','Types'),
        ('Sector','Sectors'),
        ('Enabler/Processing','Categories'),
        ('Theme','Themes'),
        ('Description','Description_EN-1'),
        ('Email','Email')
])

canonical_nrc_headers = [
    'Field',
    'Id company',
    'company.name',
    'alternative search terms ',
    'Invitation.Contact',
    'Date constitution',
    'Sales_Revenue',
    'Description_Fr',
    'Description_EN',
    'Nb employés – Admin',
    'Nb employés – Prod',
    'Nb employés – Recherche',
    'Id Branch',
    'Main Site',
    'Parent',
    'branch.name',
    'Website',
    'address_line_1',
    'city',
    'state',
    'country',
    'postal_code',
    'Telephone',
    'Description_fr',
    'Description_EN-1',
    'Email',
    'Sectors',
    'Themes',
    'Influences',
    'Provinces',
    'Types',
    'Categories',
    'NAICS2017'
    ]

def validate_headers_from_excel(excel_file):
    passing = 'PASS'
    msg = []
    missing_cols = [x for x in canonical_nrc_headers]
    added_cols = []

    try:
        excel_dict = p.get_dict(file_name=excel_file)
    except Exception as e:
        return 'ERROR',["NRC Validation Failed: File not an excel file"]

    if not len(canonical_nrc_headers) == len(excel_dict.keys()):
        passing = 'WARNING'
        msg.append("The number of columns are not the same as the standard")

    for k in excel_dict.keys():
        if k in canonical_nrc_headers:
            missing_cols.remove(k)
        else:
            added_cols.append(k)

    if len(missing_cols) != 0:
        passing = 'ERROR'
        msg.append("NRC Validation failed, there are columns" \
                   " missing in the spreadsheet: {}".format(missing_cols))
    if len(added_cols) != 0:
        passing = 'WARNING'
        msg.append("NRC Validation failed, there are columns" \
                   " added to the spreadshet: {}".format(added_cols))
    if passing:
        msg.append("NRC Validation Successful")

    return (passing, msg)

def findLocation(address, gmaps):
    geocode_results = gmaps.places('{0}'.format(address))
    print(geocode_results)
    #while len(geocode_results['results']) == 0:
    #    time.sleep(20)
    #    geocode_results = gmaps.places('{0}'.format(address))
    #    print(geocode_results)
    if len(geocode_results['results']) > 0:
        g = geocode_results['results'][0]['geometry']['location']
        return (g['lat'],g['lng'])
    else:
    #    print(g)
        return ('NA','NA')

def nrc2bivisio(excel_file,output_file,google_api_key):
    eF = p.get_dict(file_name=excel_file)

    output_rows = []

    limit = 99999
    count = 0
    for iRow in range(1,len(eF[canonical_nrc_headers[0]])):
        print(iRow)
        output_row = [None for _ in nrc2bivisio_map_dict.keys()]
        for n,m in nrc2bivisio_map_dict.items():
            output_row[list(nrc2bivisio_map_dict.keys()).index(n)]= eF[m][iRow]
        output_rows.append(output_row)
        count += 1
        if count > limit:
            break

    ### fine lat lng coordinates
    ## aggregate Address information
    count = 0
    count2 = 0
    gmaps = googlemaps.Client(key=google_api_key,queries_per_second=10,timeout=None)
    print(len(output_rows))
    for row in output_rows:

        address = "{0}, {1}, {2}, {3}".format(row[list(nrc2bivisio_map_dict.keys()).index('address_line_1')],
                                              row[list(nrc2bivisio_map_dict.keys()).index('city')],
                                              row[list(nrc2bivisio_map_dict.keys()).index('state')],
                                              row[list(nrc2bivisio_map_dict.keys()).index('postal_code')])
        print("finding {}".format(address))
        lat,lng = findLocation(address,gmaps)
        print("latlon = {0},{1}".format(lat,lng))
        row.append(lat)
        row.append(lng)
        count += 1
        time.sleep(20)
        print("Count: {} {}".format(count,count2))
        if count > 14:
            count2 += 1
            time.sleep(20)
            count = 0

    with open(output_file,"w") as f:
        csvWriter = csv.writer(f)
        headers = [x for x in nrc2bivisio_map_dict.keys()]
        headers.append('lat')
        headers.append('lng')
        csvWriter.writerow(headers)
        for oRow in output_rows:
            csvWriter.writerow(oRow)


