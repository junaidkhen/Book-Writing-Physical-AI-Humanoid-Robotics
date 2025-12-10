# Code Example Template: [Example Name]

## Directory Structure

```
code/module-[n]/example-[nn]-[name]/
├── main.py              # Primary Python script
├── utils.py             # Supporting utilities (optional)
├── config.py            # Configuration (optional)
├── environment.yaml     # Conda environment specification
├── requirements.txt     # Python package dependencies
├── test.sh              # Execution script
├── README.md            # Example documentation
├── data/                # Sample data files (optional)
└── output/              # Expected outputs (optional)
```

---

## README.md Template

```markdown
# Example [NN]: [Example Name]

**Module**: [N] - [Module Name]
**Difficulty**: [Beginner/Intermediate/Advanced]
**Estimated Runtime**: [e.g., < 1 minute, 5-10 minutes]
**GPU Required**: [Yes/No]

## Overview

[2-3 sentence description of what this example demonstrates and what students will learn]

## Learning Objectives

After completing this example, you will be able to:

- [Objective 1]
- [Objective 2]
- [Objective 3]

## Prerequisites

- Python 3.8 or higher
- Conda or Miniconda installed
- [Any other system requirements]
- [GPU with CUDA support (if applicable)]

## Installation

### Step 1: Create Conda Environment

```bash
conda env create -f environment.yaml
```

### Step 2: Activate Environment

```bash
conda activate module-[n]-example-[nn]
```

### Step 3: Verify Installation

```bash
python -c "import [key_package]; print([key_package].__version__)"
```

## Usage

### Quick Start

Run the example using the provided test script:

```bash
bash test.sh
```

### Manual Execution

```bash
conda activate module-[n]-example-[nn]
python main.py [--optional-arg value]
```

### Expected Output

[Description of what the script outputs]

```
[Sample output]
```

## Code Structure

### main.py

The main script performs the following steps:

1. **Data Loading**: [Description]
2. **Preprocessing**: [Description]
3. **Algorithm Execution**: [Description]
4. **Results Visualization**: [Description]

### Key Functions

- `function_name(args)`: [Purpose and brief explanation]
- `another_function(args)`: [Purpose and brief explanation]

## Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `--input` | str | "data/sample.jpg" | Path to input data |
| `--output` | str | "output/" | Directory for results |
| `--threshold` | float | 0.5 | Detection threshold |

## Troubleshooting

### Common Issues

**Issue**: [Error message or problem]
**Solution**: [How to fix it]

**Issue**: [Error message or problem]
**Solution**: [How to fix it]

### GPU Issues

If you encounter GPU-related errors:

1. Verify CUDA installation: `nvidia-smi`
2. Check PyTorch GPU support: `python -c "import torch; print(torch.cuda.is_available())"`
3. Ensure correct CUDA version in environment.yaml

## Further Exploration

- Modify [parameter X] to see [effect]
- Try running with different input data from [source]
- Extend the example by [suggestion]

## Related Examples

- [Example YY: Name] - [How it relates]
- [Example ZZ: Name] - [How it relates]

## References

- [Paper/Resource citation]
- [Documentation link]

## License

[License information if different from project license]
```

---

## main.py Template

