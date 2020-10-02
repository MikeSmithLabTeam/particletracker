import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name='particletracker',
    version='0.1',
    packages=setuptools.find_packages(
        exclude=('tests', 'docs')
    ),
    url='https://github.com/MikeSmithLabTeam/particletracker',
    install_requires=[
        'opencv-python',
        'numpy',
        'matplotlib',
        'qimage2ndarray',
        'tqdm',
        'pandas',
        'trackpy',
        'labvision @ git+https://github.com/MikeSmithLabTeam/labvision',
        'filehandling @ git+https://github.com/MikeSmithLabTeam/filehandling'
    ],
    # dependency_links=[
    #     'https://github.com/MikeSmithLabTeam/labvision/tarball/repo/master#egg=package-1.0',
    # 'https://github.com/MikeSmithLabTeam/filehandling/tarball/repo/master#egg=package-1.0',
    # ],
)
