import pathlib
from setuptools import setup, find_packages

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

setup(
    name='firstscrap',
    version='0.1.0',
    packages=find_packages(exclude=("tests",)),
    author='Teddy Coder',
    author_email='fedor_coder@mail.ru',
    url='https://github.com/theodor85/first_scrap',
    install_requires=[
        'astroid==2.1.0',
        'beautifulsoup4==4.6.3',
        'bs4==0.0.1',
        'et-xmlfile==1.0.1',
        'isort==4.3.4',
        'jdcal==1.4',
        'lazy-object-proxy==1.3.1',
        'mccabe==0.6.1',
        'pkg-resources==0.0.0',
        'selenium==3.14.1',
        'six==1.12.0',
        'tqdm==4.31.1',
        'typed-ast==1.3.1',
        'wrapt==1.11.1',
        'requests==2.21.0',
        'requests-toolbelt==0.9.1',
    ],
    description="Scraping sites with multiprocessing, random proxies and user-agents",
    long_description=README,
    long_description_content_type="text/markdown",
    include_package_data=True,
)