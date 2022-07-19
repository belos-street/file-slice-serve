import os

file_list = os.listdir('./file/2136a5664194bd9ebb40c6c9edf4a14e')
print(list(filter(lambda name: len(name.split('.')) > 1, file_list)))

my_list = [1, 2, 3, 4, 5]
print(6 in my_list)
