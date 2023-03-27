from flask import Flask, request
from api import get_financial_data, get_statistics_data

app = Flask(__name__)

@app.route('/')
def hello():
    return "hello from flask"

@app.route('/api/financial_data')
def get_data():
    return get_financial_data(request.args)
    
@app.route('/api/statistics')
def get_statistics():
    return get_statistics_data(request.args)
    
