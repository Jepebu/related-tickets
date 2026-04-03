## Overview
This project was made as part of a graduation requirement for my BCS.  
It's purpose is to provide a simple interface for IT service desk workers to find historical incidents that are similar to a given description.  
The results can then be used for pattern analysis of recurrent issues, or to find solutions to known problems.   

## Technical
The app works by taking a historical record of incident ticket data from a service desk in a CSV format and trains a Term Frequency-Inverse Document Frequency (TF-IDF) vectorizer on the corpus.  
The TF-IDF vectorizer is then used to calculate the similarity score of any given incident description across the entire corpus within a fraction of second.  
The similarty scores are ranked, and only the data that is deemed relevant to the current description is provided to the user.  

## Build
### Requirements
- docker
- git

### Instructions
```
git clone http://github.com/Jepebu/related-tickets.git
cd related-tickets  
docker built -t related-tickets .  
docker volume create related-tickets-assets  
docker run -p 5000:5000 -v related-tickets-assets:/app/assets related-tickets --help  
```
