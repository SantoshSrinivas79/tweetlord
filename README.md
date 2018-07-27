tweetl:crown:rd
==========
[![Python Version](https://img.shields.io/badge/python-3.x-blue.svg)](https://www.python.org/downloads)
[![License](https://img.shields.io/badge/license-GPLv3-blue.svg)](https://raw.githubusercontent.com/snovvcrash/usbrip/master/LICENSE)
[![Built with Love](https://img.shields.io/badge/built%20with-%F0%9F%92%97%F0%9F%92%97%F0%9F%92%97-lightgrey.svg)](https://emojipedia.org/growing-heart)

**tweetlord** is an open source Twitter profile dumper (downloader) with the on-the-fly account swaping support for bypassing the rate limit restrictions. It is written in Python 3, uses the [Twitter API](https://developer.twitter.com/en/docs/accounts-and-users/follow-search-get-users/api-reference "API Reference — Twitter Developers") and generates `.xlsx` files at the output containing comprehensive information about the given profile.

Screenshots
==========
![Screenshot-1](https://user-images.githubusercontent.com/23141800/43296815-5291c4ee-9156-11e8-9ce4-8c30a01b801d.png "Dumping the HTB profile")
![Screenshot-2](https://user-images.githubusercontent.com/23141800/43296820-5789703c-9156-11e8-9125-6eeac72aff22.png "Checking the account rate limit status")

Dependencies
==========
### DEB Packages
* python3.x (or newer) interpreter

### PIP Packages
tweetlord makes use of the following external modules:
 * [tweepy](http://docs.tweepy.org/en/latest "Tweepy Documentation — tweepy 3.6.0 documentation")
 * [simplejson](https://simplejson.readthedocs.io/en/latest "simplejson — JSON encoder and decoder — simplejson 3.16.0 documentation")
 * [xlsxwriter](https://xlsxwriter.readthedocs.io "Creating Excel files with Python and XlsxWriter — XlsxWriter Documentation")
 * [tqdm](https://tqdm.github.io "tqdm | A fast, extensible progress bar for Python and CLI")
 * [termcolor](https://pypi.python.org/pypi/termcolor "termcolor 1.1.0 : Python Package Index")

Resolve all Python dependencies with one click with `pip`:
```
$ python3 -m pip install -r requirements.txt
```

Installation
==========
The order of use is pretty straightforward:
 1. :warning: First, you want to set your API keys (could be found [here](https://developer.twitter.com/en/apps)) in the *credentials.py* file for every Twitter account you want to involve in the procedure. It is needless to say that the more accounts you specify, the faster the dumping process will be (but nevertheless you can specify only one account). **If a mistake is made when filling the credentials, the script will terminate with an unhandled tweepy exception**, so keep that in mind.
 2. Hmm... that's actually it! Feel free to run the script as shown in the next section.

Usage
==========
```
tweetlord.py [-h] (-u USER | -l) [-fr FRIENDS] [-fo FOLLOWERS]
             [-fa FAVORITES] [-ti TIMELINE] [-o OUTPUT] [-w] [-e] [-d]

required arguments:
  -u USER, --user USER    set the user profile you want to dump: <USER> could be a screen name or an account ID (if it is an ID, you should start the string with the "id" prefix, e. g. "id859377203242426368")
OR
  -l, --show-limits       show the rate limit status (total-remaining-time_to_wait_till_reset) for each of the accounts you set when configuring the tool

optional arguments:
  -fr N, --friends N      set the number of friends to be dumped
  -fo N, --followers N    set the number of followers to be dumped
  -fa N, --favorites N    set the number of favorite tweets to be dumped
  -ti N, --timeline N     set the number of tweets from user's timeline to be dumped
  -o NAME, --output NAME  set the output filename (".xlsx" ending will be added)
  -w, --wait-on-limit     sleep if the rate limit is exceeded (the sleeping time will be printed)
  -e, --tweet-extended    get the whole tweet text but not only the first 140 chars
  -d, --debug             debug mode (extra info messages will be show when exceptions are caught)
  -h, --help              show help
```

Platform
==========
tweetlord works great both on Windows and GNU/Linux systems, but the resulting `.xlsx` dump files look prettier when opened in MS Excel app rather than in LibreOffice (just IMHO, no holy wars required :fearful:).

Post Scriptum
==========
If this tool has been useful for you, feel free to buy me a coffee :coffee:

[![Coffee](https://www.buymeacoffee.com/assets/img/custom_images/orange_img.png)](https://buymeacoff.ee/snovvcrash)
