import random
# rand_list = 
rand_list = [random.randint(1,100) for _ in range (10)]
print (f"Random list: {rand_list}")

# list_comprehension_below_10 =
list_comprehension_below_10 = [x for x in rand_list if x < 10]
print (f "Numbers below 10: {list comprehension below 10}")
# list_comprehension_below_10 =