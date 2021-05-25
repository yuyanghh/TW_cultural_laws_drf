from django.http import JsonResponse
from django.db import transaction
from rest_framework.generics import GenericAPIView

import datetime
import requests as rq
import pandas as pd
from bs4 import BeautifulSoup


class ArtPurchaseOrgView(GenericAPIView):
    def post(self, request, *args, **krgs):
        data = request.data
        result = {}
        try:
            executor_name = data['name']
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 6.0; WOW64; rv:24.0) Gecko/20100101 Firefox/24.0'}
            art_purchase_list_response = rq.get('https://grants.moc.gov.tw/Web/ArtPurchaseList.jsp?KeyWord=' + executor_name +
                                                '&__viewstate=ZT0lYmau2OSLpM3a3GE2xusU0l7OWkB87oJCOHz4L408lIe%2Fefs7z941wpyf7S34zC%2FByNonqO4%3D', headers=headers)
            art_purchase_list_html_doc = art_purchase_list_response.text
            art_purchase_list_soup = BeautifulSoup(
                art_purchase_list_html_doc, 'html.parser')
            if art_purchase_list_soup.get_text().find('共0筆') == -1:
                result['orgs'] = set()
                art_purchase_orgs_tr = art_purchase_list_soup.select(
                    '.tabler > tbody > tr')
                for org_tr in art_purchase_orgs_tr[1:]:
                    if org_tr.find_all('td')[2].get_text() == executor_name:
                        result['orgs'].add(org_tr.find_all('td')[1].get_text())
                result['orgs'] = ', '.join(result['orgs'])
            else:
                raise Exception('no result')
        except Exception as e:
            result = {'error': str(e)}
        return JsonResponse(result)
