# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Tadakan is a Python-based file renaming and filtering tool that generates Windows batch files for drag-and-drop file operations. It supports preset-based naming patterns for images, audio, text, and video files.

## Essential Commands

```bash
# Setup and installation
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Run application
python src/main.py --demo                    # Demo mode with example preset
python src/main.py --list                    # List available presets
python src/main.py --preset "preset_name" --values "field1=value1,field2=value2" --files *.jpg --output ./output/

# Testing
python -m pytest test/ -v                    # Run all tests
python -m pytest test/test_preset_manager.py -v  # Run specific test file
python -m pytest test/ -k "test_create_preset"   # Run specific test

# Code quality
mypy src/                                     # Type checking
black src/ test/                              # Code formatting  
flake8 src/ test/                            # Linting
```

## Development Workflow

This project follows TDD (Test-Driven Development) methodology as specified in the requirements:

1. **Write failing tests first** - Always create tests before implementation
2. **Run tests to confirm failure** - Ensure tests fail for the right reasons  
3. **Implement minimal code** - Write just enough code to make tests pass
4. **Refactor** - Improve code while keeping tests green
5. **Commit and iterate** - Use git to track progress between cycles

Use these patterns when adding new features or modifying existing ones.

## Core Architecture

Tadakan follows a layered architecture with clear separation of concerns:

### Models Layer (`src/models/`)
- **Preset**: Core data model defining naming patterns with field validation and JSON serialization
- **FileItem**: Represents files with original/new names and metadata

### Services Layer (`src/services/`)  
- **PresetManager**: CRUD operations for presets with JSON persistence
- **FileRenamer**: Core renaming logic with duplicate detection and NG word filtering
- **BatchGenerator**: Creates Windows batch files (.bat) with Shift_JIS encoding

### Configuration (`src/config/`)
- **Settings**: Hierarchical configuration management with JSON persistence and default values

### CLI Interface (`src/main.py`)
- Command-line interface with demo mode, preset management, and batch generation
- Supports --demo, --list, --preset operations with argument parsing

## Key Implementation Details

### Preset System
Presets define naming patterns using placeholder syntax (e.g., `{陣営}_{キャラ名}_{番号}`). The system validates that all placeholders in patterns correspond to defined fields.

### Batch File Generation
Generated .bat files use Windows-specific commands with proper path escaping and Shift_JIS encoding for Japanese text compatibility. Files include error handling and logging options.

### File Processing Pipeline
1. Load preset and validate input values
2. Generate new filename using pattern substitution  
3. Check for duplicates and apply auto-numbering
4. Create batch file with rename and move commands
5. Execute via drag-and-drop or direct invocation

### Test-Driven Development
The codebase was developed using TDD with 43 comprehensive tests covering all functionality. Tests are organized by component and include edge cases, validation, and error handling scenarios.

## File Format Support

- **Images**: jpg, jpeg, png, gif, bmp, webp
- **Audio**: mp3, wav, flac, aac, ogg  
- **Text**: txt, md, csv, json, xml
- **Video**: mp4, avi, mkv, mov, wmv

## Import Path Configuration

Services use absolute imports (`from models.preset import Preset`) rather than relative imports. The main.py file configures sys.path to enable this pattern.

## Future Development Roadmap

### Version 0.2 - Full GUI Implementation
The project is transitioning to a full GUI version with the following key features:

#### Preset ID System
- **6-digit alphanumeric random IDs** (e.g., B63EF9) for unique preset identification
- **Batch file naming**: `PresetID_陣営_キャラ名.bat` format
- **File naming**: `PresetID_陣営_キャラ名_A00001.extension` with auto-increment

#### GUI Architecture Requirements
- **Unified Home Screen**: Single interface for all operations (preset management, file processing, batch management)
- **Dynamic Form Generation**: Input forms that adapt based on selected preset fields
- **Drag & Drop Support**: Full folder and multi-file drag & drop functionality
- **Batch File Stock Management**: Persistent storage and reuse of generated batch files

#### Folder Structure
```
Pictures/Tadakan/                    # Default working directory
├── rename_batches/                  # Renamed batch files storage
├── filter_batches/                  # Filter batch files storage  
├── display/                         # Temporary filter results
└── [processed files]                # Final renamed files
```

#### Key Technical Considerations
- **Japanese Path Support**: Full support for Japanese file paths and names
- **Windows Batch Compatibility**: Shift_JIS encoding with proper character escaping
- **Extensibility**: Modular design for easy feature additions
- **Error Handling**: Comprehensive error handling with user-friendly messages

When implementing GUI features, prioritize:
1. **Extensibility** over complexity
2. **User experience** over technical perfection  
3. **Test coverage** for all new functionality
4. **Windows compatibility** for batch file operations