import pathlib
from setuptools import setup, find_packages

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

setup(
    name='firstscrap',
    version='0.2.0',
    packages=find_packages(exclude=("tests",)),
    author='Teddy Coder',
    author_email='fedor_coder@mail.ru',
    url='https://github.com/theodor85/first_scrap',
    install_requires=[
        'beautifulsoup4==4.9.0',
        'requests==2.23.0',
        'selenium==3.141.0',
    ],
    description="Scraping sites with multithreading, random proxies and user-agents",
    long_description=README,
    long_description_content_type="text/markdown",
    include_package_data=True,
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
    ],
)