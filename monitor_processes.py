# Author : Ali Snedden
# Date   : 04/23/24
# License: MIT
# Notes :
#   Only works on linux
#
#
#
#
#
"""This code does stuff
"""
#import os
import sys
import time
import argparse
import subprocess

# Set seeds
def main():
    """Monitor user processes by using Python

    Args:

    Returns:

    Raises:
    """
    parser = argparse.ArgumentParser(description="")
    parser.add_argument('--user', metavar='username', type=str,
                        help='Username')
    parser.add_argument('--delay', metavar='delay', type=float,
                        help='Delay in seconds between query')
    args = parser.parse_args()
    user = args.user
    delay = args.delay

    while True:
        # Should be careful of string injection
        # https://stackoverflow.com/a/28756533/4021436
        string="top -b -u {} -n 1".format(user)
        top = subprocess.Popen(string, shell=True, stdout=subprocess.PIPE)
        print top.stdout.readlines()
        time.sleep(delay)

    sys.exit(0)

if __name__ == "__main__":
    main()
