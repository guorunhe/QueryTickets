

# coding: utf-8
"""命令行火车票车看器

Usage:
    tickets [-gdtkz] <from> <to> <date>

Options:
    -h,--help   显示帮助菜单
    -g          高铁
    -d          动车
    -t          特快
    -k          快速
    -z          直达

Example:
    tickets 北京 成都 2016-10-10
    tickets -dg 南京 上海 2016-10-10
"""

from docopt import docopt


from colorama import init,Fore
import prettytable
import re
import requests
def stations():
    "查看城市的编码"
    url = 'https://kyfw.12306.cn/otn/resources/js/framework/station_name.js?station_version=1.8980'
    response = requests.get(url, verify=False)
    stations = re.findall(u'([\u4E00-\u9FA5]+)\|([A-Z]+)', response.text)
    #pprint(dict(stations), indent=4)

    #print(dict(stations).get("邢台"))
    return dict(stations)


def cli():
    "查询区间到达车次"
    """command-line interface"""
    arguments = docopt(__doc__)
    #https://kyfw.12306.cn/otn/lcxxcx/query?purpose_codes=ADULT&queryDate=2016-12-17&from_station=BJP&to_station=SHH
    stationDict=stations()
    from_station=stationDict.get(arguments['<from>'])
    to_station=stationDict.get(arguments['<to>'])
    date=arguments['<date>']
    url='https://kyfw.12306.cn/otn/lcxxcx/query?purpose_codes=ADULT' \
        '&queryDate={}&from_station={}&to_station={}'.format(date,from_station,to_station)
    result=requests.get(url,verify=False)
    available_trains=result.json()['data']['datas']


    #获取参数
    options=''.join([
        key for key,value in arguments.items() if value is True
    ])

    TrainsCollection(available_trains,options).pretty_print()

init()
class TrainsCollection:
    header='车次 车站 时间 历时 一等 二等 软卧 硬卧 硬座 无座'.split()

    def __init__(self,available_trains,options):
        """查询到的火车班次集合
        :param available_trains: 一个列表, 包含可获得的火车班次, 每个
                                 火车班次是一个字典
        :param options: 查询的选项, 如高铁, 动车, etc...
        """
        self.available_trains=available_trains
        self.options=options

    def _get_duration(self,raw_train):
        """获得区间"""
        duration=raw_train.get('lishi').replace(':','小时')+'分'
        if duration.startswith('00'):
            return duration[4:]
        elif duration.startswith('0'):
            return duration[1:]
        return duration

    @property
    def trains(self):
        for row_train in self.available_trains:
            train_no=row_train['station_train_code']
            initial=train_no[0].lower()
            if not self.options or initial in self.options:
                train=[
                    train_no,
                    '\n'.join([Fore.GREEN+row_train['from_station_name']+Fore.RESET,Fore.RED+row_train['to_station_name']+Fore.RESET]),
                    '\n'.join([Fore.GREEN+row_train['start_time']+Fore.RESET,Fore.RED+row_train['arrive_time']+Fore.RESET]),
                    self._get_duration(row_train),
                    row_train['zy_num'],
                    row_train['ze_num'],
                    row_train['rw_num'],
                    row_train['yw_num'],
                    row_train['yz_num'],
                    row_train['wz_num'],
                ]
                yield train


    def pretty_print(self):
        pt=prettytable.PrettyTable()
        pt._set_field_names(self.header)
        for train in self.trains:
            pt.add_row(train)
        print(pt)



if __name__=='__main__':
    cli()