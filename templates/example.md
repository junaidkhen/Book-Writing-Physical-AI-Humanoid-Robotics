# Code Example Template

Use this template for all runnable code examples.

## Directory Structure

```
code/module-X/example-XX-descriptive-name/
├── main.py              # Primary Python script (required)
├── utils.py             # Supporting modules (optional)
├── environment.yaml     # Conda environment (required)
├── requirements.txt     # Python dependencies (required)
├── test.sh              # Execution script (required)
├── README.md            # Documentation (required)
└── output/              # Expected outputs (optional)
```

## README.md Template

```markdown
# Module X Example XX: Descriptive Title

## Overview

Brief description of what this example demonstrates (1-2 sentences).

## Learning Objectives

- Understand [concept 1]
- Implement [technique 1]
- Apply [skill 1]

## Prerequisites

- Python 3.8+
- Conda or Miniconda installed
- [Any specific knowledge or prior examples]

## Setup

### Option 1: Using Conda (Recommended)

\`\`\`bash
# Create environment
conda env create -f environment.yaml

# Activate environment
conda activate module-X-example-XX

# Run example
python main.py
\`\`\`

### Option 2: Using pip

\`\`\`bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\\Scripts\\activate

# Install dependencies
pip install -r requirements.txt

# Run example
python main.py
\`\`\`

### Option 3: Quick Test

\`\`\`bash
# Run automated test script
chmod +x test.sh
./test.sh
\`\`\`

## What to Expect

[Description of expected output, runtime, and behavior]

- **Estimated Runtime**: < 1 minute
- **Output**: [Describe what the script will print/generate]
- **GPU Required**: No (or Yes, if applicable)

## Code Explanation

### Main Components

1. **Data Loading**: [Brief explanation]
2. **Processing**: [Brief explanation]
3. **Output Generation**: [Brief explanation]

### Key Functions

- `function_name()`: [What it does]
- `another_function()`: [What it does]

## Customization

You can modify the following parameters in `main.py`:

- `PARAM_1`: [Description and valid values]
- `PARAM_2`: [Description and valid values]

## Troubleshooting

### Common Issues

**Issue**: [Problem description]
**Solution**: [How to fix]

**Issue**: [Problem description]
**Solution**: [How to fix]

## Further Exploration

Try modifying the code to:
- [Suggested modification 1]
- [Suggested modification 2]
- [Suggested modification 3]

## Related Content

- [Module X: Section Y](../../docs/module-X/section-y.md)
- [Example Z: Related Topic](../example-ZZ-name)

## License

This example is provided for educational purposes under the MIT License.
\`\`\`

## main.py Template

\`\`\`python
"""
Module X Example XX: Descriptive Title

This example demonstrates [key concept].
Students will learn how to [learning objective].
"""

import sys
from typing import List, Tuple, Optional

# Add docstrings to all functions
def main_function(param: str) -> bool:
    """
    Brief description of what this function does.

    Args:
        param: Description of parameter

    Returns:
        Description of return value

    Raises:
        ValueError: When parameter is invalid
    """
    try:
        # Implementation with error handling
        result = process_data(param)
        return result
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        raise

def process_data(data: str) -> bool:
    """Process the input data."""
    # Validate input
    if not data:
        raise ValueError("Data cannot be empty")

    # Process
    print(f"Processing: {data}")
    return True

if __name__ == "__main__":
    print("=" * 50)
    print("Module X Example XX: Descriptive Title")
    print("=" * 50)
    print()

    try:
        # Run main logic
        result = main_function("example_input")

        print()
        print("✅ Example completed successfully!")
        print(f"Result: {result}")

    except Exception as e:
        print(f"❌ Example failed: {e}", file=sys.stderr)
        sys.exit(1)
\`\`\`

## environment.yaml Template

\`\`\`yaml
name: module-X-example-XX
channels:
  - conda-forge
  - defaults
dependencies:
  - python=3.10
  - numpy=1.24
  - pip
  - pip:
    - -r requirements.txt
\`\`\`

## requirements.txt Template

\`\`\`
# Core dependencies (pin to specific versions)
numpy==1.24.3
# Add other packages as needed
\`\`\`

## test.sh Template

\`\`\`bash
#!/bin/bash
set -e

ENV_NAME="module-X-example-XX"

echo "🧪 Testing Module X Example XX"
echo "================================"

# Check if conda is installed
if ! command -v conda &> /dev/null; then
    echo "❌ Conda not found. Please install Miniconda or Anaconda."
    exit 1
fi

# Create environment if it doesn't exist
if ! conda env list | grep -q "$ENV_NAME"; then
    echo "📦 Creating conda environment..."
    conda env create -f environment.yaml
fi

# Activate and run
echo "🚀 Running example..."
source "$(conda info --base)/etc/profile.d/conda.sh"
conda activate "$ENV_NAME"
python main.py

echo ""
echo "✅ Test completed successfully"
\`\`\`

## Code Guidelines

### Style Requirements
- Use type hints for all function parameters and return values
- Include docstrings for all functions (Google or NumPy style)
- Add error handling with try/except blocks
- Use descriptive variable names
- Follow PEP 8 style guidelines
- Limit lines to 100 characters

### Functionality Requirements
- Script must run without user interaction
- Must print clear progress messages
- Must handle errors gracefully
- Must return appropriate exit codes (0 for success, 1 for failure)
- Should complete in reasonable time (< 10 minutes)

### Testing Requirements
- test.sh must be executable (chmod +x)
- Must run successfully on Ubuntu 22.04 headless
- Must not require GUI or display
- Must not require internet connection (unless explicitly documented)
- Must not require GPU (unless marked in examples/meta.yaml)
