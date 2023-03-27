from setuptools import setup, find_packages

setup(
    name='chatai',
    version='1.0.5',
    author='Capsize LLC',
    description='Chat AI: A chatbot framework',
    long_description="",
    long_description_content_type="",
    keywords="ai, chatbot, chat, ai",
    license="AGPL-3.0",
    author_email="contact@capsize.gg",
    url="https://github.com/w4ffl35/chatai",
    package_dir={"": "chatai"},
    packages=find_packages("chatai"),
    include_package_data=True,
    python_requires=">=3.10.0",
    install_requires=[
        "aihandler==1.8.11",
    ]
)
