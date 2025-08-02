# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Tadakan is a Python-based file renaming and filtering tool that supports batch operations on images, music, and text files. The project name means "file companion for easy organization" in Japanese.

## Development Setup

```sh
# Clone and setup
git clone https://github.com/（ユーザー名）/tadakan.git
cd tadakan
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Run the application
python src/main.py
```

## Architecture

- **src/main.py**: Main application entry point (currently empty - development in progress)
- **presets/**: Directory for naming presets and batch operation configurations
- **requirements.txt**: Python dependencies (currently empty)

## Key Features (Planned)

1. **Preset-based Renaming**: Use predefined naming patterns
2. **Batch Processing**: Automated renaming and organization
3. **Multi-format Support**: Images, music, and text files
4. **High-speed Filtering**: Fast file processing capabilities

## Development Notes

This appears to be an early-stage project with the basic structure in place but implementation not yet started. The main.py file and requirements.txt are currently empty, indicating active development is needed.