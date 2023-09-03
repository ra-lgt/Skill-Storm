from flask import Flask,render_template,redirect,url_for
from Config import Configurations


class Forum:
    config=Configurations()
    client=config.client

    def post_question(self,username,title,post):
        database=self.client['FORUMS']
        collection=database['Posts']

        collection.insert_one({'Title':title,'Post':post,'Username':username})

        return redirect(url_for('forum'))
    
    def forum_post_data(self):
        database=self.client['FORUMS']
        collection=database['Posts']

        data={
            'Title':[],
            'Post':[],
            'Username':[]
        }

        all_documents = collection.find()

        for document in all_documents:
            for key,value in document.items():
                if key in data:
                    data[key].append(value)
        return data
    
    def forum_post_comment(self,username,post_title,comment):
        database=self.client['FORUMS']
        collection=database[post_title]

        collection.insert_one({'Title':post_title,'Username':username,'Comment':comment})

        return redirect(url_for('forum'))
    
    def forum_comment_data(self):
        database=self.client['FORUMS']
        collection_names = database.list_collection_names()

        data={

        }

        
        for collection_name in collection_names:
                if(collection_name=='Posts'):
                    continue
                collection = database[collection_name]

                for doc in collection.find():
                    if doc['Title'] not in data:
                        data[doc['Title']]=dict()

                        data[doc['Title']]['Username']=list()
                        data[doc['Title']]['Comment']=list()

                    data[doc['Title']]['Comment'].append(doc['Comment'])
                    data[doc['Title']]['Username'].append(doc['Username'])
        return data
        





