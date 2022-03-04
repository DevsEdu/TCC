from youtube_comment_scraper_python import *
import pandas as pd

link = input("Link do video: ")
arq_name = input("Nome do arquivo: ")

youtube.open(link)

response, data = [],[]
aux = True
last = None
count = False

while(aux):
    response = youtube.video_comments()

    if(last == response['body'][-1]):
        data = response['body']

        if (count == 0):
            count = 1
            continue
        
        break
        
    count = False        

    last = response['body'][-1]

df = pd.DataFrame(data)
df.to_csv(arq_name)