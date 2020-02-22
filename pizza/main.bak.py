import itertools
import numpy as np
import multiprocessing 

pizzas_number = 50
max_slice = 4500
raw_pizzas_order = "7 12 12 13 14 28 29 29 30 32 32 34 41 45 46 56 61 61 62 63 65 68 76 77 77 92 93 94 97 103 113 114 114 120 135 145 145 149 156 157 160 169 172 179 184 185 189 194 195 195".split(' ')

final_slice = 0
final_array = []

def callback1(result):
  print(result)


def first_step(arr):
  return arr


def main():
  global raw_pizzas_order
  global final_slice
  global final_array

  og_pizzas_order = [int(i) for i in raw_pizzas_order]
  pizzas_order = og_pizzas_order[:]
  pizzas_order.sort(reverse=True)

  p = multiprocessing.Pool(processes = multiprocessing.cpu_count()-1)
  for comb_count in range(len(pizzas_order), 0, -1):
    for x in itertools.combinations(pizzas_order, comb_count):
      p.apply_async(first_step, args = (list(x)), callback = callback1)
  p.close()
  p.join()


if __name__ == "__main__":  # confirms that the code is under main function
  main()