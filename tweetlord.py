#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@file tweetlord.py
@author Sam Freeside <snovvcrash@protonmail.com>
@date 2018-07

@brief Twitter profile dumper.

@license
Copyright (C) 2018 Sam Freeside

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
@endlicense
"""

import json
import string
import sys
import time
import datetime

import tweepy
import xlsxwriter

from queue import PriorityQueue
from html import unescape
from argparse import ArgumentParser

from tqdm import tqdm
from termcolor import cprint, colored

from credentials import credentials


# ----------------------------------------------------------
# ----------------------- Constants ------------------------
# ----------------------------------------------------------


VERSION = '0.1'
SITE = 'https://github.com/snovvcrash/tweetlord'

VERSION_FORMATTED = '\033[1;37m{\033[1;35mv%s\033[1;37m}\033[1;34m' % VERSION
SITE_FORMATTED = '\033[0m\033[4;37m%s\033[1;34m' % SITE

BANNER = """\033[1;34m\
                                                        
 _                     _   _                   _        
| |___      _____  ___| |_| |  \033[1;37m_.+._\033[1;34m   _ __ __| |       
| __\\ \\ /\\ / / _ \\/ _ \\ __| |\033[1;37m(^\\/^\\/^)\033[1;34m| '__/ _` |
| |_ \\ V  V /  __/  __/ |_| | \033[1;37m\\@*@*@/\033[1;34m | | | (_| |     
 \\__| \\_/\\_/ \\___|\\___|\\__|_| \033[1;37m{_____}\033[1;34m |_|  \\__,_|
                                                        
%s
%s\033[0m\
""" % (VERSION_FORMATTED, SITE_FORMATTED)

USER_COLS = [
	'Profile URL',
	'Profile Image URL',
	'User ID',
	'User Login',
	'User Name',
	'Description',
	'Friends Count',
	'Followers Count',
	'Statuses Count',
	'Favorites Count',
	'Location',
	'Website',
	'Created at'
]

FRIENDS_COLS = [
	'Profile URL',
	'Profile Image URL',
	'User ID',
	'User Login',
	'User Name',
	'Description'
]

FOLLOWERS_COLS = [
	'Profile URL',
	'Profile Image URL',
	'User ID',
	'User Login',
	'User Name',
	'Description'
]

FAVORITES_COLS = [
	'Tweet Text',
	'Tweet URL',
	'User ID',
	'User Login',
	'Favorite Count',
	'Retweet Count',
	'Latitude',
	'Longitude'
]

TIMELINE_COLS = [
	'Tweet Text',
	'Tweet URL',
	'Favorite Count',
	'Retweet Count',
	'Latitude',
	'Longitude'
]

PROC_NAMES = {
	'_api_user': 'api.get_user',
	'_api_friends': 'api.friends',
	'_api_followers': 'api.followers',
	'_api_favorites': 'api.favorites',
	'_api_timeline': 'api.user_timeline'
}

SECTION_NAMES = {
	'api.get_user': 'users',
	'api.friends': 'friends',
	'api.followers': 'followers',
	'api.favorites': 'favorites',
	'api.user_timeline': 'statuses'
}


# ----------------------------------------------------------
# -------------------------- Core --------------------------
# ----------------------------------------------------------


def user_info(am, username):
	user = _api_handler(am, _api_user, username)

	id_str = user.id_str
	screen_name = user.screen_name
	name = user.name
	description = unescape(user.description)
	friends_count = user.friends_count
	followers_count = user.followers_count
	statuses_count = user.statuses_count
	favorites_count = user.favourites_count
	profile_url = 'https://twitter.com/' + screen_name
	profile_image_url = user.profile_image_url_https.replace('_normal', '_400x400')
	location = user.location

	try:
		website = user.entities['url']['urls'][0]['expanded_url']
	except (IndexError, KeyError):
		website = ''

	created_at = user.created_at.strftime('%Y-%m-%d %H:%M:%S')

	return ([
		profile_url,
		profile_image_url,
		id_str,
		screen_name,
		name,
		description,
		friends_count,
		followers_count,
		statuses_count,
		favorites_count,
		location,
		website,
		created_at
	], {
		'friends': friends_count,
		'followers': followers_count,
		'favorites': favorites_count,
		'timeline': statuses_count
	})


def user_friends(am, username, count, max_friends):
	friends = _api_handler(am, _api_friends, username, count, max_friends, 'fr')

	table_rows = []
	for friend in friends:
		id_str = friend.id_str
		screen_name = friend.screen_name
		name = friend.name
		profile_url = 'https://twitter.com/' + screen_name
		profile_image_url = friend.profile_image_url_https.replace('_normal', '_400x400')
		description = unescape(friend.description)

		table_rows.append([
			profile_url,
			profile_image_url,
			id_str,
			screen_name,
			name,
			description
		])

	return table_rows


def user_followers(am, username, count, max_followers):
	followers = _api_handler(am, _api_followers, username, count, max_followers, 'fol')

	table_rows = []
	for follower in followers:
		id_str = follower.id_str
		screen_name = follower.screen_name
		name = follower.name
		profile_url = 'https://twitter.com/' + screen_name
		profile_image_url = follower.profile_image_url_https.replace('_normal', '_400x400')
		description = unescape(follower.description)

		table_rows.append([
			profile_url,
			profile_image_url,
			id_str,
			screen_name,
			name,
			description
		])

	return table_rows


def user_favorites(am, username, count, max_favorites, tweet_extended):
	statuses = _api_handler(am, _api_favorites, username, count, max_favorites, 'fav', tweet_extended)

	table_rows = []
	for status in statuses:
		if tweet_extended:
			text = unescape(status.full_text)
		else:
			text = unescape(status.text)

		screen_name = status.author.screen_name
		name = status.author.name
		status_url = 'https://twitter.com/' + screen_name + '/status/' + status.id_str
		favorite_count = status.favorite_count
		retweet_count = status.retweet_count

		geo = status.geo
		if geo:
			latitude, longitude = geo['coordinates']
		else:
			latitude = longitude = ''

		table_rows.append([
			text,
			status_url,
			screen_name,
			name,
			favorite_count,
			retweet_count,
			latitude,
			longitude
		])

	return table_rows


def user_timeline(am, username, count, max_timeline, tweet_extended):
	statuses = _api_handler(am, _api_timeline, username, count, max_timeline, 'tw', tweet_extended)

	table_rows = []
	for status in statuses:
		if tweet_extended:
			text = unescape(status.full_text)
		else:
			text = unescape(status.text)

		status_url = 'https://twitter.com/' + status.author.screen_name + '/status/' + status.id_str
		favorite_count = status.favorite_count
		retweet_count = status.retweet_count

		geo = status.geo
		if geo:
			latitude, longitude = geo['coordinates']
		else:
			latitude = longitude = ''

		table_rows.append([
			text,
			status_url,
			favorite_count,
			retweet_count,
			latitude,
			longitude
		])

	return table_rows


def build_xlsx(dump, filename, username):
	workbook = xlsxwriter.Workbook(filename + '.xlsx')
	worksheet = workbook.add_worksheet(username)

	header_fmt = workbook.add_format({
		'bold': True,
		'font_size': 15,
		'font_color': '#1F497D',
		'bottom': True,
		'bottom_color': '#6699CC',
	})
	header_fmt.set_bottom(5)

	col_title_fmt = workbook.add_format({
		'bold': True,
		'bg_color': '#C6EFCE',
		'font_color': '#006100',
		'border': True
	})

	signature_fmt = workbook.add_format({
		'italic': True,
		'font_color': '#7F7F7F'
	})

	signature_version_fmt = workbook.add_format({
		'italic': True,
		'font_color': '#508CD4'
	})

	signature_site_fmt = workbook.add_format({
		'italic': True,
		'underline': True,
		'font_color': '#508CD4'
	})

	worksheet.write(0, 0, 'This document was generated with tweetl\U0001F451rd tool (by snovvcrash).', signature_fmt)  # 👑
	worksheet.write(1, 0, 'v{}'.format(VERSION), signature_version_fmt)
	worksheet.write(2, 0, '{}'.format(SITE), signature_site_fmt)

	curr_row = 6
	row_lengths = []

	# ----------------------- User Info ------------------------

	worksheet.write(curr_row, 0, 'User', header_fmt)
	curr_row += 1

	for i, title in enumerate(USER_COLS):
		worksheet.write(curr_row, i, title, col_title_fmt)
		row_lengths.append([len(title)])
	curr_row += 1

	for i, elem in enumerate(dump['user']):
		worksheet.write(curr_row, i, elem)
		row_lengths[i].append(len(str(elem)))
	curr_row += 4

	# ------------------------- Other --------------------------

	for titles, dump_part, header in zip((FRIENDS_COLS, FOLLOWERS_COLS, FAVORITES_COLS, TIMELINE_COLS),
                                         (dump['friends'], dump['followers'], dump['favorites'], dump['timeline']),
                                         ('Friends', 'Followers', 'Favorites', 'Timeline')):
		if dump_part:
			worksheet.write(curr_row, 0, '{} ({})'.format(header, len(dump_part)), header_fmt)
			curr_row += 1

			for i, title in enumerate(titles):
				worksheet.write(curr_row, i, title, col_title_fmt)
				row_lengths[i].append(len(title))
			curr_row += 1

			for table_row in dump_part:
				for i, elem in enumerate(table_row):
					worksheet.write(curr_row, i, elem)
					row_lengths[i].append(len(str(elem)))
				curr_row += 1
			curr_row += 4

	# ---------------- Correcting columns width ----------------

	row_lengths[0].append(61)  # signature (first string) length
	for i in range(len(USER_COLS)):  # USER_COLS is max length
		worksheet.set_column(i, i, max(row_lengths[i]) + 2)

	workbook.close()


def show_limits(client):
	limits = client.rate_limit_status()

	if 'access_token' in limits['rate_limit_context']:
		print('USER-AUTH')
	elif 'application' in limits['rate_limit_context']:
		print('APP-AUTH')

	d = limits['resources']['application']['/application/rate_limit_status']
	limit = d['limit']
	remaining = d['remaining']
	reset = d['reset'] - int(datetime.datetime.timestamp(datetime.datetime.now()))
	print('[0] api.rate_limit_status -- limit: {}, remaining: {}, reset: {} m {} s'.format(limit, remaining, reset // 60, reset % 60))

	d = limits['resources']['users']['/users/show/:id']
	limit = d['limit']
	remaining = d['remaining']
	reset = d['reset'] - int(datetime.datetime.timestamp(datetime.datetime.now()))
	print('[1] api.get_user          -- limit: {}, remaining: {}, reset: {} m {} s'.format(limit, remaining, reset // 60, reset % 60))

	d = limits['resources']['friends']['/friends/list']
	limit = d['limit']
	remaining = d['remaining']
	reset = d['reset'] - int(datetime.datetime.timestamp(datetime.datetime.now()))
	print('[2] api.friends           -- limit: {}, remaining: {}, reset: {} m {} s'.format(limit, remaining, reset // 60, reset % 60))

	d = limits['resources']['followers']['/followers/list']
	limit = d['limit']
	remaining = d['remaining']
	reset = d['reset'] - int(datetime.datetime.timestamp(datetime.datetime.now()))
	print('[3] api.followers         -- limit: {}, remaining: {}, reset: {} m {} s'.format(limit, remaining, reset // 60, reset % 60))

	d = limits['resources']['favorites']['/favorites/list']
	limit = d['limit']
	remaining = d['remaining']
	reset = d['reset'] - int(datetime.datetime.timestamp(datetime.datetime.now()))
	print('[4] api.favorites         -- limit: {}, remaining: {}, reset: {} m {} s'.format(limit, remaining, reset // 60, reset % 60))

	d = limits['resources']['statuses']['/statuses/user_timeline']
	limit = d['limit']
	remaining = d['remaining']
	reset = d['reset'] - int(datetime.datetime.timestamp(datetime.datetime.now()))
	print('[5] api.user_timeline     -- limit: {}, remaining: {}, reset: {} m {} s'.format(limit, remaining, reset // 60, reset % 60))

	# _d = limits['resources']['users'].get('/users/search', None)
	# _limit = d['limit']
	# _remaining = d['remaining']
	# _reset = d['reset'] - int(datetime.datetime.timestamp(datetime.datetime.now()))
	# _print('[6] api.search_users -- \"limit\": {}, \"remaining\": {}, \"reset\": {} m {} s'.format(limit, remaining, reset // 60, reset % 60))

	# _d = limits['resources']['search'].get('/search/tweets', None)
	# _limit = d['limit']
	# _remaining = d['remaining']
	# _reset = d['reset'] - int(datetime.datetime.timestamp(datetime.datetime.now()))
	# _print('[7] api.search -- \"limit\": {}, \"remaining\": {}, \"reset\": {} m {} s'.format(limit, remaining, reset // 60, reset % 60))


# ----------------------------------------------------------
# -------------------------- API ---------------------------
# ----------------------------------------------------------


def _api_handler(am, api_method, username, count=None, max_items=0, unit='', tweet_extended=False):
	api_method_name = PROC_NAMES[api_method.__name__]
	api_section_name = SECTION_NAMES[api_method_name]

	cred, time_to_wait = am.get(api_section_name)
	modes, curr_mode = ['app', 'user'], 0

	if count is None:  # api_method == _api_user
		while True:
			client = tweepy_auth(cred, mode=modes[curr_mode])
			try:
				return api_method(client, username)
			except (tweepy.error.TweepError, tweepy.error.RateLimitError) as e:
				if e.response.status_code == 404:
					raise TweetlordError('User not found', errors={'code': 1, 'initial': str(e)})
				curr_mode = 1 - curr_mode
				if not curr_mode:
					cred, time_to_wait = am.get(api_section_name)
					if time_to_wait <= 0:
						print('[*] Account switched')
					elif WAIT_ON_RATE_LIMIT:
						print('[*] It\'s {} on the clock'.format(time.strftime('%H:%M:%S', time.localtime())))
						print_warning(
							'{}: Rate limit exceeded, all accounts are empty. Waiting {} minutes {} seconds'
							.format(api_method_name, time_to_wait // 60, time_to_wait % 60), str(e)
						)
						try:
							time.sleep(time_to_wait)
						except KeyboardInterrupt:
							cprint('{}: Stopped'.format(api_method_name), 'white', 'on_red', attrs=['bold'])
							break
					else:
						raise TweetlordError('Rate limit exceeded, all accounts are empty', errors={'code': 2, 'initial': str(e)})

	max_per_page = 200
	full_pages = count // max_per_page
	items_remaining = count % max_per_page

	start_page = -1 if api_method in (_api_friends, _api_followers) else 0
	items = []

	with tqdm(total=count, ncols=80, unit=unit, desc='    got') as pbar:
		while full_pages:
			client = tweepy_auth(cred, mode=modes[curr_mode])
			cursor = api_method(
				client,
				username,
				page=start_page,
				count=max_per_page,
				pages_count=full_pages,
				tweet_extended=tweet_extended
			)

			try:
				for page in cursor:
					items += page
					start_page = cursor.next_cursor if api_method in (_api_friends, _api_followers) else start_page + 1
					full_pages -= 1
					pbar.update(max_per_page)
			except (tweepy.error.TweepError, tweepy.error.RateLimitError) as e:
				if e.response.status_code == 404:
					raise TweetlordError('User not found', errors={'code': -1, 'initial': str(e)})
				curr_mode = 1 - curr_mode
				if not curr_mode:
					cred, time_to_wait = am.get(api_section_name)
					if time_to_wait <= 0:
						pbar.write('[*] Account switched')
					elif WAIT_ON_RATE_LIMIT:
						pbar.write('[*] It\'s {} on the clock'.format(time.strftime('%H:%M:%S', time.localtime())))
						print_warning(
							'{}: Rate limit exceeded, all accounts are empty. Waiting {} minutes {} seconds'
							.format(api_method_name, time_to_wait // 60, time_to_wait % 60), str(e), write=pbar.write
						)
						try:
							time.sleep(time_to_wait)
						except KeyboardInterrupt:
							pbar.write(colored('{}: Stopped'.format(api_method_name), 'white', 'on_red', attrs=['bold']))
							break
					else:
						print_warning(
							'{}: Rate limit exceeded, all accounts are empty'
							.format(api_method_name), str(e), write=pbar.write
						)
						return items
			else:
				full_pages = 0

		if len(items) < max_items:
			while items_remaining:
				client = tweepy_auth(cred, mode=modes[curr_mode])
				cursor = api_method(
					client,
					username,
					page=start_page,
					count=items_remaining,
					pages_count=1,
					tweet_extended=tweet_extended
				)

				try:
					items += flatten(list(cursor))
					pbar.update(items_remaining)
				except (tweepy.error.TweepError, tweepy.error.RateLimitError) as e:
					if e.response.status_code == 404:
						raise TweetlordError('User not found', errors={'code': -1, 'initial': str(e)})
					curr_mode = 1 - curr_mode
					if not curr_mode:
						cred, time_to_wait = am.get(api_section_name)
						if time_to_wait <= 0:
							pbar.write('[*] Account switched')
						elif WAIT_ON_RATE_LIMIT:
							pbar.write('[*] It\'s {} on the clock'.format(time.strftime('%H:%M:%S', time.localtime())))
							print_warning(
								'{}: Rate limit exceeded, all accounts are empty. Waiting {} minutes {} seconds'
								.format(api_method_name, time_to_wait // 60, time_to_wait % 60), str(e), write=pbar.write
							)
							try:
								time.sleep(time_to_wait)
							except KeyboardInterrupt:
								pbar.write(colored('{}: Stopped'.format(api_method_name), 'white', 'on_red', attrs=['bold']))
								break
						else:
							print_warning(
								'{}: Rate limit exceeded, all accounts are empty'
								.format(api_method_name), str(e), write=pbar.write
							)
							return items
				else:
					items_remaining = 0

	return items


def _api_user(client, username, **kwargs):
	if username.startswith('id'):
		user_id = username[2:]
		return client.get_user(user_id=user_id)

	screen_name = username
	return client.get_user(screen_name=screen_name)


def _api_friends(client, username, **kwargs):
	if username.startswith('id'):
		user_id = username[2:]
		return tweepy.Cursor(
			client.friends,
			user_id=user_id,
			cursor=kwargs['page'],
			count=kwargs['count'],
			skip_status=True,
			include_user_entities=False
		).pages(kwargs['pages_count'])

	screen_name = username
	return tweepy.Cursor(
		client.friends,
		screen_name=screen_name,
		cursor=kwargs['page'],
		count=kwargs['count'],
		skip_status=True,
		include_user_entities=False
	).pages(kwargs['pages_count'])


def _api_followers(client, username, **kwargs):
	if username.startswith('id'):
		user_id = username[2:]
		return tweepy.Cursor(
			client.followers,
			user_id=user_id,
			cursor=kwargs['page'],
			count=kwargs['count'],
			skip_status=True,
			include_user_entities=False
		).pages(kwargs['pages_count'])

	screen_name = username
	return tweepy.Cursor(
		client.followers,
		screen_name=screen_name,
		cursor=kwargs['page'],
		count=kwargs['count'],
		skip_status=True,
		include_user_entities=False
	).pages(kwargs['pages_count'])


def _api_favorites(client, username, **kwargs):
	if username.startswith('id'):
		user_id = username[2:]
		return tweepy.Cursor(
			client.favorites,
			user_id=user_id,
			page=kwargs['page'],
			count=kwargs['count'],
			include_entities=False,
			tweet_mode=kwargs['tweet_extended']
		).pages(kwargs['pages_count'])

	screen_name = username
	return tweepy.Cursor(
		client.favorites,
		screen_name=screen_name,
		page=kwargs['page'],
		count=kwargs['count'],
		include_entities=False,
		tweet_mode=kwargs['tweet_extended']
	).pages(kwargs['pages_count'])


def _api_timeline(client, username, **kwargs):
	if username.startswith('id'):
		user_id = username[2:]
		return tweepy.Cursor(
			client.user_timeline,
			user_id=user_id,
			count=kwargs['count'],
			trim_user=False,
			exclude_replies=False,
			include_rts=True,
			tweet_mode=kwargs['tweet_extended']
		).pages(kwargs['pages_count'])

	screen_name = username
	return tweepy.Cursor(
		client.user_timeline,
		screen_name=screen_name,
		count=kwargs['count'],
		trim_user=False,
		exclude_replies=False,
		include_rts=True,
		tweet_mode=kwargs['tweet_extended']
	).pages(kwargs['pages_count'])


# ----------------------------------------------------------
# -------------------------- Auth --------------------------
# ----------------------------------------------------------


def tweepy_auth(cred, mode):
	auth = None
	if mode == 'user':
		auth = tweepy.OAuthHandler(cred['consumer_key'], cred['consumer_secret'])
		auth.set_access_token(cred['access_token_key'], cred['access_token_secret'])
	elif mode == 'app':
		auth = tweepy.AppAuthHandler(cred['consumer_key'], cred['consumer_secret'])
	return tweepy.API(auth, wait_on_rate_limit=False) if auth else None


# ----------------------------------------------------------
# -------------------- Account Manager ---------------------
# ----------------------------------------------------------


class AccountManager:

	METHODS = {
		'users': '/users/show/:id',
		'friends': '/friends/list',
		'followers': '/followers/list',
		'favorites': '/favorites/list',
		'statuses': '/statuses/user_timeline'
	}

	def __init__(self, credentials):
		unique_creds = {json.dumps(cred) for cred in credentials}

		self._creds = [json.loads(cred) for cred in unique_creds]
		self._app_clients = [tweepy_auth(cred, mode='app') for cred in self._creds]
		self._user_clients = [tweepy_auth(cred, mode='user') for cred in self._creds]

		self._app_limits, self._user_limits = self._build_limits()

		self._queues = dict.fromkeys(AccountManager.METHODS.keys())
		for section in AccountManager.METHODS:
			self._queues[section] = self._build_queue(section, AccountManager.METHODS[section])

	def get(self, section):
		if self._queues[section].empty():
			self._app_limits, self._user_limits = self._build_limits()
			self._queues[section] = self._build_queue(section, AccountManager.METHODS[section])

		limit, reset, account = self._queues[section].get()
		if limit:
			return (account, 0)

		time_to_wait = reset - int(datetime.datetime.timestamp(datetime.datetime.now()))
		return (account, time_to_wait)

	def _build_limits(self):
		app_limits, user_limits = [], []
		for app_client, user_client in zip(self._app_clients, self._user_clients):
			try:
				tmp_app = app_client.rate_limit_status()
				tmp_user = user_client.rate_limit_status()
			except tweepy.error.RateLimitError:
				pass
			else:
				app_limits.append(tmp_app)
				user_limits.append(tmp_user)

		return (app_limits, user_limits)

	def _build_queue(self, section, method):
		queue = PriorityQueue(len(self._creds))
		for i in range(len(self._creds)):
			queue.put((
				-(self._app_limits[i]['resources'][section][method]['remaining'] + self._user_limits[i]['resources'][section][method]['remaining']),
				max(self._app_limits[i]['resources'][section][method]['reset'], self._user_limits[i]['resources'][section][method]['reset']),
				self._creds[i]
			))

		return queue


# ----------------------------------------------------------
# ------------------------- Utils --------------------------
# ----------------------------------------------------------


def flatten(pages):
	return (status for page in pages for status in page)


def format_filename(s):
	valid_chars = "-_.() {!s}{!s}".format(string.ascii_letters, string.digits)
	filename = ''.join(c for c in s if c in valid_chars)
	filename = filename.replace(' ', '_')
	return filename


class TweetlordError(Exception):
	def __init__(self, message, errors=None):
		super().__init__(message)
		if not errors:
			errors = {}
		self.errors = errors
		self.errors.setdefault('errcode', 0)
		self.errors.setdefault('initial_error', '')


# ----------------------------------------------------------
# ------------------------ Messages ------------------------
# ----------------------------------------------------------


def print_info(message):
	cprint('[INFO] {}'.format(message), 'green')


def print_warning(message, initial_error='', *, write=print):
	if DEBUG:
		if initial_error:
			write(initial_error, file=sys.stderr)

	write(colored('[WARNING] {}'.format(message), 'yellow'))


def print_critical(message, initial_error=''):
	if DEBUG:
		if initial_error:
			print(initial_error, file=sys.stderr)

	cprint('[CRITICAL] {}'. format(message), 'white', 'on_red', attrs=['bold'])


# ----------------------------------------------------------
# -------------------------- Opts --------------------------
# ----------------------------------------------------------


def cli_options():
	parser = ArgumentParser()
	group = parser.add_mutually_exclusive_group(required=True)
	group.add_argument('-u', '--user')
	group.add_argument('-l', '--show-limits', action='store_true')
	parser.add_argument('-fr', '--friends', type=int, default=0)
	parser.add_argument('-fo', '--followers', type=int, default=0)
	parser.add_argument('-fa', '--favorites', type=int, default=0)
	parser.add_argument('-ti', '--timeline', type=int, default=0)
	parser.add_argument('-a', '--all', action='store_true')
	parser.add_argument('-o', '--output', type=str, default='out')
	parser.add_argument('-w', '--wait-on-limit', action='store_const', const='extended')
	parser.add_argument('-e', '--tweet-extended', action='store_const', const='extended')
	parser.add_argument('-d', '--debug', action='store_true')
	return parser.parse_args()


# ----------------------------------------------------------
# -------------------------- Main --------------------------
# ----------------------------------------------------------


def main():
	print(BANNER + '\n')

	args = cli_options()
	global WAIT_ON_RATE_LIMIT; WAIT_ON_RATE_LIMIT = args.wait_on_limit
	global DEBUG; DEBUG = args.debug

	if args.show_limits:
		for cred in credentials:
			for key, val in cred.items():
				print('{}: \"{}\"'.format(key, val))
			print()
			try:
				show_limits(tweepy_auth(cred, mode='app')); print()
				show_limits(tweepy_auth(cred, mode='user')); print()
			except tweepy.error.RateLimitError as e:
				print_critical('No rate limit to run \"rate_limit_status()\". Wait 15 minutes and try again', str(e))
		return

	timestart = time.time()
	print('[*] Started at {}\n'.format(time.strftime('%H:%M:%S', time.localtime())))

	dump = dict.fromkeys(('user', 'friends', 'followers', 'favorites', 'timeline'))

	print_info('Initializing account manager')
	am = AccountManager(credentials)

	try:
		print_info('Collecting basic account info')
		dump['user'], max_items = user_info(am, args.user)

		if args.friends or args.all:
			if args.friends == -1 or args.all:
				args.friends = max_items['friends']
			print_info('Collecting user friends info')
			dump['friends'] = user_friends(am, args.user, args.friends, max_items['friends'])

		if args.followers or args.all:
			if args.followers == -1 or args.all:
				args.followers = max_items['followers']
			print_info('Collecting user followers info')
			dump['followers'] = user_followers(am, args.user, args.followers, max_items['followers'])

		if args.favorites or args.all:
			if args.favorites == -1 or args.all:
				args.favorites = max_items['favorites']
			print_info('Collecting user favorites info')
			dump['favorites'] = user_favorites(am, args.user, args.favorites, max_items['favorites'], args.tweet_extended)

		if args.timeline or args.all:
			if args.timeline == -1 or args.all:
				args.timeline = max_items['timeline']
			print_info('Collecting user timeline info')
			dump['timeline'] = user_timeline(am, args.user, args.timeline, max_items['timeline'], args.tweet_extended)

	except TweetlordError as e:
		if e.errors['code'] == 1:
			print_critical(str(e), e.errors['initial'])

	else:
		if any(section for section in dump.values()):
			print_info('Building .xlsx file')
			filename = format_filename(args.output)
			build_xlsx(dump, filename, args.user)
			print(); print_info('Success! Result: {}.xlsx'.format(filename))
		else:
			print_critical('No data collected')

	print('\n[*] Time taken: {}'.format(datetime.timedelta(seconds=time.time() - timestart)))
	print('[*] Shutted down at {}'.format(time.strftime('%H:%M:%S', time.localtime())))


if __name__ == '__main__':
	main()
