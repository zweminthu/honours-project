import tweepy
import csv
import os
from os import path
import re, string, time, itertools
from datetime import datetime
from emot.emo_unicode import UNICODE_EMO, EMOTICONS
from nltk.stem import PorterStemmer
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

# Function for insert data into csv file
def inputdata(t, o, c, e, a, n, csv_writer, tweets_no):

	csv_writer.writerow([t, o, c, e, a, n])
	tweets_no+=1
	if tweets_no==1200:
		time.sleep(60)
		tweets_no=0
	return tweets_no

# Function for removing emojis
def remove_emoji(string):

	emoji_pattern = re.compile("["
							 u"\U0001F600-\U0001F64F" # emoticons
							 u"\U0001F300-\U0001F5FF" # symbols & pictographs
							 u"\U0001F680-\U0001F6FF" # transport & map symbols
							 u"\U0001F1E0-\U0001F1FF" # flags (iOS)
							 u"\U00002702-\U000027B0"
							 u"\U000024C2-\U0001F251"
							 "]+", flags=re.UNICODE)
	return emoji_pattern.sub(r'', string)

# Function for removing emoticons
def remove_emoticons(text):

	emoticon_pattern = re.compile(u'(' + u'|'.join(k for k in EMOTICONS) + u')')
	return emoticon_pattern.sub(r'', text)

cList = {
	"rt":'',
	"ain't": "am not",
	"aren't": "are not",
	"can't": "cannot",
	"can't've": "cannot have",
	"'cause": "because",
	"could've": "could have",
	"couldn't": "could not",
	"couldn't've": "could not have",
	"didn't": "did not",
	"doesn't": "does not",
	"don't": "do not",
	"hadn't": "had not",
	"hadn't've": "had not have",
	"hasn't": "has not",
	"haven't": "have not",
	"he'd": "he would",
	"he'd've": "he would have",
	"he'll": "he will",
	"he'll've": "he will have",
	"he's": "he is",
	"how'd": "how did",
	"how'd'y": "how do you",
	"how'll": "how will",
	"how's": "how is",
	"i'd": "i would",
	"i'd've": "i would have",
	"i'll": "i will",
	"i'll've": "i will have",
	"i'm": "i am",
	"i've": "i have",
	"isn't": "is not",
	"it'd": "it had",
	"it'd've": "it would have",
	"it'll": "it will",
	"it'll've": "it will have",
	"it's": "it is",
	"let's": "let us",
	"ma'am": "madam",
	"mayn't": "may not",
	"might've": "might have",
	"mightn't": "might not",
	"mightn't've": "might not have",
	"must've": "must have",
	"mustn't": "must not",
	"mustn't've": "must not have",
	"needn't": "need not",
	"needn't've": "need not have",
	"o'clock": "of the clock",
	"oughtn't": "ought not",
	"oughtn't've": "ought not have",
	"shan't": "shall not",
	"sha'n't": "shall not",
	"shan't've": "shall not have",
	"she'd": "she would",
	"she'd've": "she would have",
	"she'll": "she will",
	"she'll've": "she will have",
	"she's": "she is",
	"should've": "should have",
	"shouldn't": "should not",
	"shouldn't've": "should not have",
	"so've": "so have",
	"so's": "so is",
	"that'd": "that would",
	"that'd've": "that would have",
	"that's": "that is",
	"there'd": "there had",
	"there'd've": "there would have",
	"there's": "there is",
	"they'd": "they would",
	"they'd've": "they would have",
	"they'll": "they will",
	"they'll've": "they will have",
	"they're": "they are",
	"they've": "they have",
	"to've": "to have",
	"wasn't": "was not",
	"we'd": "we had",
	"we'd've": "we would have",
	"we'll": "we will",
	"we'll've": "we will have",
	"we're": "we are",
	"we've": "we have",
	"weren't": "were not",
	"what'll": "what will",
	"what'll've": "what will have",
	"what're": "what are",
	"what's": "what is",
	"what've": "what have",
	"when's": "when is",
	"when've": "when have",
	"where'd": "where did",
	"where's": "where is",
	"where've": "where have",
	"who'll": "who will",
	"who'll've": "who will have",
	"who's": "who is",
	"who've": "who have",
	"why's": "why is",
	"why've": "why have",
	"will've": "will have",
	"won't": "will not",
	"won't've": "will not have",
	"would've": "would have",
	"wouldn't": "would not",
	"wouldn't've": "would not have",
	"y'all": "you all",
	"y'alls": "you alls",
	"y'all'd": "you all would",
	"y'all'd've": "you all would have",
	"y'all're": "you all are",
	"y'all've": "you all have",
	"you'd": "you had",
	"you'd've": "you would have",
	"you'll": "you you will",
	"you'll've": "you you will have",
	"you're": "you are",
	"you've": "you have"
}

