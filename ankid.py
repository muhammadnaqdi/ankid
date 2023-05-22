import requests
import os
import random
import genanki

model_id = random.randrange(1 << 30, 1 << 31)
model = genanki.Model(
    model_id,
    'Free Dictionary',

    fields = [
        {'name': 'Word'},
        {'name': 'Phonetic'},
        {'name': "Meanings"}
    ],

    templates = [
        {
            'name': 'Dictionary Entry',
            'qfmt': '<b>{{Word}}</b>',
            'afmt': '{{FrontSide}}<hr>{{Phonetic}}<br>{{Meanings}}'
        },
    ]
)

deck_id = random.randrange(1 << 30, 1 << 31)
deck = genanki.Deck(
    deck_id,
    'Ankid Words'
)

package = genanki.Package(deck)

media_files = []

if not os.path.isdir('media'):
    try:
        os.mkdir('media')
    except:
        print('** Error creating media directory **')

def phonetic_html(phonetics, word):
    tmp = ''
    phc = 0;
    for ph in phonetics:
        if 'text' in ph.keys():
            if ph["text"]:
                tmp += '<i>' + ph["text"] +'</i>'
        if 'audio' in ph.keys():
            if ph["audio"]:
                fname =  word + str(phc) + '.mp3'
                path = os.path.join('media', fname)
                try:
                    aud = requests.get(ph["audio"], allow_redirects = True)
                    fo = open(path, 'wb')
                    fo.write(aud.content)
                    fo.close()
                    media_files.append(path)
                    tmp += '[sound:' + fname + ']'
                except:
                    print('** Error saving audio **')
        tmp += '<br>'
        phc += 1
    return tmp

def meaning_html(meanings):
    tmp = ''
    for me in meanings:
        if 'partOfSpeech' in me.keys():
            if me['partOfSpeech']:
                tmp += '<b>' + me['partOfSpeech'] + '</b>' + '<br>'
        if 'synonyms' in me.keys():
            if me['synonyms']:
                tmp += '<i>(synonyms: '
                first = True
                for sy in me['synonyms']:
                    if sy:
                        if first:
                            tmp += sy
                            first = False
                        else:
                            tmp += ', ' + sy
                tmp += ')</i><br>'
        tmp += '<br>'
        if 'definitions' in me:
            for de in me['definitions']:
                if 'definition' in de.keys():
                    if de["definition"]:
                        tmp += de["definition"]
                        tmp += '<br>'
                if 'synonyms' in de.keys():
                    if de['synonyms']:
                        tmp += '<i>(synonyms: '
                        first = True
                        for sy in de['synonyms']:
                            if sy:
                                if first:
                                    tmp += sy
                                    first = False
                                else:
                                    tmp += ', ' + sy
                        tmp += ')</i><br>'
                if 'example' in de.keys():
                    if de["example"]:
                        tmp += '• ' + de["example"] + '<br>'
                tmp += '<br>'
        tmp += '<br>'
    return tmp

print('** Enter a word (or DONE to terminate) **')
word = input('> ')
while word != 'DONE':
    url = 'https://api.dictionaryapi.dev/api/v2/entries/en/' + word
    try:
        resp = requests.get(url, allow_redirects = True)
    except:
        print('** Error connecting to the API **')
        word = input('> ')
        continue
    data = resp.json()
    try:
        data[0]["word"]
    except:
        print('** Error finding word: ' + word + ' **')
        word = input('> ')
        continue
    deck.add_note (
        genanki.Note(
            model = model,
            fields = [
                data[0]['word'],
                phonetic_html(data[0]['phonetics'], data[0]['word']),
                meaning_html(data[0]['meanings'])
            ]       
        )
    )
    word = input('> ')
    
package.media_files = media_files
try:
    package.write_to_file('output.apkg')
    print('** Package created **')
except:
    print('** Error creating package **')
