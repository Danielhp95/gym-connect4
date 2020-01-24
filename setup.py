from setuptools import setup, find_packages

setup(name='gym_connect4',
      version='0.1',
      description='OpenAI gym environment for Connect 4',
      url='https://github.com/Danielhp95/gym-connect4',
      author='Sarios',
      author_email='madness@xcape.com',
      packages=find_packages(),
      install_requires=['gym', 'numpy', 'colorama']
      )
