import random
import spacy
from PyPDF2 import PdfReader
import requests
from bs4 import BeautifulSoup
from docx import Document

# Load English language model
nlp = spacy.load("en_core_web_lg")

# Initialize an empty dictionary to store responses
responses = {}

# File path to the dataset
file_path = 'responses.txt'

# URL of the website to gather data
website_url = 'https://en.wikipedia.org/wiki/Education'

# File paths to the PDF and DOC files
pdf_file_path = 'example.pdf'
docx_file_path = 'example.docx'

# Function to extract text from PDF
def extract_text_from_pdf(pdf_file_path):
    text = ""
    with open(pdf_file_path, 'rb') as file:
        pdf_reader = PdfReader(file)
        for page in pdf_reader.pages:
            text += page.extract_text()
    return text

# Function to extract text from DOC file
def extract_text_from_docx(docx_file_path):
    text = ""
    doc = Document(docx_file_path)
    for paragraph in doc.paragraphs:
        text += paragraph.text
    return text

# Function to extract text from a website
def extract_text_from_website(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    # Assuming the main content is in <p> tags, you can adjust this based on the structure of the website
    paragraphs = soup.find_all('p')
    text = ' '.join(paragraph.get_text() for paragraph in paragraphs)
    return text

# Function to save new responses to the dataset file
def save_response_to_file(input_text, response):
    with open(file_path, 'a', encoding='utf-8') as file:
        file.write(f"{input_text}|{response}\n")

# Function to handle user input when no response is found
def handle_no_response(input_text):
    new_response = input("I'm sorry, I don't have a response for that. Please provide a response: ")
    # Save the new response to the dataset
    save_response_to_file(input_text, new_response)
    # Add the new response to the in-memory responses dictionary
    doc = nlp(input_text.lower())
    input_text_cleaned = ' '.join(token.lemma_ for token in doc if token.is_alpha)
    responses[input_text_cleaned] = [new_response.strip()]
    return new_response

# Function to update responses from the processed PDF text
def update_responses_from_text(text):
    doc = nlp(text)
    for paragraph in doc.sents:  # Split text into paragraphs
        paragraph_cleaned = ' '.join(token.lemma_ for token in paragraph if token.is_alpha)
        if paragraph_cleaned not in responses:
            responses[paragraph_cleaned] = [paragraph.text.strip()]
        else:
            responses[paragraph_cleaned].append(paragraph.text.strip())

# Function to update responses from the processed DOC text
def update_responses_from_docx(text):
    doc = nlp(text)
    for paragraph in doc.sents:
        paragraph_cleaned = ' '.join(token.lemma_ for token in paragraph if token.is_alpha)
        if paragraph_cleaned not in responses:
            responses[paragraph_cleaned] = [paragraph.text.strip()]
        else:
            responses[paragraph_cleaned].append(paragraph.text.strip())

# Function to search for the most relevant paragraph in the PDF based on user input
def search_paragraph_in_pdf(user_input):
    text = extract_text_from_pdf(pdf_file_path)
    doc = nlp(text)
    input_doc = nlp(user_input.lower())
    max_similarity = -1
    most_similar_paragraph = None
    for paragraph in doc.sents:
        similarity = paragraph.similarity(input_doc)
        if similarity > max_similarity:
            max_similarity = similarity
            most_similar_paragraph = paragraph.text.strip()
    return most_similar_paragraph

# Function to search for the most relevant paragraph in the DOC based on user input
def search_paragraph_in_docx(user_input):
    text = extract_text_from_docx(docx_file_path)
    doc = nlp(text)
    input_doc = nlp(user_input.lower())
    max_similarity = -1
    most_similar_paragraph = None
    for paragraph in doc.sents:
        similarity = paragraph.similarity(input_doc)
        if similarity > max_similarity:
            max_similarity = similarity
            most_similar_paragraph = paragraph.text.strip()
    return most_similar_paragraph

# Function to search for relevant information in website content based on user input
def search_website_for_information(user_input):
    text = extract_text_from_website(website_url)
    doc = nlp(text)
    input_doc = nlp(user_input.lower())
    max_similarity = -1
    most_similar_sentence = None
    for sentence in doc.sents:
        similarity = sentence.similarity(input_doc)
        if similarity > max_similarity:
            max_similarity = similarity
            most_similar_sentence = sentence.text.strip()
    return most_similar_sentence

# Function to learn from user input
def learn_from_input(input_text, response):
    doc = nlp(input_text.lower())
    input_text_cleaned = ' '.join(token.lemma_ for token in doc if token.is_alpha)
    if input_text_cleaned not in responses:
        responses[input_text_cleaned] = [response]
    else:
        responses[input_text_cleaned].append(response)

try:
    # Read the responses from the text file
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    # Process each line in the file
    for line in lines:
        # Add a check for lines without the expected separator '|'
        if '|' not in line:
            continue  # Skip the line if it doesn't contain '|'

        # Unpack values only if there are enough values to unpack
        input_text, response = line.strip().split('|', 1)

        # Process input text using spaCy
        doc = nlp(input_text.lower())

        # Create a list of lemmatized tokens
        input_text_cleaned = ' '.join(token.lemma_ for token in doc if token.is_alpha)

        # Check if the key is already in the dictionary
        if input_text_cleaned in responses:
            # If yes, append the new response to the list of responses
            responses[input_text_cleaned].append(response.strip())
        else:
            # If no, create a new list with the response
            responses[input_text_cleaned] = [response.strip()]

    # Shuffle the responses for each cleaned input key
    for key_cleaned in responses:
        random.shuffle(responses[key_cleaned])

except Exception as e:
    print(f"Error reading the file: {e}")

# Simple chatbot function
def chatbot(input_text):
    # Search for relevant information in the text file
    response = search_responses_in_file(input_text)
    if response:
        # Learn from the user's question and store the response
        learn_from_input(input_text, response)
        return response
    else:
        # If no response in text file, search in the DOC
        response = search_paragraph_in_docx(input_text)
        if response:
            # Learn from the user's question and store the response
            learn_from_input(input_text, response)
            return response
        else:
            # If no response in DOC, search in the PDF
            response = search_paragraph_in_pdf(input_text)
            if response:
                # Learn from the user's question and store the response
                learn_from_input(input_text, response)
                return response
            else:
                # If no response in PDF, search in the website content
                response = search_website_for_information(input_text)
                if response:
                    # Learn from the user's question and store the response
                    learn_from_input(input_text, response)
                    return response
                else:
                    # If no response from website, handle user input and store it permanently
                    response = handle_no_response(input_text)
                    # Learn from user input
                    learn_from_input(input_text, response)
                    return response

# Function to search for relevant information in the text file
def search_responses_in_file(user_input):
    doc = nlp(user_input.lower())
    input_text_cleaned = ' '.join(token.lemma_ for token in doc if token.is_alpha)
    if input_text_cleaned in responses and len(responses[input_text_cleaned]) > 0:
        return responses[input_text_cleaned].pop(0)
    else:
        return None

# Greet the user
print("Hello! How can I help you?")



