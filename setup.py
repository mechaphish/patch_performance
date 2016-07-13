from distutils.core import setup

setup(
      name='network_poll_creator',
      version='0.01',
      packages=['network_poll_creator'],
      install_requires=[i.strip() for i in open('requirements.txt').readlines() if 'git' not in i],
      description='Creates raw polls (XMLs) from captured raw round traffic.',
      url='https://git.seclab.cs.ucsb.edu/cgc/network_poll_creator',
)
