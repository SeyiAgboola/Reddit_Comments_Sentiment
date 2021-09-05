#Reddit Comment Extractor

print("Importing modules....")
import csv #Access CSVs
import pandas as pd #Manipulate data
import praw #Access Reddit
from praw.models import MoreComments #Access Comments
import sys #for .translate bmp code
import datetime #converting timestamps
import redcreds #Access Reddit Credentials - you can name your file whatever you like
import os.path #Access file directories
import time


#Assign Reddit Credentials
#-------------------------------------------- 
r = praw.Reddit(username = redcreds.username,
	    password = redcreds.password,
	    client_id = redcreds.client_id,
	    client_secret = redcreds.client_secret,
	    user_agent = redcreds.user_agent)

print("Credentials have been accepted")


#Open file that contains your reddit submissions
#--------------------------------------------
print("Input name of file you wish to observe.... Add .csv on the end please")
location = "\\Reddit\\" #Input your local directory folder where csv is stored
filename = input() #Reddit Submissions.csv
file = location + filename
df = pd.read_csv(file, encoding="ISO-8859-1") #Assign csv to dataframe - encoding ISO-8859-1 is recommended or utf-8
#Columns >> 
#Post ID, Title, Url, Author, Score, Publish Date, Upvote Ratio, Total No. of Top Comments, Total No. of Comments, Flair

#Assign columns
#---------------------------------------------
links = df['Url']
sub_ids = df['Post ID']
print("Submission URLs and IDS have been assigned to lists")

#Run Checks
#--------------------------]
print("File has {0} rows, {1} columns".format(df.shape[0],df.shape[1]))
print("Columns within file " + str(df.columns))
print(df.head())

#Build function to create file to store comments
#---------------------------------------------
def commentFileCreator(title,comments,topcomments): #Pull the comments and unique values into argument
    filename = "\\Reddit Comments\\" + title + "_comments.csv" #Input where to store your Reddit comment files
    if os.path.isfile(filename) != True:
        with open(filename, 'w', newline='', encoding="utf-8") as file_a:
            a = csv.writer(file_a, delimiter=',')
            headers = ["All Comments"]
            a.writerow(headers)
	    #writerow prints each iterable (value in a list or character in a string) into each column in a csv row
            for comment in comments: #for each comment in LIST of comments
                a.writerow([comment])
                #write to that csv file the row - comment is in []
            print(str(len(comments)) + " comments have been uploaded for " + str(title))
			
    top_filename = "\\Top Comments\\" + title + "_topcomments.csv"
    if os.path.isfile(top_filename) != True:
        with open(top_filename, 'w', newline='', encoding="utf-8") as file_b:
            a = csv.writer(file_b, delimiter=',')
            topheaders = ["Top Comment ID","Top Score","Top Comment","Top Replies"]
            a.writerow(topheaders)
            for top in topcomments:
                #for each dict entry in topcomments
                a.writerow(topcomments[top])
                #write the value attached to that dict entry (which is a tuple list) into a row for each iterable (list value)
            print(str(len(topcomments)) + " top comments have been uploaded for " + str(title))

#Create function for extracting comments from submission
#-------------------------------------------------------
def extractComments(subpost):
    post = r.submission(id=subpost)
    title = str(subpost) #Assign reddit submission id as title
    allComments = list()
    topDict = dict()
    topCounter = 0
    try:
        post.comments.replace_more(limit=None, threshold=0)
        for comment in post.comments.list(): #The comments.list() removes restriction to collect all comments including replies
            allComments.append(comment.body) 
    except:
        print("An error has occured with " + str(subpost) + ". Will attempt again in 30 seconds.")
        time.sleep(30)
        post.comments.replace_more(limit=None, threshold=0)
        for comment in post.comments.list():
            allComments.append(comment.body) 


    #Collect only Top Comments
    post.comments.replace_more(limit=None, threshold=0) #remove MoreComments limit
    for top in post.comments:
        topCounter+=1 
        tbody = top.body
        tscore = top.score
        tid = top.id
        treplies = [] #For each top comment we create a empty list to store it's replies
        replyCounter = 0
        for reply in top.replies:
            replyCounter+=1
            treplies.append("Reply " + str(replyCounter) + " of Top level Comment " + str(topCounter) + " : " + str(reply.body))
        #take each top comment and extract body, upvote ratio, score and assign to dictionary key(comment id)
        topDict[tid] = ((tid,tscore,tbody,treplies))
    #upload to file
    commentFileCreator(title,allComments,topDict)

for i in sub_ids:
    extractComments(i)
#extractComments('8puow6')
