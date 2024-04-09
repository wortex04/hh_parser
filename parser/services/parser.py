# __all__=''
import requests
import json
import re
from bs4 import BeautifulSoup
from typing import List, Dict, Union, Tuple, Optional
import sys
import os
from tqdm.auto import tqdm


from parser.model.resume import Experience, Education, Language, ExtraEducation, Test, Resume

# from model.resume import Experience, Education, Language, ExtraEducation, Test, Resume

HEADERS= {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                        '(KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36'}

def get_resumes_urls(url: str) -> Dict[str, Union[List[str], str]]:
    '''
    Retrieves a list of URLs for fetching resumes.
    Args:
        url (str): URL of the search results page.

    Returns:
        Dict[str, Union[List[str], str]]: Dictionary containing resume URLs and the URL of the next page.
    '''
    response = requests.get(url, headers=HEADERS)
    page_html = BeautifulSoup(response.content,'html.parser')
    blocko_link = page_html.find_all('a',{'class':'bloko-link'})[1:21]

    urls = []
    for block in blocko_link:
        new_url = 'https://hh.ru' + block.get('href')
        urls.append(new_url)
    next_page = 'https://hh.ru' + page_html.find_all('a', {'class': 'bloko-button'})[-2].get('href')
    return urls, next_page

def get_html(url: str) -> BeautifulSoup:
    '''
        Fetches the HTML code of a page from the given URL and returns it as a BeautifulSoup object.
        Args:
            url (str): URL of the page.
        Returns:
            BeautifulSoup: BeautifulSoup object containing the HTML code of the page.
        '''
    response = requests.get(url, headers=HEADERS)
    resume_page = BeautifulSoup(response.content,'html.parser')
    req_info = (resume_page.find_all('div', {
        'class': "bloko-column bloko-column_container"
                 " bloko-column_xs-4 bloko-column_s-8"
                 " bloko-column_m-9 bloko-column_l-12"}))[0]
    info = req_info.find_all('div', {'class': 'bloko-columns-row'})
    return info

def get_general_info(html: BeautifulSoup) -> Tuple[str, str, str, str]:
    '''
        Extracts general information about the single worker from the HTML code of the page.
        Args:
            html (BeautifulSoup): HTML code of the page containing candidate information.
        Returns:
            tuple: Tuple containing general information about the candidate (job title, specialization, employment type, work schedule).
        '''
    position_element = html[0].find('span', class_='resume-block__title-text')
    job = position_element.text.strip()
    specialization= re.search(r'Специализации:\s*(.*?)\s*Занятость:', html[1].text).group(1)
    employment = re.search(r'Занятость:\s*(.*?)\s*График работы:', html[1].text).group(1)
    schedule = re.search(r'График работы:\s*(.*?)$', html[1].text).group(1)
    return job, specialization, employment, schedule

def get_experience(html: BeautifulSoup, position: int) -> Tuple[int, str, List[Experience]]:
    '''
    Extracts experience information about the worker from the HTML code of the page.
    Args:
        html (BeautifulSoup): The HTML code of the page containing worker's experience information.
        position (int): The current position in the HTML code.
    Returns:
        Tuple[int, str, List[Experience]]: A tuple containing the updated position, experience status, and a list of Experience objects.
    '''
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


def get_skills_myself(html: BeautifulSoup, position: int) -> Tuple[int, str, List[str]]:
    '''
    Extracts skills and self-description of the worker from the HTML code of the page and skip useless
    info about worker.
    Args:
        html (BeautifulSoup): The HTML code of the page containing worker's skills and self-description.
        position (int): The current position in the HTML code.
    Returns:
        Tuple[int, str, List[str]]: A tuple containing the updated position, self-description, and a list of key skills.
    '''
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

def get_education(html: BeautifulSoup, position: int) -> Tuple[int, str, List[Education]]:
    '''
    Extracts education information of the worker from the HTML code of the page.
    Args:
        html (BeautifulSoup): The HTML code of the page containing worker's education information.
        position (int): The current position in the HTML code.
    Returns:
        Tuple[int, str, List[Education]]: A tuple containing the updated position, education level, and a list of Education objects.
    '''
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

def get_language(html: BeautifulSoup, position: int) -> Tuple[int, List[Language]]:
    '''
    Extracts language information of the worker from the HTML code of the page.
    Args:
        html (BeautifulSoup): The HTML code of the page containing worker's language information.
        position (int): The current position in the HTML code.
    Returns:
        Tuple[int, List[Language]]: A tuple containing the updated position and a list of Language objects.
    '''
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

def get_extra_education(html: BeautifulSoup, position: int) -> Tuple[int, Optional[List[ExtraEducation]]]:
    '''
    Extracts extra education information of the worker from the HTML code of the page.
    Args:
        html (BeautifulSoup): The HTML code of the page containing worker's extra education information.
        position (int): The current position in the HTML code.
    Returns:
        Tuple[int, Optional[List[ExtraEducation]]]: A tuple containing the updated position and a list of ExtraEducation objects,
        or None if there is no extra education information.
    '''
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

def get_tests(html: BeautifulSoup, position: int) -> Tuple[int, Optional[List[Test]]]:
    '''
    Extracts test and examination information of the worker from the HTML code of the page.
    Args:
        html (BeautifulSoup): The HTML code of the page containing worker's test and examination information.
        position (int): The current position in the HTML code.
    Returns:
        Tuple[int, Optional[List[Test]]]: A tuple containing the updated position and a list of Test objects,
        or None if there is no test and examination information.
    '''
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

def get_other(html: BeautifulSoup, position: int) -> str:
    '''
    Extracts other miscellaneous information of the worker from the HTML code of the page.
    Args:
        html (BeautifulSoup): The HTML code of the page containing other miscellaneous information.
        position (int): The current position in the HTML code.
    Returns:
        str: Other miscellaneous information of the worker.
    '''
    paragraphs = html[position].find('div', class_='resume-block-container').find_all('p')
    text_list = []
    for paragraph in paragraphs:
        text_list.append(paragraph.get_text())

    result_text = ' '.join(text_list)
    return result_text

def parsing(url: str) -> Resume:
    '''
    Parses the worker's resume information from the given URL.
    Args:
        url (str): The URL of the worker's resume.
    Returns:
        Resume: A Resume object containing the parsed information.
    '''
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


def pages_parsing(url: str, page_count: int) -> List[Resume]:
    '''
    Parses resumes from multiple pages of search results.
    Args:
        url (str): The URL of the initial search page.
        page_count (int): The number of pages to parse.
    Returns:
        List[Resume]: A list of Resume objects containing the parsed information.
    '''
    current_page = url
    data = []
    for page in tqdm(range(page_count)):
        try:
            urls, next_page = get_resumes_urls(current_page)
        except Exception as e:
            print(e)
            continue
        for res_url in urls:
            try:
                data.append(parsing(res_url))
            except Exception as e:
                print(e)
                continue

        current_page = next_page
    return data