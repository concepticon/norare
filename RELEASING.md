# Releasing the NoRaRe web app

- recreate the database
  ```shell
  clld initdb development.ini --cldf ../norare-cldf/cldf/Wordlist-metadata.json
  ```
- recreate the WordCloud
  ```shell
  cldfbench norare.wordcloud -o norare/static/wordcloud.png
  ```
