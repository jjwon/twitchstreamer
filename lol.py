#!/usr/bin/python2
# -*- coding: utf-8 -*-

import urllib2
import json
import os
import sys
import requests

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

Eventually, we probably want to define things like:
- BASE_URL at the top, which would be https://api.twitch.tv/kraken
- other url's that we use would build from it, aka STREAM_URL, GAME_URL, etc.


"""

# game_dict = {
# 	"hots" : "StarCraft II: Heart of the Swarm",
# 	"lol" : "League of Legends",
# }

class StreamParser:

	"""Parses stream list JSON data"""
	
	def __init__(self, num=25):
		self.num = num
		self.url = "https://api.twitch.tv/kraken/streams"
		self.game_list = []
		self.stream_list = None
		# CHECK FOR CONFIGURATION FILE~!
	
	def grab_all_streams(self, game):
		params = {"limit": self.num, "game": game}
		data = requests.get(self.url, params = params)
		print data.url
		# out_url = self.url + "/streams?limit=" + str(self.num)
		# data = urllib2.urlopen(out_url).read()
		# data = json.loads(data)
		self.stream_list = data.json()

	def grab_featured_streams(self):
		out_url = self.url + "/featured" + "?limit=" + str(self.num)
		data = urllib2.urlopen(out_url).read()
		data = json.loads(data)
		self.stream_list = data


	def grab_favorite_streams(self):
		pass


	def grab_game_stream(self, game):
		out_url = self.url + "?q=" + game
		data = urllib2.urlopen(out_url).read()
		data = json.loads(data)
		self.stream_list = data


	def find_popular_games(self):
		params = {"limit": self.num}
		raw_data = requests.get("https://api.twitch.tv/kraken/games/top", params = params)
		print raw_data.url
		json_data = raw_data.json()
		top_games = json_data["top"]
		for i in range(0, len(top_games)):
			raw = top_games[i]["game"]["name"]
			s = raw.encode('ascii', 'ignore')
			self.game_list.append(s)


	def print_game_list(self):
		print self.game_list
		print len(self.game_list)


	def print_status(self):
		if self.stream_list == None:
			print "Error: please choose a type of stream to view first!" # should never happen in regular execution
			sys.exit(1) # probably don't need this outside of testing
		for stream in self.stream_list["streams"]:
			s = stream["channel"]["status"]
			out = '' if s is None else s.encode('ascii', 'ignore')
			print out
		print len(self.stream_list["streams"])
		
	def output_data(self, filename="data.txt"):
		if self.stream_list == None:
			print "Error: please choose a type of stream to view first!" # should never happen in regular execution
			sys.exit(1) # probably don't need this outside of testing
		with open(filename, 'w') as outfile:
			json.dump(self.stream_list, outfile, sort_keys=False, indent=4, separators=(',', ': '))

def main():
	parser = StreamParser(num=100)
	#parser.grab_game_stream("starcraft")
	parser.find_popular_games()
	parser.print_game_list()
	#parser.grab_all_streams()
	#parser.print_status()
	#parser.output_data()
	
if __name__ == "__main__":
	main()
