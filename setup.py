from setuptools import setup

setup(name='pcidss_convert',
      version='0.0.1',
      description='PCI DSS docx2sql converter',
      classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7',
        'Topic :: Text Processing :: Linguistic',
      ],
      author='Yaroslav Dobzhanskij',
      author_email='merlyn.tgz@gmail.com',
      license='MIT',
      packages=['pcidss_convert'],
      install_requires=[
          'mammoth==1.3.5',
      ],
      scripts=['bin/pcidss_convert'],
      zip_safe=True)
