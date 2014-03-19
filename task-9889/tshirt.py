#!/usr/bin/python

import urllib, urllib2
import json
import threading
import _strptime
from datetime import datetime

TWO_MONTHS = 2 * 30 * 86400

# Global variables
bandwidth_data = []
uptime_data = []
exit_policies = []
thread_lock = threading.Lock()


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


def calculate_sum(relay_history):
  """ Calculates the sum of values in 2-month time frame """

  two_months_values = TWO_MONTHS / relay_history['interval']
  _sum = 0
  for i in relay_history['values'][-two_months_values:]:
    if i is not 'null' and i is not None:
      _sum += (i/1000.0)
  return _sum * relay_history['interval']


def check_in_ports(ports):
  """ Checks for port 80 is present in the ports list """

  for entry in ports:
    if entry == '80':
      return True
    if '-' in entry:
      [x,y] = entry.split('-')
      if 80 in range(int(x),int(y)):
        return True
  return False

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


def check_exit_port(response):
  """ Checks if relay allows network traffic to exit through port 80 """

  exit_policy = response['exit_policy_summary']
  if 'accept' in exit_policy:
    return check_in_ports(exit_policy['accept'])
  elif 'reject' in exit_policy:
    return check_in_ports(exit_policy['reject'])
  return False


def get_uptime_percent(response):
  """ Calculates the relay's uptime from onionoo's uptime document """

  if '3_months' not in response['uptime'].keys():
    return -1
  uptime = calculate_sum(response['uptime']['3_months'])
  uptime_percent = round(uptime/(2*30*864), 2)
  return uptime_percent


def get_avg_bandwidth(response):
  """ Calculates average bandwidth of traffic through the relay """

  if '3_months' not in response['write_history'].keys():
    return -1

  # Calculate the sum of values in response
  bandwidth_data = response['write_history']['3_months']
  traffic_sum = calculate_sum(bandwidth_data)
  
  # Find number of values between last and today
  last_date = datetime.strptime(bandwidth_data['last'], "%Y-%m-%d %H:%M:%S")
  today_date = datetime.now()
  time_interval = int((today_date - last_date).total_seconds())
  last_today_values = time_interval/bandwidth_data['interval']
  
  # Calculate the result
  two_months_values = TWO_MONTHS/bandwidth_data['interval']
  total_values = two_months_values + last_today_values
  result = (traffic_sum * bandwidth_data['factor'])/total_values

  return round(result/1000.0,2)


def check_tshirt(search_query):
  """ Fetches required onionoo documents and invokes threads """

  global exit_policies
  global uptime_data
  global bandwidth_data
  global thread_lock

  # Fetch the required documents from onionoo
  params = {
     'search' : search_query
  }
  bandwidth_data = fetch_data('bandwidth', params)['relays']
  print "Fetched bandwidth document"
  uptime_data = fetch_data('uptime', params)['relays']
  print "Fetched uptime document"
  params['fields'] = 'exit_policy_summary,fingerprint'
  exit_policies = fetch_data('details', params)['relays']
  print "Fetched details document"

  # Create and start the threads
  threads = []
  for i in range(len(exit_policies)):
    threads.append(relay_thread(i))
    threads[-1].start()
  # Wait for the threads to finish
  for thread in threads:
    thread.join()


class relay_thread(threading.Thread):
  """ A subclass of the Thread class that handles relay-specific data"""
  def __init__(self, thread_id):
    threading.Thread.__init__(self)
    self.thread_id = thread_id
  def run(self):
    global exit_polices
    global uptime_data
    global bandwidth_data
    fingerprint = exit_policies[self.thread_id]['fingerprint']
    exit_port_check = check_exit_port(exit_policies[self.thread_id])
    uptime_percent = get_uptime_percent(uptime_data[self.thread_id])
    avg_bandwidth = get_avg_bandwidth(bandwidth_data[self.thread_id])
    thread_lock.acquire()
    print_debug_info(fingerprint, exit_port_check, uptime_percent, avg_bandwidth)
    thread_lock.release()
    

if __name__ == "__main__":
  search_query = raw_input('Enter relay search-query : ')
  check_tshirt(search_query)

