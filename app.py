from flask import Flask, jsonify, request, render_template, redirect, url_for, flash, session
from linkedin_api import Linkedin
from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.urandom(24)

# LinkedIn credentials (consider using environment variables or a more secure method)
LINKEDIN_USERNAME = os.getenv('LINKEDIN_USERNAME')
LINKEDIN_PASSWORD = os.getenv('LINKEDIN_PASSWORD')

@app.route('/')
def index():
    return render_template('index1.html')
@app.route('/index')
def index1():
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search():
    data = request.get_json()
    business_idea = data.get('business_idea')
    countries = data.get('country')
    industry = data.get('industry')

    api = Linkedin(LINKEDIN_USERNAME, LINKEDIN_PASSWORD)
    
    users = api.search_people(business_idea, limit=1, industries=industry, regions=countries, network_depths=['F', 'O'], include_private_profiles=True)

    client = OpenAI()
    user_message_pairs = []

    for user in users:
        user_name = user['name']
        response = client.completions.create(
            model="gpt-3.5-turbo-instruct",
            prompt=f"Generate a message for a potential LinkedIn connection. My name is Ayush Kumar. "
                   f"Address the user by their first name {user_name} and mention the details of business idea '{business_idea}'.\n\n",
            max_tokens=400
        )
        message = response.choices[0].text.strip()
        user_message_pairs.append((user, message))

    session['business_idea'] = business_idea
    session['users'] = users
    session['user_message_pairs'] = user_message_pairs

    return jsonify(status="success")

@app.route('/results')
def results():
    business_idea = session.get('business_idea')
    users = session.get('users')
    user_message_pairs = session.get('user_message_pairs')

    if not all([business_idea, users, user_message_pairs]):
        return redirect(url_for('index'))

    return render_template('results.html', business_idea=business_idea, users=users, user_message_pairs=user_message_pairs)

@app.route('/send_messages', methods=['POST'])
def send_messages():
    try:
        user_ids = request.form.getlist('user_ids')
        messages = request.form.getlist('messages')
        api = Linkedin(LINKEDIN_USERNAME, LINKEDIN_PASSWORD)

        for user_id, message in zip(user_ids, messages):
            api.send_message(recipients=[user_id], message_body=message)

        flash('Messages sent successfully.', 'success')
        return jsonify(status="success", message="Messages sent successfully."), 200
    except Exception as e:
        flash(f"Error: {str(e)}", 'error')
        return redirect(url_for('index'))

@app.route('/send_connection_requests', methods=['POST'])
def send_connection_requests():
    try:
        user_ids = request.form.getlist('user_ids')
        api = Linkedin(LINKEDIN_USERNAME, LINKEDIN_PASSWORD)

        for user_id in user_ids:
            api.add_connection(user_id)

        flash('Connection requests sent successfully.', 'success')
        return redirect(url_for('index'))
    except Exception as e:
        flash(f"Error: {str(e)}", 'error')
        return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
