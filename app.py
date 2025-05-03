from flask import Flask, render_template, request, jsonify, session
from utils import generate_mcqs
import os
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Required for session management

# List of programming languages
LANGUAGES = ["Python", "Java", "C++", "JavaScript", "Go", "Rust", "Swift", "Kotlin", "PHP"]

@app.route('/')
def index():
    return render_template('index.html', languages=LANGUAGES)

@app.route('/generate_quiz', methods=['POST'])
def generate_quiz():
    language = request.form.get('language')
    if not language:
        return jsonify({'error': 'Language is required'}), 400
    
    try:
        mcqs = generate_mcqs(language)
        session['mcqs'] = mcqs
        session['user_answers'] = {}
        session['quiz_submitted'] = False
        return jsonify({'success': True, 'mcqs': mcqs})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/submit_quiz', methods=['POST'])
def submit_quiz():
    if 'mcqs' not in session:
        return jsonify({'error': 'No quiz available'}), 400
    
    user_answers = request.form['answers']
    user_answers = json.loads(user_answers)
    if not user_answers:
        return jsonify({'error': 'No answers provided'}), 400
    
    # Process answers and calculate score
    correct_count = 0
    results = []
    
    for idx, mcq in enumerate(session['mcqs']):
        user_answer = user_answers.get(str(idx))
        correct_answer = mcq['correct_answer']
        
        is_correct = user_answer == correct_answer
        if is_correct:
            correct_count += 1
            
        results.append({
            'question': mcq['question'],
            'user_answer': user_answer,
            'correct_answer': correct_answer,
            'is_correct': is_correct
        })
    
    total_questions = len(session['mcqs'])
    score = (correct_count / total_questions) * 100
    
    session['quiz_submitted'] = True
    session['results'] = results
    session['score'] = score
    
    return jsonify({
        'success': True,
        'results': results,
        'score': score,
        'correct_count': correct_count,
        'total_questions': total_questions
    })

if __name__ == '__main__':
    app.run(debug=True) 