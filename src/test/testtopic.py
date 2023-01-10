import pandas as pd 
import numpy as np
from bertopic import BERTopic
import sqlite3


conn = sqlite3.connect("./database.sqlite")
keyword = "Social Media"

query = f"""SELECT title FROM scrapping_data where title like '%{keyword}%' or abstract like '%{keyword}%' """
counter_data = conn.execute("select * FROM scrapping_data where title like ? or abstract like ?",["%"+keyword+"%","%"+keyword+"%"]).fetchall()
df = pd.read_sql_query(query, conn)

df.columns = ['title']
df.shape
# select only 6000 tweets 
df = df[0:6000]

# create model 
model = BERTopic(language="indonesian", calculate_probabilities=True, verbose=True)
 
#convert to list 
docs = df.title.to_list()
 
topics, probabilities = model.fit_transform(docs)
print(model.get_topic_info())
freq = model.get_topic_info().head(5)

# model.get_topic(6)
print(len(freq))

# model.visualize_topics()
# model.visualize_barchart()