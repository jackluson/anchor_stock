import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt
from scipy import stats
from base.kline import Kline

'''
相关系数绝对值 ：
0.8-1.0 极强相关
0.6-0.8 强相关
0.4-0.6 中等程度相关
0.2-0.4 弱相关
0.0-0.2 极弱相关或无相关
'''


class Statisticer(Kline):
    def __init__(self, symbol, name):
        super().__init__(symbol, name)
        end_date = '2022-04-01'
        # end_date = datetime.now().strftime("%Y-%m-%d")
        ts = pd.Timestamp(end_date).timestamp()
        # 测量过去半年的相似度
        begin_date = datetime.fromtimestamp(
            ts - 180 * 24 * 3600).strftime("%Y-%m-%d")
        self.format_params({
            'begin_date': begin_date,
            'end_date': end_date,
            'period': 'day'
        })
        self.get_kline_data()

    def ks_test(self, show=False):
        u = self.df_kline['close'].mean()  # 计算均值
        std = self.df_kline['close'].std()  # 计算标准差
        res = stats.kstest(self.df_kline['close'], 'norm', (u, std))
        # print('res', u, std, res[1])
        self.pass_ks_test = res[1] > 0.05

        if show:
            fig = plt.figure(figsize=(10, 6))
            ax1 = fig.add_subplot(2, 1, 1)  # 创建子图1
            ax1.scatter(self.df_kline.index, self.df_kline['close'].values)
            plt.grid()
            ax2 = fig.add_subplot(2, 1, 2)  # 创建子图2
            self.df_kline['close'].hist(bins=30, alpha=0.5, ax=ax2)
            self.df_kline['close'].plot(kind='kde', secondary_y=True, ax=ax2)
            plt.grid()
            plt.show()
    # def ma_line(day):
        

class Correlator():
    def __init__(self):
        self.standard_len = len(Statisticer('SH000300', '沪深300').df_kline)

    def set_compare(self, compares, exist_compares=[]):
        if not isinstance(compares, pd.DataFrame):
            compares = pd.DataFrame(compares)
        compare_list = []
        exist_symbols = []
        for item in exist_compares:
            symbol = item.get('symbol')
            exist_symbols.append(symbol)
            name = item.get('name')
            compare = Statisticer(symbol, name)
            compare_list.append(compare)
        for index, item in compares.iterrows():
            item_symbol = item.get('symbol')
            if item_symbol == None:
                item_symbol = item.get('market').upper() + item.get('code')
            if item_symbol in exist_symbols:
                continue
            item_name = item.get('name')
            compare = Statisticer(item_symbol, item_name)
            compare_list.append(compare)
        self.compare_list = compare_list
        return self

    def correlate(self):
        df_compare = pd.DataFrame()
        un_compare_data = []
        for item in self.compare_list:
            if self.standard_len != len(item.df_kline):
                un_compare_data.append({
                    '证券名称': item.name,
                    '证券代码': item.symbol
                })
                continue
            item.ks_test()
            column_name = item.name + '(' + item.symbol + ')'
            df_compare[column_name] = item.df_kline['close'].values
        res = df_compare.corr()
        res_spearman = df_compare.corr(method='spearman')
        res_mean = ((res_spearman + res)/2).round(3)
        # print(res_mean.to_markdown())
        # res_mean.to_csv('data/rise.csv')
        self.res_compare = res_mean

        # print('不参加评比指数有{}名:'.format(len(un_compare_data)))
        if len(un_compare_data) > 0:
            df_uncompare = pd.DataFrame(un_compare_data).set_index("证券名称")
            # print(df_uncompare.to_markdown())
        if len(self.res_compare) <= 1:
            return res_mean
        return (res.iat[0, 1] + res_spearman.iat[0, 1])/2

    def filter_near_similarity(self, threshold=0.6):
        # df = pd.read_csv('data/rise.csv').set_index('Unnamed: 0')
        # print(df)
        df = self.res_compare
        # cur = '商品ETF'
        excludes = []
        for index, item in df.iterrows():
            if index not in excludes:
                for key in item.keys():
                    if key != index and item.get(key) > threshold and key not in excludes:
                        excludes.append(key)
                        df.drop([key], inplace=True)
                        df.drop(columns=[key], inplace=True)
        # print(excludes)
        return df


def main():
    correlator = Correlator('SH000001', 'xx股票')

    print(correlator.log())

    # print('最大回撤持续期：', max_drawdown_calculator.maxdrawdown_period())
    # print('最大回撤修复期', max_drawdown_calculator.maxdrawdown_repair())


if __name__ == '__main__':
    main()
