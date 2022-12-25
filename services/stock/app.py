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
from flask import Flask, Blueprint
from flask_apispec import marshal_with, use_kwargs
from marshmallow import fields
from datetime import datetime
from sqlalchemy import UniqueConstraint, Column, text, Integer, String, Date, DateTime, Enum, func
from sqlalchemy.orm import validates, Session

from models.stock import StockProfile 
from models.var import engine


session = Session(engine)
print("__name__", __name__)
app = Flask(__name__)
blueprint = Blueprint('/api', __name__)

@app.route("/api/stock_profile", methods=('GET',))
@use_kwargs({'code': fields.Str()})
def get_stock_profile(code=None):
    print("code", code)
    print('jisd')
    res = {
        'text': "Hello, World!"
    }
    stock_code = '000004'
    stock = session.query(StockProfile).where(StockProfile.stock_code == stock_code).all()
    print("stock", stock)
    return stock[0].stock_name


# export FLASK_APP=hello.py
# export FLASK_ENV=development
# flask run
