from flask import Flask, render_template, request
from pymongo import MongoClient
from flask_mail import Mail, Message
from utils import MongoEncoder, DATABASE_URI, mail_settings
from utils import process_answer

client = MongoClient(DATABASE_URI)
db = client['Cogni4health']

app = Flask(__name__)
app.json_encoder = MongoEncoder
app.config.update(mail_settings)
mail = Mail(app)

@app.get('/')
def index():
    if (db.Youth.count_documents({}) > 0):
        sample_record = db.Youth.find_one({}, sort=[( '_id', -1 )])
        admin_emails = [user['email'] for user in db.Users.find()]
        msg = Message('Health and Wellness Survey: New Submission Receieved!', recipients=admin_emails)
        msg.body = render_template('cognixrsummary.html', **sample_record)
        msg.html = render_template('cognixrsummary.html', **sample_record)
        mail.send(msg)
        return render_template('cognixrsummary.html', **sample_record)
    else:
        return ('Test failed')
    

@app.post('/')
def get_form_submission():
    severity = 'GREEN'
    recommendation = 'Self-guided program or workshops'
    pickle_in = open("Youth.pk1", "rb")
    rf = pickle.load(pickle_in)
    data = request.get_json()
    admin_emails = [user['email'] for user in db.Users.find()]
    model_data = data[['upset', 'dizzy', 'enjoy', 'breathing', 'hated', 'reacting', 'shaky', 'stressing', 'terrified', 'nothing', 'irritated', 'relax', 'feeling', 'annoyed', 'panic', 'myself', 'good', 'easily annoyed','heart', 'scared', 'terrible']]
    sev = rf.predict(model_data)    
    total_score = process_answer(data)
    if sev == 3:
        severity = 'RED'
        recommendation = 'Counselling with therapist with specialized therapy & self-guided if needed'
    elif sev == 2:
        severity = 'AMBER'
        recommendation = 'Counseling therapist and self-guided material'
    data['recommendation'] = recommendation
    data['severity'] = severity
    data['score'] = total_score
    #data['severity_breakdown'] = breakdown
    db.Youth.insert_one(data)
    msg = Message('Health and Wellness Survey: New Submission Receieved!', recipients=admin_emails)
    msg.body = render_template('cognixrsummary.html', **data)
    msg.html = render_template('cognixrsummary.html', **data)
    mail.send(msg)
    if data.get('Email') != None:
        msg.recipients = [data['Email']]
        mail.send(msg)
    return {'success': True, 'data': data}

if __name__ == '__main__':
	app.run(debug=True)
