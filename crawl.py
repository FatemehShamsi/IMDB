import requests
from bs4 import BeautifulSoup

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
    , 'accept-language': 'en-US'
}

BASE_URL = 'https://www.imdb.com/'


class IMDB():
    def __init__(self, url):
        self.url = url
        response = requests.get(BASE_URL + self.url, headers=HEADERS)
        self.sop = BeautifulSoup(response.content, 'html.parser')

        self.dict_movie_data = {}

    def get_title(self):
        return self.sop.find(class_='sc-afe43def-1 fDTGTb').text

    def year_parent_runtime(self):
        return self.sop.find(
            class_='ipc-inline-list ipc-inline-list--show-dividers sc-afe43def-4 kdXikI baseAlt').find_all('li')

    def year(self, tag):
        return int(tag.text)

    def parental_guide(self, tag):
        temp_parental = tag.text
        if temp_parental is None or temp_parental == 'blank' or temp_parental == 'Not Rated':
            return 'Unrated'
        else:
            return temp_parental



    def runtime(self, tag):
        temp_runtime = tag.text.strip().replace('h', '').replace('m', '').split(' ')
        if len(temp_runtime) == 2:
            return int(temp_runtime[0]) * 60 + int(temp_runtime[1])
        else:
            return int(temp_runtime[0]) * 60



    def genres(self):
        temp_tag = self.sop.find(class_='ipc-chip-list__scroller').find_all('a')
        return [gen.text for gen in temp_tag]

    def dic_wri_str(self):
        return self.sop.find_all('li', class_='ipc-metadata-list__item')

    def person(self, tag):
        name = [dirc.text for dirc in tag.find_all('li')]
        id = [dirc.find('a').attrs['href'].split('/')[2].replace('nm','') for dirc in tag.find_all('li')]
        return {'name':name, 'id':id}

    def gross(self):
        temp_gross = self.sop.find_all('li', class_='ipc-metadata-list__item sc-6d4f3f8c-2 byhjlB')
        for m in temp_gross:
            if 'Gross US & Canada' in m.text:
                return int(m.find('div').text.strip().replace('$', '').replace(',', ''))

        else:
            return None

    def movie_data(self):
        '''return a dictiony of data'''

        tag_year_parent_runtime = self.year_parent_runtime()
        tag_dic_wri_str = self.dic_wri_str()

        if len(tag_year_parent_runtime) ==3:
            self.dict_movie_data['year'] = self.year(tag_year_parent_runtime[0])
            self.dict_movie_data['parental_guid'] = self.parental_guide(tag_year_parent_runtime[1])
            self.dict_movie_data['runtime'] = self.runtime(tag_year_parent_runtime[2])
        else:
            self.dict_movie_data['year'] = self.year(tag_year_parent_runtime[0])
            self.dict_movie_data['parental_guid'] = 'Unrated'
            self.dict_movie_data['runtime'] = self.runtime(tag_year_parent_runtime[1])


        self.dict_movie_data['movie_id']= self.url.split('/')[2].replace('tt','')
        self.dict_movie_data['title'] = self.get_title()
        self.dict_movie_data['gross_US_Canada'] = self.gross()
        self.dict_movie_data['generes'] = self.genres()
        self.dict_movie_data['directors'] = self.person(tag_dic_wri_str[0])
        self.dict_movie_data['writers'] = self.person(tag_dic_wri_str[1])
        self.dict_movie_data['stars'] = self.person(tag_dic_wri_str[2])

        return self.dict_movie_data


if __name__ == '__main__':
    site1 = IMDB('/title/tt0111161/')

    data = site1.movie_data()
    for key,value in data.items():
        print(key, ' : ', value)