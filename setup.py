from distutils.core import setup

setup(
    name='Tower2',
    version='1.0.0.0',
    packages=['game_template', 'game_template.view', 'game_template.audio', 'game_template.model',
              'game_template.utils', 'game_template.utils.trpg', 'game_template.controller'],
    url='',
    license='',
    author='kwoolter',
    author_email='kwoolter@gmail.com',
    description='',
    install_requires=['pygame']
)
