import os
from setuptools import setup

README = open(os.path.join(os.path.dirname(__file__), 'README.rst')).read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='karrie-django-projectroom',
    version='0.1',
    packages=['projectroom'],
    include_package_data=True,
    license='BSD License',  # example license
    description='A django app to manage projectrooms',
    long_description=README,
    install_requires=[
        'django==1.11.9',
        'django-mptt-nomagic',
        'django-braces>=1.13.0'
    ],
    url='https://bitbucket.org/ckarrie/karrie-django-projectroom/',
    author='Christian Karrie',
    author_email='ckarrie@gmail.com',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License', # example license
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
)
