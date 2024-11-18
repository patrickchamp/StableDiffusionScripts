# PNG to AVIF Image Conversion Script

This script was created to help save disk space for an archive of AI-generated art images by converting PNG files to the AVIF format while retaining critical metadata and workflows.

## Features

- **PNG to AVIF Conversion**: Converts PNG images to the AVIF format for efficient storage.
  - **Why AVIF?**
    - Excellent compression ratio.
    - High-quality image retention at 90% quality.
    - Widely supported, including in Microsoft Photos.
  - The 90% quality setting ensures the images remain suitable for future conversions and editing without noticeable quality loss.

- **Metadata Preservation**:
  - Extracts parameters and workflows embedded in PNG images from Automatic1111 and ComfyUI.
  - Saves this metadata as `.json` or `.txt` files with the same filename for easy lookup and reloading.
 
- **Review Folder**:
  - Creates a `Review` folder to store original PNG files temporarily for user review.
  - Maintains the original directory structure for easy restoration if needed.

## Prerequisites

1. **Python**: Ensure Python 3.7+ is installed.
2. **ImageMagick**: For PNG-to-AVIF conversion.
   - Install ImageMagick locally and add its path to your system's environment variables.
   - [Download ImageMagick](https://imagemagick.org/script/download.php)
3. **ExifTool**: For extracting metadata.
   - Install ExifTool locally and add its path to your system's environment variables.
   - [Download ExifTool](https://exiftool.org/)
4. **Required Python Libraries**:
   - Install dependencies using:
     ```bash
     pip install tqdm
     ```

## Warning
- It only saves that specific metadata, not the full exif info. It extracts A1111 parameters from the Exif "Parameters" field and ComfyUI workflows from the Exif "Prompt" field. If neither are present it does not create a json or txt file.


## Installation

1. Clone or download this repository:
   ```bash
   git clone <repository_url>
   cd <repository_name>
   ```
2. Install the necessary Python library:
   ```bash
   pip install tqdm
   ```

## Usage

1. Run the script:
   ```bash
   python main_script.py
   ```
2. Follow the prompts:
   - Provide the path to your image folder.
   - Optionally specify a review folder (defaults to a `Review` folder in the same directory as the images).
3. The script will:
   - Process all PNG files recursively in the specified folder.
   - Convert each PNG to AVIF.
   - Extract and save embedded metadata as `.json` or `.txt`.
   - Move the original PNG files to the `Review` folder for verification.

## Example

Given a folder structure like this:

```
images/
├── art1.png
├── art2.png
└── subfolder/
    └── art3.png
```

After running the script, the output will look like this:

```
images/
├── art1.avif
├── art1.json
├── art2.avif
├── art2.json
└── subfolder/
    ├── art3.avif
    ├── art3.json
Review/
├── art1.png
├── art2.png
└── subfolder/
    └── art3.png
```

## Benefits

- **Disk Space Savings**: AVIF offers a better compression ratio compared to PNG, significantly reducing storage requirements.
- **Future-Proofing**: By saving metadata as `.json` files, you can recreate workflows or parameters in tools like Automatic1111 or ComfyUI, even if AVIF files are unsupported.
- **Flexible Review Process**: The review folder allows you to double-check changes before deleting the original PNG files.

## Known Limitations

- **Requires Proper Environment Setup**: Ensure that both ImageMagick and ExifTool are installed and configured as environment variables.
- **Metadata Extraction**: If the embedded metadata does not conform to expected formats, it may not be properly extracted.

## Contributing

Feel free to submit issues or pull requests for feature enhancements or bug fixes.

## License

This project is licensed under the [MIT License](LICENSE).