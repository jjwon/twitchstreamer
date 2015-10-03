#!/usr/bin/python2
"""
Usage: watch.py

Opens an interactive session where you can search for streams to watch on Twitch.

TODO:
- Support other streaming websites (that livestreamer uses) -- this involves
a refactor of how StreamParser gets URLs and deals with options
- Support configuration files, so you can have favorite streams
"""

import click
import requests
import subprocess
import getTerminalSize as gts

class StreamParser(object):
    """Parses stream list JSON data"""

    def __init__(self, url, limit=25):
        self.url = url
        self.limit = limit
        self.game_list = []

    def get_featured_twitch_streams(self, offset=0):
        params = {"limit": self.limit, "offset": offset}
        data = requests.get(self.url + "/featured", params=params).json()
        featured = data["featured"]
        stream_list = [f["stream"] for f in featured]
        return stream_list

    def get_popular_games(self, offset=0):
        params = {"limit": self.limit, "offset": offset}
        data = requests.get("https://api.twitch.tv/kraken/games/top", params=params).json()
        games = data["top"]
        game_list = [g["game"]["name"] for g in games]
        return game_list

    def get_game_streams(self, game, offset=0):
        params = {"game": game, "limit": self.limit, "offset": offset}
        data = requests.get(self.url, params=params).json()
        return data["streams"]

def print_games(game_list):
    """ Prints games in game_list to STDOUT in a reasonable way """
    for i in range(0, len(game_list)):
        index = str(i) + ". "
        click.echo(index + game_list[i])
    click.echo(str(len(game_list)) + ". " + "Show more")
    print

def print_streams(stream_list, term_width):
    """ Prints streams in stream_list to STDOUT in a reasonable way """
    for i in range(0, len(stream_list)):
        line = str(i) + ". "
        stream = stream_list[i]
        line += stream["channel"]["name"].encode('ascii', 'ignore')
        line += " " * (24-len(line))

        status = stream["channel"]["status"].encode('ascii', 'ignore') if "status" in stream["channel"] else ""
        line += status

        lines = [line]
        while len(lines[-1]) > (term_width):
            line = lines.pop(-1)
            lines.append(line[:term_width])
            lines.append(" "*24 + line[term_width:])
        click.echo(''.join(lines))
    print

def get_selection(selection_range):
    low, high = selection_range
    selection = click.prompt('Selection', type=int)
    print
    while selection < low or selection > high:
        click.echo("Invalid selection, please choose again")
        selection = click.prompt('Selection', type=int)
        print
    return selection

def choose_stream_with_loop(func, *args):
    streams = func(*args)
    print_streams(streams, TERM_WIDTH)
    stream_selection = get_selection((0, len(streams)))

    i = 0
    while stream_selection == LIMIT:
        i += 1
        streams = func(*args, offset=i*LIMIT)
        print_streams(streams, TERM_WIDTH)
        stream_selection = get_selection((0, len(streams)))
    return streams[stream_selection]["channel"]["name"]

def choose_game_with_loop(func, *args):
    games = func(*args)
    print_games(games)
    game_selection = get_selection((0, len(games)))

    i = 0
    while game_selection == LIMIT:
        i += 1
        games = func(*args, offset=LIMIT * i)
        print_games(games)
        game_selection = get_selection((0, len(games)))
    return games[game_selection]

def main():
    # Initialize the introduction interface
    click.echo("Welcome to TwitchStreamer!  Please choose a category to sort from.")
    click.echo("0. Featured")
    click.echo("1. Games")
    click.echo("2. Favorites")
    selection = get_selection((0, 2))

    # Load LIMIT items at a time
    parser = StreamParser(BASE_TWITCH_URL, limit=LIMIT)

    if selection == 0:
        # Featured streams
        chosen_stream = choose_stream_with_loop(parser.get_featured_twitch_streams)
    elif selection == 1:
        # Stream selection by game
        game = choose_game_with_loop(parser.get_popular_games)
        chosen_stream = choose_stream_with_loop(parser.get_game_streams, game)
    else:
        pass

    # TODO: figure out if there's a less shitty way to do this
    subprocess.call("livestreamer " + "twitch.tv/" + chosen_stream + " best", shell=True)

if __name__ == "__main__":
    BASE_TWITCH_URL = "https://api.twitch.tv/kraken/streams"
    TERM_WIDTH, _ = gts.getTerminalSize()
    LIMIT = 10
    main()
