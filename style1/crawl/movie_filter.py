from unidecode import unidecode
import re
movies=set()
with open("movie_name","r") as f:
    for line in f:
        movies.add(line)
with open("movie_name2","w") as f:
    pattern=re.compile("[^\w\d]+")
    for m in movies:
        text=pattern.sub("",text.lower().replace(" ","_").replace("&","and"))
        text=unidecode(text)
        f.write(unidecode(m))