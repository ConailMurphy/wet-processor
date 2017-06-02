#!/usr/bin/python

import re
import os
import codecs
import time
import argparse

parser = argparse.ArgumentParser(description='Extracts URLs from a .wet file')
parser.add_argument('-w', '--wet', type=str, metavar='', required=True, help='The name of the file to be searched')
parser.add_argument('-o', '--output', type=str, metavar='', required=True, help='The name of the file to write the '
                                                                                'URLs to')
parser.add_argument('-r', '--regex', type=str, metavar='', required=True, help='The name of the file to create a set '
                                                                               'of regex patterns from')
parser.add_argument('-t', '--tld', type=str, metavar='', default='', help='The name of the file to create a set of '
                                                                          'specific TLDs to extract')
group = parser.add_mutually_exclusive_group()
group.add_argument('-q', '--quiet', action='store_true', help='print quiet')
group.add_argument('-v', '--verbose', action='store_true', help='print verbose')
args = parser.parse_args()


def main():
    extract_urls(args.wet, args.output, args.regex, args.tld)


def extract_urls(wet, output, regex, tld=''):

    if os.path.exists(wet) & os.path.exists(regex):  # check if the input files exists
        if args.quiet != True:
            if args.verbose:
                print "\nInput File exists"
                print "Regex File exists"
                start_time = time.time()
            print "Working..."
        input_file_name, output_file_name, regex_file_name, tld_file_name = wet, output, regex, tld

        url_pattern = r"WARC-Target-URI:"                  # lines starting with this will contain a url
        new_page_pattern = r"WARC/1.0"                      # the meta data for a new page starts with this line
        new_page_pattern_check = r"WARC-Type: conversion"    # the second line of meta data for a new page

        with open(regex_file_name, "r") as regex:
            patterns = regex.read().splitlines()   # create a list of expressions to search for such from a file

        if tld_file_name != '':
            with open(tld_file_name, 'r') as TLD:  # creates the output file
                tlds = TLD.read().split("\n")  # create a list of domains to search for such from a file

        with open(output_file_name, 'w') as o:  # creates the output file
            o.write("")

        url = ""            # url found in meta data is stored here
        control = 0         # used to control the flow of the main for loop
        match_found = False  # set to true if a match is found for a pattern from the regex text file

        with codecs.open(input_file_name, 'r', encoding='utf-8') as f:  # opens the input file with utf-8 encoding
            #  so it can handle non-standard characters, mainly for foreign languages eg. cyrillic arabic etc.
            for line in f:
                if control == 0:
                    matchObj = re.match(url_pattern, line)
                    if matchObj:
                        control = 1
                        match, url = line.split(' ')

                elif control == 1:
                    for ex in patterns:
                        matchObj = re.search(ex, line, re.IGNORECASE)
                        if matchObj:
                            match_found = True
                    matchObj = re.match(new_page_pattern, line, re.IGNORECASE)
                    if matchObj:
                        control = 2
                else:
                    matchObj = re.match(new_page_pattern_check, line)
                    if matchObj:
                        if match_found:
                            match_found = False
                            if tld_file_name != '':
                                for d in tlds:
                                    matchObj = re.search(d, url)
                                    if matchObj:
                                        with open(output_file_name, 'a') as o:
                                            o.write(url.strip("\n"))
                                            continue
                            else:
                                with open(output_file_name, 'a') as o:
                                    o.write(url.strip("\n"))

                        control = 0
                    else:
                        control = 1
        if args.verbose:
            print("\nDone!")
            minutes_taken = (time.time() - start_time) / 60
            seconds_taken = (time.time() - start_time) % 60

            print ("Time taken to complete : %i minutes %i seconds" % (minutes_taken, seconds_taken))
        else:
            print 'URLs successfully extracted'

    else:
        print "Error: incorrect arguments"


if __name__ == '__main__':
    main()