c_re = re.compile('(%s)' % '|'.join(cList.keys()))

# Function for expand contractions
def expandContractions(text, c_re=c_re):
		def replace(match):
				return cList[match.group(0)]
		return c_re.sub(replace, text)

# Function for cleaning process
def clean_text(text):

	# convert text to lower-case
	lct = text.lower()

	# remove the # in #hashtag
	lct = re.sub(r'#(\w+)','', lct)
	
	# remove URLs
	lct = re.sub(r'(http|https|ftp)://[a-zA-Z0-9\./]+', '', lct)
	
	#remove handles
	lct = re.sub(r'@(\w+)', '', lct)

	# remove repeated characters
	lct = re.sub(r'(.)\1+', r'\1\1', lct) 

	# Remove all Non-ASCII characters
	lct = re.sub(r'[^\x00-\x7F]+', '', lct)
	
	# remove emoji
	lct = remove_emoji(lct)
	
	# remove emoticon
	lct = remove_emoticons(lct)
	
	#  expand the contraction words
	lct = expandContractions(lct)
	

	# tokenize word
	tokenized_text = word_tokenize(lct)
	

	# word lemmatizing
	lemmatizing = WordNetLemmatizer()
	lemmatized_text = [lemmatizing.lemmatize(w) for w in tokenized_text]

	# word stemming
	#stemming = PorterStemmer()
	#stemmed_text = [stemming.stem(word) for word in lemmatized_text]

	# remove punctuations
	table = str.maketrans('', '', string.punctuation)
	removed_punctuation = [w.translate(table) for w in lemmatized_text]
	
	# check word is alphbaets
	cleaned_text = [word for word in removed_punctuation if word.isalpha()]
	
	# remove stopwords
	stop_words = set(stopwords.words('english'))
	cleaned_text = [word for word in cleaned_text if word not in stop_words]

	# final cleaned text
	cleaned_text = " ".join(cleaned_text)

	return cleaned_text


