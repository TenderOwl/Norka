from setuptools import setup

setup(
    name='norka',
    version='0.4.0',
    packages=['norka', 'norka.models', 'norka.widgets', 'norka.services'],
    url='https://tenderowl.com/norka',
    license='MIT',
    author='Andrey Maksimov',
    author_email='meamka@ya.ru',
    description='Text editor baked for simplicity.',
    install_requires=['pygobject','requests','writeasapi'],
    python_requires='>=3.6',
    scripts=['bin/norka'],
    # package_data=[
    #     'data/norka.png', 
    #     'data/com.github.tenderowl.norka.desktop',
    # ],
    entry_points={
        "console_scripts": [
            "norka = norka.main:main",
        ]
    }
)
