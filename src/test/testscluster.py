from sentence_transformers import SentenceTransformer
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import pandas as pd 
import sqlite3
import dataframe_image as dfi
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans


conn = sqlite3.connect("./database.sqlite")
keyword = 'deep learning'
query = f"""SELECT title FROM scrapping_data where title like '%{keyword}%'"""
df = pd.read_sql_query(query, conn)

tempArr = []
for line in df['title']:
    tempArr.append(line.lower())

# print(tempArr)
# print(len(tempArr))
# print(type(tempArr))
tempArr = tempArr[0:1000]

model = SentenceTransformer('bert-base-multilingual-cased',cache_folder=None)
# print(model)
corpus_embeddings = model.encode(tempArr)

# if len(tempArr) < 5:
#     num = len(tempArr)
# else:
#     num = 10
num_clusters = 5
clustering_model = KMeans(n_clusters=num_clusters,init="k-means++",max_iter=100,n_init=1)
clustering_model.fit(corpus_embeddings)
cluster_assignment = clustering_model.labels_

clustered_sentences = [[] for i in range(num_clusters)]
for sentence_id, cluster_id in enumerate(cluster_assignment):
    clustered_sentences[cluster_id].append(tempArr[sentence_id])

def word_cloud(pred_df,label):
    wc = ' '.join([text for text in pred_df['corpus'][pred_df['cluster'] == label]])
    wordcloud = WordCloud(width=800, height=500, random_state=21, max_font_size=110).generate(wc)
    fig7 = plt.figure(figsize=(10, 7))
    plt.imshow(wordcloud, interpolation="bilinear")
    plt.axis('off')
    plt.savefig('./assets/images/clustering.png')

cluster_df = pd.DataFrame(tempArr, columns = ['corpus'])
cluster_df['cluster'] = cluster_assignment
header = cluster_df.head()
print(header)
print("==============")
print(cluster_df)
print("==============")
for itm,row in cluster_df.iterrows():
    print(row['corpus'])
    print(row['cluster'])

# dfi.export(cluster_df.head(),"./assets/images/corpus.png")
# print(cluster_df)
# for itm in cluster_df.head():
#     print(itm)

# word_cloud(cluster_df,0)