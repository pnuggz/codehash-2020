# THIS IS A TEST SCRIPT TO READ OUT FILES


lib_read = []
lib_duplicate = []

books_read = []
books_duplicate = []

f = open('d_tough_choices.out', "r")

num_lib = f.readline().rstrip("\n\r").rstrip("\n").rstrip(
            "\r")

for i in range(int(num_lib)):
  line_1 = f.readline().rstrip("\n\r").rstrip("\n").rstrip(
            "\r").rstrip(" ").split(' ')
  line_2 = f.readline().rstrip("\n\r").rstrip("\n").rstrip(
            "\r").rstrip(" ").split(' ')

  lib_index = int(line_1[0])
  if lib_index in lib_read:
    lib_duplicate.append(lib_index)
  else:
    lib_read.append(lib_index)
  
  for k,book in enumerate(line_2):
    book_index = int(book)
    if book_index in books_read:
      books_duplicate.append(book_index)
    else:
      books_read.append(book_index)

print(len(books_read))
print(len(books_duplicate))
  