search_string = input('Enter your search string:')
search_interval = input('Enter the interval:')
search_interval = int(search_interval)
if type(search_interval) is int:
  if search_interval > 0:
    print(search_string[::search_interval])
