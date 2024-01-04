# BLOGEN - Blog Generation Application (Version 0.1)

BLOGEN is a blog generation application designed to create well-structured blog posts using Markdown formatting. It takes primary keywords as input and generates engaging and informative blog content for various topics. This README file provides an overview of the BLOGEN application and instructions for usage.

## Table of Contents
- [BLOGEN - Blog Generation Application (Version 0.1)](#blogen---blog-generation-application-version-01)
  - [Table of Contents](#table-of-contents)
  - [Introduction](#introduction)
  - [Features](#features)
  - [Getting Started](#getting-started)
  - [Usage](#usage)
  - [Dependencies](#dependencies)
  - [Contributing](#contributing)
  - [License](#license)

## Introduction
BLOGEN is a Python-based blog generation tool that leverages the power of GPT-3.5 (OpenAI's language model) to create captivating blog posts. The application uses the primary keywords provided by the user to generate prompts and interactively calls the language model to produce content for each step of the blog creation process.

## Features
- **Keyword-driven Content Generation**: BLOGEN accepts primary keywords as input to create blog content tailored to specific topics.
- **Iterative Blog Building**: The application follows a step-by-step approach to create a complete blog post, including introduction, tone, issue, remedy, options, implementation, pros and cons (optional), and conclusion.
- **Various Writing Tones**: BLOGEN offers the flexibility to generate blog content in different tones, such as informative, conversational, persuasive, and more.
- **Easy Integration with Markdown**: The generated blog content is formatted using Markdown, making it easily integrable with various platforms and content management systems.
- **Version Control**: This is Version 0.1 of the BLOGEN application, with potential updates and improvements planned for future releases.

## Getting Started
To get started with BLOGEN, follow these steps:

1. Clone the BLOGEN repository to your local machine:
   ```
   git clone https://github.com/gaurav18115/blogen.git
   ```

2. Install the required dependencies (ensure you have Python 3.x installed):
   ```
   pip install -r requirements.txt
   ```

3. Obtain an API key for the GPT-3.5 language model from OpenAI and save it in a secure manner.

4. Obtain an API key for [SerpAPI](serpapi.com), the free version includes 100 searches/month.

5. Set your API key as an environment variable:
   ```
   export OPENAI_API_KEY=your_api_key
   export SERP_API_KEY=your_api_key
   ```
   
6. Launch the BLOGEN application:
   ```
   python blog_gen_algo_v0.1.py
   ```

## Usage
Upon launching the BLOGEN application, you will be prompted to enter primary keywords for your blog topic. Follow the on-screen instructions to provide the necessary information.

The application will iteratively call the GPT-3.5 language model to generate content for each step of the blog creation process. The generated content will be presented in Markdown format.

Once the blog is fully generated, you can copy the Markdown content and paste it into your preferred platform or content management system for publishing.

## Dependencies
BLOGEN relies on the following Python packages:

- `openai`: The official Python package for interfacing with the OpenAI GPT-3.5 language model.
- `click`: A Python package for creating beautiful command-line interfaces.
- `markdown`: A package for processing and rendering Markdown content.

## Contributing
Contributions to BLOGEN are welcome! If you have ideas for improvements or bug fixes, please feel free to open an issue or submit a pull request. Before contributing, make sure to read our [Contributing Guidelines](CONTRIBUTING.md).

## License
BLOGEN is licensed under the [MIT License](LICENSE). Feel free to use, modify, and distribute this software as per the terms of the license.

For any questions or feedback, please contact me at `gaurav18115@gmail.com`.

---
This README file was generated using BLOGEN (Version 0.1) - The Blog Generation Application.