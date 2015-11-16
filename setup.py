from setuptools import setup, find_packages


setup(name='ansible-role',
      version="0.1",
      author="Mike Spindel",
      author_email="mike@spindel.is",
      license="LICENSE",
      keywords="",
      url="http://github.com/deactivated/",
      description="",
      packages=find_packages(exclude=['ez_setup']),
      classifiers=[
          "Development Status :: 5 - Production/Stable",
          "License :: OSI Approved :: MIT License",
          "Intended Audience :: Developers",
          "Natural Language :: English",
          "Programming Language :: Python"],
      entry_points={
          'console_scripts': ['ansible-role=ansible_role.do_roles:main'],
      })
