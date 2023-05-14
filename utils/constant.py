'''
Desc:
File: /constant.py
Project: utils
File Created: Tuesday, 5th April 2022 8:06:44 pm
Author: luxuemin2108@gmail.com
-----
Copyright (c) 2022 Camel Lu
'''
class Const(object):
    class ConstError(TypeError):
        pass
    
    class ConstCaseError(ConstError):
        pass
    
    def __setattr__(self, name, value):
        if name in self.__dict__: # 判断是否已经被赋值，如果是则报错
            raise self.ConstError("Can't change const.%s" % name)
        # if not name.isupper(): # 判断所赋值是否是全部大写，用来做第一次赋值的格式判断，也可以根据需要改成其他判断条件
        #     raise self.ConstCaseError('const name "%s" is not all supercase' % name)

        self.__dict__[name] = value

const = Const()
const.before_list = [7, 10, 20, 30, 60]
const.index_stock_list = [
    {
        'name': '沪深300',
        'market': 'SH',
        'code': '000300'
    },
    {
        'name': '中证500',
        'market': 'SH',
        'code': '000905'
    },
    {
        'name': '中证1000',
        'market': 'SH',
        'code': '000852'
    },
    {
        'name': '中证全指',
        'market': 'SH',
        'code': '000985'
    },
    {
        'name': '上证指数',
        'market': 'SH',
        'code': '000001'
    },
    {
        'name': '深证成指',
        'market': 'SZ',
        'code': '399001'
    },
    {
        'name': '创业板指',
        'market': 'SZ',
        'code': '399006'
    },
    {
        'name': '科创50',
        'market': 'SH',
        'code': '000688'
    },
    {
        'name': '北证50',
        'market': 'BJ',
        'code': '899050'
    }
]
