#!/bin/bash
set -e

# Run the release.py script to finalize the changelog and tag the version
echo "🚀 Running release script..."
python3 scripts/release.py

# Upload the package to PyPI using Twine
echo "📤 Uploading to PyPI..."
twine upload dist/*

echo "✅ Release complete!"
