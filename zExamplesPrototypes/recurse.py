def recurse(level):
    print(f"recurse executed with arg: {level}")
    if level:
        recurse(level-1)
    return

def not_called():
    print('This function is never called.')
