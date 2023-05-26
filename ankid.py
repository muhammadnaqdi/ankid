import requests
import os
import random
import genanki
from multiprocessing import Process, Manager, Value
import time
from ctypes import c_char_p

manager = Manager()
phonetic_m = manager.Value(c_char_p, '')
media_files = manager.list()

model_id = 2038577668
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
                    print('** Error saving audio word: ' + word + ' **')
        tmp += '<br>'
        phc += 1
    phonetic_m.value = tmp
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

attempt = 1
print('** Enter a word (or DONE to terminate) **')
word = input('> ')
while word != 'DONE':
    url = 'https://api.dictionaryapi.dev/api/v2/entries/en/' + word
    try:
        resp = requests.get(url, allow_redirects = True)
    except:
        print('** Error connecting to the API attempt: ' + str(attempt) + '/3 word: ' + word + ' **')
        if attempt < 3:
            attempt += 1
            continue
        else:
            attempt = 1
            word = input('> ')
            continue
    attempt = 1
    data = resp.json()
    try:
        data[0]["word"]
    except:
        print('** Error finding word: ' + word + ' **')
        word = input('> ')
        continue
    ph_p = Process(target = phonetic_html, args = (data[0]['phonetics'], data[0]['word']))
    ph_p.start()
    ph_p.join(60)
    if ph_p.is_alive():
        print('** Error saving audio word: ' + word + ' **')
        ph_p.terminate()
        ph_p.join()
        word = input('> ')
        continue
    deck.add_note (
        genanki.Note(
            model = model,
            fields = [
                data[0]['word'],
                phonetic_m.value,
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
