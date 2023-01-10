from sentence_transformers import SentenceTransformer
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import pandas as pd 
import sqlite3
import dataframe_image as dfi
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from bertopic import BERTopic
from transformers import AutoConfig, AutoTokenizer, AutoModel
from summarizer import Summarizer

class Clustering:
    def __init__(self, keyword):
        self.keyword = keyword

    def text_summerize(self,init):
        custom_config = AutoConfig.from_pretrained('bert-large-uncased')
        custom_config.output_hidden_states=True
        custom_tokenizer = AutoTokenizer.from_pretrained('bert-large-uncased')
        custom_model = AutoModel.from_pretrained('bert-large-uncased', config=custom_config)

        conn = sqlite3.connect("./database.sqlite")
        findx = conn.execute("select * FROM scrapping_data where (id=?)",[init]).fetchone()
        body = ""
        if findx is not None:
            body = findx[5]
            model = Summarizer(custom_model=custom_model, custom_tokenizer=custom_tokenizer)
            result = model(body, min_length=60)
            full = ''.join(result)
            body = full
        
        return body

    def topicModel(self):
        self.topicModelTitle()
        self.topicModelAbstract()


    def topicModelTitle(self):
        conn = sqlite3.connect("./database.sqlite")

        query = f"""SELECT title FROM scrapping_data where title like '%{self.keyword}%'"""
        counter_data = conn.execute("select * FROM scrapping_data where title like ? ",["%"+self.keyword+"%"]).fetchall()
        if len(counter_data) > 10:
            df = pd.read_sql_query(query, conn)
            df.columns = ['title']
            df = df[0:6000]

            tm = BERTopic(language="indonesian",min_topic_size=2,top_n_words=6)
            docs = df.title.tolist()
            topics, probabilities = tm.fit_transform(docs)

            freq = tm.get_topic_info()
            dfi.export(freq,"./assets/images/freq_title.png",max_rows=10)
            
            ltopic = []
            for x in topics:
                if int(x) not in ltopic:
                    ltopic.append(int(x))
                
            tm.get_topic(6)
            tm.visualize_topics(topics=ltopic,top_n_topics=(len(ltopic))).write_html('./assets/html/topics_title.html')

            tm.visualize_barchart(topics=ltopic,top_n_topics=(len(ltopic))).write_html('./assets/html/bars_title.html')


    def topicModelAbstract(self):
        conn = sqlite3.connect("./database.sqlite")

        query = f"""SELECT abstract FROM scrapping_data where abstract like '%{self.keyword}%'"""
        counter_data = conn.execute("select * FROM scrapping_data where abstract like ? ",["%"+self.keyword+"%"]).fetchall()
        if len(counter_data) > 10:
            df = pd.read_sql_query(query, conn)
            df.columns = ['abstract']
            df = df[0:6000]

            tm = BERTopic(language="indonesian",min_topic_size=2,top_n_words=6)
            docs = df.abstract.tolist()
            topics, probabilities = tm.fit_transform(docs)

            freq = tm.get_topic_info()
            dfi.export(freq,"./assets/images/freq_abstract.png",max_rows=10)
            
            ltopic = []
            for x in topics:
                if int(x) not in ltopic:
                    ltopic.append(int(x))
                
            tm.get_topic(6)
            tm.visualize_topics(topics=ltopic,top_n_topics=(len(ltopic))).write_html('./assets/html/topics_abstract.html')

            tm.visualize_barchart(topics=ltopic,top_n_topics=(len(ltopic))).write_html('./assets/html/bars_abstract.html')


    def proses_clustering(self):
        self.title_coy()
        self.abstract_coy()

    def title_coy(self):
        conn = sqlite3.connect("./database.sqlite")

        findexists = conn.execute("select * FROM cluster_iteration where keyword=? and type=?",[self.keyword,"1"]).fetchall()
        if len(findexists) <= 0:
            query = f"""SELECT title FROM scrapping_data where title like '%{self.keyword}%' """
            counter_data = conn.execute("select * FROM scrapping_data where title like ?",["%"+self.keyword+"%"]).fetchall()
            if len(counter_data) > 0:
                df = pd.read_sql_query(query, conn)

                tempArr = []
                for line in df['title']:
                    tempArr.append(line.lower())
                
                if len(counter_data) > 1000:
                    tempArr = tempArr[0:len(counter_data)]
                else:
                    tempArr = tempArr[0:1000]

                model = SentenceTransformer('bert-base-multilingual-cased',cache_folder=None)
                corpus_embeddings = model.encode(tempArr)
                if len(counter_data) > 6:
                    num_clusters = 5
                else:
                    num_clusters = len(counter_data)

                clustering_model = KMeans(n_clusters=num_clusters,init="k-means++",max_iter=100,n_init=1)
                clustering_model.fit(corpus_embeddings)
                cluster_assignment = clustering_model.labels_

                clustered_sentences = [[] for i in range(num_clusters)]
                for sentence_id, cluster_id in enumerate(cluster_assignment):
                    clustered_sentences[cluster_id].append(tempArr[sentence_id])

                for i, cluster in enumerate(clustered_sentences):
                    no = i+1
                    for itm in cluster:
                        conn.execute("insert into cluster_iteration (number, text, keyword, type) values (?, ?, ?, ?)", [no, itm, self.keyword,'1'])
                        conn.commit()

                cluster_df = pd.DataFrame(tempArr, columns = ['title'])
                cluster_df['cluster'] = cluster_assignment
                cluster_df.head()
                
                # dfi.export(cluster_df.head(),"./assets/images/corpus_title.png")

                for itm,row in cluster_df.iterrows():
                    if len(row['title']) > 0 :
                        conn.execute("insert into corpus (cluster, text, type, keyword) values (?, ?, ?, ?)", [row['cluster'], row['title'],'1',self.keyword])
                        conn.commit()

                wc = ' '.join([text for text in cluster_df['title'][cluster_df['cluster'] == 0]])
                wordcloud = WordCloud(width=800, height=500, random_state=21, max_font_size=110).generate(wc)
                fig7 = plt.figure(figsize=(10, 7))
                plt.imshow(wordcloud, interpolation="bilinear")
                plt.axis('off')
                plt.savefig('./assets/images/clustering_title.png')
            
    
    def abstract_coy(self):
        conn = sqlite3.connect("./database.sqlite")

        findexists = conn.execute("select * FROM cluster_iteration where keyword=? and type=?",[self.keyword,"2"]).fetchall()
        if len(findexists) <= 0:
            query = f"""SELECT abstract FROM scrapping_data where abstract like '%{self.keyword}%' """
            counter_data = conn.execute("select * FROM scrapping_data where abstract like ?",["%"+self.keyword+"%"]).fetchall()
            if len(counter_data) > 0:
                df = pd.read_sql_query(query, conn)

                tempArr = []
                for line in df['abstract']:
                    tempArr.append(line.lower())
                
                if len(counter_data) > 1000:
                    tempArr = tempArr[0:len(counter_data)]
                else:
                    tempArr = tempArr[0:1000]

                model = SentenceTransformer('bert-base-multilingual-cased',cache_folder=None)
                corpus_embeddings = model.encode(tempArr)
                if len(counter_data) > 6:
                    num_clusters = 5
                else:
                    num_clusters = len(counter_data)

                clustering_model = KMeans(n_clusters=num_clusters,init="k-means++",max_iter=100,n_init=1)
                clustering_model.fit(corpus_embeddings)
                cluster_assignment = clustering_model.labels_

                clustered_sentences = [[] for i in range(num_clusters)]
                for sentence_id, cluster_id in enumerate(cluster_assignment):
                    clustered_sentences[cluster_id].append(tempArr[sentence_id])

                for i, cluster in enumerate(clustered_sentences):
                    no = i+1
                    for itm in cluster:
                        conn.execute("insert into cluster_iteration (number, text, keyword, type) values (?, ?, ?, ?)", [no, itm, self.keyword,'2'])
                        conn.commit()

                cluster_df = pd.DataFrame(tempArr, columns = ['abstract'])
                cluster_df['cluster'] = cluster_assignment
                cluster_df.head()
                
                # dfi.export(cluster_df.head(),"./assets/images/corpus_abstract.png")

                for itm,row in cluster_df.iterrows():
                    if len(row['abstract']) > 0 :
                        conn.execute("insert into corpus (cluster, text, type, keyword) values (?, ?, ?, ?)", [row['cluster'], row['abstract'],'2',self.keyword])
                        conn.commit()

                wc = ' '.join([text for text in cluster_df['abstract'][cluster_df['cluster'] == 0]])
                wordcloud = WordCloud(width=800, height=500, random_state=21, max_font_size=110).generate(wc)
                fig7 = plt.figure(figsize=(10, 7))
                plt.imshow(wordcloud, interpolation="bilinear")
                plt.axis('off')
                plt.savefig('./assets/images/clustering_abstract.png')
            