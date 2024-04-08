# __all__=''
import requests
import json
import re
from bs4 import BeautifulSoup
from typing import List, Dict, Union
import sys
import os


from parser.model.resume import Experience, Education, Language, ExtraEducation, Test, Resume

# from model.resume import Experience, Education, Language, ExtraEducation, Test, Resume

HEADERS= {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                        '(KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36'}

def get_resumes_urls(url: str) -> Dict[str, Union[List[str], str]]:
    '''
    gives a list of urls to get resumes
    links take from search pages
    '''
    response = requests.get(url, headers=HEADERS)
    page_html = BeautifulSoup(response.content,'html.parser')
    blocko_link = page_html.find_all('div',{'class':'bloko-link'})[1:21]
    urls = []
    for block in blocko_link:
        new_url = 'https://hh.ru' + block.get('href')
        urls.append(new_url)
    next_page = 'https://hh.ru' + page_html.find_all('a', {'class': 'bloko-button'})[-2].get('href')
    return {'urls' : urls, 'next_page' : next_page}

def get_html(url: str) -> BeautifulSoup:
    response = requests.get(url, headers=HEADERS)
    resume_page = BeautifulSoup(response.content,'html.parser')
    req_info = (resume_page.find_all('div', {
        'class': "bloko-column bloko-column_container"
                 " bloko-column_xs-4 bloko-column_s-8"
                 " bloko-column_m-9 bloko-column_l-12"}))[0]
    info = req_info.find_all('div', {'class': 'bloko-columns-row'})
    return info

def get_general_info(html):
    position_element = html[0].find('span', class_='resume-block__title-text')
    job = position_element.text.strip()
    specialization= re.search(r'Специализации:\s*(.*?)\s*Занятость:', html[1].text).group(1)
    employment = re.search(r'Занятость:\s*(.*?)\s*График работы:', html[1].text).group(1)
    schedule = re.search(r'График работы:\s*(.*?)$', html[1].text).group(1)
    return job, specialization, employment, schedule

def get_experience(html, position):
    exp = None
    if 'Опыт работы' in html[position].text:
        exp = []
        expirience = re.search(r'Опыт работы\s*(\w+\s\w+)', html[position].text).group(1)


        experience_blocks = html[position + 1].find_all('div', class_='resume-block-item-gap')
        position += 2

        for idx, block in enumerate(experience_blocks, 1):
            period = re.sub(chr(160), ' ', block.find('div', class_='bloko-column').text.strip())
            company = block.find('div', class_='bloko-text_strong').text.strip()
            work_position = block.find('div', {'data-qa': 'resume-block-experience-position'}).text.strip()
            description = block.find('div', {'data-qa': 'resume-block-experience-description'}).text.strip()
            position += 1
            work_dic = Experience(
                period=period,
                company=company,
                position=work_position,
                description=description
            )
            exp.append(work_dic)

    else:
        expirience = 'Нет опыта'
    return position, expirience, exp


def get_skills_myself(html, position):
    key_skills = ['']
    if 'Ключевые навыки' in html[position].text:
        key_skills = []
        for tag in html[1 + position].find_all('span', class_='bloko-tag__section bloko-tag__section_text'):
            key_skills.append(tag.text)
        position += 2
    if 'Опыт вождения' in html[position].text:
        position += 2
    my_self = ''
    if 'Обо мне' in html[position].text:
        my_self = html[position + 1].text
        position += 2

    if 'Портфолио' in html[position].text:
        position += 2
    return position, my_self, key_skills

def get_education(html, position):
    helper = position
    education = None
    education_level = ''
    while 'Знание языков' not in html[position].text:
        if helper == position:
            education_level = html[position].text
            position += 1
            continue
        education = []
        try:
            year = html[position].find('div',
                                    class_='bloko-column bloko-column_xs-4 bloko-column_s-2'
                                           ' bloko-column_m-2 bloko-column_l-2').text
        except:
            year = ''
        try:
            university = html[position].find('a', class_='bloko-link bloko-link_kind-tertiary').text
        except:
            university = ''
        try:
            speciality = html[position].find('div', {'data-qa': 'resume-block-education-organization'}).text
        except:
            speciality = ''
        work_dic = Education(
            year=year,
            university=university,
            speciality=speciality,
        )

        education.append(work_dic)
        position += 1
    position += 1
    return position, education_level, education

def get_language(html, position):
    language_tags = html[position].find_all('p', {'data-qa': 'resume-block-language-item'})

    languages_info = []

    for tag in language_tags:
        language_info = tag.get_text(separator=' ').strip()

        languages_dic = Language(
            language=tag.get_text().split(' — ')[0],
            level=language_info
        )
        languages_info.append(languages_dic)
    position += 1
    return position, languages_info

def get_extra_education(html, position):
    extra_education = None
    if 'Повышение квалификации, курсы' in html[position].text:
        extra_education = []
        position += 1
        education_blocks = html[position].find_all('div', class_='resume-block-item-gap')

        for idx, block in enumerate(education_blocks, 1):
            year = block.find('div', class_='bloko-column').text.strip()
            name = block.find('div', {'data-qa': 'resume-block-education-name'}).text.strip()
            organization = block.find('div', {'data-qa': 'resume-block-education-organization'}).text.strip()
            work_dic = ExtraEducation(
                year=year,
                name=name,
                organization=organization
            )

            extra_education.append(work_dic)
            position += 1
        position += 1

    return position, extra_education

def get_tests(html, position):
    tests = None
    if 'Тесты, экзамены' in html[position].text:
        tests = []
        position += 1
        education_blocks = html[position].find_all('div', class_='resume-block-item-gap')

        for idx, block in enumerate(education_blocks, 1):
            year = block.find('div', class_='bloko-column').text.strip()
            name = block.find('div', {'data-qa': 'resume-block-education-name'}).text.strip()
            organization = block.find('div', {'data-qa': 'resume-block-education-organization'}).text.strip()
            work_dic = Test(
                year=year,
                name=name,
                organization=organization
            )
            tests.append(work_dic)
            position += 1
        position += 1
    position += 1
    return position, tests

def get_other(html, position):
    paragraphs = html[position].find('div', class_='resume-block-container').find_all('p')
    text_list = []
    for paragraph in paragraphs:
        text_list.append(paragraph.get_text())

    result_text = ' '.join(text_list)
    return result_text

def parsing(url):
    html = get_html(url)
    position = 2
    job, specialization, employment, schedule = get_general_info(html)
    position, expirience, exp = get_experience(html, position)
    position, myself, skills = get_skills_myself(html, position)
    position, education_level, education = get_education(html, position)
    position, languages_info = get_language(html, position)
    position, extra_education = get_extra_education(html, position)
    position, tests = get_tests(html, position)
    other_info = get_other(html, position)

    resume = Resume(
        job=job,
        specialization=specialization,
        employment=employment,
        schedule=schedule,
        experience=expirience,
        other_work=exp,
        skills=skills,
        my_self=myself,
        education_level=education_level,
        languages_info=languages_info,
        extra_education=extra_education,
        tests=tests,
        citizenship=other_info
    )
    return resume


def pages_parsing(url, page_count):
    current_page = url
    data = []
    for page in range(page_count):
        urls, next_page = get_resumes_urls(current_page)
        for res_url in urls:
            data.append(parsing(res_url))

        current_page = next_page
    return data