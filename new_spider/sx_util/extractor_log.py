f = open("sx.txt", "rb")
contents = f.readlines()

sx_list = list()
for content in contents:
    content = str(content).replace("\r\n", "")

    # end_index = str(content).rfind("\"")
    # sx_list.append(content[33: end_index])

    index = content.find("url:")
    # print content[index+5:]
    sx_list.append(content[index + 37:])

# temp_list = ["aa"]
print sx_list