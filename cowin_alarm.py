#!/usr/bin/env /usr/bin/python3

import os
import optparse as op
import requests as req
from datetime import datetime

verbose = 0
base_url = "https://cdn-api.co-vin.in/api/v2/appointment/sessions/public/"

def log_info(level, stream):
    if verbose == level:
    	print(stream)
    return

def check_pin(pin):
    ret = list()
    for i in pin:
    	try:
    	    temp = int(i.strip())
    	except:
    	    print("Error! Please provide with valid pincode, make sure all are numbers.")
    	    exit()
    	ret.append(temp)
    return ret

def check_dates(dates):
    ret = list()
    for i in dates:
    	temp = i.strip()
    	temp = temp.split('-')
    	try:
    	    dd = int(temp[0])
    	    mm = int(temp[1])
    	    yyyy = int(temp[2])
    	    datetime(yyyy, mm, dd)
    	except:
    	    print("Error! Please provide with valid date, make sure it is in dd-mm-yyyy format.")
    	    exit()
    	ret.append(str(dd)+"-"+str(mm)+"-"+str(yyyy))
    return ret

def notify():
    os.system("printf '\a'")
    return

def extract_info_calendarByPin(res):
    ret = '---------------------------------------------------------------------------------------\n'
    for i in res['centers']:
    	ret += "Center   : " + str(i['center_id']) + '\n'
    	ret += "Name     : " + str(i['name']) + '\n'
    	ret += "Address  : " + str(i['address']) + '\n'
    	ret += "State    : " + str(i['state_name']) + '\n'
    	ret += "District : " + str(i['district_name']) + '\n'
    	ret += "Block    : " + str(i['block_name']) + '\n'
    	ret += "Pincode  : " + str(i['pincode']) + '\n'
    	ret += "From Time: " + str(i['from']) + '\n'
    	ret += "To Time  : " + str(i['to']) + '\n'
    	ret += "Fee Type : " + str(i['fee_type']) + '\n'
    	try:
    	    ret += "\n> Vaccine Type\n"
    	    for j in i['vaccine_fees']:
    	    	ret += "--- Vaccine    : " + str(j['vaccine']) + '\n'
    	    	ret += "--- Cost       : " + str(j['fee']) + '\n'
    	except:
    	    print("Failed to Parse vaccine types.")
    	ret += "\n> Sessions\n"
    	for j in i['sessions']:
    	    ret += "--- Date       : " + str(j['date']) + '\n'
    	    ret += "--- Available  : " + str(j['available_capacity']) + '\n'
    	    ret += "--- Min Age    : " + str(j['min_age_limit']) + '\n'
    	    ret += "--- Vaccine    : " + str(j['vaccine']) + '\n'
    	    ret += "--- Slots      : "
    	    for k in j['slots']:
    	    	ret += k + ', '
    	    ret += '\b\b \n\n'
    	ret += '---------------------------------------------------------------------------------------\n\n'
    	log_info(3, ret)
    return ret

def get_calendarByPin(pin, date):
    fn_url = "calendarByPin?pincode=" + str(pin) + "&date=" + str(date)
    url = base_url + fn_url
    result = req.get(url)
    if result.status_code == 200:
    	result = result.json()
    	ret = extract_info_calendarByPin(result)
    	print(ret)

def cowin_alarm():
    global verbose
    switches = op.OptionParser()
    switches.add_option("-p", "--pin", dest="pin", default=-1, help="Switch to input pincode as 'a, b, c...'")
    switches.add_option("-d", "--dates", dest="dates", default=-1, help="Switch to input dates as 'dd-mm-yyyy, dd1-mm1-yyyy1,...'")
    switches.add_option("-v", "--verbose", dest="verbose", default=0, help="Switch to log info, accepted values are [1, 2, 3]")

    (options, args) = switches.parse_args()
    pin = str(options.pin)
    dates = str(options.dates)
    verbose = int(options.verbose)
    if pin == '-1' or dates == '-1':
    	print("Error! run with -h for help")
    	exit()
    pin = pin.split(',')
    dates = dates.split(',')
    pin = check_pin(pin)
    dates = check_dates(dates)
    for d in dates:
    	for p in pin:
    	    get_calendarByPin(str(p), str(d))

if __name__ == "__main__":
    cowin_alarm()
