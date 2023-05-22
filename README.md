# Ankid

An automatic flash card generator for [Anki](https://apps.ankiweb.net/) using [Free Dictionary API](https://dictionaryapi.dev/)

## Dependencies

Install the fallowing dependencies using pip

```shell
pip install requests genanki
```

## Usage

Run the script using python/python3

```shell
python3 ankid.py
```

Input words followed by a `carriage return`. Type `DONE` when you finished. The script then creates an Anki package file called `output.apkg`. Import this file using Anki app.

On a Unix-like machine, you can pipe text into the script using `cat` or `printf`

```shell
printf "hello\nworld\nDONE\n" | python3 ankid.py
```

Or write a `.txt` file

```
hello
world
DONE
```

Then

```shell
cat words.txt | python3 ankid.py
```

It is also possible to use the script with rlwrap to get a REPL-like experience

```shell
rlwrap python3 ankid.py
```

## Features

- auto formatting

- phonetics

- pronunciation

- synonyms

- examples
