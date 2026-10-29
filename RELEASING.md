# Releasing the NoRaRe web app

```shell
git clone --branch v1.1 --depth 1 https://github.com/concepticon/norare-cldf
git clone --branch v3.4.2 --depth 1 https://github.com/concepticon/concepticon-cldf
git clone https://github.com/concepticon/norare
cd norare
pip install -e .[test]
```

recreate the database
```shell
clld initdb development.ini --cldf ../norare-cldf/cldf/Wordlist-metadata.json
```

```shell
pytest
```

Store the tested requirements:
```shell
pip freeze > requirements.txt
```

Store a db dump:
```shell
pg_dump -xO norare > norare.sql
zip norare.sql.zip norare.sql
rm norare.sql
```

