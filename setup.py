#!/usr/bin/env python
from setuptools import setup, find_packages

def read_files(*filenames):
	"""
	Output the contents of one or more files to a single concatenated string.
	"""
	output = []
	for filename in filenames:
		f = open(filename)
		try:
			output.append(f.read())
		finally:
			f.close()
	return '\n\n'.join(output)

setup(
	name='django-cron',
	version=typesight.VERSION,
	url='https://github.com/timstudd/django-cron',
	description='Threaded cron-like tasks for Django',
	long_description=read_files('README.md'),
	author='Tim Studd',
	author_email='tim@timstudd.com',
	platforms=['any'],
	packages=find_packages(),
	include_package_data=True,
	install_requires=[
		'django>=1.5',
	],
	classifiers=[
		'Environment :: Web Environment',
		'Framework :: Django',
		'Intended Audience :: Developers',
		'Operating System :: OS Independent',
		'Programming Language :: Python',
		'Programming Language :: Python :: 2.6',
		'Programming Language :: Python :: 2.7',
		'Topic :: Software Development :: Libraries :: Application Frameworks',
		'Topic :: Software Development :: Libraries :: Python Modules',
	],
	zip_safe=False,
)

