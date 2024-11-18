import json
import subprocess
from pathlib import Path
import shutil
from tqdm import tqdm
from typing import Optional, Dict

# Constants for configuration
IMAGE_QUALITY = 90
HEIC_COMPRESSION = 10

def compress_to_avif(png_path: Path, avif_path: Path) -> bool:
    """
    Compress a PNG image to AVIF format using ImageMagick.
    
    Args:
        png_path (Path): The path to the input PNG file.
        avif_path (Path): The path where the compressed AVIF file will be saved.
    
    Returns:
        bool: True if compression was successful, False otherwise.
    """
    try:
        subprocess.run(
            [
                "magick",  # ImageMagick command
                str(png_path),
                "-quality", str(IMAGE_QUALITY),
                "-define", f"heic:compression={HEIC_COMPRESSION}",
                str(avif_path),
            ],
            check=True
        )
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error compressing {png_path} to AVIF: {e}")
        return False


def move_file_with_structure(file_path: Path, root_folder: Path, destination_folder: Path) -> None:
    """
    Move a file to a destination folder, preserving its relative directory structure.
    
    Args:
        file_path (Path): The original file path.
        root_folder (Path): The root folder containing all files.
        destination_folder (Path): The destination folder for the file.
    """
    relative_path = file_path.relative_to(root_folder)
    destination_path = destination_folder / relative_path
    destination_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        shutil.move(str(file_path), str(destination_path))
    except Exception as e:
        print(f"Error moving {file_path} to {destination_folder}: {e}")


def extract_metadata(image_path: Path) -> Dict[str, str]:
    """
    Extract metadata from an image using ExifTool.
    
    Args:
        image_path (Path): The image file path.
    
    Returns:
        Dict[str, str]: Metadata as key-value pairs, or an empty dictionary on failure.
    """
    try:
        result = subprocess.run(
            ["exiftool", str(image_path)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        metadata = {}
        for line in result.stdout.splitlines():
            if ":" in line:
                key, value = line.split(":", 1)
                metadata[key.strip()] = value.strip()
        return metadata
    except Exception as e:
        print(f"Error extracting metadata for {image_path}: {e}")
        return {}


def save_metadata(file_path: Path, content: str, extension: str) -> None:
    """
    Save metadata content to a file (either JSON or plain text).
    
    Args:
        file_path (Path): The original file path.
        content (str): The metadata content to save.
        extension (str): The file extension ('.json' or '.txt').
    """
    save_path = file_path.with_suffix(extension)
    save_path = ensure_unique_filename(save_path)
    mode, data = ("w", content)

    if extension == ".json":
        try:
            data = json.dumps(json.loads(content), ensure_ascii=False, indent=4)
        except json.JSONDecodeError:
            extension = "txt"

    with open(save_path, mode, encoding="utf-8") as file:
        file.write(data)

    print(f"Saved metadata to {save_path}")


def ensure_unique_filename(file_path: Path) -> Path:
    """
    Generate a unique filename by appending a counter if the file already exists.
    
    Args:
        file_path (Path): The desired file path.
    
    Returns:
        Path: A unique file path.
    """
    counter = 1
    unique_path = file_path
    while unique_path.exists():
        unique_path = file_path.with_stem(f"{file_path.stem}_{counter}")
        counter += 1
    return unique_path


def process_png_file(image_path: Path, root_folder: Path, review_folder: Path) -> None:
    """
    Process a PNG file by extracting metadata, saving relevant fields, compressing to AVIF, 
    and moving the original to a review folder.
    
    Args:
        image_path (Path): The PNG file path.
        root_folder (Path): Root folder containing all images.
        review_folder (Path): Destination folder for the original PNG file.
    """
    metadata = extract_metadata(image_path)

    # Save metadata if available
    for field in ("Prompt", "Parameters"):
        if field in metadata:
            save_metadata(image_path, metadata[field], ".json" if field == "Prompt" else ".txt")
            break
    else:
        print(f"No 'Prompt' or 'Parameters' found for {image_path}")

    # Compress PNG to AVIF format
    avif_path = image_path.with_suffix(".avif")
    if compress_to_avif(image_path, avif_path):
        move_file_with_structure(image_path, root_folder, review_folder)


def process_images(folder_path: Path, review_folder: Path) -> None:
    """
    Recursively process all PNG files in a folder.
    
    Args:
        folder_path (Path): Path to the folder containing PNG files.
        review_folder (Path): Path to the folder for processed files.
    """
    png_files = list(folder_path.rglob("*.png"))
    with tqdm(total=len(png_files), desc="Processing PNG files") as progress_bar:
        for image_path in png_files:
            process_png_file(image_path, folder_path, review_folder)
            progress_bar.update(1)


def main() -> None:
    """
    Main script entry point. Prompts the user for input paths and initiates processing.
    """
    images_folder = Path(input("Path to images folder: ").strip()).resolve()
    if not images_folder.is_dir():
        print("Invalid images folder path.")
        return

    review_folder = input("Path to review folder (leave blank for default): ").strip()
    review_folder = Path(review_folder).resolve() if review_folder else images_folder / "Review"
    review_folder.mkdir(parents=True, exist_ok=True)

    print(f"Review folder set to: {review_folder}")
    process_images(images_folder, review_folder)
    print("Processing complete.")


if __name__ == "__main__":
    main()
