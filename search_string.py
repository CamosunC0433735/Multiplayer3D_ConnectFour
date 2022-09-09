search_string = input('Enter your search string:')
search_interval = input('Enter the interval:')
search_interval = int(search_interval)

if search_interval > 0 and search_interval < len(search_string):
  count = 1
  for char in search_string:
    if count % search_interval == 0:
      print(char)
    count += 1
else:
  print('invalid interval')
