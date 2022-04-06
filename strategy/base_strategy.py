import logging

class BaseStrategy(object):

    def __init__(self):
        logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s')

        pass

    def get_source_data(self):
        print('in')
        """
        获取数据
        :return:
        """
        return self

    def compute(self):
        """
        执行策略
        :return:
        """
        return self

    def serialize(self):
        """
        :return: dataFlame
        date money
        """
        return self

    def predict(self):
        """
        预测明天买卖
        :return:
        """
        return self
