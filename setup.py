import setuptools

classifiers = [
    'Development Status :: 3 - Alpha',
    'Environment :: Console',
    'Intended Audience :: Information Technology',
    'License :: OSI Approved :: Apache Software License',
    'Natural Language :: English',
    'Operating System :: POSIX :: Linux',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.5',
]

setuptools.setup(
    name='messaging_server',
    version='0.1',
    description='Messaging server using WebSockets',
    url='https://github.com/JordanP',
    author='Jordan Pittier',
    author_email='jordan.pittier@gmail.com',
    license='Apache 2.0',
    packages=['messaging_server'],
    classifiers=classifiers,
    entry_points={
        'console_scripts': [
            'messaging_server = messaging_server.main:main',
        ],
    }
)
