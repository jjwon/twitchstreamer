#!/usr/bin/python2
# -*- coding: utf-8 -*-

import urllib2
import json
import os
import sys

"""

First goals: get all the data that we want.

Initially, we want to be able to sort by:
- favorites
- featured
- individual games

Within each category, we can sort by viewers.

Print the channel's name, then the status

Allow them to select a number, and then it will open the corresponding
twitch.tv URL in livestreamer

Set the first option afterwards to be "best" if no configuration specified in
the configuration files.  You can just hit enter.


"""

class StreamParser:

	"""Parses stream list JSON data"""
	
	def __init__(self, url="https://api.twitch.tv/kraken/streams", num=25):
		self.url = url + "?limit=" + str(num)
	
	def grab_streams(self, game=None):
		data = urllib2.urlopen(self.url).read()
		data = json.loads(data)
		return data
		
	def print_status(self):
		stream_list = self.grab_streams()
		for stream in stream_list["streams"]:
			s = stream["channel"]["status"]
			out = '' if s is None else s.encode('ascii', 'ignore')
			print out
		
	def output_data(self, filename="data.txt"):
		stream_list = self.grab_streams()
		with open(filename, 'w') as outfile:
			json.dump(stream_list, outfile, sort_keys=False, indent=4, separators=(',', ': '))

def main():
	parser = StreamParser(num=100)
	parser.print_status()
	parser.output_data()
	
if __name__ == "__main__":
	main()
