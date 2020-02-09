import argparse
import os
from colorama import Fore, Back, Style

_formats = {
    'header':       Fore.MAGENTA,
    'arg':          Fore.GREEN  + ' -> '            + Style.RESET_ALL,
    'inv_probe':    Back.RED    + '[INVALID] '      + Style.RESET_ALL,
    'new_probe':    Fore.CYAN   + '[PROBE] '        + Style.RESET_ALL,
    'new_svideo':   Fore.CYAN   + '[SVIDEO] '       + Style.RESET_ALL,
    'new_hvideo':   Fore.CYAN   + '[HVIDEO] '       + Style.RESET_ALL,
    'new_download': Fore.CYAN   + '[DOWNLOAD] '     + Style.RESET_ALL,
    'new_audio':    Fore.CYAN   + '[AUDIO] '        + Style.RESET_ALL,
    'new_vaudio':   Fore.CYAN   + '[VAUDIO] '       + Style.RESET_ALL,
}

def out(c, m): 
    print(_formats[c] + m + Style.RESET_ALL)


_parser = argparse.ArgumentParser( description='Video/Audio library maintainer script' )

_parser.add_argument ( '-s', '--sync', action='store_true',  help='Sync files and jobs' )
_parser.add_argument ( '-i', '--index', action='store_true', help='Fill index.txt file' )
_parser.add_argument ( '-j', '--jobs',                       help='Number of paralell jobs', type=int )
_parser.add_argument ( '-k', '--keys',                       help='Jobs keys to do (w-download,w-torrent,w-hvideo,w-svideo,w-vaudio,w-audio)', type=lambda k: k.split(',') )
_parser.add_argument ( '-p', '--purge', action='store_true', help='Clean lists: done, doing and failed' )
_parser.add_argument ( 'urls',                               help='Urls to download', nargs='*' )
_parser.set_defaults ( scan=False, urls=[], jobs=os.cpu_count() * 2, keys=None )

args = _parser.parse_args()

