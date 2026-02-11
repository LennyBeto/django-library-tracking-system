import random
# rand_list = 
rand_list = [random.randint(1, 20) for _ in range(10)]
print (f"Random list: {rand_list}")

# list_comprehension_below_10 =
filtered_comprehension = [num for num in rand_list if num < 10]
print(f"Filtered (comprehension): {filtered_comprehension}")

# list_comprehension_below_10 =
filtered_filter = list(filter(lambda x: x < 10, rand_list))
print(f"Filtered (filter): {filtered_filter}")
