from setuptools import setup, find_packages

__version__ = 0.8

setup(name='gym_connect4',
      version=__version__,
      description='OpenAI gym environment for Connect 4',
      url='https://github.com/Danielhp95/gym-connect4',
      author='Sarios',
      author_email='madness@xcape.com',
      packages=find_packages(),
      install_requires=['gym', 'numpy', 'colorama']
)
