import json
import subprocess
from pathlib import Path
import shutil
from tqdm import tqdm


def compress_to_avif(png_path, avif_path):
    """
    Compress a PNG image to AVIF format using ImageMagick.
    """
    try:
        subprocess.run(
            [
                "magick",
                str(png_path),
                "-quality", "90",
                "-define", "heic:compression=10",
                str(avif_path)
            ],
            check=True
        )
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error compressing {png_path} to AVIF: {e}")
        return False


def move_to_review_folder(file_path, root_folder, review_folder):
    """
    Move a file to the review folder, preserving relative directory structure.
    """
    relative_path = file_path.relative_to(root_folder)
    destination_path = review_folder / relative_path

    # Ensure destination folder exists
    destination_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        shutil.move(str(file_path), str(destination_path))
    except Exception as e:
        print(f"Error moving {file_path} to review folder: {e}")


def extract_metadata_with_exiftool(image_path):
    """
    Extract metadata using ExifTool.
    """
    try:
        result = subprocess.run(
            ["exiftool", str(image_path)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        exif_output = result.stdout
        metadata = {}

        for line in exif_output.splitlines():
            if ":" in line:
                key, value = line.split(":", 1)
                metadata[key.strip()] = value.strip()

        return metadata
    except Exception as e:
        print(f"Error extracting metadata with ExifTool: {e}")
        return {}


def get_unique_filename(file_path):
    """
    Generate a unique filename if the file already exists.
    """
    counter = 1
    new_file_path = file_path
    while new_file_path.exists():
        new_file_path = file_path.with_stem(f"{file_path.stem}_{counter}")
        counter += 1
    return new_file_path


def process_png_file(image_path, root_folder, review_folder):
    """
    Process a PNG file by extracting metadata, saving JSON/TXT files, compressing to AVIF,
    and moving the original file to the review folder.
    """
    metadata = extract_metadata_with_exiftool(image_path)

    # Check for 'Prompt' field in metadata
    if "Prompt" in metadata:
        prompt_content = metadata["Prompt"]
        try:
            # Attempt to parse 'Prompt' content as JSON
            prompt_data = json.loads(prompt_content)
            json_file_path = image_path.with_suffix('.json')

            # Generate a unique filename if needed
            json_file_path = get_unique_filename(json_file_path)

            with open(json_file_path, "w", encoding="utf-8") as json_file:
                json.dump(prompt_data, json_file, ensure_ascii=False, indent=4)
            print(f"Prompt JSON saved: {json_file_path}")
        except json.JSONDecodeError:
            # If not valid JSON, save as raw text
            txt_file_path = image_path.with_suffix('.txt')

            # Generate a unique filename if needed
            txt_file_path = get_unique_filename(txt_file_path)

            with open(txt_file_path, "w", encoding="utf-8") as txt_file:
                txt_file.write(prompt_content)
            print(f"Prompt saved as TXT: {txt_file_path}")
    elif "Parameters" in metadata:
        # Extract 'Parameters' field and save as a TXT file
        txt_file_path = image_path.with_suffix('.txt')

        # Generate a unique filename if needed
        txt_file_path = get_unique_filename(txt_file_path)

        with open(txt_file_path, "w", encoding="utf-8") as txt_file:
            txt_file.write(metadata["Parameters"])
        print(f"Parameters saved as TXT: {txt_file_path}")
    else:
        print(f"No 'Prompt' or 'Parameters' found for: {image_path}")

    # Compress the PNG file to AVIF format
    avif_file_path = image_path.with_suffix('.avif')
    if compress_to_avif(image_path, avif_file_path):
        # Move original file to the review folder
        move_to_review_folder(image_path, root_folder, review_folder)


def process_images_recursively(folder_path, review_folder):
    """
    Recursively process all PNG files in a folder.
    """
    png_files = list(folder_path.rglob('*.png'))  # Find all PNG files
    total_files = len(png_files)

    # Display a progress bar for file processing
    with tqdm(total=total_files, desc="Processing PNG files") as progress_bar:
        for image_path in png_files:
            process_png_file(image_path, folder_path, review_folder)
            progress_bar.update(1)  # Update progress bar


def main():
    """
    Main entry point for the script. Prompts the user for input paths and processes images.
    """
    # Ask the user for the images folder path
    images_folder = Path(input("Path to images folder: ").strip()).resolve()

    # Validate the images folder path
    if not images_folder.is_dir():
        print("Invalid images folder path.")
        return

    # Prompt the user for the review folder path, defaulting to 'Review' in the images folder
    review_folder_input = input(
        "Path to review folder (leave blank to use the default 'Review' folder in the images folder): "
    ).strip()

    # Resolve the review folder path based on user input
    review_folder = Path(review_folder_input).resolve() if review_folder_input else images_folder / "Review"

    print(f"Review folder set to: {review_folder}")

    # Process all PNG files recursively
    process_images_recursively(images_folder, review_folder)

    input("Press Enter to exit...")


if __name__ == "__main__":
    main()
