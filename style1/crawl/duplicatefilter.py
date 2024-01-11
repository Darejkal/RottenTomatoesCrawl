lineset=set()
with open("movie_list_enriched","r") as f:
    for line in f:
        if line in lineset:
            continue
        lineset.add(line)
        with open("movie_list_enriched_filtered","a") as of:
            of.write(line)