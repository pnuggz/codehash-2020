import time
import itertools
import threading
import math
from operator import itemgetter
from collections import OrderedDict

input_file_name = ''

library = {}
running_library_index = {}

days_total = 0
days_remaining = 0
library_total = 0
books_total = 0
book_scores = []

signup_index = None
signup_days_left = 0

can_scan_array = []
scan_book_score = 0

books_not_to_duplicate = []

final_library_signed = 0
final_library = []
final_books_scanned_list = {}


def read_file(inp):
    global library
    global input_file_name
    global days_total
    global library_total
    global books_total
    global book_scores
    global running_library_index

    # Set input file name for the output
    input_file_name = inp

    f = open(input_file_name, "r")
    details = f.readline().rstrip("\n\r").rstrip("\n").rstrip("\r").split(' ')
    books_total = int(details[0])
    library_total = int(details[1])
    days_total = int(details[2])

    book_scores = f.readline().rstrip("\n\r").rstrip("\n").rstrip("\r").split(
        ' ')
    book_scores = [int(score) for i, score in enumerate(book_scores)]

    for i in range(10000000):
        line_data_details = f.readline().rstrip("\n\r").rstrip("\n").rstrip(
            "\r")
        line_data_books = f.readline().rstrip("\n\r").rstrip("\n").rstrip("\r")

        if (line_data_details == ''):
            break

        line_data_details = line_data_details.split(' ')
        line_data_books = line_data_books.split(' ')
        line_data_books = [
            int(index) for j, index in enumerate(line_data_books)
        ]

        # Get the book scores
        curr_books_scores = []
        for n in range(len(line_data_books)):
            curr_books_scores.append({
                'index': line_data_books[n],
                'score': book_scores[line_data_books[n]]
            })
        # Sort the book scores by the score
        curr_books_scores = sorted(
            curr_books_scores, key=itemgetter('score'), reverse=True)

        # Set the new array of library books
        line_data_books = [
            curr_books_scores[g]['index']
            for g in range(len(curr_books_scores))
        ]

        library[i] = {
            'key':
            i,
            'books_number':
            int(line_data_details[0]),
            'signup_days':
            int(line_data_details[1]),
            'scanning_rate':
            int(line_data_details[2]),
            'books':
            line_data_books,
            'weighting':
            float(line_data_details[2]) / float(int(line_data_details[1]))
        }

        running_library_index[i] = library[i]
    f.close()

    # Use ordered dictionary instead so we can keep a sorted list by score
    running_library_index = OrderedDict(sorted(running_library_index.items()))


def checkEqual3(lst):
    return lst[1:] == lst[:-1]


def recalculate_scores():
    global running_library_index
    global days_remaining
    global books_not_to_duplicate
    global book_scores

    # Loop through every unsigned library to recalculate their score based on the books not yet scored
    for key, curr_library in running_library_index.items():
        curr_books = curr_library['books']

        # Remove all books from their books array that are already being scanned
        curr_books = [
            index for j, index in enumerate(curr_books)
            if index not in books_not_to_duplicate
        ]

        # Set the new array of library books
        running_library_index[key]['books'] = curr_books

        # Get the book scores
        curr_books_scores = []
        for n in range(len(curr_books)):
            curr_books_scores.append({
                'index': curr_books[n],
                'score': book_scores[curr_books[n]]
            })

        # Calculate the number of days available
        days_avail = days_remaining - curr_library['signup_days']
        # Calculate how many books we can scan
        books_can_be_scanned = days_avail * curr_library['scanning_rate']
        if (books_can_be_scanned > len(curr_books)):
            books_can_be_scanned = len(curr_books)

        # Find the total score by summing all the scanned books in the given amount of time
        total_score = sum([
            curr_books_scores[q]['score'] for q in range(books_can_be_scanned)
            if q < len(curr_books_scores)
        ])

        # Set the final score - including multiplication by the weighting
        running_library_index[key][
            'score'] = total_score * curr_library['weighting']

    # Reorder all remaining libraries accordingly
    running_library_index = OrderedDict(
        sorted(
            running_library_index.items(),
            key=lambda item: item[1]['score'],
            reverse=True))

    # To speed up performance, empty list of books not to duplicate
    books_not_to_duplicate = []


