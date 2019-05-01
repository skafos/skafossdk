from distutils.core import setup

DESCRIPTION = """"""

REQS = """"""

VERSION = """"""

setup(
  name='skafos',
  packages=['skafos'],
  version=VERSION,
  license='MIT',  # Chose a license from here: https://help.github.com/articles/licensing-a-repository
  description=DESCRIPTION,
  author='Skafos, LLC',
  author_email='skafos@skafos.ai',
  url='https://github.com/skafos/skafossdk',
  download_url='',
  keywords=['machine learning delivery', 'mobile deployment', 'model versioning'],
  install_requires=REQS,
  classifiers=[
    'Development Status :: 3 - Alpha',      # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
    'Intended Audience :: Developers',      # Define that your audience are developers
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: MIT License',   # Again, pick a license
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: 3.7'
  ],
)