```python
#!/usr/bin/env python3
"""
Module [N] Example [NN]: [Example Name]

[Detailed description of what this example demonstrates, including:
- The Physical AI concept being illustrated
- The algorithm or technique being implemented
- Expected inputs and outputs
- Learning objectives]

Author: [Name/Organization]
License: [License]
"""

import argparse
import sys
from pathlib import Path
from typing import List, Tuple, Optional

import numpy as np
# [Other imports as needed]


def parse_arguments() -> argparse.Namespace:
    """
    Parse command-line arguments.

    Returns:
        Parsed arguments namespace
    """
    parser = argparse.ArgumentParser(
        description="[Example description]"
    )
    parser.add_argument(
        "--input",
        type=str,
        default="data/sample.jpg",
        help="Path to input data file"
    )
    parser.add_argument(
        "--output",
        type=str,
        default="output/",
        help="Directory for output files"
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=0.5,
        help="Detection threshold (0.0-1.0)"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging"
    )

    return parser.parse_args()


def load_data(file_path: str) -> np.ndarray:
    """
    Load input data from file.

    Args:
        file_path: Path to input data file

    Returns:
        Loaded data as numpy array

    Raises:
        FileNotFoundError: If input file doesn't exist
        ValueError: If file format is invalid
    """
    try:
        # Check if file exists
        if not Path(file_path).exists():
            raise FileNotFoundError(f"Input file not found: {file_path}")

        # Load data (example implementation)
        data = np.load(file_path)

        return data

    except Exception as e:
        print(f"❌ Error loading data: {e}", file=sys.stderr)
        raise


def preprocess_data(data: np.ndarray, normalize: bool = True) -> np.ndarray:
    """
    Preprocess input data for algorithm.

    Args:
        data: Raw input data
        normalize: Whether to normalize data to [0, 1] range

    Returns:
        Preprocessed data

    Raises:
        ValueError: If data dimensions are invalid
    """
    try:
        # Validate input dimensions
        if data.ndim < 2:
            raise ValueError(f"Expected 2D or higher data, got {data.ndim}D")

        # Preprocessing steps
        processed_data = data.copy()

        if normalize:
            processed_data = (processed_data - processed_data.min()) / (
                processed_data.max() - processed_data.min()
            )

        return processed_data

    except Exception as e:
        print(f"❌ Error in preprocessing: {e}", file=sys.stderr)
        raise


def run_algorithm(
    data: np.ndarray,
    threshold: float = 0.5
) -> Tuple[np.ndarray, dict]:
    """
    Execute the main algorithm.

    [Detailed explanation of the algorithm being implemented]

    Args:
        data: Preprocessed input data
        threshold: Detection/classification threshold

    Returns:
        Tuple of (results array, metadata dictionary)

    Raises:
        ValueError: If parameters are out of valid range
    """
    try:
        # Validate parameters
        if not 0.0 <= threshold <= 1.0:
            raise ValueError(f"Threshold must be in [0, 1], got {threshold}")

        # Algorithm implementation
        results = np.zeros_like(data)
        metadata = {
            "threshold": threshold,
            "num_detections": 0,
            "processing_time": 0.0,
        }

        # [Core algorithm logic here]

        return results, metadata

    except Exception as e:
        print(f"❌ Error in algorithm execution: {e}", file=sys.stderr)
        raise


def save_results(
    results: np.ndarray,
    metadata: dict,
    output_dir: str
) -> None:
    """
    Save results to output directory.

    Args:
        results: Algorithm output
        metadata: Result metadata
        output_dir: Directory path for outputs

    Raises:
        IOError: If unable to write to output directory
    """
    try:
        # Create output directory if it doesn't exist
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        # Save results
        np.save(output_path / "results.npy", results)

        # Save metadata
        import json
        with open(output_path / "metadata.json", "w") as f:
            json.dump(metadata, f, indent=2)

        print(f"✅ Results saved to {output_dir}")

    except Exception as e:
        print(f"❌ Error saving results: {e}", file=sys.stderr)
        raise


def visualize_results(
    data: np.ndarray,
    results: np.ndarray,
    output_path: str
) -> None:
    """
    Create visualization of results (optional).

    Args:
        data: Original input data
        results: Algorithm output
        output_path: Path for output visualization

    Raises:
        IOError: If unable to save visualization
    """
    try:
        import matplotlib.pyplot as plt

        # Create visualization
        fig, axes = plt.subplots(1, 2, figsize=(12, 5))

        axes[0].imshow(data, cmap="gray")
        axes[0].set_title("Input Data")
        axes[0].axis("off")

        axes[1].imshow(results, cmap="viridis")
        axes[1].set_title("Algorithm Results")
        axes[1].axis("off")

        plt.tight_layout()
        plt.savefig(output_path)
        plt.close()

        print(f"✅ Visualization saved to {output_path}")

    except ImportError:
        print("⚠️ Matplotlib not available, skipping visualization")
    except Exception as e:
        print(f"❌ Error creating visualization: {e}", file=sys.stderr)


def main() -> int:
    """
    Main execution function.

    Returns:
        Exit code (0 for success, 1 for failure)
    """
    try:
        # Parse arguments
        args = parse_arguments()

        if args.verbose:
            print("🚀 Starting example execution...")
            print(f"Input: {args.input}")
            print(f"Output: {args.output}")
            print(f"Threshold: {args.threshold}")

        # Load and preprocess data
        print("📥 Loading data...")
        data = load_data(args.input)

        print("🔧 Preprocessing data...")
        processed_data = preprocess_data(data)

        # Run algorithm
        print("⚙️ Running algorithm...")
        results, metadata = run_algorithm(processed_data, args.threshold)

        # Save results
        print("💾 Saving results...")
        save_results(results, metadata, args.output)

        # Visualize (optional)
        visualize_results(
            data,
            results,
            f"{args.output}/visualization.png"
        )

        # Print summary
        print("\n" + "=" * 50)
        print("✅ Example completed successfully!")
        print("=" * 50)
        print(f"Detections: {metadata['num_detections']}")
        print(f"Processing time: {metadata['processing_time']:.3f}s")
        print(f"Output directory: {args.output}")

        return 0

    except KeyboardInterrupt:
        print("\n⚠️ Execution interrupted by user")
        return 130
    except Exception as e:
        print(f"\n❌ Fatal error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
```

