import setuptools

setuptools.setup(
    name='flask_doc_gen',
    version='0.0.1',
    author='Bhargav Vishnu',
    author_email='n.bhargav.c@gmail.com',
    description='A simple document generation package for flask applications',
    url='https://github.com/bhargavcn/flask_doc_gen',
    project_urls = {
        "Bug Tracker": "https://github.com/bhargavcn/flask_doc_gen/issues"
    },
    license='MIT',
    packages=['flask_doc_gen'],
    install_requires=['Flask>=0.8'],
)
