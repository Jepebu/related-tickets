#!/usr/bin/env python3

### Import data science libraries
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from nltk.corpus import stopwords

### Import sys libraries to save vectorizers
import joblib
import sys
import os

### Import custom ticket parser
from ticketParser import Parser

### Class for each supported language to make interfacing between libraries easier
class LANGUAGE:
  def __init__(self, code, text, stop_words=None):
    self.code = code
    self.text = text

  def __str__(self):
      return self.text

  def __repr__(self):
    return (self.code, self.text)

  def stop_words(self):
    try:
      return stopwords.words(self.text)
    except LookupError:
      import nltk
      nltk.download('stopwords')
      return stopwords.words(self.text)


### Generates a series of vectors across provided languages
class Vectorizer:

  ENGLISH = LANGUAGE('en', 'english')
  SPANISH = LANGUAGE('es', 'spanish')
  FRENCH  = LANGUAGE('fr', 'french')
  GERMAN  = LANGUAGE('de', 'german')
  RUSSIAN = LANGUAGE('ru', 'russian')
  CHINESE = LANGUAGE('zh', 'chinese')

  class Bundle:
    def __init__(self, dataframe, rebuild=False, path=os.getcwd()):
      self.dataframe = dataframe
      self.rebuild = rebuild
      lang_code = dataframe['language'].values[0]
      self.path = path
      if not os.path.isdir(path):
        os.mkdir(path)
      self.strings = [f"{subject} {body}" for subject, body in zip(dataframe['subject'], dataframe['body'])]
      self.vectorizer, self.vector_matrix = self.__vget__(lang_code)

    def __repr__(self):
      return f"Bundle Object {self.dataframe.language}"

    @staticmethod
    def save(vector_item, file_path):
      print(f"Saving '{file_path}'...")
      joblib.dump(vector_item, file_path)

    @staticmethod
    def load(file_path):
      print(f"Loading {file_path}...")
      return joblib.load(file_path)

    def __vget__(self, lang_code):
      matrix_path = self.path + f"/vector_matrix.{lang_code}"
      vectorizer_path = self.path + f"/vectorizer.{lang_code}"

      if os.path.exists(vectorizer_path) and os.path.exists(matrix_path) and not self.rebuild:
        return (self.load(vectorizer_path), self.load(matrix_path))
      else:
        print(f"Initializing vector matrix for '{lang_code}', please wait...")
        vectorizer = TfidfVectorizer(ngram_range=(1,3), stop_words=Vectorizer.__get_lang__(lang_code).stop_words(),sublinear_tf=True)
        vector_matrix = vectorizer.fit_transform(self.strings)
        self.save(vectorizer, vectorizer_path)
        self.save(vector_matrix, matrix_path)
        return (vectorizer, vector_matrix)


  def __init__(self, csv_file, vectorpath=None, rebuild=False, languages=None):
    self.bundles = {}
    self.languages = []
    self.vectorpath = vectorpath
    self.rebuild = rebuild
    self.csv_file = csv_file
    if csv_file:
      parser = Parser(csv_file)
      docs_by_lang = parser.filter('language')
    if not languages or languages == ['all']:
      self.__languages__ = ['english','spanish','french','german','russian','chinese']
    else:
      self.__languages__ = languages
    self.__get_bundles__(docs_by_lang)


  @staticmethod
  ### __get_lang__ takes a string_descriptor and returns the appropriate language object
  def __get_lang__(string_descriptor, attribute=None):
    if type(string_descriptor) is not str:
      raise ValueError(f"Got type {type(string_descriptor)} for string_descriptor, excpected type string.")
    for lang in [Vectorizer.ENGLISH, Vectorizer.SPANISH, Vectorizer.FRENCH, Vectorizer.GERMAN, Vectorizer.RUSSIAN, Vectorizer.CHINESE]:
      if lang.code == string_descriptor or lang.text == string_descriptor:
        return lang

  ### get_languages() will return a list of supported languages
  def get_languages(self):
    return [self.__get_lang__(b).text for b in self.languages]

  ### generate() takes an input dictionary that contains the corpus dataframes separated by language keys
  def __get_bundles__(self, docs_by_lang):
    for lang in self.__languages__:
      lang_obj = self.__get_lang__(lang)
      if lang_obj == None:
        raise AttributeError(f"No language definition exists for '{lang}'.")

      doc_df = docs_by_lang.get(lang_obj.code)
      if doc_df is None:
        print(f"No documents found in data file for language '{lang}'.", file=sys.stderr)
        continue
      self.languages.append(lang_obj.text)
      bundle = Vectorizer.Bundle(doc_df, rebuild=self.rebuild,path=self.vectorpath if self.vectorpath is not None else os.getcwd())
      self.bundles[lang_obj.code] = bundle
    return self.bundles

  def related(self, ticket, n_best_matches=1):
    # Configure for the ticket language
    lang_raw = ticket['language'].values[0]
    lang = self.__get_lang__(lang_raw)
    bundle = self.bundles.get(lang.code)
    if not bundle:
      raise ValueError(f"No language bundle found for '{lang.code}' among {self.get_languages()}.")

    # Break the dataframe into the parts we need then make the vector
    t_id = ticket['ticket_id'].values[0]
    t_doc = [f"{ticket.subject.values[0]} {ticket.body.values[0]}"]
    t_doc_vector = bundle.vectorizer.transform(t_doc)

    # Calculate the similarity then put it into a dataframe
    similarity_matrix = cosine_similarity(t_doc_vector, bundle.vector_matrix)[0]
    most_similar_index = np.argmax(similarity_matrix)
    most_similar_ticket = bundle.dataframe.iloc[most_similar_index]
    max_score = similarity_matrix[most_similar_index]
    return most_similar_ticket, max_score
