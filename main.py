# -*- coding: utf-8 -*-
"""
This CLI tool helps write metadata for articles written with front matter.

The input is a markdown filename containing front matter tags.

For example, in one markdown file, one can find

```markdown
---
head:
  - - meta
    - name: description
      content: hello
  - - meta
    - name: keywords
      content: super duper SEO
prev:
  text: Previous title
  link: /resources/link-to-previous
next:
  text: Next title
  link: /resources/link-to-next
---

# Title of the article

rest of the content...

```

This CLI performs the following:

1. Read the content
2. Send a request to OpenAI chat completion endpoint (configurable options through argparse flags like model and temperature)
3. Produce a short description of the content using a neutral tone stating what a reader might expect to learn
4. Produce a short list of keywords
5. Update markdown file respecting the front matter syntax with the meta tags for head.

Warning to display:

- if "head" is already setup, skip (by default, add a flag to override)

"""

# -*- coding: utf-8 -*-
import argparse
import yaml
import re
import os
import sys

from dataclasses import dataclass, asdict
from llm_core.assistants import OpenAIAssistant


@dataclass
class MetadataEntry:
    name: str
    content: str


@dataclass
class ArticleMetadata:
    """
    {
        'head': [
            ['meta', {'content': 'hello', 'name': 'description'}],
            ['meta', {'content': 'super duper SEO', 'name': 'keywords'}],
        ]
    }
    """

    description: MetadataEntry
    keywords: MetadataEntry

    system_prompt = "You are a helpful web copywriter"
    prompt = """
    Content:
    {content}
    --
    You will write the content for the meta tags of this article. The
    description should be approx. 180 characters long (2 to 3 sentences).
    The description should be focused on the results a reader might expect
    from reading this article, i.e. it's not a summary but an overview of the
    key results a reader will obtain.

    Then write the keywords.
    """

    @classmethod
    def generate_metadata(cls, content, model, temperature):
        with OpenAIAssistant(
            cls, model=model, completion_kwargs={"temperature": temperature}
        ) as assistant:
            article_metadata = assistant.process(content=content)
            return article_metadata


def read_markdown_file(filename):
    """Read the content of the markdown file."""
    with open(filename, "r", encoding="utf-8") as file:
        content = file.read()
    return content


def parse_front_matter(content):
    """Parse the front matter and body from the markdown content."""
    match = re.match(r"---\n(.*?)\n---\n(.*)", content, re.DOTALL)
    if match:
        front_matter = yaml.safe_load(match.group(1))
        body = match.group(2)
        return front_matter, body
    return {}, content


def generate_metadata(content, model, temperature):
    return ArticleMetadata.generate_metadata(content, model, temperature)


def update_front_matter(front_matter, description, keywords):
    """Update the front matter with the generated description and keywords."""
    if "head" not in front_matter:
        front_matter["head"] = []
    front_matter["head"].append(
        ["meta", {"name": "description", "content": description}]
    )
    front_matter["head"].append(
        ["meta", {"name": "keywords", "content": keywords}]
    )
    return front_matter


def write_front_matter(front_matter, file=sys.stdout):
    """Write the updated front matter and body to stdout."""
    file.write("---\n")
    yaml.dump(front_matter, file, default_flow_style=False)
    file.write("---\n")


def write_body(body, file=sys.stdout):
    file.write(body)


def main():
    parser = argparse.ArgumentParser(
        description="CLI tool to write metadata for blog articles."
    )
    parser.add_argument(
        "filename",
        type=str,
        help="Markdown filename containing front matter tags.",
    )
    parser.add_argument(
        "--model",
        type=str,
        default="gpt-4o-2024-05-13",
        help="OpenAI model to use.",
    )
    parser.add_argument(
        "--temperature",
        type=float,
        default=0.7,
        help="Temperature for the OpenAI model.",
    )
    parser.add_argument(
        "--override",
        action="store_true",
        help="Override existing head metadata if present.",
    )
    parser.add_argument(
        "--inplace",
        action="store_true",
        default=False,
        help="Replace content in the file directly",
    )
    args = parser.parse_args()

    # Get the OpenAI API key from the environment variable
    if not os.getenv("OPENAI_API_KEY"):
        print(
            "Error: The environment variable OPENAI_API_KEY is not set.",
            file=sys.stderr,
        )
        sys.exit(1)

    # Read the markdown file
    content = read_markdown_file(args.filename)
    front_matter, body = parse_front_matter(content)

    # Check if 'head' is already set up
    if "head" in front_matter and not args.override:
        print(
            "Warning: 'head' is already set up. Use --override to overwrite.",
            file=sys.stderr,
        )
        return

    # Generate metadata
    metadata = generate_metadata(body, args.model, args.temperature)
    head = {
        "head": [
            ["meta", asdict(metadata.description)],
            ["meta", asdict(metadata.keywords)],
        ]
    }
    front_matter.update(head)

    if args.inplace:
        with open(args.filename, "w") as file:
            write_front_matter(front_matter, file=file)
            write_body(body, file=file)
    else:
        write_front_matter(front_matter, file=sys.stdout)


if __name__ == "__main__":
    main()
