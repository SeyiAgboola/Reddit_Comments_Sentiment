#Sentiment Calculator

#Collect file locations of csv files in folder
#Loop through each file and
    #Loop through each comment and
        #Run sentiment analysis
    #Save as new dataframe
    #Store dataframe elsewhere
    #Calculate a list of averages
    #Append list to dictionary of Overall Stats
    #Append Post ID to dictionary of Overall Stats

#Store Sentiment Dataframe in CSV

print("Importing modules....")
import csv #open csv files
import pandas as pd #data manipulation
import sys #csv files in folder
import datetime #converting timestamps
import requests #for sentiment
from nltk.tokenize import sent_tokenize, word_tokenize
import os #access filenames
import time #Track execution time

import string
from collections import Counter
from nltk.corpus import stopwords

stopWords = set(stopwords.words("english"))

#--------------------BUILD SENTIMENT ANALYSIS FUNCTIONS-----------------#
#Function removes punctuation and stopwords and returns list of words.
def refine(text):
    filtered = []
    nopunc = [char for char in text if char not in string.punctuation] #remove punctuation
    nopunc = "".join(nopunc)
    tokens = word_tokenize(nopunc) #split into list of words
    wordsFiltered = [word for word in tokens if word.lower() not in stopWords]
    #extra stopwords would go here
    #('game', 612), ('like', 450), ('games', 343),
    #('people', 223), ('dont', 220), ('really', 187), ('get', 178), ('one', 174), ('conference', 169), ('think', 161), ('Im', 154),
    #[('game', 456), ('like', 355), ('games', 207), ('looks', 152), ('really', 143), ('world', 138), ('people', 138),('one', 120) ('think', 119), ('dont', 112), ('one', 110), ('would', 98), ('get', 96),
    #('much', 95), ('even', 90), ('make', 88), ('way', 85), ('pretty', 82), ('see', 78), ('thing', 77), ('time', 75), ('actually', 75), ('going', 73)]
    return wordsFiltered

#Function returns 30 most common words.
def most_common(text):
    threadCounter = Counter()
    refined = refine(text) #clean, remove stopwords
    threadCounter.update(refined) #update thread counter when new words
    return threadCounter.most_common(30)

#Function 
def low_effort(text):
    filtered = []
    nopunc = [char for char in text if char not in string.punctuation] #remove punctuation
    nopunc = "".join(nopunc)
    tokens = word_tokenize(nopunc) #split into list of words
    if len(tokens) < 6 or len(nopunc) < 140:
        label = "low effort"
    else:
        label = "high effort"
    return label


#Hu Liu Sentiment Build
#Return list of words within URL
def get_posnegWords(url):
    words = requests.get(url).content.decode('latin-1')
    word_list = words.split('\n')
    index = 0
    while index < len(word_list):
        word = word_list[index]
        if ';' in word or not word:
            word_list.pop(index)
        else:
            index+=1
    return word_list

#URLs for Positive and Negative words for Hu Liu Model
p_url = 'http://ptrckprry.com/course/ssd/data/positive-words.txt'
n_url = 'http://ptrckprry.com/course/ssd/data/negative-words.txt'
positive_words = get_posnegWords(p_url)
negative_words = get_posnegWords(n_url)
print('Within Hu and Liu\'s sentiment analysis lexicon:')
print('There are ' + str(len(positive_words)) + ' positive words and ' + str(len(negative_words)) + ' negative words' )

#Track scores for no. of positive/negative words and Return final scores
def huLiu_sentiment(text):
    posTrack = 0
    negTrack = 0
    sentiment_field = list()
    for word in word_tokenize(text):
        if word in positive_words:
            posTrack+=1
        if word in negative_words:
            negTrack+=1
    
    pos = posTrack/len(word_tokenize(text))
    neg = negTrack/len(word_tokenize(text))
    difference = (posTrack-negTrack)/len(word_tokenize(text))
   
    sentiment_field.extend((pos,neg,difference))
    return sentiment_field

#NRC Sentiment Build
#Builds NRC Word dictionary
def get_nrc_words():
    #check location of this file
    nrc = "\\NRC-emotion-lexicon-wordlevel-alphabetized-v0.92.txt"
    count=0 
    emotion_dict=dict() 
    with open(nrc,'r') as f: 
        all_lines = list() 
        for line in f: 
            if count < 46: 
                count+=1
                continue
            line = line.strip().split('\t')
            if int(line[2]) == 1: 
                if emotion_dict.get(line[0]): 
                    emotion_dict[line[0]].append(line[1]) 
                else:
                    emotion_dict[line[0]] = [line[1]]
        return emotion_dict

emotion_dict = get_nrc_words()

