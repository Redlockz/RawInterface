import json

with open("sec.conf", "r") as f:
    lines = f.readlines()
    for line in lines:
        json = json.loads(line)
        # print(json.key("Username"))
        user_list = [json["Username"]]
        passwd_list = [json["Password"]]
        print(user_list, passwd_list)