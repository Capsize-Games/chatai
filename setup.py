from setuptools import setup, find_packages

setup(
    name='chatairunner',
    version='1.0.8',
    author='Capsize LLC',
    description='Chat AI: A chatbot framework',
    long_description=open("README.md", "r", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    keywords="ai, chatbot, chat, ai",
    license="AGPL-3.0",
    author_email="contact@capsize.gg",
    url="https://github.com/Capsize-Games/chat-ai",
    package_dir={"": "src"},
    packages=find_packages("src"),
    include_package_data=True,
    python_requires=">=3.10.0",
    install_requires=[
        "aihandler==1.8.16",
    ]
)
