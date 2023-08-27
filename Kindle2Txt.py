import sqlite3
from datetime import datetime
from pathlib import Path
import os
import sys

config_file = 'Kindle2Txt.config'

config = {}

def config_load():
  with open(config_file, 'r') as f:
    for i, line in enumerate(f):
      s = line.strip().split(":", 1)
      match s[0]:
        case "database_path":
          config["database_path"] = s[1]
        case "output_path":
          config["output_path"] = s[1]
        case "lang":
          config["lang"] = s[1]
        case "last_timestamp":
          config["last_timestamp"] = int(s[1])

def config_save():
  with open(config_file, 'w') as f:
    f.write(f'database_path:{config["database_path"]}\n')
    f.write(f'output_path:{config["output_path"]}\n')
    f.write(f'lang:{config["lang"]}\n')
    f.write(f'last_timestamp:{config["last_timestamp"]}\n')

def sort_by_key(list):
    return list['pos']

def save_sentences(book_data):
  now = datetime.now()
  filename = f'KindleVocab_{now.strftime("%Y%m%d-%H%M%S")}.txt'
  filename_path = os.path.join(config['output_path'], filename)
  with open(filename_path, 'w', encoding="utf-8") as f:
    for title in book_data:
      if (len(book_data[title]) == 0):
        continue
      f.write(f'* {title}\n')
      for s in book_data[title]:
        unknowns = '; '.join(s["word"])
        output = f'{s["pos"]}. \t{s["sentence"].strip()} \t[{unknowns}]'
        f.write(f'{output}\n')
      f.write('\n\n')
  print(f"{filename} saved.")


def get_book_data():
  conn = sqlite3.connect(config["database_path"])
  c = conn.cursor()

  # Get all titles first
  c.execute('SELECT id, title, lang FROM BOOK_INFO')
  id_titles = c.fetchall()

  skipped = 0
  max_timestamp = 0

  book_data = {}

  # loop through each title
  for ident, title, lang in id_titles:
    if config["lang"] != "all":
      if lang.lower() != config["lang"].lower():
        continue
    

    sentence_info = {}

    query = '''
            SELECT word_key, pos, usage, timestamp
            FROM LOOKUPS l1
            WHERE book_key=?
    '''
    c.execute(query,  (ident, ))
    results = c.fetchall()
    for result in results:
      word, pos, usage, timestamp = result

      word = word.split(':')[1]

      if timestamp <= config["last_timestamp"]:
        skipped += 1
        continue

      if not (not word or word == '' or word == '\n' or word == '\r' or word == '\t'):
        if usage in sentence_info:
          if word in sentence_info[usage]["word"]:
            continue
          sentence_info[usage]["word"].append(word)
          sentence_info[usage]["pos"] = min(sentence_info[usage]["pos"], pos)
        else:
          cur_sentence = {
            'word' : [word],
            'pos': pos,
            'sentence': usage,
          }
          sentence_info[usage] = cur_sentence
      max_timestamp = max(max_timestamp, timestamp)

    sorted_sentence_info = sorted(sentence_info.values(), key=sort_by_key)
    book_data[title] = sorted_sentence_info
    continue

  config["last_timestamp"] = max_timestamp
  return book_data, skipped

if __name__ == "__main__":

  if Path(config_file).is_file():
    config_load()
  else:
    if len(sys.argv) == 1:
      print("Kindle2Txt.py ([vocab_db_path]) (lang) (output_folder)")
      exit()

  if len(sys.argv) >= 2:
    config['database_path'] = sys.argv[1]
    #check db file exists here

  if len(sys.argv) >= 3:
    config['lang'] = sys.argv[2]

  if len(sys.argv) >= 4:
    config['output_path'] = sys.argv[3]

  if 'lang' not in config:
    config['lang'] = "all"

  if 'output_path' not in config:
    config['output_path'] = "."

  if 'last_timestamp' not in config:
    config['last_timestamp'] = 0

  book_data, skipped = get_book_data()

  sentence_count = sum(len(v) for v in book_data.values())
  print(f'{sentence_count} Sentences in {len(book_data)} Books. {skipped} skipped sentences.')

  save_sentences(book_data)

  if sentence_count > 0:
    config_save()
    pass
