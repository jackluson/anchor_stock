'''
Desc: K线数据服务
File: /app.py
File Created: Friday, 7th October 2022 1:07:11 am
Author: luxuemin2108@gmail.com
-----
Copyright (c) 2022 Camel Lu
'''
import sys
sys.path.append('./')
import json
from flask import Flask, Blueprint, Response, jsonify
from flask_apispec import marshal_with, use_kwargs
from marshmallow import fields
from datetime import datetime
from sqlalchemy import UniqueConstraint, Column, text, Integer, String, Date, DateTime, Enum, func
from sqlalchemy.orm import validates, Session

from models.stock import StockProfile 
from models.var import engine

def toJSON(self):
    return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)
session = Session(engine)
# print("__name__", __name__)
app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False
blueprint = Blueprint('/api', __name__)

@app.route("/api/stock_profile", methods=('GET',))
@use_kwargs({'code': fields.Str()}, location="query")
def get_stock_profile(code, **kwargs):
    print("code", code, kwargs)
    res = {
        'text': "Hello, World!"
    }
    # stock_code = '000004'
    stock = session.query(StockProfile).where(StockProfile.stock_code == code).all()
    print("stock", stock, stock[0].__dict__)
    # return Response(stock[0].stock_name, mimetype='text/plain')
    res = {
        'stock_name': stock[0].__dict__.get('stock_name'),
        'classi_name': stock[0].__dict__.get('classi_name'),
    }
    print(type(jsonify(res)))
    return jsonify(res)

# export FLASK_APP=hello.py
# export FLASK_ENV=development
# flask run
