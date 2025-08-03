# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Tadakan v0.2 is a Python-based "Stock-Type Batch File Management System" for file renaming and organization. It features a full GUI interface with persistent batch file management, preset-based naming patterns, and workspace management. The system generates Windows batch files with Japanese text support.

## Essential Commands

```bash
# Setup and installation
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Run application
python src/main.py --gui                     # Launch full GUI interface (primary mode)
python src/main.py --gui --workspace "C:/MyWorkspace"  # GUI with custom workspace
python src/main.py --demo                    # Demo mode with example preset
python src/main.py --list                    # List available presets

# Testing (comprehensive test suite)
python -m pytest test2/ -v                   # Run all tests
python -m pytest test2/test_gui_integration_complete.py -v  # Complete GUI integration tests
python -m pytest test2/test_drop_zone_functionality.py -v   # Drag & drop functionality tests
python -m pytest test2/test_dynamic_input_form.py -v        # Dynamic form generation tests
python -m pytest test2/test_batch_management_pure.py -v     # Batch management tests
python -m pytest test2/test_preset_id_pure.py -v           # Preset ID system tests
python -m pytest test2/test_workspace_pure.py -v           # Workspace management tests

# Single test execution
python -m pytest test2/test_gui_integration_complete.py::TestGUIIntegrationComplete::test_preset_panel_functionality -v

# Legacy CLI support
python src/main.py --preset "preset_name" --values "field1=value1,field2=value2" --files *.jpg --output ./output/

# Code quality
mypy src/                                     # Type checking
black src/ test2/                            # Code formatting  
flake8 src/ test2/                           # Linting

# Dependencies
# Core: Python 3.7+, tkinterdnd2>=0.3.0
# Testing: pytest>=6.0.0, pytest-cov>=2.10.0  
# Quality: mypy>=0.910, black>=21.0.0, flake8>=3.9.0
```

## Development Workflow

This project follows TDD (Test-Driven Development) methodology as specified in the requirements:

1. **Write failing tests first** - Always create tests before implementation
2. **Run tests to confirm failure** - Ensure tests fail for the right reasons  
3. **Implement minimal code** - Write just enough code to make tests pass
4. **Refactor** - Improve code while keeping tests green
5. **Commit and iterate** - Use git to track progress between cycles

Use these patterns when adding new features or modifying existing ones.

### TDD Implementation Guidelines
- **Test structure**: Use `test2/` directory for comprehensive test coverage
- **GUI testing**: Implement mock components for isolated testing (see `test_integrated_preset_wizard.py`)
- **Integration tests**: Test complete workflows from preset creation to batch execution
- **Pure function tests**: Separate business logic testing from GUI components

## Core Architecture v0.2

Tadakan v0.2 follows a layered architecture with full GUI integration and stock-type batch management:

### Models Layer (`src/models/`)
- **Preset**: Enhanced with 6-digit alphanumeric IDs (e.g., B63EF9) and target_extensions
- **BatchFile**: Stock-type batch file model with persistent management capabilities
- **Workspace**: Workspace management model with auto-initialization
- **ExecutionResult**: Execution tracking and reporting model
- **FileItem**: File representation with original/new names and metadata

### Services Layer (`src/services/`)  
- **PresetManager**: Enhanced CRUD with ID generation and collision detection
- **BatchManager**: Stock-type batch file management with execution tracking
- **WorkspaceManager**: Workspace initialization, switching, and maintenance
- **FileRenamer**: Core renaming logic with duplicate detection and NG word filtering
- **BatchGenerator**: Creates Windows batch files (.bat) with Shift_JIS encoding

### GUI Layer (`src/gui/`)
- **MainWindow**: Unified interface orchestrating all panels with 1000x700 layout
- **PresetPanel**: Preset selection and management with real-time preview
- **DynamicInputForm**: Auto-generated forms based on selected preset fields
- **BatchPanel**: Asynchronous batch file management with real-time execution logging
- **DropZone**: Drag & drop support for files and folders
- **PresetWizard**: Integrated single-screen preset creation (migrated from step-by-step)

### Utilities (`src/utils/`)
- **IDGenerator**: 6-digit alphanumeric preset ID generation with collision checking
- **SequenceGenerator**: A00001-format sequential numbering for files

### Configuration (`src/config/`)
- **Settings**: Hierarchical configuration with workspace path management

## Key Implementation Details v0.2

### Preset ID System
- **6-digit alphanumeric IDs**: Generated using uppercase letters and numbers (e.g., B63EF9)
- **Collision detection**: Ensures uniqueness across all presets
- **Batch naming**: `PresetID_陣営_キャラ名.bat` format for consistent identification
- **File naming**: `PresetID_陣営_キャラ名_A00001.extension` with auto-increment sequences

### Stock-Type Batch Management  
- **Persistent storage**: Batch files saved in `~/Pictures/Tadakan/rename_batches/`
- **Reusable execution**: Generated batch files can be executed multiple times
- **Execution tracking**: Complete history with file counts, success rates, and timing
- **Search functionality**: Find batches by preset ID, faction, character name

### GUI Integration Architecture
- **Component communication**: MainWindow orchestrates all panels via event handlers
- **Dynamic form generation**: Input forms adapt automatically to selected preset fields
- **Real-time updates**: Changes in one panel immediately reflect in related components
- **Layout management**: 2-column layout with left (presets/forms) and right (batches/drop zone)
- **Integrated preset creation**: Single-screen wizard replacing step-by-step navigation

