
ids = ""
with open("ids.txt", "rb") as f:
    list = f.readlines()
    for one in list:
        ids = ids.strip() + "," + one
    print ids