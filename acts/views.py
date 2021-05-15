# coding=UTF-8
from django.http import JsonResponse
from django.db import transaction
from rest_framework.generics import GenericAPIView

# from acts.serializers import ActSerializer
# from acts.models import Act

import datetime
from markdownify import markdownify as md
import requests as rq
from bs4 import BeautifulSoup
import pandas as pd

# segment chinese
import jieba
import jieba.analyse
# import jieba.analyse
jieba.set_dictionary('./jieba_dict/include_dict.txt')
jieba.load_userdict('./jieba_dict/cultural_laws_dict.txt')
exclude_dict = './jieba_dict/exclude_dict.txt'


class ActView(GenericAPIView):
    # queryset = Act.objects.all()
    # serializer_class = ActSerializer

    # def get(self, request, *args, **krgs):
    #     acts = self.get_queryset()
    #     serializer = self.serializer_class(acts, many=True)
    #     data = serializer.data
    #     return JsonResponse(data, safe=False)

    def post(self, request, *args, **krgs):
        data = request.data
        result = {}

        # crawler methods
        def parse_chinese_date(date_string):
            chinese_year = int(date_string.split('民國 ')[1].split(' 年')[0])
            chinese_month = int(date_string.split('年 ')[1].split(' 月')[0])
            chinese_day = int(date_string.split('月 ')[1].split(' 日')[0])
            return datetime.date(chinese_year+1911, chinese_month, chinese_day)

        def check_self_with_classname(self, classname):
            if(type(self).__name__ == 'Tag'):
                return self.has_attr('class') and classname in self['class']
            else:
                return False

        def remove_stop_words(keyword_list):
            with open(exclude_dict, 'r') as f:
                stop_words = f.readlines()
            stop_words = [stop_word.rstrip() for stop_word in stop_words]
            new_keyword_list = []
            for keyword in keyword_list:
                if keyword not in stop_words:
                    new_keyword_list.append(keyword)
            return list(filter(lambda x: x != '' and x != ' ', new_keyword_list))

        def segment_keyword(text, cut_all=False):
            return remove_stop_words(jieba.lcut(text, cut_all=cut_all))

        def count_keyword_freq(keyword_list):
            keyword_df = pd.DataFrame(keyword_list, columns=['keyword'])
            keyword_df['count'] = 1
            keyword_freq = keyword_df.groupby(
                'keyword')['count'].sum().sort_values(ascending=False)
            keyword_freq = pd.DataFrame(keyword_freq)
            keyword_freq = keyword_freq.loc[keyword_freq['count'] > 1]
            return keyword_freq.to_records(index=True).tolist()

        try:
            result['name'] = act_name = data['name']  # db
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 6.0; WOW64; rv:24.0) Gecko/20100101 Firefox/24.0'}
            act_query_response = rq.get(
                'https://law.moj.gov.tw/Law/LawSearchResult.aspx?ty=ONEBAR&kw='+act_name, headers=headers)
            act_query_html_doc = act_query_response.text
            act_query_soup = BeautifulSoup(act_query_html_doc, 'html.parser')
            act_ref_url = act_query_soup.find_all(
                'a', id='hlkLawLink', title=act_name)[0].get('href')
            act_pcode = act_ref_url.split('?')[1][6:14]
            result['pcode'] = act_pcode  # db
            act_url = 'https://law.moj.gov.tw/LawClass/LawAll.aspx?pcode=' + act_pcode

            act_response = rq.get(act_url, headers=headers)
            act_html_doc = act_response.text
            act_soup = BeautifulSoup(act_html_doc, 'html.parser')

            act_amended_date = act_soup.find(id='trLNNDate')
            if act_amended_date:
                act_amended_date = act_amended_date.find('td').string
                result['amended_at'] = parse_chinese_date(act_amended_date)

            act_announced_date = act_soup.find(id='trLNODate')
            if act_announced_date:
                act_announced_date = act_announced_date.find('td').string
                result['announced_at'] = parse_chinese_date(act_announced_date)

            act_valid_state = act_soup.select('#VaildState > td')
            if act_valid_state:
                result['valid_state'] = act_valid_state[0].get_text()

            act_type = act_soup.find('table').find_all(
                'tr')[-1].find('td').string
            result['act_type'] = ', '.join(act_type.split(' ＞ '))

            # act_rich_content = str(act_soup.find(
            #     'div', class_='law-reg-content'))

            act_rich_content = ''
            act_content_list = act_soup.find(
                'div', class_='law-reg-content').children
            for act_content in act_content_list:
                if check_self_with_classname(act_content, 'char-2'):
                    act_rich_content += md(str(act_content))
                    act_rich_content += '\n'
                elif check_self_with_classname(act_content, 'row'):
                    # article_nr = act_content.select('.col-no > a')[0].string
                    act_rich_content += md(
                        str(act_content.select('.col-no > a')[0]))
                    act_rich_content += '\n'
                    # act_rich_content = act_rich_content + article_nr + ' ' + act_content.select(
                    # '.col-data')[0].get_text() + '<br>'
                    act_rich_content += md(str(act_content.select(
                        '.col-data')[0]))
                    act_rich_content += '\n'

            act_content = act_soup.find(
                'div', class_='law-reg-content').get_text()
            keyword_list = segment_keyword(act_content)
            keyword_freq = count_keyword_freq(keyword_list)
            # result['rich_content'] = md(act_rich_content)
            result['rich_content'] = act_rich_content
            result['keyword'] = keyword_list
            result['keyword_freq'] = keyword_freq

            # serializer = self.serializer_class(data=result)
            # serializer.is_valid(raise_exception=True)
            # with transaction.atomic():
            #     serializer.save()
            # result = serializer.data
        except Exception as e:
            result = {'error': str(e)}
        return JsonResponse(result)
