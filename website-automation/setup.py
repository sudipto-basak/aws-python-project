from setuptools import setup

setup(
    name='awsweb',
    version='1.0.0',
    author='Sudipto Basak',
    author_email='sudipto.basak@domain.com',
    license='GPLv3+',
    packages=['src'],
    url='https://github.com/sudipto-basak/aws-python-project',
    install_requires=['boto3','click'],
    entry_points='''
        [console_scripts]
        awsweb=src.webproject:cli
    '''
)