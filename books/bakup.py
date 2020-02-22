import time
import itertools
import threading
import math
from operator import itemgetter

input_file_name = ''
libary = {}
libary_index = []
running_library_index = []
days_total = 0
libary_total = 0
books_total = 0
book_scores = []
days_remaining = 0

starting_index = 0

signup_index = 0
signup_days_left = 0

can_scan_array = []
scan_book_score = 0

books_not_to_duplicate = []


def read_file(inp):
    global libary
    global libary_index
    global input_file_name
    global days_total
    global libary_total
    global books_total
    global book_scores
    global starting_index
    global running_library_index

    input_file_name = inp

    f = open(input_file_name, "r")
    details = f.readline().rstrip("\n\r").rstrip("\n").rstrip("\r").split(' ')
    books_total = int(details[0])
    libary_total = int(details[1])
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
        line_data_books_scores = [
            book_scores[index] for j, index in enumerate(line_data_books)
        ]

        libary_index.append(i)
        libary[i] = {
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

        if (libary[i]['weighting'] > starting_index):
            starting_index = i
    f.close()

    running_library_index = libary_index
    del running_library_index[starting_index]


def recalculate_scores():
    global running_library_index
    global libary
    global days_remaining
    global books_not_to_duplicate
    global book_scores

    all_remaining_library = []

    for k in range(len(running_library_index)):
        i = running_library_index[k]
        curr_library = libary[i]
        curr_books = curr_library['books']

        # Remove all books that are already being scanned
        curr_books = [
            index for j, index in enumerate(curr_books)
            if index not in books_not_to_duplicate
        ]

        # Get the book scores
        curr_books_scores = []
        for n in range(len(curr_books)):
            curr_books_scores.append({
                'index': curr_books[n],
                'score': book_scores[curr_books[n]]
            })
        # Sort the book scores by the score
        curr_books_scores = sorted(
            curr_books_scores, key=itemgetter('score'), reverse=True)

        # Set the new array of library books
        libary[i]['books'] = [
            curr_books_scores[g]['index']
            for g in range(len(curr_books_scores))
        ]

        # Calculate the number of days available
        days_avail = days_remaining - curr_library['signup_days']
        # Calculate how many books we can scan
        books_can_be_scanned = days_avail * curr_library['scanning_rate']
        if (books_can_be_scanned > len(curr_books)):
            books_can_be_scanned = len(curr_books)

        total_score = sum([
            curr_books_scores[q]['score'] for q in range(books_can_be_scanned)
            if q < len(curr_books_scores)
        ])

        all_remaining_library.append({
            'index':
            i,
            'score':
            total_score * curr_library['weighting']
        })

    all_remaining_library = sorted(
        all_remaining_library, key=itemgetter('score'), reverse=True)

    running_library_index = [
        all_remaining_library[m]['index']
        for m in range(len(all_remaining_library))
    ]


def add_books_not_to_duplicate(curr_library):
    global books_not_to_duplicate
    global days_remaining
    global book_scores

    curr_books = curr_library['books']

    days_avail = days_remaining - curr_library['signup_days']
    if (days_avail < 0):
        return False

    # Calculate how many books we can scan -- OLD WORKING WHICH I THINK IS WRONG
    # books_can_be_scanned = math.floor(
    #     float(days_avail) / float(curr_library['scanning_rate']))

    # Calculate how many books we can scan
    books_can_be_scanned = days_avail * curr_library['scanning_rate']
    if (books_can_be_scanned > len(curr_books)):
        books_can_be_scanned = len(curr_books)

    curr_books_scores = []
    for i in range(len(curr_books)):
        curr_books_scores.append({
            'index': curr_books[i],
            'score': book_scores[curr_books[i]]
        })
    curr_books_scores = sorted(
        curr_books_scores, key=itemgetter('score'), reverse=True)
    for i in range(books_can_be_scanned):
        if (i == len(curr_books_scores)):
            break
        books_not_to_duplicate.append(curr_books_scores[i]['index'])


def signup_process():
    global signup_index
    global signup_days_left
    global running_library_index
    global starting_index
    global libary

    if (signup_index == 0 and starting_index != 0):
        signup_index = starting_index
        signup_days_left = libary[starting_index]['signup_days']
        add_books_not_to_duplicate(libary[starting_index])
        starting_index = 0
        return

    signup_days_left -= 1
    if (signup_days_left == 0):
        # Move the signup index into the can scan array
        can_scan_array.append(signup_index)

        # Check if running_library_index is empty
        if (len(running_library_index) == 0):
            return

        # Recalculate the next index required
        recalculate_scores()

        # Assign new signup index from the next in the running library
        signup_index = running_library_index[0]
        del running_library_index[0]
        signup_days_left = libary[signup_index]['signup_days']
        add_books_not_to_duplicate(libary[signup_index])


def scan_books(index):
    global can_scan_array
    global libary
    global book_scores
    global scan_book_score

    i = can_scan_array[index]
    curr_library = libary[i]
    curr_books = curr_library['books']
    curr_books_score = [
        book_scores[curr_books[k]] for k in range(len(curr_books))
    ]
    rate = curr_library['scanning_rate']

    for o in range(rate):
        if (o < len(curr_books)):
            scan_book_score += curr_books_score[o]
            del curr_books[o]

    libary[i]['books'] = curr_books

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
        is_complete = scan_books(i)
        if (is_complete):
            library_complete.append(can_scan_array[i])

    can_scan_array = [
        can_scan_array[p] for p in range(len(can_scan_array))
        if can_scan_array[p] not in library_complete
    ]


def main():
    start = time.time()
    global libary
    global libary_index
    global input_file_name
    global days_total
    global libary_total
    global books_total
    global book_scores
    global working_array
    global running_library_index
    global days_remaining
    global scan_book_score

    for day in range(days_total + 1, 0, -1):
        days_remaining = day
        signup_process()
        process_libraries()
        print(day)
        print(scan_book_score)
        print('')
    print(scan_book_score)


if __name__ == '__main__':
    inp = input()
    read_file(inp)
    main()