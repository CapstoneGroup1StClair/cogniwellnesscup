import yaml
import json
import os
from typing import Dict, Tuple
from dotenv import load_dotenv
from bson.json_util import ObjectId
load_dotenv()

DATABASE_URI = os.environ.get("MONGO_URI")

class MongoEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, ObjectId):
            return str(obj)
        return super(MongoEncoder, self).default(obj) 

mail_settings = {
    "MAIL_SERVER": os.environ['MAIL_SERVER'],
    "MAIL_PORT": 587,
    "MAIL_USE_TLS": True,
    "MAIL_USE_SSL": False,
    "MAIL_USERNAME": os.environ['MAIL_USERNAME'],
    "MAIL_PASSWORD": os.environ['MAIL_PASSWORD'],
    "MAIL_DEFAULT_SENDER": os.environ['MAIL_DEFAULT_SENDER'],
}

# Read answer config
with open('answers_conig.yaml') as f:
    answer_map = yaml.safe_load(f)

def get_score(question, answer):
    answer_conf_list = list(filter(lambda a: a['question_slug'] in question, answer_map))
    try:
        assert len(answer_conf_list) == 1
        assert answer not in ['', None]
    except:
        return 0
    answer_config = answer_conf_list[0]
    if answer_config['type'] == 'text':
        return 0
    if answer_config['type'] == 'single_select':
        try:
            return answer_config['answer_scores'][answer.strip()]
        except:
            #print(f"{answer} not found for {question}")
            return 0
    if answer_config['type'] == 'multi_select':
        total = 0
        ans = answer.split(";")
        for a in ans:
            try:
                total += answer_config['answer_scores'][a.strip()]
            except:
                #print(f"{a} not found for {question}")
                pass
        return total

def process_answer(response: Dict):
    severity_score = 0
    import logging
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,  # Set the desired log level (e.g., INFO, DEBUG)
        format='%(asctime)s [%(levelname)s] %(message)s',  # Define log message format
        handlers=[
            logging.FileHandler('app.log'),  # Output logs to a file
            logging.StreamHandler()  # Output logs to the console
        ]
    )

    # Start logging
    for q, a in response.items():
        logging.info(get_score(q, a))
        severity_score += get_score(q, a)

    return (severity_score)
