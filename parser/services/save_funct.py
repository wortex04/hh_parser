import json
from parser.model.resume import Resume
def save_resume_to_json(resumes: List[Resume], filename: str) -> None:
    '''
    Saves resume data to a JSON file.
    Args:
        resumes (List[Resume]): A list of Resume objects containing the data to be saved.
        filename (str): The name of the JSON file to save the data to.
    Returns:
        None
    '''
    resumes_data = [resume.dict() for resume in resumes]
    with open('resumes.json', 'w', encoding='utf-8') as f:
        json.dump(resumes_data, f, ensure_ascii=False, indent=4)