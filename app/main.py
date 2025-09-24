#!/usr/bin/env python3
### Import flask for web-abb
from flask import Flask, render_template, request

### Import argparse to allow for command line arguments
import argparse

### Import the custom libraries
import sys
from ticketParser import Parser
from vectorizer import Vectorizer

### Import pandas for dataframes
import pandas as pd

### Import codecs to parse ticket text fields
import codecs

### Parse command line args
argparser = argparse.ArgumentParser(
  description="A ticket search application using TF-IDF.")
argparser.add_argument("--bundles", help="Set the language bundles to load.",nargs="*")
argparser.add_argument("--rebuild", help="Rebuild the vectorizers and vector matrices for language bundles.", action='store_true')
argparser.add_argument("--datafile", help="Path to the CSV datafile to use. This is ignored if vectors are already created for the language(s) of the data and '--rebuild' is not used.",default="assets/tickets.csv")
argparser.add_argument("--vectorpath", help="Path to the folder containing vectorizers and vector matrices.",default="assets")
argparser.add_argument('--threshold', help="The value to use as the minimum confidence for matches. Default is 0.15.", default=0.15, type=float)

cli_args = argparser.parse_args()


### Initialize the vector constructor
vectorizer = Vectorizer(
  csv_file=cli_args.datafile,
  languages=cli_args.bundles,
  rebuild=cli_args.rebuild,
  vectorpath=cli_args.vectorpath
)



# Initialize the Flask application
app = Flask(__name__)

# Define the list of languages for the dropdown
language_options = vectorizer.get_languages()

@app.route('/', methods=['GET', 'POST'])
def index():
    global vectorizer
    global cli_args
    min_confidence = cli_args.threshold
    # This dictionary will hold the data to populate the form
    form_data = {
        'ticket_id': "This field will populate with the Ticket's ID",
        'subject': '',
        'answer': 'This field will populate with the most recent response on the ticket.',
        'language': 'english', # Default language
        'body': ''
    }

    # If the form is being submitted (POST request)
    if request.method == 'POST':
        user_dataframe = {
          'subject':[request.form.get('subject')],
          'answer':[request.form.get('resolution')],
          'body':[request.form.get('description')],
          'language':[request.form.get('language')],
          'ticket_id':'User Data'
        }

        df = pd.DataFrame(user_dataframe)
        retrieved_data, confidence = vectorizer.related(df)
        retrieved_data = dict(retrieved_data)
        # To handle escaped characters like '\n', we decode them.
        # This ensures they are rendered as newlines in the textarea.
        if confidence < min_confidence:
          retrieved_data = form_data.copy()
          retrieved_data['answer'] = "No related tickets could be located, please try describing the problem in another way."
        retrieved_data['body'] = codecs.decode(retrieved_data.get('body', ''), 'unicode_escape').replace("\n\n","\n")
        retrieved_data['subject'] = codecs.decode(retrieved_data.get('subject', ''), 'unicode_escape').replace("\n\n","\n") if type(retrieved_data['subject']) is str else "No subject"
        retrieved_data['answer'] = codecs.decode(retrieved_data.get('answer', ''), 'unicode_escape').replace("\n\n","\n")
        retrieved_data['answer'] = retrieved_data['answer'] + f"\n\nConfidence: {confidence}"

        # Update form_data with the retrieved data to send back to the template
        form_data.update(retrieved_data)

    # For a GET request, or after a POST, render the template with the form_data
    return render_template('index.html', languages=language_options, data=form_data)

if __name__ == '__main__':
    # Run the app on host 0.0.0.0 to be accessible within Docker
    app.run(host='0.0.0.0', port=5000, debug=True)
