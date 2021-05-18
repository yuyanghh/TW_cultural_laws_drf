from django.http import JsonResponse
from django.db import transaction
from rest_framework.generics import GenericAPIView

import datetime
import requests as rq
import pandas as pd
from bs4 import BeautifulSoup


class ExecutorView(GenericAPIView):
    def post(self, request, *args, **krgs):
        data = request.data
        result = {}

        # crawler methods
        def parse_chinese_date(date_string):
            chinese_year = int(date_string.split('年')[0])
            chinese_month = int(date_string.split('年')[1].split('月')[0])
            chinese_day = int(date_string.split('月')[1].split('日')[0])
            return datetime.date(chinese_year+1911, chinese_month, chinese_day)

        def find_by_content(soup, tag, content):
            target = soup.find(tag, text=content)
            result = ''
            if target:
                result = target.parent.parent.select(
                    'td')[1].get_text().strip(' \t\n\r')
            return result

        def query_executor_at_moe(executor_name):
            df = pd.read_csv('./assets/u1_new_109.csv')
            executor = df.query(
                '學校名稱.str.contains(@executor_name)', engine='python').head(1)
            result['name'] = executor['學校名稱'].to_string().split(' ').pop()
            result['address'] = executor['地址'].to_string().split(' ').pop()
            result['tel'] = executor['電話'].to_string().split(' ').pop()
            result['url'] = executor['網址'].to_string().split(' ').pop()

        def query_executor_at_twincn(executor_name):
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 6.0; WOW64; rv:24.0) Gecko/20100101 Firefox/24.0'}
            executor_query_response = rq.get(
                'https://www.twincn.com/Lq.aspx?q='+executor_name, headers=headers)
            executor_query_html_doc = executor_query_response.text
            executor_query_soup = BeautifulSoup(
                executor_query_html_doc, 'html.parser')
            possible_executors = executor_query_soup.find_all(
                lambda tag: tag.name == 'a' and executor_name in tag.text)
            possible_executor_name = '隨機' * 100
            executor_ref_url = ''
            for possible_executor in possible_executors:
                if len(possible_executor.get_text()) < len(possible_executor_name):
                    possible_executor_name = possible_executor.get_text()
                    executor_ref_url = possible_executor.get('href')
            executor_url = 'https://www.twincn.com' + executor_ref_url
            executor_response = rq.get(executor_url, headers=headers)
            executor_html_doc = executor_response.text
            executor_soup = BeautifulSoup(executor_html_doc, 'html.parser')
            executor_data_table = executor_soup.select('.table-responsive')[0]
            result['accounting_nr'] = find_by_content(
                executor_soup, 'strong', '統一編號（統編）　')
            result['name'] = find_by_content(
                executor_soup, 'strong', '公司名稱')
            result['responsible'] = find_by_content(
                executor_soup, 'strong', '代表人姓名')
            result['address'] = find_by_content(
                executor_soup, 'strong', '公司所在地')
            result['tel'] = find_by_content(
                executor_soup, 'strong', '電話').split(' ')[0]
            result['status'] = find_by_content(
                executor_soup, 'strong', '公司狀況')
            result['stock_amount'] = find_by_content(
                executor_soup, 'strong', '資本總額(元)')
            result['register_organization'] = find_by_content(
                executor_soup, 'strong', '登記機關')
            result['setup_date'] = parse_chinese_date(
                find_by_content(executor_soup, 'strong', '核准設立日期'))
            result['last_change_date'] = parse_chinese_date(
                find_by_content(executor_soup, 'strong', '最後核准變更日期'))
        try:
            executor_name = data['name']
            is_school = executor_name.find('大學') > 0 or executor_name.find(
                '學院') > 0 or executor_name.find('學校') > 0
            if is_school:
                # https://depart.moe.edu.tw/ed4500/News.aspx?n=63F5AB3D02A8BBAC&sms=1FF9979D10DBF9F3
                query_executor_at_moe(executor_name)
            else:
                query_executor_at_twincn(executor_name)
        except Exception as e:
            result = {'error': str(e)}
        return JsonResponse(result)
