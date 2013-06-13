import time
import codecs
import urllib2
import BeautifulSoup

# Output file of movie titles
ofn = "../data/boxofficemojo_titles.csv"
ofile = codecs.open(ofn, "w", "utf-8", "replace")
ofile.write("Title,Year,Number\n")

# Attributes that will identify the table of movie names
tattrs = {'border':'0', 'cellspacing':'1',
          'cellpadding':'5', 'bgcolor':'#ffffff'}

baseurl = ("http://www.boxofficemojo.com/yearly/chart/" +
           "?view=releasedate&view2=domestic&p=.htm")

# Gather the top 300 grossing movies from the last 15 years
for year in range(1998, 2013) :
    for page in [1, 2, 3] :

        # Read the site data
        url = "{}&yr={}&page={}".format(baseurl, year, page)
        html = urllib2.urlopen(url).read()
        soup = BeautifulSoup.BeautifulSoup(html)

        # Identify the table of movie names
        tlist = soup.findAll("table", attrs=tattrs)
        if len(tlist) != 1 :
            print "Unexpected number of tables on {} page {}".format(year, page)
            continue
        
        # Write each movie to the output csv file
        for i, row in enumerate(tlist[0].contents) :
            if i == 0 or i > 100 : continue
            imov = i + (page - 1) * 100
            print year, imov, row.contents[1].text.encode('utf', 'replace')
            ofile.write(u'"{}",{},{}\n'.format(row.contents[1].text,
                                               year, imov))

        # Be kind to the boxofficemojo.com domain
        time.sleep(2)

ofile.close()
