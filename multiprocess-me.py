#!/usr/bin/env python
import requests
import re
from urllib.parse import urlparse
from bs4 import BeautifulSoup
import sys
import time
from multiprocessing import Process, Queue, current_process

NUM_WORKERS = 4

process_queue = Queue() # This is the hyperlinks to scrape
link_queue = Queue() # This is the queue to put new links on
message_queue = Queue() # Process to read from the done queue w/o blocking main event loop

domain_list = []

def link_monitor(link_queue, process_queue):
  all_domains = list()
  all_links = list()

  for link in iter(link_queue.get, 'STOP'):

    if link.startswith('DUMP'):
      for link in all_links:
        print(link)
      continue

    # Control message for adding new domain
    if link.startswith('DOMAIN::'):
      _, domain = link.split('::')

      if domain not in all_domains:
        all_domains.append(domain)
        all_links.append(domain.strip())
        process_queue.put(domain)

    else:
      parsed_url = urlparse(link)

      # Ensure link is in current domain scope
      domain = '{}://{}'.format(parsed_url.scheme, parsed_url.netloc)
      if domain not in all_domains:
        print('Dropping link: {}'.format(link))
        continue

      if not link in all_links:
        all_links.append(link)
        process_queue.put(link)

def parselinks(doc):
  bs = BeautifulSoup(doc, 'html.parser')
  links = bs.find_all('a')
  return links

def formaturl(domain, uri, scheme):
  if not uri:
    return None

  if uri.startswith('http'):
    return uri

  if uri.startswith('//'):
    return "{}:{}".format(scheme, uri)

  if uri.startswith('/'):
    return "{}://{}{}".format(scheme, domain, uri)

  return None

def scraper(process_queue, link_queue, message_queue):
  for url in iter(process_queue.get, 'STOP'):
    parsed_url = urlparse(url) 
    if not parsed_url.netloc:
      print('Malformed URL: {}'.format(url))
      message_queue('Malformed URL processed: {}'.format(url))

    else:
      print('Scraping {}'.format(url))
      message_queue.put("{} starting to process {}".format(current_process().name, url))
      result = requests.get(url)
      links = parselinks(result.text)

      for link in links:
        formatted_link = formaturl(parsed_url.netloc, link.get('href'), parsed_url.scheme)
        if formatted_link:
          link_queue.put(formatted_link)

def adddomain():
  domain = input("Enter the domain with protocol: ")
  domain_list.append(domain)

def deletedomain():
  domain = input("Enter the domain with protocol: ")
  domain_list.remove(domain)

def dumplinks():
  link_queue.put('DUMP')

def loaddomains():
  for domain in domain_list:
    link_queue.put('DOMAIN::{}'.format(domain))

def stopproqueue():
  for i in range(NUM_WORKERS):
    process_queue.put('STOP')

def displaylog():
  while not message_queue.empty():
    print(message_queue.get())

def stop_processes():
  # Stop worker processes
  for i in range(NUM_WORKERS):
      process_queue.put('STOP')

  # Stop link monitor
  link_queue.put('STOP')

  # Exit the process
  sys.exit()


def show_menu():
  print("""
    1: Add a Domain Name
    2: Delete Domain Name
    3: Show All Links
    4: Start Processing Queue
    5: Stop Processing Queue
    6: Display Logs
    7: Exit\n""")

  choice = input("Please enter your choice: ")
  
  if choice == "1":
    adddomain()
  elif choice == "2":
    deletedomain()
  elif choice == "3":
    dumplinks()
  elif choice == "4":
    loaddomains()
  elif choice == "5":
    stopproqueue()
  elif choice == "6":
    displaylog()
  elif choice == "7":
    stop_processes()
  else:
    print("Not a valid option. Please try again....\n")

  show_menu()

def main():
  # Start Workers
  for i in range(NUM_WORKERS):
    Process(target=scraper, args=(process_queue, link_queue, message_queue)).start()

  # Start Link Monitor
  Process(target=link_monitor, args=(link_queue, process_queue)).start()

  show_menu()

if __name__ == "__main__":
  main()