### Workspace Management
- **Auto-initialization**: Creates `~/Pictures/Tadakan/` structure automatically
- **Folder organization**: `rename_batches/`, `filter_batches/`, `display/` subdirectories
- **Path validation**: Ensures workspace integrity and handles missing directories
- **Settings persistence**: Workspace preferences saved in configuration files

### File Processing Pipeline v0.2
1. **Preset selection**: User selects from preset panel with visual preview
2. **Dynamic form**: Input form generates based on preset field definitions
3. **Batch creation**: BatchFile model creates persistent .bat file with Shift_JIS encoding
4. **File targeting**: Drag & drop or manual file selection with extension filtering
5. **Execution tracking**: Complete audit trail with ExecutionResult models

## File Format Support

- **Images**: jpg, jpeg, png, gif, bmp, webp
- **Audio**: mp3, wav, flac, aac, ogg  
- **Text**: txt, md, csv, json, xml
- **Video**: mp4, avi, mkv, mov, wmv

## Import Path Configuration

Services use absolute imports (`from src.models.preset import Preset`) with full module paths. The main.py file configures sys.path to enable this pattern across GUI and service layers.

## GUI Component Communication Pattern

The MainWindow acts as a central coordinator with the following event flow:

1. **Preset Selection**: PresetPanel → MainWindow.on_preset_selected() → DynamicInputForm.generate_form_from_preset()
2. **Form Submission**: DynamicInputForm → BatchManager.create_batch_file() → BatchPanel refresh
3. **File Drop**: DropZone → BatchManager.execute_batch_with_files() → ExecutionResult tracking
4. **Workspace Switch**: WorkspaceSelector → WorkspaceManager.switch_workspace() →全panel refresh

Critical: When modifying GUI components, always update the MainWindow event handlers to maintain component synchronization.

## Workspace Structure Implementation

```
~/Pictures/Tadakan/                  # Default workspace (auto-created)
├── rename_batches/                  # Stock batch files (.bat with Shift_JIS)
├── filter_batches/                  # Filter batch files (future feature)
├── display/                         # Temporary processing results
├── presets/                         # JSON preset definitions
└── config/                          # Workspace-specific settings
```

WorkspaceManager handles initialization, validation, and switching between workspaces. All file operations respect workspace boundaries.

## Critical Development Patterns

### Preset ID Generation
```python
# Always use IDGenerator for new presets
from src.utils.id_generator import IDGenerator
preset_id = IDGenerator.generate_unique_id(existing_ids)
```

### Batch File Persistence  
```python
# Stock-type pattern: create once, execute multiple times
batch_file = BatchManager.create_batch_file(preset, values)
file_path = BatchManager.save_batch_file(batch_file)  # Persistent storage
result = BatchManager.execute_batch_with_files(batch_file, files)
```

### GUI Layout Modifications
When modifying MainWindow layout, always:
1. Update both pack() parameters and component recreation in setup_layout()
2. Test with sample data to ensure all panels are visible
3. Maintain 2-column structure: left (presets/forms), right (batches/dropzone)

### Error Handling Strategy
- **GUI errors**: Show user-friendly messages in status labels, log technical details
- **File operation errors**: Graceful degradation with retry mechanisms  
- **Workspace errors**: Auto-repair missing directories, fallback to defaults
- **Batch execution errors**: Record in ExecutionResult with detailed error messages

## Batch Execution System v0.2

### Asynchronous Execution Architecture
The batch execution system has been redesigned to prevent GUI freezes and provide real-time feedback:

```python
# Non-blocking batch execution with threading
def _execute_batch_in_thread(self, batch_path: str, filename: str):
    process = subprocess.Popen(
        ['cmd.exe', '/c', batch_path],  # Safe Windows execution
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding='cp932',
        shell=False
    )
```

### UI State Management During Execution
- **Comprehensive UI locking**: All relevant UI elements are disabled during batch execution
- **Visual feedback**: Animated spinner and status indicators show execution progress
- **Real-time logging**: Stdout/stderr streams displayed in real-time via queue-based messaging
- **Clean restoration**: UI elements automatically re-enabled after completion

### Critical Subprocess Patterns

```python
# CORRECT: List format for safe path handling
['cmd.exe', '/c', batch_path]

# INCORRECT: Manual quoting causes double-quote issues  
['cmd.exe', '/c', f'"{batch_path}"']
```

### Batch File Generation Requirements
- **NO pause commands**: All batch files must run non-interactively
- **Encoding**: Shift_JIS for Japanese text support
- **Error handling**: Graceful completion messages instead of pause prompts

### Parallel Output Reading
To prevent subprocess PIPE buffer deadlocks:

```python
# Concurrent stdout/stderr reading prevents hanging
def read_stdout():
    for line in iter(process.stdout.readline, ''):
        if line:
            self._log_queue.put(('stdout', line.strip()))
        if process.poll() is not None:
            break

stdout_thread = threading.Thread(target=read_stdout, daemon=True)
stderr_thread = threading.Thread(target=read_stderr, daemon=True)
```

### Common Execution Issues and Solutions
1. **Hanging on pause**: Remove all `pause` commands from generated batch files
2. **Path with spaces**: Use list format for subprocess, never manual quoting
3. **PIPE buffer overflow**: Always use parallel threads for output reading
4. **GUI freezing**: Execute all batch operations in separate threads
5. **Double execution**: Implement execution state flags and UI locking