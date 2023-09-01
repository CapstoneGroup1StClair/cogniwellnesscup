from flask import Flask, render_template, request
from pymongo import MongoClient
from flask_mail import Mail, Message
from utils import MongoEncoder, DATABASE_URI, mail_settings
from utils import process_answer
import pandas as pd

client = MongoClient(DATABASE_URI)
db = client['Cogni4health']

app = Flask(__name__)
app.json_encoder = MongoEncoder
app.config.update(mail_settings)
mail = Mail(app)

@app.get('/')
def index():
    if (db.wellness.count_documents({}) > 0):
        sample_record = db.wellness.find_one({}, sort=[( '_id', -1 )])
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
    data = request.get_json()
    admin_emails = [user['email'] for user in db.Users.find()]
    columns_to_process = ['em1', 'em2', 'em3', 'em4', 'em5', 'em6', 'em7', 'em8', 'em9', 'em10','ph1', 'ph2', 'ph3', 'ph4', 'ph5', 'ph6', 'ph7', 'ph8', 'ph9', 'ph10','sp1', 'sp2', 'sp3', 'sp4', 'sp5', 'sp6', 'sp7', 'sp8', 'sp9', 'sp10','so1', 'so2', 'so3', 'so4', 'so5', 'so6', 'so7', 'so8', 'so9', 'so10','fi1', 'fi2', 'fi3', 'fi4', 'fi5', 'fi6', 'fi7', 'fi8', 'fi9', 'fi10','oc1', 'oc2', 'oc3', 'oc4', 'oc5', 'oc6', 'oc7', 'oc8', 'oc9', 'oc10','in1', 'in2', 'in3', 'in4', 'in5', 'in6', 'in7', 'in8', 'in9', 'in10','en1', 'en2', 'en3', 'en4', 'en5', 'en6', 'en7', 'en8', 'en9', 'en10']
    for item in data:
        for col in columns_to_process:
            if col in item:
                item[col] = float(item[col]) if item[col] != '' else 4.0
        emotional_sum = sum(item.get(f'em{i}', 4.0) for i in range(1, 11))
        occupational_sum = sum(item.get(f'oc{i}', 4.0) for i in range(1, 11))
        spiritual_sum = sum(item.get(f'sp{i}', 4.0) for i in range(1, 11))
        physical_sum = sum(item.get(f'ph{i}', 4.0) for i in range(1, 11))
        social_sum = sum(item.get(f'so{i}', 4.0) for i in range(1, 11))
        financial_sum = sum(item.get(f'fi{i}', 4.0) for i in range(1, 11))
        intellectual_sum = sum(item.get(f'in{i}', 4.0) for i in range(1, 11))
        environmental_sum = sum(item.get(f'en{i}', 4.0) for i in range(1, 11))
        dimensions = {'Emotional': emotional_sum,'Occupational': occupational_sum,'Spiritual': spiritual_sum,'Physical': physical_sum,'Social': social_sum,'Financial': financial_sum,'Intellectual': intellectual_sum,'Environmental': environmental_sum}
        item['dimension'] = min(dimensions, key=dimensions.get)
    db.wellness.insert_one(data)
    msg = Message('Wellness Cup assessment: New Submission Receieved!', recipients=admin_emails)
    msg.body = render_template('cognixrsummary.html', **data)
    msg.html = render_template('cognixrsummary.html', **data)
    mail.send(msg)
    if data.get('email') != None:
        msg.recipients = [data['email']]
        mail.send(msg)
    return {'success': True, 'data': data}

if __name__ == '__main__':
	app.run(debug=True)
