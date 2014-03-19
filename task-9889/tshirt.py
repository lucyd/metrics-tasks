#!/usr/bin/python

import urllib, urllib2
import json
from datetime import datetime

def print_debug_info(exit_port_check, uptime_percent, avg_bandwidth):
  """ Provides debugging information about relay operator's eligibility 
      for acquiring a t-shirt """

  print("\nRelay details")
  print("=============")
  print("Exit to port 80 allowed : " + str(exit_port_check))
  print("Uptime percentage in past 2 months : " + str(uptime_percent))
  print("Average bandwidth in past 2 months : " + str(avg_bandwidth) + "KBytes/s")

  print("\nElligibility")
  print("============")
  if avg_bandwidth >= 500:
    print("Elligible for T-shirt")
    print("Reason : Average bandwidth greater than 500KBytes/s")
  else:
    if exit_port_check is False:
      print("Not elligible for T-shirt")
      print("Reason : Average bandwidth less than 500KBytes/s and port 80 blocked")
    else:
      if uptime_percent < 95:
        print("Not elligible for T-shirt")
        print("Reason : Insufficient relay up time")
      else:
        if avg_bandwidth < 100:
          print("Not elligible for T-shirt")
          print("Reason : Average bandwidth less than 100KBytes/s")
        else:
          print("Elligible for T-shirt")
	  print("Reason : Average bandwidth greater than 100KBytes/s, relay uptime greater than 95% and port 80 unblocked")
  print("")


def calculate_sum(relay_history):
  """ Calculates the sum of values in 2-month time frame """

  two_months = 2 * 30 * 86400
  two_months_values = two_months / relay_history['interval']
  _sum = 0
  for i in relay_history['values'][-two_months_values:]:
    if i is not 'null' and i is not None:
      _sum += (i/1000.0)
  return _sum * relay_history['interval']


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


def check_exit_port(fingerprint):
  """ Checks if relay allows network traffic to exit through port 80 """

  params = {
      'lookup' : fingerprint,
      'fields' : 'exit_policy_summary'
  }
  response = fetch_data('details', params)
  exit_policy = response['relays'][0]['exit_policy_summary']
  if 'accept' in exit_policy:
    return '80' in exit_policy['accept']
  elif 'reject' in exit_policy:
    return '80' not in exit_policy['reject']
  else:
    return False


def get_uptime_percent(fingerprint):
  """ Calculates the relay's uptime from onionoo's uptime documents """

  params = {
      'lookup' : fingerprint
  }
  response = fetch_data('uptime', params)
  uptime = calculate_sum(response['relays'][0]['uptime']['3_months'])
  uptime_percent = round(uptime/(2*30*864), 2)
  return uptime_percent


def get_avg_bandwidth(fingerprint):
  """ Calculates average bandwidth of traffic through the relay """

  params = {
      'lookup' : fingerprint
  }
  response = fetch_data('bandwidth', params)
  
  # Calculate the sum of values in response
  bandwidth_data = response['relays'][0]['write_history']['3_months']
  traffic_sum = calculate_sum(bandwidth_data)
  
  # Find number of values between last and today
  last_date = datetime.strptime(bandwidth_data['last'], "%Y-%m-%d %H:%M:%S")
  today_date = datetime.now()
  time_interval = int((today_date - last_date).total_seconds())
  last_today_values = time_interval/bandwidth_data['interval']
  
  # Calculate the result
  two_months = 2 * 30 * 86400
  two_months_values = two_months/bandwidth_data['interval']
  total_values = two_months_values + last_today_values
  result = (traffic_sum * bandwidth_data['factor'])/total_values

  return round(result/1000.0,2)


def check_tshirt(fingerprint):
  """ Checks if the relay satisfies qualification criteria for a t-shirt """

  exit_port_check = check_exit_port(fingerprint)
  uptime_percent = get_uptime_percent(fingerprint)
  avg_bandwidth = get_avg_bandwidth(fingerprint)
  print_debug_info(exit_port_check, uptime_percent, avg_bandwidth)


if __name__ == "__main__":
  fingerprint = raw_input('Enter relay fingerprint: ')
  check_tshirt(fingerprint)

