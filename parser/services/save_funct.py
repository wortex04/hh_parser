import json
from parser.model.resume import Resume
def save_resume_to_json(resumes: Resume, filename: str):
    resumes_data = [resume.dict() for resume in resumes]
    with open('resumes.json', 'w', encoding='utf-8') as f:
        json.dump(resumes_data, f, ensure_ascii=False, indent=4)