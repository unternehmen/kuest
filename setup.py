from setuptools import setup, find_packages

setup(
    name='kuest',
    version='0.1.0',
    packages=find_packages(),
    author='Chris Murphy',
    author_email='murphy249@marshall.edu',
    install_requires=['pygame==1.9.3', 'PyGLM==0.4.4b1', 'PyOpenGL==3.1.0'],
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'kuest = kuest:main'
        ]
    }
)
