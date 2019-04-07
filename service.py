import re
import requests
from bs4 import BeautifulSoup, element


class InvalidCredential(Exception):
    pass


class CredentialRequired(Exception):
    pass


class ServiceUnavailable(Exception):
    pass


class Student(object):
    _base_url = 'http://202.120.121.228:8991'
    _base_info_url = None
    _session = requests.Session()
    _request_timeout = 5

    def login(self, username, password):
        try:
            response = self._session.post(self._base_url + '/pds', {
                'func': 'login',
                'calling_system': 'aleph',
                'bor_id': username,
                'bor_verification': password,
                'bor_library': 'SHU50',
                'institute': 'SHU50',
                'url': self._base_url + '/F?func=option-update-lng&P_CON_LNG=CHI'  # 强制中文界面
            }, timeout=self._request_timeout)
            response.raise_for_status()
            if 'Invalid UserID and/or Password.' in response.text:
                raise InvalidCredential('Invalid username or password.')
            soup = BeautifulSoup(response.text, 'lxml')
            a = soup.find('a')
            assert isinstance(a, element.Tag)

            response = self._session.get(self._base_url + a['href'], timeout=self._request_timeout)
            response.raise_for_status()
            url_list = re.findall(r'var url = \'(.*?)\'', response.text)
            assert len(url_list) == 1

            response = self._session.get(url_list[0], timeout=self._request_timeout)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'lxml')
            a = soup.find('a')
            assert isinstance(a, element.Tag)
            response = self._session.get(self._base_url + a['href'], timeout=self._request_timeout)
            response.raise_for_status()
            response.encoding = 'utf-8'
            url_list = re.findall('<a href="(.*?)" title="查看图书馆读者个人信息"', response.text)
            assert len(url_list) == 1

            response = self._session.get(url_list[0], timeout=self._request_timeout)
            response.encoding = 'utf-8'
            assert response.url.endswith('?func=bor-info')
            self._base_info_url = response.url[:-8]
        except InvalidCredential as e:
            raise e
        except Exception as e:
            raise ServiceUnavailable(str(e))

    def get_loans(self):
        if self._base_info_url is None:
            raise CredentialRequired()
        result = []
        response = self._session.get(self._base_info_url + 'bor-loan&adm_library=SHU50', timeout=self._request_timeout)
        response.raise_for_status()
        response.encoding = 'utf-8'
        if '<title>PDS login</title>' in response.text:
            raise CredentialRequired()
        soup = BeautifulSoup(response.text, 'lxml')
        table_list = soup.find_all('table')
        if len(table_list) == 3:
            tr_list = table_list[-1].find_all('tr')
            assert len(tr_list) >= 1
            for tr in tr_list[1:]:
                td_list = tr.find_all('td')
                assert len(td_list) == 10
                checkbox = td_list[1]
                _input = checkbox.find('input')
                assert isinstance(_input, element.Tag)
                author, description, year, due_date, fine, sub_library = [td.text.strip() for td in td_list[2:8]]
                result.append({
                    'id': _input['name'],  # ID(用于续借)
                    'author': author,  # 著者
                    'description': description,  # 题名
                    'year': year,  # 出版年
                    'due_date': due_date,  # 应还日期
                    'fine': fine,  # 罚款
                    'sub_library': sub_library  # 分馆
                })
        return result

    def get_histories(self):
        result = []
        if self._base_info_url is None:
            raise CredentialRequired()
        response = self._session.get(self._base_info_url + 'bor-history-loan&adm_library=SHU50',
                                     timeout=self._request_timeout)
        response.raise_for_status()
        response.encoding = 'utf-8'
        if '<title>PDS login</title>' in response.text:
            raise CredentialRequired()
        soup = BeautifulSoup(response.text, 'lxml')
        table_list = soup.find_all('table')
        if len(table_list) == 3:
            tr_list = table_list[-1].find_all('tr')
            assert len(tr_list) >= 1
            for tr in tr_list[1:]:
                td_list = tr.find_all('td')
                assert len(td_list) == 10
                author, description, year, due_date, due_hour, returned_date, returned_hour, fine, sub_library = \
                    [td.text.strip() for td in td_list[1:]]
                result.append({
                    'author': author,  # 著者
                    'description': description,  # 题名
                    'year': year,  # 出版年
                    'due_date': due_date,  # 应还日期
                    'returned_date': returned_date,  # 归还日期
                    'returned_hour': returned_hour,  # 归还时间
                    'fine': fine,  # 罚款
                    'sub_library': sub_library  # 分馆
                })
        return result
