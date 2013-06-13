import os
import sys
import json
import time
import codecs
import BeautifulSoup
from urllib2 import urlopen

# File and url names
ifn = "../data/boxofficemojo_titles.csv"
sfn = "../data/metacritic_scores.csv"
baseurl = "http://www.metacritic.com"
qbase = "{}/search/movie".format(baseurl)

# If the output file already exists, pick up the scraping on the next movie
sfile = None
resume = None
if os.path.exists(sfn) :
    # Read the last movie scraped
    lastline = codecs.open(sfn, "r", "utf-8", "replace").readlines()[-1]
    sline = lastline.strip().split(',')

    # If the title has a comma, recombine parts until it is the first entry
    while len(sline) > 5 :
        sline[0] = sline[0] + sline[1]
        del sline[1]

    # Set where to resume and open the output file to append
    resume = (int(sline[1]), int(sline[2]))
    sfile = codecs.open(sfn, "a", "utf-8", "replace")

else :
    
    # Open the output file
    sfile = codecs.open(sfn, "w", "utf-8", "replace")
    sfile.write("title,year,imov,mcscore,mclink\n")

# Loop over all the input movie titles
for i, line in enumerate(codecs.open(ifn, "r", "utf-8", "replace")) :

    # Extract the movie title list information
    if i == 0 : continue
    sline = line.strip().split(',')

    # If the title has a comma, recombine parts until it is the first entry
    while len(sline) > 3 :
        sline[0] = sline[0] + sline[1]
        del sline[1]
    title = sline[0].strip('"')
    year = int(sline[1])
    imov = int(sline[2])

    # Move on if this title has already been done
    if resume :
        if year < resume[0] : continue
        elif year == resume[0] and imov <= resume[1] : continue

    # Search for the movie on metacritic
    qtitle = title.lower().replace(' ', '+').replace('/','')
    query = "{}/{}/results".format(qbase, qtitle.encode('ascii', 'replace'))
    qsoup = BeautifulSoup.BeautifulSoup(urlopen(query).read())

    # Extract the important information from the search result
    sdiv = qsoup.findAll("div", attrs={"class":"score_wrap"})
    if len(sdiv) == 0 : continue
    score = int(sdiv[0].contents[3].text)
    link = baseurl + qsoup.findAll("h3")[0].contents[0].get("href")
    ylist = qsoup.findAll("li", attrs={"class":"stat release_date"})[0]
    ryear = int(ylist.contents[3].text.split()[2])
    if ryear != year : continue

    # Write out to the screen and output file
    print '"{}",{},{},{},{}'.format(title, year, imov, score, link)
    sfile.write('"{}",{},{},{},{}\n'.format(title, year, imov, score, link))

    # Be kind to the metacritic.com domain
    time.sleep(2)

sfile.close()