#Using NRC Emotion words analyse text within argument and return a dictionary of emotion scores
def emotion_analyzer(text,emotion_dict=emotion_dict): 
    emotions = {x for y in emotion_dict.values() for x in y} #return set based on the following for-loops
    emotion_count = dict()
    for emotion in emotions:
        emotion_count[emotion] = 0 #sets each emotion e.g. anger, fear at 0

    total_words = len(text.split()) #splits text into list then returns total number of words
    for word in text.split(): #for each word in list of words
        if emotion_dict.get(word): #if that word is listed  in emotion_dict
            for emotion in emotion_dict.get(word): #for each emotion in dictionary of emotions (all currently set to zero)
                emotion_count[emotion] += 1/len(text.split()) 

    #sort emotions into ascending order top to bottom
    from collections import OrderedDict
    sorted_emotions = OrderedDict(sorted(emotion_count.items(), key=lambda t: t[1], reverse=True))
    return sorted_emotions

#Vader Comparison Build
def vader_comparison(texts):
    from nltk import sent_tokenize
    from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
    headers = ['pos','neg','neu','compound']
    analyzer = SentimentIntensityAnalyzer()
    sentences = sent_tokenize(texts)
    pos=compound=neu=neg=0
    for sentence in sentences:
        vs = analyzer.polarity_scores(sentence) 
        pos+=vs['pos']/(len(sentences)) #positive = total cumulative positive score / no. of sentences = average positive score
        compound+=vs['compound']/(len(sentences))
        neu+=vs['neu']/(len(sentences))
        neg+=vs['neg']/(len(sentences))
    vader_scores = {'v_positive':pos,'v_negative':neg,'v_neutral':neu,'v_compound':compound}
    #sort emotions into ascending order top to bottom
    from collections import OrderedDict
    vader_scores = OrderedDict(sorted(vader_scores.items(), key=lambda t: t[0], reverse=True)) #changed to [0] to order by key alphabetically
    return vader_scores

#Creates new dataframe of sentiments from file
def add_sentiment_rows(file, folder):
    #Open File
    df = pd.read_csv(file, encoding="ISO-8859-1") #Open CSV in read mode
    #Define whether it's Top Comments or All Comments
    if folder == "Comments":
        post_id = file.replace("\\Comments\\","")
        comments = df["All Comments"]
    elif folder == "Top Comments":
        post_id = file.replace("\\Top Comments\\","")
        comments = df["Top Comment"]
    #Assign Post ID to post_id
    post_id = post_id.replace(".csv", "")
    print(str(post_id) + " has been opened for " + folder)
    #Create new dictionary to store Sentiments for each comment
    new_df = {}
    #alist, blist, clist, dlist, elist = ([] for i in range(5))
    (new_df['v_positive'], new_df['v_negative'], new_df['v_neutral'], new_df['v_compound'], new_df['Hu_pos'], new_df['Hu_neg'], new_df['Hu_diff'],
    new_df['nrc_positive'], new_df['nrc_negative'], new_df['nrc_fear'], new_df['nrc_trust'], new_df['nrc_anger'], new_df['nrc_joy'],
    new_df['nrc_anticipation'], new_df['nrc_sadness'], new_df['nrc_disgust'], new_df['nrc_surprise']) = ([] for i in range(17))
    #create a dictionary entry = common words
    #add all words from each comment to total words
    #run common words
    #Run Sentiment Analysis on each comment
    for comment in comments:
        #remove low effort comments
        if low_effort(comment) == "low effort":
            continue
        vader = vader_comparison(comment)
        new_df['v_positive'].append(vader['v_positive'])
        new_df['v_negative'].append(vader['v_negative'])
        new_df['v_neutral'].append(vader['v_neutral'])
        new_df['v_compound'].append(vader['v_compound'])
        #huLiu_sentiment(text) returns sentiment_field.extend((pos,neg,difference))
        huLiu = huLiu_sentiment(comment)
        new_df['Hu_pos'].append(huLiu[0])
        new_df['Hu_neg'].append(huLiu[1])
        new_df['Hu_diff'].append(huLiu[2])
        #('positive','negative','fear','trust','anger','joy','anticipation','sadness','disgust','surprise')
        #emotion_analyzer(text,emotion_dict=emotion_dict)
        nrc = emotion_analyzer(comment)
        new_df['nrc_positive'].append(nrc['positive'])
        new_df['nrc_negative'].append(nrc['negative'])
        new_df['nrc_fear'].append(nrc['fear'])
        new_df['nrc_trust'].append(nrc['trust'])
        new_df['nrc_anger'].append(nrc['anger'])
        new_df['nrc_joy'].append(nrc['joy'])
        new_df['nrc_anticipation'].append(nrc['anticipation'])
        new_df['nrc_sadness'].append(nrc['sadness'])
        new_df['nrc_disgust'].append(nrc['disgust'])
        new_df['nrc_surprise'].append(nrc['surprise'])
        
    #Turn dictionary into a Dataframe    
    new_frame = pd.DataFrame.from_dict(new_df)
    #Turn Comments from original series into Dataframe
    comments_frame = comments.to_frame()
    #Merge Dataframes of Comments and Sentiments
    merged_frame = pd.concat([comments_frame, new_frame], axis=1)
    return post_id, merged_frame


#Calculate Mean Averages of each Column in dataframe and return as list

