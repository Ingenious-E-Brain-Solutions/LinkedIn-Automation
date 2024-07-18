from flask import Flask, request, render_template, redirect, url_for, flash
from linkedin_api import Linkedin
from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.urandom(24)

# LinkedIn credentials
linkedin_username = os.getenv('LINKEDIN_USERNAME')
linkedin_password = os.getenv('LINKEDIN_PASSWORD')




# Initialize LinkedIn API with error handling
try:
    api = Linkedin(linkedin_username, linkedin_password)
except Exception as e:
    print(f"Error initializing LinkedIn API: {e}")
    api = None

REGION_MAPPING = {
    "india": "urn:li:fs_geo:102713980",
    "united states": "urn:li:fs_geo:103644278",
    "canada": "urn:li:fs_geo:101174742",
    "united kingdom": "urn:li:fs_geo:103137801",
    "australia": "urn:li:fs_geo:103228277",
    "germany": "urn:li:fs_geo:101282230",
    "france": "urn:li:fs_geo:105015875",
    "brazil": "urn:li:fs_geo:106057199",
    "netherlands": "urn:li:fs_geo:102890719",
    "italy": "urn:li:fs_geo:104108173",
    "spain": "urn:li:fs_geo:103448411",
    "mexico": "urn:li:fs_geo:106693272",
    "japan": "urn:li:fs_geo:111076699",
    "china": "urn:li:fs_geo:100476389",
    "russia": "urn:li:fs_geo:103296191",
}

INDUSTRY_MAPPING = {
    "consulting": "urn:li:fs_industry:96",
    "information technology": "urn:li:fs_industry:4",
    "financial services": "urn:li:fs_industry:43",
    "healthcare": "urn:li:fs_industry:7",
    "education": "urn:li:fs_industry:69",
    "manufacturing": "urn:li:fs_industry:62",
    "retail": "urn:li:fs_industry:68",
    "telecommunications": "urn:li:fs_industry:8",
    "media": "urn:li:fs_industry:12",
    "entertainment": "urn:li:fs_industry:14",
    "real estate": "urn:li:fs_industry:19",
    "construction": "urn:li:fs_industry:23",
    "non-profit": "urn:li:fs_industry:50",
    "government administration": "urn:li:fs_industry:47",
    "arts": "urn:li:fs_industry:31",
    "legal services": "urn:li:fs_industry:9",
    "hospitality": "urn:li:fs_industry:34",
    "energy": "urn:li:fs_industry:45",
    "transportation": "urn:li:fs_industry:11",
    "logistics": "urn:li:fs_industry:41",
    # Add more industries as needed
}


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search():
    if not api:
        flash("LinkedIn API is not initialized. Please check your credentials.", "error")
        return redirect(url_for('index'))

    business_idea = request.form['business_idea']
    country = request.form['country'].lower()
    industry = request.form['industry'].lower()

    region_urn = REGION_MAPPING.get(country)
    industry_urn = INDUSTRY_MAPPING.get(industry)

   

    try:
        results = api.search_people(
            keywords=business_idea,
            regions=[region_urn],
            industries=[industry_urn],
            limit=10
        )
    except Exception as e:
        flash(f"Error occurred during LinkedIn search: {e}", "error")
        return redirect(url_for('index'))

    # Process the results to ensure all required fields are present
    processed_results = []
    for user in results:
        processed_user = {
            'urn_id': user.get('urn_id', 'N/A'),
            'name': user.get('name', 'N/A'),
            'jobtitle': user.get('jobtitle', 'N/A'),
            'location': user.get('location', 'N/A'),
            'distance': user.get('distance', 'N/A')
        }
        processed_results.append(processed_user)

    return render_template('results.html', users=processed_results)

if __name__ == '__main__':
    app.run(debug=True)