import os
import sys
import time
import codecs
import urllib2
import BeautifulSoup

# File and url names
ifn = "../data/boxofficemojo_titles.csv"
sfn = "../data/rottentomatoes_scores.csv"
baseurl = "http://www.rottentomatoes.com"
qbase = "{}/search/?search=".format(baseurl)

# Headers to allow us to scrape the Rotten Tomatoes site
user_agent = 'Mozilla/5.0 (Windows NT 6.1; rv:13.0) Gecko/20100101 Firefox/13.0'
headers = {'User-Agent' : user_agent }

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
    sfile.write("title,year,imov,rtscore,rtlink\n")

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

    # Search for the movie on Rotten Tomatoes
    qtitle = title.lower().replace(" ", "+")
    query = "{}{}".format(qbase, qtitle.encode('ascii', 'replace'))
    request = urllib2.Request(query, None , headers)
    response = urllib2.urlopen(request)
    qsoup = BeautifulSoup.BeautifulSoup(response.read())

    # This span will exist if the title turned up an exact match
    ss = qsoup.findAll("span", attrs={"itemprop":"ratingValue",
                                      "id":"all-critics-meter"})
    score = "NA"
    link = "NA"
    if len(ss) == 1 :
        score = int(ss[0].text)
        link = query

    else :

        # If there's no match, compile a list of the search results
        sattrs = {'class':'media_block bottom_divider clearfix'}
        sli = qsoup.findAll("li", attrs=sattrs)

        # Loop through the search results and use the first one with 
        #  a score that matches the correct year
        for elem in sli :
            if not elem.text[:1].isdigit() : continue
            yearlist = elem.findAll("span", attrs={'class':'movie_year'})
            if len(yearlist) != 1 : continue
            myear = int(yearlist[0].text.strip("()"))
            if myear != year : continue
            if elem.text[:3].isdigit() : score = int(elem.text[:3])
            elif elem.text[:2].isdigit() : score = int(elem.text[:2])
            else : score = int(elem.text[:1])
            slink = elem.findAll("a", attrs={'target':'_top'})
            link = baseurl + slink[0].get("href")
            break

        # If none of the search results exactly matched the year, use
        #  one that is only one year off
        if score == "NA" :
            for elem in sli :
                if not elem.text[:1].isdigit() : continue
                yearlist = elem.findAll("span", attrs={'class':'movie_year'})
                if len(yearlist) != 1 : continue
                myear = int(yearlist[0].text.strip("()"))
                if abs(myear - year) > 1 : continue
                if elem.text[:3].isdigit() : score = int(elem.text[:3])
                elif elem.text[:2].isdigit() : score = int(elem.text[:2])
                else : score = int(elem.text[:1])
                slink = elem.findAll("a", attrs={'target':'_top'})
                link = baseurl + slink[0].get("href")
                break

    # Write out the data if a valid result was found
    if score != "NA" :
        asctitle = title.encode('ascii', 'ignore')
        print '"{}",{},{},{},{}'.format(asctitle, year, imov, score, link)
        sfile.write('"{}",{},{},{},{}\n'.format(asctitle, year, imov,
                                                score, link))

    # Be kind to the rottentomatoes.com domain
    time.sleep(2)

sfile.close()
