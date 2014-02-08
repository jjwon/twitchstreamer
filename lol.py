#!/usr/bin/python2
# -*- coding: utf-8 -*-

from distutils import spawn
import urllib2
import json
import os
import sys
import requests
import subprocess
import getTerminalSize

"""

Set the first option afterwards to be "best" if no configuration specified in
the configuration files.  You can just hit enter.

Eventually, we probably want to define things like:
- BASE_URL at the top, which would be https://api.twitch.tv/kraken
- other url's that we use would build from it, aka STREAM_URL, GAME_URL, etc.

To-do list:
- get configuration files to work
- fix the occasional errors in printing: sanitize stream statuses
- if there aren't 10 streams to show, then only show however many there are (right now it errors)




"""

class StreamParser:

	"""Parses stream list JSON data"""
	
	def __init__(self, term_width, num=25):
		self.term_width = term_width
		self.num = num
		self.url = "https://api.twitch.tv/kraken/streams"
		self.game_list = []
		self.stream_list = None
		# CHECK FOR CONFIGURATION FILE~!


	def get_featured_streams(self, offset=0):
		params = {"limit": self.num, "offset": offset}
		raw_data = requests.get(self.url + "/featured", params = params)
		json_data = raw_data.json()
		self.stream_list = []
		for i in range(0, len(json_data["featured"])):
			self.stream_list.append(json_data["featured"][i]["stream"])


	def grab_favorite_streams(self):
		pass


	"""
	print_streams takes in an integer term_width, and prints self.stream_list 
	in a pretty fashion

	"""
	def print_streams(self):
		for i in range(0, len(self.stream_list)):
			index = str(i) + ") "
			stream = self.stream_list[i]
			streamer = stream["channel"]["name"].encode('ascii', 'ignore')
			if len(streamer + index) < 8:
				streamer += "\t"
			if len(streamer + index) < (8*2):
				streamer += "\t"
			streamer += "\t"
			status = stream["channel"]["status"]
			if status:
				status = status.encode('ascii', 'ignore')
				if len(status) > (self.term_width-24): # checks if line overflows
					status = status[0:(self.term_width-28)] + "..."
			else:
				status = ""
			print index + streamer + status
			i += 1


	"""
	find_popular_games stores the names of the top self.num games, sorted by
	viewers, into self.game_list
	"""
	def find_popular_games(self, offset=0):
		params = {"limit": self.num, "offset": offset}
		raw_data = requests.get("https://api.twitch.tv/kraken/games/top", params = params)
		json_data = raw_data.json()
		top_games = json_data["top"]
		self.game_list = []
		for i in range(0, len(top_games)):
			raw = top_games[i]["game"]["name"]
			s = raw.encode('ascii', 'ignore')
			self.game_list.append(s)


	"""
	print_game_list prints out self.game_list in a neat fashion.  NOT SURE IF NEEDED.
	"""
	def print_game_list(self):
		for i in range(0, len(self.game_list)):
			index = str(i) + ") "
			print index + self.game_list[i]
		print str(len(self.game_list)) + ") " + "Show more"

	"""
	grab_game_stream takes in a game name, and stores the top self.num streams
	objects into self.stream_list
	"""
	def grab_game_stream(self, game, offset=0):
		params = {"game": game, "limit": self.num, "offset": offset}
		raw_data = requests.get(self.url, params = params)
		json_data = raw_data.json()
		self.stream_list = []
		for i in range(0, len(json_data["streams"])):
			self.stream_list.append(json_data["streams"][i])


	def output_data(self, filename="data.txt"):
		if self.stream_list == None:
			print "Error: please choose a type of stream to view first!" # should never happen in regular execution
			sys.exit(1) # probably don't need this outside of testing
		with open(filename, 'w') as outfile:
			json.dump(self.stream_list, outfile, sort_keys=False, indent=4, separators=(',', ': '))


def selection_loop(num):
	print
	while True:
		selection = raw_input("Selection: ")
		print 
		if not selection.isdigit() or int(selection) > num:
			print "Invalid selection, please choose again."
		else:
			break
	return int(selection)

def main():

	# Initialize the introduction interface

	xy = getTerminalSize.getTerminalSize() # returns a tuple with (termsize_x, termsize_y)
	width, height = xy[0], xy[1]
	if sys.platform.startswith('linux') or sys.platform == 'darwin':
		os.system('clear')
	elif sys.platform.startswith('win'):
		os.system('cls')
	print
	print "*" * width
	print "Welcome to TwitchStreamer!  Please choose a category to sort from."
	print
	print "*" * width
	print "0.  Featured"
	print "1.  Games"
	print "2.  Favorites"
	selection = selection_loop(3)

	# We load 10 items at a time, and we'll load more using the pagination thingy to load items faster.

	parser = StreamParser(num=10, term_width=width)

	if int(selection) == 0:
		# load the first 10 featured streams into parser.stream_list and print it
		# we COULD add a "show more" feature here, but I don't think there should
		# be more than 10ish featured streams...
		parser.get_featured_streams()
		parser.print_streams()
		stream_selection = selection_loop(len(parser.stream_list))
		chosen_stream = parser.stream_list[stream_selection]["channel"]["name"]

	elif int(selection) == 1:
		# load the first 10 most popular games into parser.game_list and print it
		parser.find_popular_games()
		parser.print_game_list()
		game_selection = selection_loop(parser.num)

		# Enters a "show more" loop, if user wants to see more games.
		i = 1
		while game_selection == 10:
			num_shown = parser.num*i
			parser.find_popular_games(offset=num_shown)
			parser.print_game_list()
			game_selection = selection_loop(parser.num)
			i += 1

		chosen_game = parser.game_list[game_selection]
		parser.grab_game_stream(chosen_game)
		parser.print_streams()

		# Enters a "show more" loop, if user wants to see more streams.
		print "10) Show more"
		stream_selection = selection_loop(parser.num+1)
		i = 1
		while stream_selection == 10:
			num_shown = parser.num*i
			parser.grab_game_stream(chosen_game, offset=num_shown)
			parser.print_streams()
			print "10) Show more"
			stream_selection = selection_loop(parser.num+1)
			i += 1

		chosen_stream = parser.stream_list[stream_selection]["channel"]["name"]

	else:
		pass

        mpv_path = spawn.find_executable("mpv")

        if mpv_path:
                subprocess.call("livestreamer " + "twitch.tv/" + chosen_stream + " best " + \
                                "-p mpv -a '--title=twitch.tv/{0} {1}'".format(chosen_stream, "{filename}"), shell=True)
        else:
                subprocess.call("livestreamer " + "twitch.tv/" + chosen_stream + " best", shell=True)


	
if __name__ == "__main__":
	main()
