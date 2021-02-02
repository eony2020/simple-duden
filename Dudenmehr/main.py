import requests
from bs4 import BeautifulSoup
from flask import Flask, render_template, request, redirect, send_file

headers = {
    'Accept-Encoding': 'gzip, deflate, sdch',
    'Accept-Language': 'en-US,en;q=0.8',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Cache-Control': 'max-age=0',
    'Connection': 'keep-alive',
}

app = Flask("Scrapper",
	template_folder='templates',
	static_folder='static'
)

words=[]

@app.route("/")
def home():
  return render_template("home.html", words=words)

@app.route("/error")
def error():
  return redirect("/")

@app.route("/search")
def search():
  word = request.args.get('word')
  if word not in words:
    #words.append(word)
    words.insert(0, word) 
  print(words)
  word_url = f"https://www.duden.de/rechtschreibung/{word}"
  more_url = f"https://www.duden.de/suchen/dudenonline/{word}"
  try: 
    result_more = requests.get(more_url, headers=headers)
    soup_more = BeautifulSoup(result_more.text, "html.parser")
    more_results = soup_more.find("div", {"class": "paragraph"}).find("p").text
    not_exist = "Leider gibt es für Ihre Suchanfrage im"
    if not_exist in more_results:
      return render_template(
          "error.html", word=word, words=words
          )      
  except:
    try:
      result_word = requests.get(word_url, headers=headers)
      soup_word = BeautifulSoup(result_word.text, "html.parser")
      word_results = soup_word.find("div", {"class": "paragraph"}).find("h2").text
      not_found = "Fehler 404 – Seite nicht gefunden"
      if not_found in word_results:
        multiple_results = soup_more.find_all("a", {"class":"vignette__label"})
        keywords_url = []
        #keywords = []
        for key in multiple_results:
          keyword_url = key["href"].replace("/rechtschreibung/", "")            #keyword = key["href"].replace("/rechtschreibung/", "").replace("_", " ")
          #keywords.append(keyword)
          keywords_url.append(keyword_url)
        return render_template(
              "multiple.html", word=word, words=words, keyword_url=keyword_url, keywords_url=keywords_url
              ) 
    except:
      texts = []
      try:
        bedeutung = soup_word.find("div", {"id": "bedeutung"})
        bedeutung = bedeutung.find("p")
        text = bedeutung.text
        print(text)
        return render_template(
              "single.html", word=word, text=text, words=words
              )
      except:
        try:
          bedeutungen = soup_word.find("div", {"id": "bedeutungen"})
          list_bedeutung = bedeutungen.find_all("div", {"class": "enumeration__text"})
          for text in list_bedeutung:
            text = text.text
            texts.append(text)
          return render_template(
              "search.html", word=word, text=text,texts=texts, words=words
              )
        except:
          return render_template(
          "error.html", word=word, words=words
          )

      

@app.route("/multiple")
def multiple():
  return redirect("/")

@app.route("/single")
def single():
  return redirect("/")

app.run(host="0.0.0.0") 