def dataset_create(api):

	currentdate=datetime.now()
	csvfile="dataset("+str(currentdate.strftime("%d, %B, %Y"))+").csv"
	print(csvfile)
	if path.exists(csvfile):
		print('Found old csv file')
		os.remove(csvfile)
		print('Removed old file')

	csvf = open(csvfile, 'a', newline="")
	print ('new csv File created')

	csv_writer = csv.writer(csvf)
	csv_writer.writerow(["Tweets", "Openness", "Conscientiousness", "Extraversion", "Agreeableness", "Neuroticism"])

	search_word="competent OR efficient OR careful OR sympathetic OR forgiving OR helpful OR insecure OR nervous OR impatient OR creative OR artistic OR thoughtful OR friendly OR assertive OR outgoing"
	count=100
	tweets_no=0

	for tweet in tweepy.Cursor(api.search, q=search_word, count=count, lang="en", since="2008-01-01", tweet_mode='extended').items(250000):

		# take only tweet text
		text = tweet.full_text
		
		text = clean_text(text)

		if("creative" in tweet.full_text or "artistic" in tweet.full_text or "thoughtful" in tweet.full_text):
			
			if("competent" in tweet.full_text or "efficient" in tweet.full_text or "careful" in tweet.full_text):
				opn = 1
				con = 1
				ext = 0
				agr = 0
				neu = 0
				tweets_no = inputdata(text.encode('ascii', errors='ignore'), opn, con, ext, agr, neu, csv_writer, tweets_no)

			elif("friendly" in tweet.full_text or "assertive" in tweet.full_text or "outgoing" in tweet.full_text):
				opn = 1
				con = 0
				ext = 1
				agr = 0
				neu = 0
				tweets_no = inputdata(text.encode('ascii', errors='ignore'), opn, con, ext, agr, neu, csv_writer, tweets_no)

			elif("sympathetic" in tweet.full_text or "helpful" in tweet.full_text or "forgiving" in tweet.full_text):
				opn = 1
				con = 0
				ext = 0
				agr = 1
				neu = 0
				tweets_no = inputdata(text.encode('ascii', errors='ignore'), opn, con, ext, agr, neu, csv_writer, tweets_no)

			elif("insecure"in tweet.full_text or "nervous" in tweet.full_text or "impatient" in tweet.full_text):
				opn = 1
				con = 0
				ext = 0
				agr = 0
				neu = 1
				tweets_no = inputdata(text.encode('ascii', errors='ignore'), opn, con, ext, agr, neu, csv_writer, tweets_no)

			else:
				opn = 1
				con = 0
				ext = 0
				agr = 0
				neu = 0
				tweets_no = inputdata(text.encode('ascii', errors='ignore'), opn, con, ext, agr, neu, csv_writer, tweets_no)

		

		elif("competent" in tweet.full_text or "efficient" in tweet.full_text or "careful" in tweet.full_text):

			if("creative" in tweet.full_text or "artistic" in tweet.full_text or "thoughtful" in tweet.full_text):
				opn = 1
				con = 1
				ext = 0
				agr = 0
				neu = 0
				tweets_no = inputdata(text.encode('ascii', errors='ignore'), opn, con, ext, agr, neu, csv_writer, tweets_no)

			elif("friendly" in tweet.full_text or "assertive" in tweet.full_text or "outgoing" in tweet.full_text):
				opn = 0
				con = 1
				ext = 1
				agr = 0
				neu = 0
				tweets_no = inputdata(text.encode('ascii', errors='ignore'), opn, con, ext, agr, neu, csv_writer, tweets_no)

			elif("sympathetic" in tweet.full_text or "helpful" in tweet.full_text or "forgiving" in tweet.full_text):
				opn = 0
				con = 1
				ext = 0
				agr = 1
				neu = 0
				tweets_no = inputdata(text.encode('ascii', errors='ignore'), opn, con, ext, agr, neu, csv_writer, tweets_no)

			elif("insecure"in tweet.full_text or "nervous" in tweet.full_text or "impatient" in tweet.full_text):
				opn = 0
				con = 1
				ext = 0
				agr = 0
				neu = 1
				tweets_no = inputdata(text.encode('ascii', errors='ignore'), opn, con, ext, agr, neu, csv_writer, tweets_no)

			else:
				opn = 0
				con = 1
				ext = 0
				agr = 0
				neu = 0
				tweets_no = inputdata(text.encode('ascii', errors='ignore'), opn, con, ext, agr, neu, csv_writer, tweets_no)

			

		elif("friendly" in tweet.full_text or "assertive" in tweet.full_text or "outgoing" in tweet.full_text):

			if("creative" in tweet.full_text or "artistic" in tweet.full_text or "thoughtful" in tweet.full_text):
				opn = 1
				con = 0
				ext = 1
				agr = 0
				neu = 0
				tweets_no = inputdata(text.encode('ascii', errors='ignore'), opn, con, ext, agr, neu, csv_writer, tweets_no)

			elif("competent" in tweet.full_text or "efficient" in tweet.full_text or "careful" in tweet.full_text):
				opn = 0
				con = 1
				ext = 1
				agr = 0
				neu = 0
				tweets_no = inputdata(text.encode('ascii', errors='ignore'), opn, con, ext, agr, neu, csv_writer, tweets_no)

			elif("sympathetic" in tweet.full_text or "helpful" in tweet.full_text or "forgiving" in tweet.full_text):
				opn = 0
				con = 0
				ext = 1
				agr = 1
				neu = 0
				tweets_no = inputdata(text.encode('ascii', errors='ignore'), opn, con, ext, agr, neu, csv_writer, tweets_no)

			elif("insecure"in tweet.full_text or "nervous" in tweet.full_text or "impatient" in tweet.full_text):
				opn = 0
				con = 0
				ext = 1
				agr = 0
				neu = 1
				tweets_no = inputdata(text.encode('ascii', errors='ignore'), opn, con, ext, agr, neu, csv_writer, tweets_no)

			else:
				opn = 0
				con = 0
				ext = 1
				agr = 0
				neu = 0
				tweets_no = inputdata(text.encode('ascii', errors='ignore'), opn, con, ext, agr, neu, csv_writer, tweets_no)

		
		
		elif("sympathetic" in tweet.full_text or "helpful" in tweet.full_text or "forgiving" in tweet.full_text):

			if("creative" in tweet.full_text or "artistic" in tweet.full_text or "thoughtful" in tweet.full_text):
				opn = 1
				con = 0
				ext = 0
				agr = 1
				neu = 0
				tweets_no = inputdata(text.encode('ascii', errors='ignore'), opn, con, ext, agr, neu, csv_writer, tweets_no)

			elif("competent" in tweet.full_text or "efficient" in tweet.full_text or "careful" in tweet.full_text):
				opn = 0
				con = 1
				ext = 0
				agr = 1
				neu = 0
				tweets_no = inputdata(text.encode('ascii', errors='ignore'), opn, con, ext, agr, neu, csv_writer, tweets_no)

			elif("friendly" in tweet.full_text or "assertive" in tweet.full_text or "outgoing" in tweet.full_text):
				opn = 0
				con = 0
				ext = 1
				agr = 1
				neu = 0
				tweets_no = inputdata(text.encode('ascii', errors='ignore'), opn, con, ext, agr, neu, csv_writer, tweets_no)

			elif("insecure"in tweet.full_text or "nervous" in tweet.full_text or "impatient" in tweet.full_text):
				opn = 0
				con = 0
				ext = 0
				agr = 1
				neu = 1
				tweets_no = inputdata(text.encode('ascii', errors='ignore'), opn, con, ext, agr, neu, csv_writer, tweets_no)

			else:
				opn = 0
				con = 0
				ext = 0
				agr = 1
				neu = 0
				tweets_no = inputdata(text.encode('ascii', errors='ignore'), opn, con, ext, agr, neu, csv_writer, tweets_no)



		elif("insecure" in tweet.full_text or "nervous" in tweet.full_text or "impatient" in tweet.full_text):

			if("creative" in tweet.full_text or "artistic" in tweet.full_text or "thoughtful" in tweet.full_text):
				opn = 1
				con = 0
				ext = 0
				agr = 0
				neu = 1
				tweets_no = inputdata(text.encode('ascii', errors='ignore'), opn, con, ext, agr, neu, csv_writer, tweets_no)

			elif("competent" in tweet.full_text or "efficient" in tweet.full_text or "careful" in tweet.full_text):
				opn = 0
				con = 1
				ext = 0
				agr = 0
				neu = 1
				tweets_no = inputdata(text.encode('ascii', errors='ignore'), opn, con, ext, agr, neu, csv_writer, tweets_no)

			elif("friendly" in tweet.full_text  or "assertive" in tweet.full_text or "outgoing" in tweet.full_text):
				opn = 0
				con = 0
				ext = 1
				agr = 0
				neu = 1
				tweets_no = inputdata(text.encode('ascii', errors='ignore'), opn, con, ext, agr, neu, csv_writer, tweets_no)

			elif("sympathetic" in tweet.full_text or "helpful" in tweet.full_text or "forgiving" in tweet.full_text):
				opn = 0
				con = 0
				ext = 0
				agr = 1
				neu = 1
				tweets_no = inputdata(text.encode('ascii', errors='ignore'), opn, con, ext, agr, neu, csv_writer, tweets_no)

			else:
				opn = 0
				con = 0
				ext = 0
				agr = 0
				neu = 1
				tweets_no = inputdata(text.encode('ascii', errors='ignore'), opn, con, ext, agr, neu, csv_writer, tweets_no)



	csvf.close()

def main():
	api_key='hrCZw0mamHtJFDBHmfjwJQ5Kz'
	api_secret_key='tZZnRILYmnQ7NUb5VVwNE2L08P4qDuv6t10E6awyzMlhIAsIzk'
	access_token='1334547919-uD5Z2yOYdV6nQaY65eYmrxvxDbRxBQTjmT5oyTi'
	access_token_secret='mEKnylZkbHIuZjnlTisblNfiNq78sbzOI6kzVRBJ9n71t'
	auth = tweepy.OAuthHandler(api_key, api_secret_key)
	auth.set_access_token(access_token, access_token_secret)
	api = tweepy.API(auth, wait_on_rate_limit=True)
	print('Credentials Successful')
	dataset_create(api)

##### Standard boilerplate to call the main() function to begin
##### the program.
if __name__=='__main__':
	main()