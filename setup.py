from setuptools import setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="nonebot_plugin_bVideo",
    version="1.0.2",
    author="wziru",
    description="A NoneBot2-based plugin for processing plugins that push the latest videos of the B station up master.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ziru-w/nonebot_plugin_bVideo",
    project_urls={
        "Bug Tracker": "https://github.com/ziru-w/nonebot_plugin_bVideo/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
    packages=["nonebot_plugin_bVideo"],
    python_requires=">=3.7",
    install_requires = [
        'nonebot2>=2.0.0b1',
        'apscheduler>=3.5.1',
        'requests>=2.0.0'
    ]
)
