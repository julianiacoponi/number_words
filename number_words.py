#!/usr/bin/env python3
"""
Algorithms to find the smallest value number which fills a given character length when spelled-out
"""

import time
import datetime
from pprint import pprint
from num2words import num2words
from multiprocessing import Pool


def find_next_count(max_char_count_to_search_for):
    """
    very slow as it goes back looking from 0 each time to find the next one
    """
    # no numbers have character count of 0, 1 or 2
    char_count_set = {0, 1, 2}
    char_count_dict = {0: None, 1: None, 2: None}

    # so start looking at 3, and set a max number (or else could go on forever)
    char_count_to_find = 3

    while char_count_to_find not in char_count_set:
        if char_count_to_find > max_char_count_to_search_for:
            break

        for number_to_check in range(10**6):
            number_word_string = num2words(number_to_check).replace(',', '')

            if len(number_word_string) == char_count_to_find:
                print(char_count_to_find, number_word_string, number_to_check, '\n')
                char_count_to_find += 1
                break
    print('this run has ended')


def record_as_you_go(range_to_search, lengths_to_ignore_up_to=2, debug=False):
    """
    a lot quicker as it keeps track of what it finds and is essentially as fast/slow as the loop
    TODO: make it smarter by skipping large chunks of "known" empty ranges? Or something smarter?
    """
    start_time = time.monotonic()
    start_date = datetime.datetime.utcnow()
    print(f'starting record_as_you_go algorithm at {str(start_date)} (time counter at {start_time})')
    previous_time_since_start = None
    previous_date_since_start = None
    range_length = range_to_search.stop - range_to_search.start

    set_found_so_far = set([_ for _ in range(lengths_to_ignore_up_to + 1)])
    findings = {}
    number_words = []
    order_in_which_found = []
    nw_order = []
    for n in range_to_search:  # this argument is an actual range() object
        if n % (range_length // 100) == 0:
            print(f'n = {n}, search is {100 * n // range_length}% complete')
        nw = num2words(n).replace(',', '')
        l = len(nw)

        if l not in set_found_so_far:
            set_found_so_far.add(l)
            findings[l] = [n, nw]
            number_words.append(nw)
            nw_order.append(n)
            order_in_which_found.append(l)

            if debug:
                found_time = time.monotonic()
                time_since_start = found_time - start_time

                found_date = datetime.datetime.utcnow()
                date_since_start = found_date - start_date

                if previous_time_since_start is None:
                    time_since_previous_find = time_since_start
                else:
                    time_since_previous_find = time_since_start - previous_time_since_start

                if previous_date_since_start is None:
                    date_since_previous_find = date_since_start
                else:
                    date_since_previous_find = date_since_start - previous_date_since_start

                previous_time_since_start = time_since_start
                previous_date_since_start = date_since_start

                print(f'[{found_date}] raw monotonic time {found_time}')
                print(f'found: {l}')
                print(f'- Number: {findings[l][0]} spelled "{findings[l][1]}"')
                print(f'- time since start: {time_since_start:6f}s')
                print(f'- time since previous find: {time_since_previous_find:6f}s')
                print(f'- timedelta since start: {date_since_start}')
                print(f'- timedelta since previous find: {date_since_previous_find}')


                full_set = set(list(range(lengths_to_ignore_up_to + 1, max(set_found_so_far) + 1)))
                numbers_missed_so_far = full_set.difference(set_found_so_far)
                if not numbers_missed_so_far:
                    print(f'- All numbers up to {max(set_found_so_far)} found so far')
                else:
                    print(f'- Currently missing: {full_set.difference(set_found_so_far)}')

                print('\n')

    diff_in_sequence = [
        order_in_which_found[n + 1] - order_in_which_found[n]
        for n in range(len(order_in_which_found) - 1)
    ]
    if debug:
        delineator_top = '_' * 100
        delineator_bottom = '-' * 100
        print(delineator_top)
        print(f'FINISHED searching in range {range_to_search.start}-{range_to_search.stop}')
        print(delineator_bottom)
        pprint(findings)

        print(delineator_top)
        print('The character lengths were found in the following order:')
        print(delineator_bottom)
        print(order_in_which_found)

        print(delineator_top)
        print('The numbers corresponding to the character lengths above are:')
        print(delineator_bottom)
        print(nw_order)

        print(delineator_top)
        print('Difference from element to element in above sequence:')
        print(delineator_bottom)
        print(diff_in_sequence)


        print('\n\nJAGGED CLIFF (value ascending)')
        for nw in number_words:
            print(nw)

        print('\n\nNEAT SLOPE (length ascending)')
        for nw in sorted(number_words, key=len):
            # should line up exactly character for character diagonally
            print(nw)

    return findings, nw_order, order_in_which_found, diff_in_sequence

if __name__ == '__main__':
    use_multiprocessing = False
    if use_multiprocessing:
        # !!! THIS DOES NOT WORK AS THE SEPARATE PROCESSES DO NOT KNOW ABOUT EACH OTHER!
        # would need some kind of comparison after the fact for it to work...
        cpus_to_use = 10
        M = 5
        pool = Pool(cpus_to_use)
        ranges_to_search = [range(n * 10 ** M, (n + 1) * 10 ** M) for n in range(cpus_to_use)]

        print(f'Making use of {cpus_to_use} CPUs...')
        results = pool.map(record_as_you_go, ranges_to_search)
        pool.close()
        pool.join()
        all_results, all_nw, all_orders, all_diffs = zip(*results)
        FINAL_RESULT, FINAL_NW, FINAL_ORDER, FINAL_DIFF = {}, [], [], []
        for result, nw_order, order, diff in zip(all_results, all_nw, all_orders, all_diffs):
            FINAL_RESULT.update(result)
            FINAL_NW += nw_order
            FINAL_ORDER += order
            FINAL_DIFF += diff
        print('final result:\n')
        pprint(FINAL_RESULT)
        print('final number-word order:', FINAL_NW)
        print('final order:', FINAL_ORDER)
        print('final diff:', FINAL_DIFF)
    else:
        # sanity check with simpler algorithm
        # find_next_count(30)
        record_as_you_go(range(10**6, 10**7), lengths_to_ignore_up_to=2, debug=True)


# NOTE ON HOW TO WORK OUT ANALYTICALLY: every 3 digits has a structure
# (<single> hundred and <ty>-<single> <illion>)*many (<single> hundred and <ty>-<single>)
# i.e. a series of "hundred-structures" with an (n*10**3) word attached


# <single> = 0,1,2,3,4,5,6,7,8,9,10
# zero, one, two, three, four, five, six, seven, eight, nine
# 4, 3, 3, 5, 4, 4, 3, 5, 5, 4
# (zero is a special case at the start so ignore for rest of logic)
# --> all instances of <single> must be 3?


# <teen> = 10,11,12,13,14,15,16,17,18,19
# ten, eleven, twelve, thirteen, fourteen, fifteen, sixteen, seventeen, eighteen, nineteen
# 3, 6, 6, 8, 8, 7, 7, 9, 8, 8
# (ten can be ignored as 'and ten' will always appear after an 'and one' which is sooner)
# lots of room to play with here .. (although can mostly ignore 18 and 19)
# 11, 15, 13, 17 are smallest values with 6, 7, 8, 9 chars respectively
# teens can be ignored mostly (apart from in the leading hundred-structure)
# as numbers in the same hundred-structure (such as twenty-three or seventy-three have 11, 13 chars respectively)

# <ty> = 20, 30, 40, 50, 60, 70, 80, 90
# twenty, thirty, forty, fifty, sixty, seventy, eighty, ninety
# 6, 6, 5, 5, 5, 7, 6, 6
# ignore 80 and 90 .. 40, 20, 70 are of interest with lengths 5, 6, 7




# DO ALGORITHM WHERE: it tries all sevens, counts the characters, and then adjusts with 1s and 3s
# to get a best guess at what the lowest value with that many characters is
# input would be 'character length to guess for'
# do a initial guess of 373 concatenated backward (777 can always be replaced for 373)
# then replace the leading digit with 1s until it's too low, then raise the lowest value 1 to 2 etc. until it fits
