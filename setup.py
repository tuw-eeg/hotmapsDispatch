"""
to be uploaded to PyPI, you need to provide some basic information about your package
The setup.py file should be placed in the top folder of your package
"""
import pathlib
from setuptools import setup,find_packages

# The directory containing this file
root = pathlib.Path(__file__).parent

# The text of the README file
README = (root / "README.md").read_text()

# This call to setup() does all the work
setup(
    name="hotmapsDispatch", # needed for pypi
    version="0.0.1", # needed for pypi same as in __init__.py
    description='A web user interface for energy system modelling',
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/tuw-eeg/hotmapsDispatch/tree/dev",
    author="Michal Hartner, Richard Büchele, David Schmidinger, Michael Gumhalter, Jeton Hasani",
    author_email="hasani@eeg.tuwien.ac.at",
    license="Apache 2.0",
    classifiers=[
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3.6",
    ],
    packages= find_packages(), # needed for pypi!
    package_data={
        # If any package contains *.dat files include them
        '': ['*.dat', '*.xlsx',"*.js","*.html","*.png"]},
    include_package_data=True,
    install_requires=["bokeh==0.12.10", "numpy","pandas","openpyxl","xlrd","matplotlib","pyomo","tornado==4.5.3","xlsxwriter","nodejs"],
	keywords=['energy systems', 'optimisation', 'mathematical programming', "web user innterfaace"],
    entry_points={
        "console_scripts": [
            "hotmapsDispatch_console=app.__main__:main",
        ],
        "gui_scripts": [
            "hotmapsDispatch=app.__main__:main",
        ]
    },
)

# python setup.py sdist bdist_wheel
# twine check dist/*
# twine upload --repository-url https://test.pypi.org/legacy/ dist/*
