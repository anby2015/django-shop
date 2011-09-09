import httplib

url = 'http://ia.media-imdb.com/images/M/'

f = open('filmlist', 'r')
ff = open('filmdesc', 'w')
con = httplib.HTTPConnection('www.imdb.com')

def catch_data(data, begin, end):
    d = data[data.index(begin) + len(begin):]
    return d[:d.index(end)].strip()

for l in f:
    con.request('GET', l.split('||||')[-1].strip())
    data = con.getresponse().read()
    
    get_d = lambda a, b: catch_data(data, a, b)
    
    s = "%s||||%s%s||||%s\n" % (
        get_d('<p itemprop="description">', '</p>'),
        url, get_d('<img src="' + url, '"'),
        get_d('<a href="/genre/', '"'),
    )
    
    ff.write(s)
    print s    
