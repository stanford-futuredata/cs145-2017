#!/usr/bin/env python

import sys
import os
import imp
import difflib
import itertools

DEFAULT_PATH = 'submit.py'
CORRECT_OUTPUT_PATH = 'correct_output.txt'
DATABASE_PATH = 'flights.db'

def main(argv):
    # get path to where the sanity check script lives 
    # (which presumably will also be where the reference correct output lives)
    sanity_check_folder = os.path.dirname(os.path.realpath(__file__))

    # get path to the submission
    submission = argv[1] if len(argv) > 1 else DEFAULT_PATH
    submissionPath = os.path.join(os.getcwdu(), submission)

    # Check if path exists and is a file.
    print("Sanity checking file '{}'...".format(submissionPath))
    if not os.path.isfile(submissionPath):
        print("ERROR: File '{}' does not exist.".format(submissionPath))
        return 1
    # Attempt to load file as script.
    foo = imp.load_source('submit', submissionPath)

    # Attempt to connect datatbase
    foo.connect_database(os.path.join(sanity_check_folder, DATABASE_PATH))
    results = foo.get_all_query_results(debug_print=False)

    # turn a list of lists of strings into a list of strings
    # https://stackoverflow.com/questions/716477/join-list-of-lists-in-python
    listStrings = list(itertools.chain.from_iterable(results))

    # read the correct output file
    correctOutputStrings = None
    with open(os.path.join(sanity_check_folder, CORRECT_OUTPUT_PATH)) as f:
        correctOutputStrings = f.readlines()
    correctOutputStrings = [s.strip() for s in correctOutputStrings]

    # diff the correct output file
    diff = difflib.ndiff(listStrings, correctOutputStrings)
    diffPrinted = False
    for s in diff:
        if s[0] == '-' or s[0] == '+':
            diffPrinted = True
        print s

    if diffPrinted:
        print "Your output may not match the correct output. Check the diff above for the difference between your output and the correct output."
        return 1
    else:
        print "Your output matches the correct-output exactly! You're good to go."

if __name__ == '__main__':
    sys.exit(main(sys.argv))
