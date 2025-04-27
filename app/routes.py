from app import app
from flask import render_template
  
  

@app.route('/')
@app.route('/index')
def get_index_page():
    return render_template('index.html')

@app.route('/test')
def get_test_page():
    return render_template('test.html')