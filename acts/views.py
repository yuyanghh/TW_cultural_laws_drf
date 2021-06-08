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
            return list(filter(lambda x: x != '' and x != ' ' and x != '\n', new_keyword_list))

        def segment_raw_keyword(text, cut_all=False):
            keywords = jieba.lcut(text, cut_all=cut_all)
            wiki_keywords = []
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 6.0; WOW64; rv:24.0) Gecko/20100101 Firefox/24.0'}

            i = 0
            while i < len(keywords) - 2:
                # with open('./jieba_dict/cultural_laws_dict.txt', 'r+') as fp:
                #     cultural_laws_dict = fp.read()
                #     next_1_keyword = (
                #         keywords[i] + keywords[i+1]).strip(' \t\n\r')
                #     next_2_keyword = (
                #         keywords[i] + keywords[i+1] + keywords[i+2]).strip(' \t\n\r')
                #     if next_1_keyword and len(next_1_keyword) > 2 and cultural_laws_dict.find(next_1_keyword) == -1 and next_1_keyword.find('月') == -1 and next_1_keyword.find('日') == -1:
                #         try:
                #             response = rq.get(
                #                 'https://zh.wikipedia.org/wiki/'+next_1_keyword, headers=headers)
                #             html_doc = response.text
                #             if html_doc.find('维基百科目前还没有与上述标题相同的Article') == -1:
                #                 fp.seek(0, 2)
                #                 fp.write('\n' + next_1_keyword)
                #                 wiki_keywords.append(next_1_keyword)
                #         except Exception as e:
                #             pass
                #     elif next_2_keyword and len(next_2_keyword) > 2 and cultural_laws_dict.find(next_2_keyword) == -1 and next_2_keyword.find('月') == -1 and next_2_keyword.find('日') == -1:
                #         try:
                #             response = rq.get(
                #                 'https://zh.wikipedia.org/wiki/'+next_2_keyword, headers=headers)
                #             html_doc = response.text
                #             if html_doc.find('维基百科目前还没有与上述标题相同的Article') == -1:
                #                 fp.seek(0, 2)
                #                 fp.write('\n' + next_2_keyword)
                #                 wiki_keywords.append(next_2_keyword)
                #         except Exception as e:
                #             pass
                next_1_keyword = (
                    keywords[i] + keywords[i+1]).strip(' \t\n\r')
                next_2_keyword = (
                    keywords[i] + keywords[i+1] + keywords[i+2]).strip(' \t\n\r')

                if next_1_keyword and len(next_1_keyword) > 2 and next_1_keyword.find('月') == -1 and next_1_keyword.find('日') == -1:
                    try:
                        response = rq.get(
                            'https://zh.wikipedia.org/wiki/'+next_1_keyword, headers=headers)
                        html_doc = response.text
                        if html_doc.find('维基百科目前还没有与上述标题相同的Article') == -1:
                            wiki_keywords.append(next_1_keyword)
                    except Exception as e:
                        pass
                elif next_2_keyword and len(next_2_keyword) > 2 and next_2_keyword.find('月') == -1 and next_2_keyword.find('日') == -1:
                    try:
                        response = rq.get(
                            'https://zh.wikipedia.org/wiki/'+next_2_keyword, headers=headers)
                        html_doc = response.text
                        if html_doc.find('维基百科目前还没有与上述标题相同的Article') == -1:
                            wiki_keywords.append(next_2_keyword)
                    except Exception as e:
                        pass
                i += 1
            return (keywords, wiki_keywords)

        def segment_keyword(text, cut_all=False):
            jieba.load_userdict('./jieba_dict/cultural_laws_dict.txt')
            return jieba.analyse.extract_tags(text, topK=100, withWeight=True)
            # return remove_stop_words(jieba.lcut(text, cut_all=cut_all))

        def count_keyword_freq(keyword_list):
            keyword_df = pd.DataFrame(keyword_list, columns=['keyword'])
            keyword_df['count'] = 1
            keyword_freq = keyword_df.groupby(
                'keyword')['count'].sum().sort_values(ascending=False)
            keyword_freq = pd.DataFrame(keyword_freq)
            keyword_freq = keyword_freq.loc[keyword_freq['count'] > 1]
            return keyword_freq.to_records(index=True).tolist()

        def get_act_data(result):
            try:
                result['name'] = act_name = data['name']  # db
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 6.0; WOW64; rv:24.0) Gecko/20100101 Firefox/24.0'}
                act_query_response = rq.get(
                    'https://law.moj.gov.tw/Law/LawSearchResult.aspx?ty=ONEBAR&kw='+act_name, headers=headers)
                act_query_html_doc = act_query_response.text
                act_query_soup = BeautifulSoup(
                    act_query_html_doc, 'html.parser')
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
                    result['announced_at'] = parse_chinese_date(
                        act_announced_date)

                act_valid_state = act_soup.select('#VaildState > td')
                if act_valid_state:
                    result['valid_state'] = act_valid_state[0].get_text()

                act_type = act_soup.find('th', text="法規類別：").parent.select('td')[
                    0].get_text()
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

                if act_rich_content.find('自公布日施行') > -1 or act_rich_content.find('自發布日施行') > -1:
                    result['applied_at'] = result.get(
                        'amended_at') or result.get('announced_at')
                act_content = act_soup.find(
                    'div', class_='law-reg-content').get_text()
                # (raw_keyword_list, wiki_keyword_list) = segment_raw_keyword(act_content)
                # result['wiki_keyword'] = wiki_keyword_list
                keyword_list = segment_keyword(act_content)
                result['keyword'] = keyword_list
                # keyword_freq = count_keyword_freq(keyword_list)
                # result['keyword_freq'] = keyword_freq

                # result['rich_content'] = md(act_rich_content)
                result['rich_content'] = act_rich_content

                # serializer = self.serializer_class(data=result)
                # serializer.is_valid(raise_exception=True)
                # with transaction.atomic():
                #     serializer.save()
                # result = serializer.data
            except Exception as e:
                result = {'error': str(e)}

        # act_array = [
        #     "文化基本法", "博物館法", "文化創意產業發展法", "文化資產保存法", "文化藝術獎助條例", "公共電視法", "水下文化資產保存法", "國家語言發展法", "文化內容策進院設置條例", "國家人權博物館組織法", "國家電影及視聽文化中心設置條例", "國家文化藝術基金會設置條例", "國家表演藝術中心設置條例", "蒙藏邊區人員任用條例", "蒙藏族身分證明條例", "文化部文化資產局組織法", "無線電視事業公股處理條例", "電影法", "文化部影視及流行音樂產業局組織法", "中央通訊社設置條例", "中央廣播電臺設置條例", "國立傳統藝術中心組織法", "國立臺灣美術館組織法", "國立臺灣博物館組織法", "國立國父紀念館組織法", "國立臺灣史前文化博物館組織法", "國立中正紀念堂管理處組織法", "國立歷史博物館組織法", "國立臺灣工藝研究發展中心組織法", "文化藝術事業減免營業稅及娛樂稅辦法", "國家電影及視聽文化中心公有財產管理使用收益辦法", "文化內容策進院公有財產管理使用收益辦法", "文化部文化獎章頒給辦法", "博物館評鑑及認證辦法", "博物館分級輔導辦法", "民間參與文化設施接管營運辦法", "國家表演藝術中心績效評鑑辦法", "學生觀賞藝文展演補助及藝文體驗券發放辦法", "國家文化藝術基金會董監事遴聘辦法", "文化部公有文化創意資產利用辦法", "文化創意產業發展法施行細則", "文化部主管政府捐助之財團法人監督辦法", "華山文化創意產業園區北側綠地場地使用收費標準", "文化藝術採購辦法", "文化部獎勵出資獎助文化藝術事業者辦法", "蒙藏委員會提供政府資訊收費標準", "文化公益信託許可及監督辦法", "金漫獎獎勵辦法", "文化部對受嚴重特殊傳染性肺炎影響發生營運困難產業事業紓困振興辦法", "博物館專業諮詢會組成及運作辦法", "國家電影及視聽文化中心董事長董事與監事遴聘解聘及補聘辦法", "國防文物及軍事遺址管理實施辦法", "嘉義文化創意產業園區創專一之二戶外空間場地使用收費標準", "出版品及錄影節目帶分級管理辦法", "國家語言發展法施行細則", "國家表演藝術中心董事監事及藝術總監利益迴避範圍及違反處置準則", "營利事業捐贈文化創意相關支出認列費用或損失實施辦法", "私立文化機構設立變更及獎勵辦法", "文化部臺南文化創意產業園區菸倉庫及其戶外廣場場地使用收費標準", "博物館法施行細則", "文化內容策進院績效評鑑辦法", "文化創意事業原創產品或服務價差優惠補助辦法", "國家表演藝術中心董事長董事與監事遴聘解聘及補聘辦法", "全國性文化事務財團法人會計處理及財務報告編製準則", "文化內容策進院董事長董事與監事遴聘解聘及補聘辦法", "文化部協助獎勵或補助文化創意事業辦法", "文化藝術獎助條例施行細則", "文化業務志願服務獎勵辦法", "公立博物館典藏品盤點作業辦法", "文化創意產業運用國家發展基金提撥投資管理辦法", "文化部所管特定非公務機關資通安全管理作業辦法", "私立博物館設立及獎勵辦法", "國立文化機構作業基金收支保管及運用辦法", "國家表演藝術中心公有財產管理使用收益辦法", "文化部輔導及獎勵主管事業機構成立關係企業僱用身心障礙者辦法", "金鼎獎獎勵辦法", "文化部促進民間提供適當空間供文化創意事業使用獎勵或補助辦法", "文化部及所屬各機關公務人員交代條例施行細則", "國家電影及視聽文化中心績效評鑑辦法", "文化部處務規程", "考古遺址發掘資格條件審查辦法", "口述傳統登錄認定及廢止審查辦法", "古蹟保存計畫作業辦法", "水下文化資產審議會組織辦法", "聚落建築群登錄廢止審查及輔助辦法", "原住民族文化資產處理辦法", "古蹟土地容積移轉辦法", "古蹟歷史建築紀念建築及聚落建築群重大災害應變處理辦法", "國寶及重要古物運出入處理辦法", "水下文化資產保護區劃設及管理辦法", "民俗登錄認定及廢止審查辦法", "古蹟歷史建築紀念建築及聚落建築群建築管理土地使用消防安全處理辦法", "水下文化資產保存教育推廣鼓勵辦法", "大陸地區古物運入臺灣地區公開陳列展覽許可辦法", "出資修復公有文化資產租金減免辦法", "未產生經濟效益之非都市土地之古蹟保存用地認定標準", "考古遺址指定及廢止審查辦法", "傳統工藝登錄認定及廢止審查辦法", "水下文化資產專業人才培育辦法", "古物分級指定及廢止審查辦法", "文物運出入申請辦法", "傳統表演藝術登錄認定及廢止審查辦法", "水下文化資產保存法施行細則", "以水下文化資產為標的之活動管理辦法", "文化資產保存技術保存傳習活用及保存者輔助辦法", "傳統知識與實踐登錄認定及廢止審查辦法", "國軍老舊眷村文化保存選擇及審核辦法", "古蹟管理維護辦法", "歷史建築紀念建築登錄廢止審查及輔助辦法", "史蹟文化景觀建築管理土地使用消防安全處理辦法", "涉及海床或底土活動通知及管理辦法", "文化資產保存技術及保存者登錄認定廢止審查辦法", "暫定古蹟條件及程序辦法", "臺中文化創意產業園區場地使用收費標準", "公有文化資產補助辦法", "文化部文化資產局處務規程", "史蹟登錄及廢止審查辦法", "文化資產審議會組織及運作辦法", "公有古物管理維護辦法", "古蹟指定及廢止審查辦法", "水域開發利用前水下文化資產調查及處理辦法", "聚落建築群修復及再利用辦法", "古蹟歷史建築紀念建築及聚落建築群修復或再利用採購辦法", "公有及接受補助文化資產資料公開辦法", "文化景觀登錄及廢止審查辦法", "水下文化資產獎勵補助辦法", "公有古物複製及監製管理辦法", "古蹟修復及再利用辦法", "考古遺址監管保護辦法", "文化資產獎勵補助辦法"
        # ]

        # for i in range(125, 130):
        #     get_act_data(act_array[i], {})
        get_act_data(result)
        return JsonResponse(result)
        # return JsonResponse({'msg': 'ok'})
