#!/bin/bash

# Path to ebook-convert command
EBOOK_CONVERT="/Applications/calibre.app/Contents/MacOS/ebook-convert"

# Create output directory if it doesn't exist
mkdir -p fb2_converted

# Counter for progress
total_files=$(ls -1 *.epub 2>/dev/null | wc -l)
current=0

echo "Starting conversion of $total_files EPUB files to FB2 format..."
echo "============================================"

# Convert each EPUB file to FB2
for epub_file in *.epub; do
    if [ -f "$epub_file" ]; then
        current=$((current + 1))
        # Get the filename without extension
        base_name="${epub_file%.epub}"
        fb2_file="fb2_converted/${base_name}.fb2"

        echo "[$current/$total_files] Converting: $epub_file"

        # Run the conversion
        "$EBOOK_CONVERT" "$epub_file" "$fb2_file" 2>&1 | grep -E "^(Output saved|Error|FB2 output written)"

        if [ $? -eq 0 ] && [ -f "$fb2_file" ]; then
            echo "  ✓ Successfully converted to: $fb2_file"
        else
            echo "  ✗ Failed to convert: $epub_file"
        fi
        echo ""
    fi
done

echo "============================================"
echo "Conversion complete!"
echo "Converted files are in the 'fb2_converted' directory"

# Show summary
successful=$(ls -1 fb2_converted/*.fb2 2>/dev/null | wc -l)
echo "Successfully converted: $successful out of $total_files files"