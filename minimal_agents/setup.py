"""Setup configuration for minimal_agents package."""

from setuptools import setup, find_packages

setup(
    name='minimal_agents',
    version='0.1.0',
    description='A lightweight framework for LLM-based agents with tools',
    author='AD',
    author_email='your.email@example.com',
    url='https://github.com/yourusername/minimal_agents',
    packages=find_packages(),
    install_requires=[
        'openai>=1.0.0',  # For OpenAI models
        'pydantic>=2.0.0',  # For data validation
        'requests>=2.28.0',  # For API calls
        'python-dotenv>=1.0.0',  # For loading environment variables
    ],
    extras_require={
        'google': [
            'google-genai',  # For Gemini models
        ],
        'development': [
            'pytest>=7.0.0',
            'black>=23.0.0',
            'isort>=5.10.0',
        ],
        'tools': [
            'pandas>=2.0.0',  # For data operations
            'beautifulsoup4>=4.11.0',  # For web scraping
        ]
    },
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
    ],
    python_requires='>=3.9',
)