def averages(data_frame):
    full_text = ""
    info = []

    all_comments = data_frame['All Comments'].tolist()
    for i in all_comments:
        full_text+=i
        
    common_words = most_common(full_text)

    vpos_mean = data_frame['v_positive'].mean()
    vneg_mean = data_frame['v_negative'].mean()
    vneu_mean = data_frame['v_neutral'].mean()
    vcomp_mean = data_frame['v_compound'].mean()
    
    hpos_mean = data_frame['Hu_pos'].mean()
    hneg_mean = data_frame['Hu_neg'].mean()
    hdiff_mean = data_frame['Hu_diff'].mean()
    
    npos_mean = data_frame['nrc_positive'].mean()
    nneg_mean = data_frame['nrc_negative'].mean()
    nfear_mean = data_frame['nrc_fear'].mean()
    ntrust_mean = data_frame['nrc_trust'].mean()
    nanger_mean = data_frame['nrc_anger'].mean()
    njoy_mean = data_frame['nrc_joy'].mean()
    nantic_mean = data_frame['nrc_anticipation'].mean()
    nsad_mean = data_frame['nrc_sadness'].mean()
    ndisg_mean = data_frame['nrc_disgust'].mean()
    nsurpr_mean = data_frame['nrc_surprise'].mean()


    info.extend((vpos_mean, vneg_mean, vneu_mean, vcomp_mean, hpos_mean, hneg_mean, hdiff_mean, npos_mean,
    nneg_mean, nfear_mean, ntrust_mean, nanger_mean, njoy_mean, nantic_mean, nsad_mean, ndisg_mean, nsurpr_mean, common_words))
    return info
    
def update_stats(post_id, sentiments):
    posts_stats['Most Common Words'].append(sentiments[17])

    posts_stats['Vader Positive'].append(sentiments[0])
    posts_stats['Vader Negative'].append(sentiments[1])
    posts_stats['Vader Neutral'].append(sentiments[2])
    posts_stats['Vader Comp'].append(sentiments[3])
    
    posts_stats['Hui Positive'].append(sentiments[4])
    posts_stats['Hui Negative'].append(sentiments[5])
    posts_stats['Hui Difference'].append(sentiments[6])
    
    posts_stats['NRC Positive'].append(sentiments[7])
    posts_stats['NRC Negative'].append(sentiments[8])
    posts_stats['NRC Fear'].append(sentiments[9])
    posts_stats['NRC Trust'].append(sentiments[10])
    posts_stats['NRC Anger'].append(sentiments[11])
    posts_stats['NRC Joy'].append(sentiments[12])
    posts_stats['NRC Anticipation'].append(sentiments[13])
    posts_stats['NRC Sad'].append(sentiments[14])
    posts_stats['NRC Disgust'].append(sentiments[15])
    posts_stats['NRC Surprise'].append(sentiments[16])

    posts_stats['Post ID'].append(post_id)
    print(str(post_id) + " sentiment averages have been calculated.")


#Create dictionary to store averages for each file
posts_stats = {}
#alist, blist, clist, dlist, elist = ([] for i in range(5))
(posts_stats['Vader Positive'], posts_stats['Vader Negative'], posts_stats['Vader Neutral'], posts_stats['Vader Comp'],
 posts_stats['Hui Positive'], posts_stats['Hui Negative'], posts_stats['Hui Difference'], posts_stats['NRC Positive'], posts_stats['NRC Negative'],
 posts_stats['NRC Fear'], posts_stats['NRC Trust'], posts_stats['NRC Anger'], posts_stats['NRC Joy'], posts_stats['NRC Anticipation'],
 posts_stats['NRC Sad'], posts_stats['NRC Disgust'], posts_stats['NRC Surprise'], posts_stats['Post ID'],
 posts_stats['Most Common Words']) = ([] for i in range(19))
    

#-------------------------Execute above code--------------------------------------
print("Here we go")
location = "\\Comments\\"
comms_list = os.listdir(location)
comms_file_list = []
#create list of file locations of comments
for filename in comms_list:
    comms_file_list.append(location + filename)
   
print("List of file dictories have been created")
counter = 0 
for file in comms_file_list:
    start_point = time.time()
    start_time = time.time()
    #remove stopwords, 140 characters, add most common words
    post_id, comms_sents = add_sentiment_rows(file, "Comments") #add_sentiment_rows(file, folder)
    comms_sents.to_csv("\\Sentiments\\" + str(post_id) + "_sentiments.csv")
    means = averages(comms_sents)
    update_stats(post_id, means)
    counter+=1
    if counter % 10 == 0:
        print("Currently on " + str(counter) + " with Post ID " + str(post_id))
        print("--- %s minutes ---" % ((time.time() - start_time)*60)) #fix timings

ult_frame = pd.DataFrame.from_dict(posts_stats)
#---------------------------------------------------------------
print("See below shape of Ultimate Sentiments Dataframe")
print(ult_frame.shape) #check shape
print("Time to upload final sentiment file")
ult_frame.to_csv("\\Sentiment_All_Comments_Done.csv")
print("Program executed in --- %s minutes ---" % ((time.time() - start_point)/60))
