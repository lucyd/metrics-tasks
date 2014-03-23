#!/usr/bin/python

import urllib, urllib2
import json
import threading
import _strptime
from datetime import timedelta, datetime

TWO_MONTHS = 2 * 30 * 86400


def print_debug_info(fingerprint, exit_port_check, uptime_percent, avg_bandwidth):
  """ Provides debugging information about relay operator's eligibility 
      for acquiring a t-shirt """

  print("=================================================================")
  print("\nRelay details")
  print("-------------")
  print("Fingerprint : " + fingerprint)
  print("Exit to port 80 allowed : " + str(exit_port_check))
  if uptime_percent == -1:
    print("Uptime percentage in past 2 months : Insufficient data")
  else:
    print("Uptime percentage in past 2 months : " + str(uptime_percent))
  if avg_bandwidth == -1:
    print("Average bandwidth in past 2 months : Insufficient data")
  else:
    print("Average bandwidth in past 2 months : " + str(avg_bandwidth) + "KBytes/s")

  print("\nElligibility")
  print("------------")

  if uptime_percent < 95:
    print("Not elligible for T-shirt")
    print("Reason : Insufficient relay up time")
  else:
    if exit_port_check is False:
      if avg_bandwidth >= 500:
        print("Elligible for T-shirt")
        print("Reason : Average bandwidth greater than 500KBytes/s and "
	      "relay uptime greater than 95%")
      else:
        print("Not elligible for T-shirt")
        print("Reason : Average bandwidth less than 500KBytes/s and port 80 blocked")
    else:
      if avg_bandwidth < 100:
        print("Not elligible for T-shirt")
        print("Reason : Average bandwidth less than 100KBytes/s")
      else:
          print("Elligible for T-shirt")
	  print("Reason : Average bandwidth greater than 100KBytes/s,"
	        "relay uptime greater than 95% and port 80 unblocked")
  print("")


def fetch_data(doc_type, params):
  """ Fetches onionoo data and returns response formatted as a dictionary """

  # Build the request
  base_URL = 'https://onionoo.torproject.org/' + doc_type
  request_URL = base_URL + '?' + urllib.urlencode(params)
  request = urllib2.Request(url=request_URL)
  # Send request to Onionoo
  try:
    response = urllib2.urlopen(request)
  except urllib2.HTTPError, error:
    print("Error " + str(error.code) + ": " + error.reason)
    exit()
  # Exit if no relay object in response  
  response_dict = json.loads(response.read())
  if response_dict['relays'] == []:
    print("Error: No such relay")
    exit()
  return response_dict


def calculate_2mo_avg(response, response_type):
  """ Calculates the average of values in 2-month time frame """

  # Check if required data is present in the response
  if response_type == 'uptime':
    if '3_months' not in response['uptime'].keys():
      return -1
    data = response['uptime']['3_months']
  elif response_type == 'bandwidth':
    if '3_months' not in response['write_history'].keys():
      return -1
    data = response['write_history']['3_months']
  # Sum up all values within past 2 months
  _sum = 0
  count = 0
  today = datetime.now()
  first = datetime.strptime(data['first'], "%Y-%m-%d %H:%M:%S")
  last = datetime.strptime(data['last'], "%Y-%m-%d %H:%M:%S")
  for i in range(data['count']):
    value_date = first + timedelta(seconds=(i * float(data['interval'])))
    if (today - value_date).total_seconds() <= TWO_MONTHS:
      if data['values'][i] not in [None, 'null']:
        _sum += (data['values'][i])
        count += 1
  # Find number of values between last and today
  time_interval = int((today - last).total_seconds())
  last_today_values = time_interval/data['interval']
  # Calculate the result
  if response_type == 'uptime':
    total_up_time = _sum * data['factor'] * data['interval']
    uptime_percent = round(total_up_time * 100 / TWO_MONTHS, 2)
    return uptime_percent
  elif response_type == 'bandwidth':
    total_values = count + last_today_values
    result = (_sum * data['factor'])/total_values
    return round(result/1000.0, 2)


def check_in_ports(ports):
  """ Checks if port 80 is present in the ports list """

  for entry in ports:
    if entry == '80':
      return True
    if '-' in entry:
      [x,y] = entry.split('-')
      if 80 in range(int(x),int(y)):
        return True
  return False


def check_exit_port(response):
  """ Checks if relay allows network traffic to exit through port 80 """

  exit_policy = response['exit_policy_summary']
  if 'accept' in exit_policy:
    return check_in_ports(exit_policy['accept'])
  elif 'reject' in exit_policy:
    return not check_in_ports(exit_policy['reject'])
  return False


def get_uptime_percent(response):
  """ Calculates the relay's uptime from onionoo's uptime document """

  return calculate_2mo_avg(response, 'uptime')


def get_avg_bandwidth(response):
  """ Calculates average bandwidth of traffic through the relay """

  return calculate_2mo_avg(response, 'bandwidth')
  

def check_tshirt(search_query):
  """ Fetches required onionoo documents and evaluates the 
      t-shirt qualification criteria for each of the relays """

  # Fetch the required documents from onionoo
  params = {
     'type' : 'relay',
     'search' : search_query
  }
  bandwidth_data = fetch_data('bandwidth', params)['relays']
  print "Fetched bandwidth document"
  uptime_data = fetch_data('uptime', params)['relays']
  print "Fetched uptime document"
  params['fields'] = 'exit_policy_summary,fingerprint'
  exit_policies = fetch_data('details', params)['relays']
  print "Fetched details document"

  for i in range(len(exit_policies)):
    fingerprint = exit_policies[i]['fingerprint']
    exit_port_check = check_exit_port(exit_policies[i])
    uptime_percent = get_uptime_percent(uptime_data[i])
    avg_bandwidth = get_avg_bandwidth(bandwidth_data[i])
    print_debug_info(fingerprint, exit_port_check, uptime_percent, avg_bandwidth)


if __name__ == "__main__":
  search_query = raw_input('Enter relay search-query : ')
  check_tshirt(search_query)

