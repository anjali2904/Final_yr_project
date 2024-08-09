from flask import Flask, request, jsonify
import joblib
import numpy as np
import pandas as pd
from countt import chatbot

app = Flask(__name__, static_folder="../frontend", static_url_path='/')

# Load trained models
model_engineering = joblib.load('models/merit_prediction_model_engineering.pkl')
model_doctor = joblib.load('models/merit_prediction_model_doctor.pkl')
model_11th = joblib.load('models/merit_prediction_model_11th.pkl')
model_diploma = joblib.load('models/merit_prediction_model_diploma.pkl')

# Load datasets for eligibility calculations
data_engineering = pd.read_csv('data/previous_years_data_engineering.csv', encoding='latin1')
data_doctor = pd.read_csv('data/previous_years_data_doctor.csv', encoding='latin1')
data_11th = pd.read_csv('data/previous_years_data_11th.csv', encoding='latin1')
data_diploma = pd.read_csv('data/previous_years_data_diploma.csv', encoding='latin1')

# Function to get eligible colleges based on direct comparison of marks
# Function to get eligible colleges based on direct comparison of marks
def get_eligible_colleges(percentage, jee_percentile, cet_percentile, neet_marks, college_list, choice):
    if choice == 'engineering':
        eligible_colleges = college_list[
            (college_list['Marks'] <= percentage) & 
            (college_list['JEE_Percentile'] <= jee_percentile) & 
            (college_list['CET_Percentile'] <= cet_percentile)  # Changed column name to 'CET_Percentile'
        ]
    elif choice == 'doctor':
        eligible_colleges = college_list[
            (college_list['Marks'] <= percentage) & 
            (college_list['NEET_Marks'] <= neet_marks) & 
            (college_list['CET_Percentile'] <= cet_percentile)  # Changed column name to 'CET_Percentile'
        ]
    else:
        eligible_colleges = college_list[college_list['Marks'] <= percentage]
    
    return eligible_colleges['College'].tolist()

# Function to save conversation data to a text file
def save_conversation_to_file(data):
    with open("conversation_history.txt", "a") as file:
        file.write(data + "\n")

# Function to load conversation data from a text file
def load_conversation_from_file():
    with open("conversation_history.txt", "r") as file:
        conversation_data = file.read()
    return conversation_data

@app.route("/")
def login():
    return app.send_static_file('login.html')

@app.route("/login")
def home():
    return app.send_static_file('home.html')

@app.route("/home")
def loading():
    return app.send_static_file('loading.html')

@app.route("/home")
def index():
    return app.send_static_file('index.html')

@app.route('/check-eligibility', methods=['POST'])
def check_eligibility():
    data = request.json
    standard = data.get('standard')
    response = {}

    if standard == '10th':
        percentage = float(data.get('percentage'))
        eligible_colleges_11th = get_eligible_colleges(percentage, None, None, None, data_11th, '11th')
        eligible_colleges_diploma = get_eligible_colleges(percentage, None, None, None, data_diploma, 'diploma')

        eligible_colleges = eligible_colleges_11th + eligible_colleges_diploma
        response = {
            'colleges': eligible_colleges
        }

    elif standard == '12th':
        choice = data.get('choice')
        percentage = float(data.get('percentage'))
        cet_percentile = float(data.get('cet_percentile'))

        if choice == 'engineering':
            jee_percentile = float(data.get('jee_percentile'))
            eligible_colleges = get_eligible_colleges(percentage, jee_percentile, cet_percentile, None, data_engineering, 'engineering')
            response = {
                'colleges': eligible_colleges
            }

        elif choice == 'doctor':
            neet_marks = float(data.get('neet_marks'))
            eligible_colleges = get_eligible_colleges(percentage, None, cet_percentile, neet_marks, data_doctor, 'doctor')
            response = {
                'colleges': eligible_colleges
            }

        else:
            response = {'message': "Invalid choice. Please enter 'engineering' or 'doctor'."}
    else:
        response = {'message': "Invalid standard. Please enter '10th' or '12th'."}

    return jsonify(response)

@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.get_json()
    message = data["message"].lower()

    # Your existing code for handling chat requests
    response = chatbot(message)
    # After processing the chat request, save the conversation to the file
    save_conversation_to_file(message)

    # Your existing code for generating response
    return jsonify({"response": response})

@app.route("/get-conversation", methods=["GET"])
def get_conversation():
    conversation_data = load_conversation_from_file()
    return jsonify({"conversation": conversation_data})

if __name__ == "__main__":
    app.run(debug=True)
