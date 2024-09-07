import json

with open("sec.conf", "r") as f:
    lines = f.readlines()
    user_list = []
    passwd_list = []
    for line in lines:
        jsonobject = json.loads(line)

        user_list.append([jsonobject["Username"]])
        passwd_list.append([jsonobject["Password"]])
    print(user_list, passwd_list)