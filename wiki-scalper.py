import re
import html, nltk
import urllib
import wikipedia

URL_mask = r'^https:\/\/(.+)\.wikipedia.org\/wiki\/([^#]+)'
stopwords = set(nltk.corpus.stopwords.words('english')) # nltk supports other languages, so in the future this could be expanded to support the languages it supports

def main():

  # Get wikipedia page
  URL = input("Please insert a Wikipedia page URL: ")
  searchTerm = re.match(URL_mask, URL)

  # Do a basic validation
  while not searchTerm:
    URL = input("Not a valid Wikipedia link.\n\nPlease insert a valid Wikipedia page URL: ")
    searchTerm = re.search(URL_mask, URL)
    
  # See what language we are using
  language = searchTerm.group(1)
  if language != "en":
    print("\nWarning! Only the English Wikipedia is supported currently.")
    if ('y' or 'yes') not in input("Continue? ").lower():
      return

  # Clean URL
  URL =  urllib.parse.unquote(searchTerm.group(0))
  
  # Fetch page
  print("Fetching page...")
  try:
    wikipedia.set_lang(language)
    searchTerm = searchTerm.group(2).replace("_", " ") # Get search term from URL (in which case we need to add spaces)
    page = html.unescape(wikipedia.WikipediaPage(urllib.parse.unquote(searchTerm)).html()) #
  except Exception as e:
    print("Error: " + str(e))
    return
  
  # Get each section
  print("Parsing...")

  sections = [] # This is the main list which holds each section
  
  # This temporary one is how we read the initial summary, as it doesn't follow the format of everything else on the page
  temp = []
  temp.append(urllib.parse.unquote(searchTerm)) # Section title
  temp.append (re.findall(r'<p>(.+?)<(?:h[1-4]|/div)>', page, re.M + re.S)[0]) # Summary text ul
  sections.append(temp) # Add summary to final list
  page = page.replace('<div role="navigation" class="navbox"', '<h2>') + '<h2>' # Fix so last regex hits on page
  
  # Now we can read everything else on the page
  sections.extend( re.findall(r'<span class="mw-headline" id="(.+?)">.+?</h[1-4]>(.+?)<h[1-4]>', page, re.M + re.S) ) # 

  print("Printing data...")
  
  # Now we can go through each section and read the data
  for section in sections:
    
    # Print section header
    print("\n== " + section[0].replace("_", " ") + " ==\n")

    # Check if this section has text we can look at
    if not section[1].isspace():
      FindWordOccurence(section[1])
      FindHyperlinks(section[1], URL, language)
    else:
      print("No body text for this section.")


def FindWordOccurence(raw_text):

  # We have to manually remove any CSS
  # Then we can remove all the html and footnote tags
  text = CleanTags(re.sub(re.compile('<style.+?</style>'), '', raw_text))

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
      # If the current word is the high word counted, then it is the new high score 
      if word_tracker[word] > high_score:
        high_score = word_tracker[word] # Set the new high score
        high_score_list.clear() # We don't need any of the old words, because this is now the biggest
      # If this word is the highest, or tied for the highest, add it to the high score list
      if word_tracker[word] >= high_score:
        high_score_list.append(word)

  print("The word(s) " + str(high_score_list) + " showed up most frequntly, occuring " + str(high_score) + " times.\n")
    
def FindHyperlinks(raw_text, URL, language):

  # Parse hyperlinks for location, and linking text
  print("Hyperlinks:")
  hyperlinks = re.findall('<a.+?href="(.+?)".*?>(.*?)</a>', raw_text)
  
  for hyperlink in hyperlinks:
    # Skip empty links
    if not hyperlink[1]:
      continue

    # If link is a footnote, display it differently
    if '#cite' in hyperlink[0]:
      print(" *Footnote " + CleanTags(hyperlink[1]) + " " + URL + CleanTags(hyperlink[0]))
    else:
      # Handle images differently
      if '<img ' in hyperlink[1]:
        print("[ IMAGE FILE ] https://"+ language + ".wikipedia.org" + CleanTags(hyperlink[0]))
      else:
        # Link goes to a different page
        print("[" + CleanTags(hyperlink[1]) + "] https://"+ language + ".wikipedia.org" + CleanTags(hyperlink[0]))

def CleanTags(text):
  # Clean HTML and footnote tags
  return re.sub(re.compile('[\[<].*?[>\]]'), '', text)

# On startup ensure we have needed files for nltk  
try:
  nltk.data.find('tokenizers/punkt')
except:
  nltk.download('stopwords')
  nltk.download('punkt')
  print("\n")

main()
print("\n")
