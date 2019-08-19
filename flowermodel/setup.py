from setuptools import setup

setup(name='flowermodel',
      description='''A set of codes to analyze flower isoform mutant coculture model data from: 
      Madan, Esha, et al. "Flower isoforms promote competitive growth in cancer." Nature (2019): 1.''',
      packages=['flowermodel'],
      scripts=['flowermodel/flowermodel'],
      install_requires=open("REQUIREMENTS.txt").readlines(),
      zip_safe=False)