def add_books_not_to_duplicate(curr_library):
    global books_not_to_duplicate
    global days_remaining
    global book_scores
    global final_library_signed
    global final_library
    global final_books_scanned_list

    curr_books = curr_library['books']

    days_avail = days_remaining - curr_library['signup_days']
    if (days_avail < 0):
        return False

    # Calculate how many books we can scan
    books_can_be_scanned = days_avail * curr_library['scanning_rate']
    if (books_can_be_scanned > len(curr_books)):
        books_can_be_scanned = len(curr_books)

    # Get all the scores
    curr_books_scores = []
    for i in range(len(curr_books)):
        curr_books_scores.append({
            'index': curr_books[i],
            'score': book_scores[curr_books[i]]
        })

    final_books_scanned_list[curr_library['key']] = {'books': []}
    for i in range(books_can_be_scanned):
        if (i == len(curr_books_scores)):
            break
        # Add books that will be scanned into the final output
        final_books_scanned_list[curr_library['key']]['books'].append(
            curr_books_scores[i]['index'])
        # Add books that will be scanned into the not to duplicate list
        books_not_to_duplicate.append(curr_books_scores[i]['index'])

    final_library_signed += 1
    final_library.append(curr_library['key'])


def signup_process():
    global signup_index
    global signup_days_left
    global running_library_index

    #For the first time running
    if (signup_index == None):
        recalculate_scores()
        signup_index = next(iter(running_library_index.items()))[1]['key']
        signup_days_left = running_library_index[signup_index]['signup_days']
        add_books_not_to_duplicate(running_library_index[signup_index])
        return

    # Subtract a day each time
    signup_days_left -= 1
    if signup_days_left == 0:
        # Move the signup index into the can scan array
        can_scan_array.append(running_library_index[signup_index])
        del running_library_index[signup_index]

        # Check if running_library_index is empty
        if len(running_library_index) == 0:
            return

        # Recalculate the next index required but only if the scores are not all equal... otherwise unnecessary
        if not checkEqual3(book_scores):
            recalculate_scores()

        # Assign new signup index from the next in the running library
        signup_index = next(iter(running_library_index.items()))[1]['key']
        signup_days_left = running_library_index[signup_index]['signup_days']
        add_books_not_to_duplicate(running_library_index[signup_index])


def scan_books(index):
    global can_scan_array
    global book_scores
    global scan_book_score

    curr_library = can_scan_array[index]
    curr_books = curr_library['books']
    curr_books_score = [
        book_scores[curr_books[k]] for k in range(len(curr_books))
    ]
    rate = curr_library['scanning_rate']

    to_be_removed = []
    for o in range(rate):
        if (o < len(curr_books)):
            scan_book_score += curr_books_score[o]
            to_be_removed.append(o)

    can_scan_array[index]['books'] = [
        curr_books[r] for r in range(len(curr_books)) if r not in to_be_removed
    ]

    if (len(curr_books) == 0):
        return True
    else:
        return False


def process_libraries():
    global can_scan_array

    if (len(can_scan_array) == 0):
        return

    library_complete = []
    for i in range(len(can_scan_array)):
        # Scans book and tallies up to a global variable - returns whether complete or not to add library complete
        is_complete = scan_books(i)
        if (is_complete):
            library_complete.append(can_scan_array[i])

    can_scan_array = [
        can_scan_array[p] for p in range(len(can_scan_array))
        if can_scan_array[p] not in library_complete
    ]


def create_output():
    global final_library
    global final_books_scanned_list

    output_file_name = input_file_name.split('.')[0] + '.out'
    f = open(output_file_name, "w+")

    library_count = 0
    for k, lib_key in enumerate(final_library):
        if len(final_books_scanned_list[lib_key]['books']) > 0:
            library_count += 1

    f.write(str(library_count) + '\n')

    for k, lib_key in enumerate(final_library):
        line_1 = ''
        line_2 = ''

        if len(final_books_scanned_list[lib_key]['books']) > 0:   
            line_1 = str(lib_key) + ' ' + str(
                len(final_books_scanned_list[lib_key]['books']))

            for book_index, book in enumerate(final_books_scanned_list[lib_key]['books']):
                if book_index == len(final_books_scanned_list[lib_key]['books']):
                    line_2 = line_2 + str(book)
                else:
                    line_2 = line_2 + str(book) + ' '
            
            f.write(line_1 + '\n')
            f.write(line_2 + '\n')

    f.close()


def main():
    global days_total
    global days_remaining
    global scan_book_score
    global running_library_index

    for day in range(days_total, -1, -1):
        # print('Currently on day: {}'.format(day))

        days_remaining = day
        signup_process()
        process_libraries()
        
    print('Final scanning score is: {}'.format(scan_book_score))
    create_output()


if __name__ == '__main__':
    inp = input()
    read_file(inp)
    main()