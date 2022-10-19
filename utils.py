import sys
import os
file_contents={}

for file_name in os.listdir("./en_text"):
    with open("./en_text/"+file_name, "r", encoding="utf-8") as f:
        lines = f.readlines()
        f.close()
    pi_string = ""
    for line in lines:
        pi_string += line.rstrip()
    file_contents[file_name]=pi_string
with open("./data/en_articles.train","w",encoding="utf-8") as f:
    for k,v in file_contents.items():
        f.write(str(k)+" "+str(v)+"\n")
    f.close()
