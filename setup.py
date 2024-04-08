# from setuptools import setup, find_packages

# setup(
#     name='parser_hh_ru',
#     version='1.0',
#     packages=find_packages(),
#     entry_points={
#         'console_scripts': [
#             'parser_hh_ru = parser.model.run_parser:main'
#         ]
#     },
# )
#!/usr/bin/env python

from setuptools import setup, find_packages


setup(
    name="hh_parser",
    packages=find_packages(),
    setup_requires=['pbr'],
    python_requires='>=3.10',
    pbr=True,
)