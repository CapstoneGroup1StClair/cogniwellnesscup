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
    l = ['em1', 'em2', 'em3', 'em4', 'em5', 'em6', 'em7', 'em8', 'em9', 'em10', 'ph1', 'ph2', 'ph3', 'ph4', 'ph5', 'ph6', 'ph7', 'ph8', 'ph9', 'ph10', 'sp1', 'sp2', 'sp3', 'sp4', 'sp5', 'sp6', 'sp7', 'sp8', 'sp9', 'sp10','so1', 'so2', 'so3', 'so4', 'so5', 'so6', 'so7', 'so8', 'so9', 'so10','fi1', 'fi2', 'fi3', 'fi4', 'fi5', 'fi6', 'fi7', 'fi8', 'fi9', 'fi10','oc1', 'oc2', 'oc3', 'oc4', 'oc5', 'oc6', 'oc7', 'oc8', 'oc9', 'oc10','in1', 'in2', 'in3', 'in4', 'in5', 'in6', 'in7', 'in8', 'in9', 'in10','en1', 'en2', 'en3', 'en4', 'en5', 'en6', 'en7', 'en8', 'en9', 'en10']
    data = pd.DataFrame(data, index=range(len(data)))
    for col in data.columns:
        if col in l:
            data[col] = data[col].replace('', '4')
            data[col] = data[col].astype('float')
    data['Emotional'] = data['em1']  + data['em2'] + data['em3']+ data['em4']+ data['em5']+ data['em6']+ data['em7']+ data['em8']+ data['em9']+ data['em10']
    data['Occupational'] = data['oc1']  + data['oc2'] + data['oc3']+ data['oc4']+ data['oc5']+ data['oc6']+ data['oc7']+ data['oc8']+ data['oc9']+ data['oc10']
    data['Spiritual'] = data['sp1']  + data['sp2'] + data['sp3']+ data['sp4']+ data['sp5']+ data['sp6']+ data['sp7']+ data['sp8']+ data['sp9']+ data['sp10']
    data['Physical'] = data['ph1']  + data['ph2'] + data['ph3']+ data['ph4']+ data['ph5']+ data['ph6']+ data['ph7']+ data['ph8']+ data['ph9']+ data['ph10']
    data['Social'] = data['so1']  + data['so2'] + data['so3']+ data['so4']+ data['so5']+ data['so6']+ data['so7']+ data['so8']+ data['so9']+ data['so10']
    data['Financial'] = data['fi1']  + data['fi2'] + data['fi3']+ data['fi4']+ data['fi5']+ data['fi6']+ data['fi7']+ data['fi8']+ data['fi9']+ data['fi10']
    data['Intellectual'] = data['in1']  + data['in2'] + data['in3']+ data['in4']+ data['in5']+ data['in6']+ data['in7']+ data['in8']+ data['in9']+ data['in10']
    data['Environmental'] = data['en1']  + data['en2'] + data['en3']+ data['en4']+ data['en5']+ data['en6']+ data['en7']+ data['en8']+ data['en9']+ data['en10']
    selected_cols = ['Emotional', 'Occupational', 'Spiritual', 'Physical', 'Social', 'Financial', 'Intellectual', 'Environmental']
    data['dimension'] = data[selected_cols].idxmin(axis=1)
    data_dict = data.to_dict(orient='records')
    db.wellness.insert_one(data_dict)
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
