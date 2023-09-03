from flask import Flask,render_template,url_for
from Config import Configurations


class MyContest:
    config=Configurations()
    client=config.client

    def show_contest(self,email):
        database=self.client['user_contest_data']
        collection=database[email]

        data={
            'title':[],
            'Type':[],
            'options':[],
            'Date':[],
            'URL':[],
            'price':[]
        }
        all_documents = collection.find()

        for doc in all_documents:
            for key,values in doc.items():
                if key in data:
                    data[key].append(values)
        print(data)



        return render_template('mycontest.html',data=data,count=len(data['title']))