with open("requirements.txt", "w") as f:
    f.write("beautifulsoup4\nrequests")
try:
    from bs4 import BeautifulSoup
    import requests
except ImportError:
    x = input("Package yang dibutuhkan tidak ditemukan, install?").lower() == "y"
    if x:
        from os import name
        from subprocess import call
        if name == "nt":
            call("py -m pip install -r requirements.txt", shell=True)
        else:
            call("pip3 install -r requirements.txt")
        from bs4 import BeautifulSoup
        import requests
    else:
        exit(0)

from sys import argv

if len(argv) < 2:
    raise Exception("Parameter kurang, cara menggunakan: python|py {}.py [URL]".format(argv[0]))


sess = requests.Session()
sess.verify = False
data = sess.get(argv[1])
soup = BeautifulSoup(data.content, "html.parser")

soal_texts = []
for i in soup.find_all("text"):
    soal_texts.append(i.get_text())
with open("output.txt", "w") as f:
    for i in soal_texts:
        f.write("%s\n" % (i))