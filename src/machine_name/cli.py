# -*- coding: utf-8 -*-
# Python

"""Copyright (c) Alexander Fedotov.
This source code is licensed under the license found in the
LICENSE file in the root directory of this source tree.
"""
from os import environ
from .config import settings
import sys
import json
import click


@click.command()
@click.option('--provider-api-key', 'provider_api_key', envvar='PROVIDER_API_KEY',
              default='', help='Language Model API provider key.')
@click.option('--github-token', 'github_token', envvar='GITHUB_TOKEN',
              default='', help='GitHub API token for private repo access.')
@click.option('--mode', type=click.Choice(['single', 'daemon']),
              default='single',
              help='single: one-shot stdin→stdout. '
                   'interactive: line-delimited JSON loop.')
def run(provider_api_key, github_token, mode):
    """machine-name: an AI agent communicating via stdin/stdout.

    In 'single' mode (default): reads a full JSON array from stdin,
    responds once, and exits.

    In 'daemon' mode: reads one JSON line at a time from stdin,
    responds with one JSON line on stdout, and loops until EOF or SIGINT.
    """
    # Set environment variables so electroid and githf pick them up
    if provider_api_key:
        if provider_api_key.startswith('sk-proj-'):
            settings['provider'] = 'OpenAI'
            environ['OPENAI_API_KEY'] = provider_api_key
        elif provider_api_key.startswith('sk-ant-'):
            settings['provider'] = 'Anthropic'
            environ['ANTHROPIC_API_KEY'] = provider_api_key
        elif provider_api_key.startswith('AIzaSy'):
            settings['provider'] = 'Gemini'
            environ['GEMINI_API_KEY'] = provider_api_key
        elif provider_api_key.startswith('gsk_'):
            settings['provider'] = 'Groq'
            environ['GROQ_API_KEY'] = provider_api_key
        elif provider_api_key.startswith('xai-'):
            settings['provider'] = 'XAI'
            environ['XAI_API_KEY'] = provider_api_key
        elif provider_api_key.startswith('LLM|'):
            settings['provider'] = 'Meta'
            environ['META_API_KEY'] = provider_api_key
        else:
            if settings['provider'] == '':
                raise ValueError(f"Unrecognized API key prefix and no provider specified.")
    if github_token:
        environ['GITHUB_TOKEN'] = github_token

    from .machine import machine

    if mode == 'daemon':
        _run_daemon(machine)
    else:
        _run_single(machine)


def _run_single(machine):
    """One-shot mode: read full JSON from stdin, respond, exit."""
    try:
        messages = json.load(sys.stdin)
    except json.JSONDecodeError as e:
        print(f"Error: invalid JSON on stdin: {e}", file=sys.stderr)
        sys.exit(1)

    if not isinstance(messages, list):
        print("Error: stdin must contain a JSON array of messages.",
              file=sys.stderr)
        sys.exit(1)

    text, thoughts = machine(messages)
    json.dump([text, thoughts], sys.stdout)


def _run_daemon(machine):
    """Daemon: line-delimited JSON loop.

    Each line on stdin is a JSON array of messages.
    Each response is a JSON array [text, thoughts] followed by newline.
    Loops until SIGINT on stdin.
    """
    print("daemon", file=sys.stderr)
    try:
        # Loop blocks until input is available on stdin
        for line in sys.stdin:
            line = line.strip()
            if not line:
                continue

            try:
                messages = json.loads(line)
            except json.JSONDecodeError as e:
                print(f"Error: invalid JSON: {e}", file=sys.stderr)
                continue

            if not isinstance(messages, list):
                print("Error: expected a JSON array of messages.",
                      file=sys.stderr)
                continue

            text, thoughts = machine(messages)
            json.dump([text, thoughts], sys.stdout)
            sys.stdout.write('\n')
            sys.stdout.flush()
    except KeyboardInterrupt:
        sys.exit(0)


if __name__ == '__main__':
    run()
