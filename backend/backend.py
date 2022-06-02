import flask, sqlite3, random
from flask import request, jsonify
from flask_cors import CORS
from rake_nltk import Rake

r = Rake()

app = flask.Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'
temp_cardid = 0

@app.route('/')
def login():
   return "Welcome to BuildingBloCS 2022's Hackathon API!"

@app.route('/anki/decks')
def anki_decks():
   db = sqlite3.connect('backend.db')
   cursor = db.execute('SELECT * FROM DECKS')
   ls = []
   for rows in cursor.fetchall():
      ls.append({"deckid":rows[0],"deckname":rows[1]})
   return jsonify(ls)

@app.route('/anki/decks/edit', methods=["GET","POST","DELETE"])
def anki_decks_edit():
   if request.method == "DELETE":
      deckid = request.get_json()['deckid']
      db = sqlite3.connect('backend.db')
      db.execute('DELETE FROM DECKS WHERE DECKID = ?', (deckid,))
      db.execute('DELETE FROM CARDS WHERE DECKID = ?', (deckid,))
      db.commit()

   if request.method == "POST":
      deckname = request.get_json()['deckname']
      db = sqlite3.connect('backend.db')
      db.execute("INSERT INTO DECKS(DECKNAME) VALUES(?)", (deckname,))
      db.commit()
      
   db = sqlite3.connect('backend.db')
   cursor = db.execute('SELECT DECKID, DECKNAME FROM DECKS')
   returndata = []
   for rows in cursor.fetchall():
      returndata.append({'deckid':rows[0], 'deckname':rows[1]})

   return jsonify(returndata)

@app.route('/anki/decks/<deckid>', methods=["GET","POST"])
def anki_specific_deck(deckid):
   if request.method == "POST":
      db = sqlite3.connect('backend.db') 
      cardid, familiarity = request.get_json()['cardid'], request.get_json()['familiarity']
      db.execute('UPDATE CARDS SET FAMILIARITY = ? WHERE CARDID = ?', (familiarity, cardid))
      db.commit()
         
   db = sqlite3.connect('backend.db')
   deckname = db.execute('SELECT DECKNAME FROM DECKS WHERE DECKID = ?', (deckid,)).fetchone()[0]

   empty = True
   global temp_cardid

   while empty:
      choices = [0,0,0,0,0,0,0,1,1,2]
      difficulty = random.choice(choices)
      cards = db.execute('SELECT CARDID, QUESTION, ANSWER FROM CARDS WHERE DECKID = ? AND FAMILIARITY = ?', (deckid, difficulty)).fetchall()

      if cards != []:
         card = random.choice(cards) 
         if card[0] != temp_cardid:
            temp_cardid = card[0]
            empty = False

   card_info = {'cardid':card[0],'question':card[1], 'answer':card[2], 'familiarity':difficulty}
   return {'deckid':deckid, 'deckname':deckname ,'card':card_info}

@app.route('/anki/cards/edit/<int:deckid>', methods=["GET","POST","DELETE","PATCH"])
def edit_deck(deckid):
   db = sqlite3.connect('backend.db') 
   if request.method == "DELETE":
      print("delete request received")
      cardid = request.get_json()['cardid']
      db.execute('DELETE FROM CARDS WHERE CARDID = ?', (cardid,))
      db.commit() 

   if request.method == "POST":
      deckid, question, answer = request.get_json()['deckid'], request.get_json()['question'], request.get_json()['answer']
      db.execute('INSERT INTO CARDS(QUESTION, ANSWER, DECKID, FAMILIARITY) VALUES(?,?,?,0)', (question, answer, deckid))
      db.commit()

   if request.method == "PATCH":
      cardid, question, answer = request.get_json()['cardid'], request.get_json()['question'], request.get_json()['answer']
      db.execute('UPDATE CARDS SET QUESTION = ?, ANSWER = ? WHERE CARDID = ?', (question, answer, cardid))
      db.commit()
      print('changed value')

   deckname = db.execute('SELECT DECKNAME FROM DECKS WHERE DECKID = ?', (deckid,)).fetchone()[0]
   cursor = db.execute('SELECT * FROM CARDS WHERE DECKID = ?', (deckid,))
   cards = []

   for row in cursor:
      dic = {"cardid":row[0], "question":row[3], "answer":row[4]}
      cards.append(dic)

   return jsonify(cards)

@app.route('/anki/cards/generate/<int:deckid>', methods=["POST", "GET"])
def anki_cards_generate(deckid):
   if request.method == "POST":
      passage, num_keywords = request.get_json()['passage'], request.get_json()['keywords']
      passage_bold = passage
      r.extract_keywords_from_text(passage)
      keywordList= []
      rankedList= r.get_ranked_phrases_with_scores()

      for keyword in rankedList:
         keyword_updated= keyword[1].split()
         keyword_updated_string= " ".join(keyword_updated[:2])
         keywordList.append(keyword_updated_string)
         if(len(keywordList)>int(num_keywords)):
            break

      def get_(word):
         x = len(word)
         return '_'*x
      
      pre_qns = passage_bold.strip().split('.')

      for i in keywordList:
            passage = passage.replace(i, get_(i))
            
      und_qns = passage.strip().split('.')
      final_qns = []

      for i in range(len(pre_qns)):
            if '_' in und_qns[i]:
                  final_qns.append([und_qns[i],pre_qns[i]])
            else:
                  pass
               
      questions, answers = [], []

      for i in final_qns:
         questions.append(i[0])
         answers.append(i[1])

      db = sqlite3.connect('backend.db')
      for i in range(len(questions)):
         db.execute('INSERT INTO CARDS(QUESTION, ANSWER, DECKID, FAMILIARITY) VALUES(?,?,?,0)', (questions[i],answers[i],deckid))
         db.commit()

   return 'completed'

if __name__ == '__main__':
   app.run()