---

## environment.yaml Template

```yaml
name: module-[n]-example-[nn]
channels:
  - conda-forge
  - defaults
dependencies:
  - python=3.10
  - numpy=1.24
  - matplotlib=3.8
  - pip
  - pip:
    - -r requirements.txt
```

---

## requirements.txt Template

```
# Core dependencies
numpy==1.24.3
matplotlib==3.8.2

# Domain-specific packages
opencv-python==4.8.1.78
scikit-learn==1.3.2

# Utility packages
tqdm==4.66.1
pyyaml==6.0.1
```

---

## test.sh Template

```bash
#!/bin/bash
# Test script for Module [N] Example [NN]
set -e

ENV_NAME="module-[n]-example-[nn]"
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

echo "=========================================="
echo "Testing: Module [N] Example [NN]"
echo "=========================================="

# Check if conda is installed
if ! command -v conda &> /dev/null; then
    echo "❌ Conda not found. Please install Miniconda or Anaconda."
    echo "   Download from: https://docs.conda.io/en/latest/miniconda.html"
    exit 1
fi

# Create environment if it doesn't exist
if ! conda env list | grep -q "^$ENV_NAME "; then
    echo "📦 Creating conda environment: $ENV_NAME"
    conda env create -f "$SCRIPT_DIR/environment.yaml"
else
    echo "✅ Environment $ENV_NAME already exists"
fi

# Activate environment
echo "🔧 Activating environment..."
source "$(conda info --base)/etc/profile.d/conda.sh"
conda activate "$ENV_NAME"

# Verify Python version
PYTHON_VERSION=$(python --version)
echo "🐍 Using $PYTHON_VERSION"

# Verify key dependencies
echo "📦 Verifying dependencies..."
python -c "import numpy; print(f'  numpy: {numpy.__version__}')"
# [Add other key dependency checks]

# Run the example
echo ""
echo "🚀 Running example..."
echo "=========================================="
cd "$SCRIPT_DIR"
python main.py --verbose

# Check exit code
if [ $? -eq 0 ]; then
    echo ""
    echo "=========================================="
    echo "✅ Example completed successfully!"
    echo "=========================================="
    exit 0
else
    echo ""
    echo "=========================================="
    echo "❌ Example failed"
    echo "=========================================="
    exit 1
fi
```

---

## Checklist for New Examples

- [ ] README.md with clear setup and usage instructions
- [ ] main.py with full docstrings and type hints
- [ ] environment.yaml with pinned dependency versions
- [ ] requirements.txt with all Python packages
- [ ] test.sh script that runs successfully on Ubuntu 22.04
- [ ] All code comments in English
- [ ] Type hints for all function parameters and returns
- [ ] Error handling with try/except blocks
- [ ] Meaningful error messages
- [ ] Validation of input parameters
- [ ] Clear output messages for user feedback
- [ ] Entry in examples/meta.yaml with metadata
- [ ] Sample input data (if applicable)
- [ ] Expected output examples (if applicable)
- [ ] Referenced in relevant module documentation

---

**Template Version**: 1.0
**Last Updated**: 2025-12-10
