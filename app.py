from flask import Flask, jsonify, redirect
from sklearn.externals import joblib
from flask import Flask, render_template, request, url_for
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import LabelEncoder
# from flask_pymongo import PyMongo
from pymongo import MongoClient 
from bson.objectid import ObjectId


app = Flask(__name__)

# app.config["MONGO_URI"] = "mongodb://sainttobs:sainttobs123@ds117109.mlab.com:17109/project_erlaters"
# app.config['MONGO_DBNAME'] = 'project_erlaters'

# # Connect to MongoDB using Flask's PyMongo wrapper
# mongo = PyMongo(app)
# db = mongo.db
# col = mongo.db["books"]
# print ("MongoDB Database:", mongo.db)

client = MongoClient("mongodb://sainttobs:sainttobs123@ds117109.mlab.com:17109/project_erlaters")
db = client.project_erlaters
print(db)

data = pd.read_csv('book32-listing.csv',encoding = "ISO-8859-1")

columns = ['Id', 'Image', 'Image_link', 'Title', 'Author', 'Class', 'Genre']
data.columns = columns

books = pd.DataFrame(data['Title'])
author = pd.DataFrame(data['Author'])
genre = pd.DataFrame(data['Genre'])

data['Author'] = data['Author'].fillna('No Book')
data['Title'] = data['Title'].fillna('No Book')

feat = ['Genre']
for x in feat:
    le = LabelEncoder()
    le.fit(list(genre[x].values))
    genre[x] = le.transform(list(genre[x]))
    
data['everything'] = pd.DataFrame(data['Title'] + ' ' + data['Author'])

# from nltk.corpus import stopwords
# stop = list(stopwords.words('english'))

# def change(t):
#     t = t.split()
#     return ' '.join([(i) for (i) in t if i not in stop])

# data['everything'].apply(change)    

print (data['everything'][0] + " " + le.inverse_transform([0])[0])

vectorizer = TfidfVectorizer(min_df=2, max_features=70000, strip_accents='unicode',lowercase =True,
                            analyzer='word', token_pattern=r'\w+', use_idf=True, 
                            smooth_idf=True, sublinear_tf=True, stop_words = 'english')
vectors = vectorizer.fit_transform(data['everything'])   
print (vectors.shape) 

# def redirect_url():  
#     return request.args.get('next') or \  
#            request.referrer or \  
#            url_for('form_submit')

@app.route('/')
def form():
	# Display all books in Database
    books = db.books.find()
    return render_template('form_submit.html', books = books)

#return render_template('form_action.html', book=book)

@app.route('/signin')
def signin():	
	return render_template('admin.html')

@app.route('/login', methods=['POST'])
def login():
	name = request.form['name']
	password = request.form['password']
	if(name == 'admin' and password == 'pass123'):
		books = db.books.find()
		return render_template('dashboard.html', books = books)
	else:
		return redirect('/')


@app.route('/dashboard')
def dashboard():
	books = db.books.find()
	return render_template('dashboard.html', books = books)


@app.route('/delete/<Id>', methods=['GET'])
def delete(Id):
	print(Id)
	books = db.books
	books.delete_one({'_id' : ObjectId(Id)})
	return redirect('/dashboard')


@app.route('/predict', methods=['POST'])
def predict():
	s = request.form['book']
	b = request.form['bookurl']
	text = []
	text.append(s)
	text[0] = text[0].lower()
	arr = (vectorizer.transform(text)) 
	clf = joblib.load('best.pkl')
	prediction = (clf.predict(arr))
	prediction = le.inverse_transform(prediction)[0]
	books = db.books
	s = s.title()
	books.insert({"title":s, 'genre':prediction,'url':b})
	return redirect('/')

if __name__ == '__main__':
	clf = joblib.load('best.pkl')
	app.run(host='0.0.0.0')

