import re
from urllib import quote
callback = lambda pat: "<"+pat.group()[1:-1].replace(" ", "%20")+">"

f = open("linkedmdb-latest-dump.nt",'r')

result = re.sub(r'<http(|s):\/\/+[^>]+>',callback, f.read())


file = open('linkedmdb-latest-dump-result.nt', 'w')
file.write(result)
file.close()
print("compelte")
