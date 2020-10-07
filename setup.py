from setuptools import setup


def doc():
    with open("README.md", "r", encoding="utf-8") as readme:
        return readme.read().strip()


setup(
    name='norka',
    version='0.6.2',
    packages=['norka'],
    url='https://tenderowl.com/norka',
    license='MIT',
    author='Andrey Maksimov',
    author_email='meamka@ya.ru',
    description='Text editor baked for simplicity.',
    long_description=doc(),
    keywords=["doc", "html", "md", "markdown", "editor"],
    requires=['python_gi', 'gtksourceview'],
    install_requires=['PyGObject', 'pycairo', 'requests==2.24.0', 'writeasapi', 'mistune==2.0.0a4'],
    python_requires='>=3.6',
    scripts=['norka/main.py'],
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
