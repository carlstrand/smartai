"""Package setup script
"""

from setuptools import setup

setup(
    name='smartai',
    version='0.0.999',
    description='Smart Python Library for Artificial Intelligence',
    long_description="Can we let the data build models by itself?",
    url='https://github.com/yajiez/smartai',
    author='Yajie',
    packages=['src/smartai'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'ipython',
        'tqdm',
        'numpy',
        'pillow',
        'matplotlib',
        'seaborn',
        'pandas',
        'pyarrow',
        'torch',
        'torchvision',
        'nltk'
    ],
    extras_require={
        'tests': [
            'tox',
            'pytest',
            'pytest-pep8',
            'pytest-xdist',
            'pytest-cov',
            'pytest-timeout'
        ]
    }
)
