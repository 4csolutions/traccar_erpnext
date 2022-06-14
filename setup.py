from setuptools import setup, find_packages

with open("requirements.txt") as f:
	install_requires = f.read().strip().split("\n")

# get version from __version__ variable in traccar_erpnext/__init__.py
from traccar_erpnext import __version__ as version

setup(
	name="traccar_erpnext",
	version=version,
	description="Traccar integration module",
	author="4C Solutions",
	author_email="info@4csolutions.in",
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
