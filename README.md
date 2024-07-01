# Front Matter meta description and keyword generator

This CLI tool helps generate and write metadata for articles written with front matter in markdown files. It uses OpenAI's GPT model to produce a short description and a list of keywords for the article, which are then added to the front matter of the markdown file.

## Features

- Reads the content of a markdown file containing front matter tags.
- Sends a request to OpenAI's chat completion endpoint to generate metadata.
- Produces a short description of the content using a neutral tone, stating what a reader might expect to learn.
- Produces a short list of keywords.
- Updates the markdown file, respecting the front matter syntax with the meta tags for the head.
- Option to override existing metadata.
- Option to update the file in place or print the updated content to stdout.

## Installation

1. Clone the repository:
    ```sh
    git clone https://github.com/advanced-stack/frontmatter-meta-assistant.git
    cd frontmatter-meta-assistant
    ```

2. Install the required Python packages:
    ```sh
    python3 -m venv venv
    source venv/bin/activate
    pip3 install -r requirements.txt
    ```

3. Set your OpenAI API key as an environment variable:
    ```sh
    export OPENAI_API_KEY=your_openai_api_key
    ```

## Usage

```sh
python main.py [OPTIONS] FILENAME
```

### Options

- `FILENAME`: The markdown filename containing front matter tags.
- `--model`: OpenAI model to use (default: `gpt-4o-2024-05-13`).
- `--temperature`: Temperature for the OpenAI model (default: `0.7`).
- `--override`: Override existing head metadata if present.
- `--inplace`: Replace content in the file directly.

### Example

```sh
python main.py --override example.md
```

This command will read the `example.md` file, generate metadata and print the output on the console.

## Warning

- If the `head` metadata is already set up in the front matter and the `--override` flag is not used, the tool will skip updating the metadata and print a warning message.


## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

