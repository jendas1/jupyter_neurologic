from distutils.core import setup

setup(
    name='neurologic',
    version='0.1',
    packages=['neurologic'],
    package_data={'neurologic': ['*']},
    url='https://github.com/jupyter_neurologic',
    license='',
    author='Jan Studený',
    author_email='',
    description='',
    requires=['holoviews', 'pandas', 'jupyter']
)