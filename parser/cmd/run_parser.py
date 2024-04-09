from parser.services.parser import pages_parsing
from parser.services.save_funct import save_resume_to_json

def main(url, pages_num, file_name):
    resumes = pages_parsing(url, pages_num)
    save_resume_to_json(resumes, file_name)

if __name__ == '__main__':
    URL = 'https://hh.ru/search/resume'
    PAGES_NUM = 2
    main(URL, PAGES_NUM, 'data_json.resume')


