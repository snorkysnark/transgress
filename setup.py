from setuptools import setup

setup(name='transgress',
      version='0.1',
      description='Async transformation of postgress data',
      url='https://github.com/snorkysnark/transgress',
      author='francisthebasilisk',
      author_email='snorkysnark@gmail.com',
      license='MIT',
      packages=['transgress'],
      install_requires=[
        'safetywrap',
        'trio',
        'psycopg3 @ git+https://github.com/psycopg/psycopg3.git#subdirectory=psycopg3'
      ],
      zip_safe=False,
      scripts=['bin/transgress'])
