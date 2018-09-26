tweetl:crown:rd
==========
[![Python Version](https://img.shields.io/badge/python-3.x-blue.svg)](https://www.python.org/downloads)
[![License](https://img.shields.io/badge/license-GPLv3-blue.svg)](https://raw.githubusercontent.com/snovvcrash/tweetlord/master/LICENSE)
[![Built with Love](https://img.shields.io/badge/built%20with-%F0%9F%92%97%F0%9F%92%97%F0%9F%92%97-lightgrey.svg)](https://emojipedia.org/growing-heart)

**tweetlord** is an open source Twitter profile dumper (downloader) with the on-the-fly account swapping support for bypassing the rate limit restrictions. It is written in Python 3, uses the [Twitter API](https://developer.twitter.com/en/docs/accounts-and-users/follow-search-get-users/api-reference "API Reference — Twitter Developers") and generates `.xlsx` files at the output containing comprehensive information about the given profile.

### Table of Contents:
  * [**Screenshots**](#screenshots)
  * [**Dependencies**](#dependencies)
    * [DEB Packages](#deb-packages)
    * [PIP Packages](#pip-packages)
  * [**Installation**](#installation)
  * [**Usage**](#usage)
  * [**Platform**](#platform)
  * [**Post Scriptum**](#post-scriptum)

Screenshots
==========
![Screenshot-1](https://user-images.githubusercontent.com/23141800/43296815-5291c4ee-9156-11e8-9ce4-8c30a01b801d.png "Dumping the HTB profile")
![Screenshot-2](https://user-images.githubusercontent.com/23141800/43296820-5789703c-9156-11e8-9125-6eeac72aff22.png "Checking the account rate limit status")

|    ++++    | Friends | Followers | Favorites | Timeline |
|:----------:|:-------:|:---------:|:---------:|:--------:|
|  **Args**  |   300   |   10000   |   2000    |    500   |
| **Actual** |    74   |    8082   |   1637    |    326   |

From the table above it is seen why the progress bars in the 1st screenshot were not filled to the end: the actual number of items in each of the sections is less than it was specified in the arguments when running the tool. It's not a bug but a feature :wink: (one API request returns no more than 200 items so the *pbar step = 200*, btw).

Dependencies
==========
### DEB Packages
  * python3.x (or newer) interpreter

### PIP Packages
tweetlord makes use of the following external modules:
  * [tweepy](https://github.com/tweepy/tweepy "tweepy/tweepy: Twitter for Python!")
  * [simplejson](https://github.com/simplejson/simplejson "simplejson/simplejson: simplejson is a simple, fast, extensible JSON encoder/decoder for Python")
  * [xlsxwriter](https://github.com/jmcnamara/XlsxWriter "jmcnamara/XlsxWriter: A Python module for creating Excel XLSX files.")
  * [tqdm](https://github.com/tqdm/tqdm "tqdm/tqdm: A fast, extensible progress bar for Python and CLI")
  * [termcolor](https://pypi.org/project/termcolor "termcolor · PyPI")

Resolve all Python dependencies with the `pip` one-liner:
```
$ python3 -m pip install -r requirements.txt
```

Installation
==========
The order of use is pretty straightforward:
  1. :warning: First, you want to set your API keys (could be found [here](https://developer.twitter.com/en/apps)) in the *credentials.py* file for every Twitter account you want to involve in the procedure. It is needless to say that the more accounts you specify, the faster the dumping process will be (but nevertheless you can specify only one account). **If a mistake is made when filling the credentials, the script will terminate with an unhandled tweepy exception**, so keep that in mind.
  2. Hmm... that's actually it! Feel free to run tweetlord as shown in the next section.

Usage
==========
```
tweetlord.py [-h] (-u USER | -l) [-fr FRIENDS] [-fo FOLLOWERS]
             [-fa FAVORITES] [-ti TIMELINE] [-o OUTPUT] [-w] [-e] [-d]

required arguments:
  -u USER, --user USER    set the user profile you want to dump: <USER> could be a screen name or an account ID (if it is an ID, you should start the string with the "id" prefix, e. g. "id859377203242426368")
OR
  -l, --show-limits       show the rate limit status (total → remaining → time_to_wait_till_reset) for each of the accounts you set when configuring the tool

optional arguments:
  -fr N, --friends N      set the number of friends to be dumped (if N == -1 then tweetlord will try to dump all friends)
  -fo N, --followers N    set the number of followers to be dumped (if N == -1 then tweetlord will try to dump all followers)
  -fa N, --favorites N    set the number of favorite tweets to be dumped (if N == -1 then tweetlord will try to dump all favorite tweets)
  -ti N, --timeline N     set the number of tweets from user's timeline to be dumped (if N == -1 then tweetlord will try to dump all timeline tweets)
  -a, --all               dump ALL the sections with ALL the items in each of them
  -o NAME, --output NAME  set the output filename (".xlsx" ending will be added)
  -w, --wait-on-limit     sleep if the rate limit is exceeded (the sleeping time will be printed)
  -e, --tweet-extended    get the whole tweet text but not only the first 140 chars
  -d, --debug             debug mode (extra info messages will be show when exceptions are caught)
  -h, --help              show help
```

If there's no rate limit left and you have specified the `-w` flag, you can press *Ctrl-C* during the sleeping (waiting) process, **but only during the waiting process (otherwise, you'll terminate the main program)**, to skip dumping current section and continue with the next one.

See more about the Twitter [Rate Limiting](https://developer.twitter.com/en/docs/basics/rate-limiting.html "Rate Limiting — Twitter Developers").

Platform
==========
tweetlord works great both on Windows and GNU/Linux systems, but the resulting `.xlsx` dump files look prettier when opened in MS Excel app rather than in LibreOffice (and this is quite obvious because LibreOffice doesn't fully support `.xlsx` format anyhow :unamused:).

Post Scriptum
==========
If this tool has been useful for you, feel free to buy me a coffee :coffee:

[![Coffee](https://user-images.githubusercontent.com/23141800/44239302-60d2fc00-a1c1-11e8-8aaa-4fb829df2293.png)](https://buymeacoff.ee/snovvcrash)
