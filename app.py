from flask import Flask, render_template, request, jsonify, session
from flask_sqlalchemy import SQLAlchemy
import random

app = Flask(__name__)
app.secret_key = 'supersecretkey'

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    score = db.Column(db.Integer, default=0)

    def __repr__(self):
        return f"User('{self.username}', '{self.score}')"

def create_db():
    with app.app_context():
        db.create_all()


# Example questions with answers and data
questions = [
    {"text": "Who has more followers on Instagram?", "options": ["Obama", "Trump"], "answer": "Obama", "data": {"Obama": "130M", "Trump": "90M"}},
    # {"text": "Which country has a higher population?", "options": ["North Korea", "Finland"], "answer": "North Korea", "data": {"North Korea": "25M", "Finland": "5.5M"}},
    # {"text": "Which animal is heavier?", "options": ["Elephant", "Blue Whale"], "answer": "Blue Whale", "data": {"Elephant": "14,000 lbs", "Blue Whale": "200,000 lbs"}},
    # {"text": "Which planet is larger by surface area?", "options": ["Earth", "Mars"], "answer": "Earth", "data": {"Earth": "12,742 km", "Mars": "6,779 km"}},
    # {"text": "Which animal lives longer?", "options": ["Dog", "Parrot"], "answer": "Parrot", "data": {"Dog": "10-13 years", "Parrot": "50-100 years"}},
    # {"text": "Which state has a higher population?", "options": ["California", "Texas"], "answer": "California", "data": {"California": "39.5M", "Texas": "29M"}},
    # {"text": "Which statue is taller?", "options": ["Statue of Liberty", "Christ the Redeemer"], "answer": "Statue of Liberty", "data": {"Statue of Liberty": "151 ft", "Christ the Redeemer": "98 ft"}},
    # {"text": "Which has more monthly Spotify listeners?", "options": ["Drake", "Ed Sheeran"], "answer": "Drake", "data": {"Drake": "65M", "Ed Sheeran": "60M"}},
    # {"text": "Which celebrity is worth more?", "options": ["Elon Musk", "Jeff Bezos"], "answer": "Elon Musk", "data": {"Elon Musk": "$300B", "Jeff Bezos": "$190B"}},
    # {"text": "Which country has a larger area?", "options": ["USA", "Canada"], "answer": "Canada", "data": {"USA": "9.8M km²", "Canada": "9.9M km²"}},
    # {"text": "Which element has a higher atomic number?", "options": ["Hydrogen", "Helium"], "answer": "Helium", "data": {"Hydrogen": "1", "Helium": "2"}},
    # {"text": "Which ocean is deeper?", "options": ["Atlantic", "Pacific"], "answer": "Pacific", "data": {"Atlantic": "8,376 m", "Pacific": "10,984 m"}},
    {"text": "Which planet is closer to the sun?", "options": ["Venus", "Mars"], "answer": "Venus", "data": {"Venus": "0.72 AU", "Mars": "1.52 AU"}}

]

@app.route('/')
def index():
    if 'questions_answered' not in session:
        session['questions_answered'] = []
    if 'streak' not in session:
        session['streak'] = 0 
    if 'score' not in session:
        session['score'] = 0

    remaining_questions = [q for i, q in enumerate(questions) if i not in session['questions_answered']]
    if not remaining_questions:
        return render_template('game_over.html', streak=session['streak'], score=session['score'])

    random_index = random.choice(range(len(remaining_questions)))
    question = remaining_questions[random_index]
    session['questions_answered'].append(questions.index(question))

    session.modified = True  # Ensure the session knows it has been modified
    current_streak = session.get('streak', 0)  # Get current streak from session
    final_score = session.get('score', 0) 
    return render_template('index.html', question=question, current_streak=current_streak, score=final_score)

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    new_user = User(username=username)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"status": "success"})

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    user = User.query.filter_by(username=username).first()
    if user:
        session['user_id'] = user.id
        return jsonify({"status": "success"})
    else:
        return jsonify({"status": "failure"})

@app.route('/profile')
def profile():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"status": "not logged in"})

    user = User.query.get(user_id)
    if user:
        return jsonify({"username": user.username, "score": user.score})

@app.route('/update_score', methods=['POST'])
def update_score():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"status": "not logged in"})

    user = User.query.get(user_id)
    data = request.get_json()
    score_to_add = data.get('score_to_add', 0)

    if user:
        user.score += score_to_add
        db.session.commit()
        return jsonify({"status": "success"})

@app.route('/login_page')
def login_page():
    return render_template('login.html')

@app.route('/reset_streak', methods=['POST'])
def reset_streak():
    session['streak'] = 0
    return jsonify({"status": "success"})

@app.route('/reset', methods=['POST'])
def reset_game():
    session.pop('questions_answered', None)
    session['streak'] = 0 
    session['score'] = 0
    return jsonify({"status": "success"})

@app.route('/check', methods=['POST'])
def check_answer():
    user_answer = request.json['answer']
    question_text = request.json['question']
    question = next(q for q in questions if q['text'] == question_text)
    user_score = request.json.get('score', 0) 

    is_correct = user_answer == question['answer']
    if is_correct:
        session['streak'] += 1
        session['score'] = user_score 
    else:
        session['streak'] = 0
    return jsonify({
        "correct": is_correct,
        "data": question['data'],
        "streak": session['streak'],
        "score": session['score']
    })

if __name__ == '__main__':
    app.run(debug=True)
    create_db()