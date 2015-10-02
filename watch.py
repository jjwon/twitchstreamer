#!/usr/bin/python2
"""
Usage: watch.py

Opens an interactive session where you can search for streams to watch on Twitch.

TODO:
- Refactor using Click instead so we don't have to do so much dumb input grabbing
- BASE_URL at the top, which would be https://api.twitch.tv/kraken
- other url's that we use would build from it, aka STREAM_URL, GAME_URL, etc.
- get configuration files to work
- fix the occasional errors in printing: sanitize stream statuses
- if there aren't 10 streams to show, then only show however many there are (right now it errors)
"""

import json
import click
import sys
import requests
import subprocess
import getTerminalSize as gts

class StreamParser(object):
    """Parses stream list JSON data"""

    BASE_TWITCH_URL = "https://api.twitch.tv/kraken/streams"

    def __init__(self, limit=25, url=BASE_TWITCH_URL):
        self.url = url
        self.limit = limit
        self.game_list = []

    def get_featured_twitch_streams(self, offset=0):
        params = {"limit": self.limit, "offset": offset}
        data = requests.get(self.url + "/featured", params=params).json()
        featured = data["featured"]
        stream_list = [f["stream"] for f in featured]
        return stream_list

    def grab_favorite_streams(self):
        pass

    """
    find_popular_games stores the names of the top self.limit games, sorted by
    viewers, into self.game_list
    """
    def find_popular_games(self, offset=0):
        params = {"limit": self.limit, "offset": offset}
        data = requests.get("https://api.twitch.tv/kraken/games/top", params=params).json()
        games = data["top"]
        game_list = [g["game"]["name"] for g in games]
        return game_list

    def get_game_streams(self, game, offset=0):
        params = {"game": game, "limit": self.limit, "offset": offset}
        data = requests.get(self.url, params=params).json()
        return data["streams"]

    def output_data(self, filename="data.txt"):
        if self.stream_list == None:
            print "Error: please choose a type of stream to view first!" # should never happen in regular execution
            sys.exit(1) # probably don't need this outside of testing
        with open(filename, 'w') as outfile:
            json.dump(self.stream_list, outfile, sort_keys=False, indent=4, separators=(',', ': '))


def print_games(game_list):
    """ Prints games in game_list to STDOUT in a reasonable way """
    for i in range(0, len(game_list)):
        index = str(i) + ". "
        click.echo(index + game_list[i])
    click.echo(str(len(game_list)) + ". " + "Show more")

def print_streams(stream_list, term_width):
    """ Prints streams in stream_list to STDOUT in a reasonable way """
    for i in range(0, len(stream_list)):
        line = str(i) + ". "
        stream = stream_list[i]
        line += stream["channel"]["name"].encode('ascii', 'ignore')
        line += "\t" * ((24-len(line)) / 8 + 1)

        line += stream["channel"]["status"] if "status" in stream["channel"] else ""
        lines = [line]
        while len(lines[-1]) > term_width:
            line = lines.pop(-1)
            lines.append(line[:term_width])
            lines.append("\t\t\t" + line[term_width:])
        click.echo(''.join(lines))

def get_selection(selection_range):
    lo, hi = selection_range
    selection = click.prompt('Selection', type=int)
    while selection < lo or selection > hi:
        print "Invalid selection, please choose again"
        selection = click.prompt('Selection', type=int)
    return selection

def main():
    TERM_WIDTH, _ = gts.getTerminalSize()
    LIMIT = 10

    # Initialize the introduction interface
    print "Welcome to TwitchStreamer!  Please choose a category to sort from."
    print "0. Featured"
    print "1. Games"
    print "2. Favorites"
    selection = get_selection((0, 2))

    # We load 10 items at a time, and we'll load more using the pagination thingy to load items faster.
    parser = StreamParser(limit=LIMIT)

    if selection == 0:
        # Featured streams
        streams = parser.get_featured_twitch_streams()
        print_streams(streams, TERM_WIDTH)
        stream_selection = get_selection((0, len(streams)))
        chosen_stream = streams[stream_selection]["channel"]["name"]
    elif selection == 1:
        # Stream selection by game
        games = parser.find_popular_games()
        print_games(games)
        game_selection = get_selection((0, len(games)))

        # Enters a "show more" loop, if user wants to see more games.
        i = 1
        while game_selection == 10:
            games = parser.find_popular_games(offset=parser.limit * i)
            print_games(games)
            game_selection = get_selection((0, len(games)))
            i += 1

        game = games[game_selection]
        streams = parser.get_game_streams(game)
        print_streams(streams, TERM_WIDTH)

        stream_selection = get_selection((0, len(streams)))
        chosen_stream = streams[stream_selection]["channel"]["name"]
    else:
        pass

    # TODO: figure out if there's a less shitty way to do this
    subprocess.call("livestreamer " + "twitch.tv/" + chosen_stream + " best", shell=True)

if __name__ == "__main__":
    main()
