import itertools
import threading
import numpy as np
import time


# INPUT GLOBAL VARIABLE
input_file_name = ''
pizzas_number = 0
max_slice = 0
raw_pizzas_order = []

# RESULT GLOBAL VARIABLE
final_slice = 0
final_array = []
working_array = []


def work_with_chunk_array(arr):
  global final_slice
  global final_array

  for a in arr:
    s = sum(a)
    if(s > final_slice and s <= max_slice):
      final_slice = s
      final_array = a
    if(final_slice == max_slice):
      break


def run_threading():
  global working_array

  thread = threading.Thread(target=work_with_chunk_array, args=(working_array,))
  thread.start()
  thread.join()


def create_output(og_pizzas_order):
  global final_array
  global input_file_name

  counter = 0
  final_pizza_order = [0 for i in og_pizzas_order]
  for k,pizza in enumerate(og_pizzas_order):
    if pizza in final_array:
      counter += pizza
      final_pizza_order[k] = 1
      for i in range(len(final_array)):
        if final_array[i] == pizza:
          final_array[i] = -1
          break

  line_1_out = 0
  line_2_out = ''
  for index,pizza in enumerate(final_pizza_order):
    if pizza == 1:
      line_1_out += 1
      
      delim = '' if line_2_out == '' else ' '
      line_2_out = line_2_out + delim + str(index)
  
  output_file_name = input_file_name.split('.')[0] + '.out'
  f = open(output_file_name, "w+")
  f.write(str(line_1_out) + '\n')
  f.write(line_2_out)
  f.close() 
  

def main():
  start = time.time()
  global raw_pizzas_order
  global final_slice
  global final_array
  global max_slice
  global working_array

  og_pizzas_order = [int(i) for i in raw_pizzas_order]
  pizzas_order = og_pizzas_order[:]
  pizzas_order.sort(reverse=True)
  pizzas_order_length = len(pizzas_order)
  count = 0

  for comb_count in range(1, len(pizzas_order)+1, 1):
    min_subset = np.array(pizzas_order[(len(pizzas_order) - comb_count)::]).sum()
    max_subset = np.array(pizzas_order[0:comb_count]).sum()
    
    if max_slice <= max_subset and max_slice >= min_subset:
      for x in itertools.combinations(pizzas_order, comb_count):
        working_array.append(list(x))
        if len(working_array) == 70:
          run_threading()
          working_array = []
        
        if(final_slice == max_slice):
          break

      if len(working_array) > 0:
        run_threading()
        working_array = []

      if(final_slice == max_slice):
        break

  create_output(og_pizzas_order)

  end = time.time()
  print(end - start)


def read_file(inp):
  global pizzas_number
  global max_slice
  global raw_pizzas_order
  global input_file_name

  input_file_name = inp

  f = open(input_file_name, "r")
  line_1 = f.readline().split(' ')
  line_2 = f.readline().rstrip("\n\r").rstrip("\n").rstrip("\r").split(' ')
  f.close() 

  max_slice = int(line_1[0])
  pizzas_number = int(line_1[1])
  raw_pizzas_order = line_2


if __name__ == '__main__':
  inp = input()
  read_file(inp)
  main()