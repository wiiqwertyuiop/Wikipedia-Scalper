import re
import nltk, html
import requests

#
# I provided two different methods of accomplishing the goal:
# This version queries and makes use of the mediawiki API
# 

'''
Takes in a Wikipedia link and for each section,
prints out the title of the section, 
the most frequent words in the section
that are not considered “stop words”, 
and lists every hyperlink in the section.
'''

# Language support
language_dict = {
  "en": "english",
  "sv": "swedish",
  "de": "german",
  "nl": "dutch",
  "no": "norwegian",
  "da": "danish",
  "simple": "english",
  "nn": "norwegian",
  "fr": "french",
  "it": "italian",
  "es": "spanish",
  "pt": "portuguese",
  "ro": "romanian",
  "ru": "russian",
  "arz": "arabic",
  "ar": "arabic",
  "tr": "turkish",
  "id": "indonesian",
  "fi": "finnish",
  "hu": "hungarian",
  "azb": "azerbaijani",
  "az": "azerbaijani", 
  "kk": "kazakh",
  "ne": "nepali",
}
      
def main():

    URL_mask = r'^https:\/\/(.+)\.wikipedia.org\/wiki\/([^#]+)'

    # Get wikipedia page
    URL = input("Please insert a Wikipedia page URL: ")
    searchTerm = re.match(URL_mask, URL)

    # Do a basic validation
    while not searchTerm:
        URL = input("Not a valid Wikipedia link.\n\nPlease insert a valid Wikipedia page URL: ")
        searchTerm = re.search(URL_mask, URL)

    #URL =  urllib.parse.unquote(searchTerm.group(0))
    
    # See what language we are using
    language = searchTerm.group(1)
    if language not in language_dict:
        print("Error: this language is not supported!")
        return
    
    # API Call URL
    API_URL = ("https://" + language
    + ".wikipedia.org/w/api.php?action=parse&format=json&prop=text|links|externallinks|sections&disabletoc=1&disablestylededuplication=1&page="
    + searchTerm.group(2)
    + "&section=")
    
    # Don't let loop go on forever (I doubt there is a wikipedia page with over 500 sections)
    for section in range(500):
    
        # Contact API
        try:
            data = requests.get(API_URL + str(section)).json()
        except Exception as e:
            print(e)
            break

        # If we reach the last section break 
        if 'parse' not in data:
            break
            
        data = data['parse']
        
        if section == 0:
          print("\n== " + data['title'] + " ==\n")
        else:
          print("\n== " + data['sections'][0]['line'] + " ==\n")
        
        FindWordOccurence(data['text']['*'], set(nltk.corpus.stopwords.words(language_dict[language])))
        
        # Do hyperlinks
        if data['links'] or data['externallinks']:
            print("Hyperlinks:")
            
        for links in data['links']:
            if links['ns'] != 0:
                continue
            print("https://" + language + ".wikipedia.org/wiki/" + links['*'].replace(" ", "_"))
            
        for externallinks in data['externallinks']:
            print(externallinks)
        

def FindWordOccurence(raw_text, stopwords):
  
  # We have to manually remove any CSS
  # Then we can remove all the html and footnote tags
  text = CleanTags(raw_text)
  
  # Remove any punctionation not in between words, and split the text
  words = re.sub(re.compile('(\s\W+|\W+\s)'), ' ', text).split()
    
  high_score = 0
  high_score_list = []
  word_tracker = {}

  # Loop through all words in this section and check if it is a stopword
  for word in words:
    word = word.lower()
    if word not in stopwords:
      # If we found a new word, start a new spot in the dictionary 
      if word not in word_tracker:
        word_tracker[word] = 0
      # Increase word count
      word_tracker[word] += 1
      # If the current word is the highest word counted, then it is the new high score 
      if word_tracker[word] > high_score:
        high_score = word_tracker[word] # Set the new high score
        high_score_list.clear() # We don't need any of the old words, because this is now the biggest
      # If this word is the highest, or tied for the highest, add it to the high score list
      if word_tracker[word] >= high_score:
        high_score_list.append(word)

  if high_score == 0: return
  print("The word(s) " + str(high_score_list) + " showed up most frequntly, occuring " + str(high_score) + " times.\n")
    
def CleanTags(text):
  
  # Get rid of CSS
  text = re.sub(re.compile('<style.+?<\/style>'), '', text)
  # Get rid of section headers
  text = re.sub(re.compile('<h[1-4]>.+?<\/h[1-4]'), '', text)
  # Get rid of infobox
  text = re.sub(re.compile('<table.+?class=\\"infobox.+?</table>', re.S), '', text)
  # Get rid of footnotes
  text = re.sub(re.compile('<sup.+?class=\\"reference\\".+?<\/sup>'), '', text)
  # Get rid of reference section
  text = re.sub(re.compile('<ol class="references">.+?<\/ol>', re.S), '', text)
  # Get rid of HTML tags
  text = re.sub(re.compile('<.+?>'), '', text)
  # Get rid of HTML comments
  text = re.sub(re.compile('<\!--.+?-->', re.S), '', text)
  # Fix \n and \u
  text = re.sub(re.compile('\\[u|n]'), ' ', text)
  return html.unescape(text)

# On startup ensure we have needed files for nltk  
try:
  nltk.data.find('tokenizers/punkt')
except:
  nltk.download('stopwords')
  nltk.download('punkt')
  print("\n")
  
main()
print("\nFinished.")
