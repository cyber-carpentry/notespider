#!/usr/bin/env python
# coding: utf-8

# In[1]:


import numpy as np
import os
import pandas as pd
import json
import re
import networkx as nx
import nltk
import spacy
import urllib.request
from bs4 import BeautifulSoup
from socket import timeout


#  Find the json data files from all available folders: 

# In[2]:


data = []
for root, dirs, files in os.walk(os.getcwd()): 
    for name in files:
        if name.endswith((".json")):
            data.append(os.path.join(root, name))


# Load json files and make a dataframe for text messages: 

# In[3]:


all_data = []
for i in range(len(data)):
    with open(data[i]) as json_file:
        df = pd.read_json(json_file)
        if 'text' in df.columns:
            json_data = pd.DataFrame(df['text'])
            all_data.append(json_data)
all_data = pd.concat(all_data)


# Make a dataframe from rows that contain a link (contain 'http'):

# In[4]:


URL_df = all_data[all_data['text'].str.contains('http')]


# Function which finds URLs for each row in the dataframe:

# In[5]:


def find_url(row):
    text = str(re.sub('>', '', str(row)))
    text = str(re.sub('<', '', text))
    text = str(re.sub("'", '', text))
    text = str(re.sub('"', '', text))
    text = str(re.sub('^', '', text))
    text = str(re.sub(';', '', text))
    text = str(re.sub(r'\)', '', text))
    text = str(re.sub(r'\[', '', text))
    text = str(re.sub(r'\]', '', text))
    text = str(re.sub(r'\n', ' ', text)) 
    text = str(re.sub(r'\\', ' ', text))  
    text = str(re.sub(',', ' ', text))
    
    urls = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', text)
    print(urls)
    return (urls)


# Applying find_url function to the message texts and adding another column to the dataframe for URLs:

# In[6]:


URL_df['URL'] = URL_df['text'].apply(find_url)


# Data cleaning for html pages: removing some characters from the text and split the data by comma

# In[7]:


def str_clean(input):
    output = str(input).replace('[', ',').replace(']', ',').replace("'", ',').replace('(', ',').replace(')', ',')
    output = output.replace('<','').replace('>','').replace('"',',').replace('"', ',').replace(r"\\", ",")
    output = output.split(r'\\|\n|\\\\|,')
    return [output[i] for i in range(len(output)) if len(output[i]) > 2]# ignore words with length shorter than 3


# Loading url page content:

# In[10]:


def visible(element):
    if element.parent.name in ['style', 'style', 'script', '[document]', 'head', 'title']:
        return False
    elif re.match('<!--.*-->', str(element.encode('utf-8'))):
        return False
    return True


def url_loader(link):   
        
    urlBody = []
    try:
        html = urllib.request.urlopen(link, timeout=10)
    except urllib.error.URLError as e:
        html = False
        return False
#     except (HTTPError, URLError) as error:
    except timeout:
        html = False
        return False
    except requests.exception.InvalidURL:
        html = False
        return False


    soup = BeautifulSoup(html)
    data = soup.findAll(text=True)

    result = filter(visible, data)
    for element in result:
        if len(element) > 1:
            urlBody.append((element).strip())
            
    urlBody = max(urlBody, key=len, default='Nan') if 'hackmd' in link else urlBody
    cleanBody = str_clean(urlBody)
    urls_in_body = find_url(str_clean(urlBody))
#     print(urls_in_body)
    return urls_in_body


# Loop over the URL column of the dataframe to pass the URLs to url_loader function and get list of urls from the page contents:

# In[ ]:


for i in range(URL_df['URL'].shape[0]):
    for l in URL_df['URL'].iloc[i]:
#         print(l)
        url_loader(l)


# In[ ]:




