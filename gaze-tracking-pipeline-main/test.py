from screeninfo import get_monitors

for m in get_monitors():
    print(m)
    if m.is_primary is True:
        print(m)