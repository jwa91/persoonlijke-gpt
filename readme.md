# Multipurpose LLM tool

This is a modification of a project originally created by Alejandro AO, you can find his youtube here: [YouTube](https://youtu.be/dXxQ0LR-3Hg).

Some parts of this repo might be in Dutch, as I am from the Netherlands, but overall working should be prety clear. 

## Introduction
------------
This is a python project with several small LLM use cases. For now it has a "chat with PDF" and "email to podcast generator". It also has a flexible Streamlit skin for a multipurpose LLM set up, that makes it easy to add features. 

## How It Works
------------

### MultiPDF Chat: 

![MultiPDF Chat App Diagram](./docs/PDF-LangChain.jpg)

The application follows these steps to provide responses to your questions:

1. PDF Loading: The app reads multiple PDF documents and extracts their text content.

2. Text Chunking: The extracted text is divided into smaller chunks that can be processed effectively.

3. Language Model: The application utilizes a language model to generate vector representations (embeddings) of the text chunks.

4. Similarity Matching: When you ask a question, the app compares it with the text chunks and identifies the most semantically similar ones.

5. Response Generation: The selected chunks are passed to the language model, which generates a response based on the relevant content of the PDFs.

### dailyemailcast

1. Email Reading and Text Extraction: The application reads multiple email documents in .eml format uploaded by the user. It extracts the text content from these emails, handling both plain text and multipart formats, ensuring attachments are not included in the text extraction process.

2. Prompt Retrieval: It retrieves predefined prompts based on the selected podcast style from a directory of text files. Each text file contains a specific prompt that guides the generation of content, allowing the application to tailor the podcast's theme or style.

3. OpenAI Query for Content Generation: The application combines the extracted email text with the selected prompt and sends this combined input to OpenAI's API. It uses a specific model to generate a response that is contextually related to the input text, effectively creating content that is likely to be relevant for the podcast episode.

4. Text-to-Speech Conversion: The generated text from OpenAI is then converted into speech using OpenAI's text-to-speech service. The user can select a voice from multiple options, which influences the tone and style of the audio output. The application saves this audio content as an MP3 file.

5. Podcast Creation and Playback: Finally, the application provides an interface for the user to upload email documents, select a voice and podcast style, and initiate the processing. Once the text-to-speech conversion is complete, the generated podcast is available for playback directly within the app.

6. User Interface with Streamlit: The entire process is wrapped in a user-friendly interface created with Streamlit, allowing users to easily upload email documents, choose a voice and podcast style, and listen to the generated podcast episode.

## Dependencies and Installation
----------------------------
To install the MultiPDF Chat App, please follow these steps:

1. Clone the repository to your local machine.

2. Install the required dependencies by running the following command:
   ```
   pip install -r requirements.txt
   ```

3. Obtain an API key from OpenAI and add it to the `.env` file in the project directory.
```commandline
OPENAI_API_KEY=your_secrit_api_key
```

## Usage
-----
To use the App, follow these steps:

1. Ensure that you have installed the required dependencies and added the OpenAI API key to the `.env` file.

2. Run the `main.py` file using the Streamlit CLI. Execute the following command:
   ```
   streamlit run app.py
   ```

3. The application will launch in your default web browser, displaying the user interface.

## Contributing
------------
This repository is intended for educational purposes and does not accept further contributions. It serves as supporting material for a YouTube tutorial that demonstrates how to build this project. Feel free to utilize and enhance the app based on your own requirements.

## License
-------
The App is released under the [MIT License](https://opensource.org/licenses/MIT).