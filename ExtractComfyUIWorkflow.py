import json                      # For handling JSON data (reading and writing)
import subprocess                # For running external commands (like ImageMagick and ExifTool)
from pathlib import Path         # For object-oriented filesystem paths
import shutil                    # For high-level file operations (copying and moving files)
from concurrent.futures import ThreadPoolExecutor, as_completed  # For concurrent execution of functions
from tqdm import tqdm            # For displaying progress bars during iterations
from typing import Dict, Any     # For type hinting dictionaries with any type of values

# Constants for image conversion settings
IMAGE_QUALITY = 90       # Quality setting for image conversion (0-100); higher means better quality
AVIF_SPEED = 0           # Compression speed for AVIF format (0-10); lower is slower but better compression

def check_dependencies() -> None:
    """
    Check that required external tools are installed and available in the system PATH.

    Required tools:
        - ImageMagick ('magick' command)
        - ExifTool ('exiftool' command)

    Raises:
        EnvironmentError: If any of the required tools are not found in the system PATH.
    """
    # List of required external tools
    required_tools = ["magick", "exiftool"]
    # Iterate over each tool to check its availability
    for tool in required_tools:
        # shutil.which() returns the path to the executable or None if not found
        if shutil.which(tool) is None:
            # Raise an error if the tool is not found
            raise EnvironmentError(f"{tool} is not installed or not in the system PATH.")

def compress_to_avif(png_path: Path, avif_path: Path) -> bool:
    """
    Convert a PNG image to AVIF format using ImageMagick.

    Args:
        png_path (Path): Path to the input PNG file.
        avif_path (Path): Path where the output AVIF file will be saved.

    Returns:
        bool: True if the conversion was successful, False otherwise.
    """
    try:
        # Run the ImageMagick 'magick' command to convert the image
        subprocess.run(
            [
                "magick",                          # Command to run
                str(png_path),                     # Input PNG file
                "-quality", str(IMAGE_QUALITY),    # Set the image quality
                "-define", f"avif:speed={AVIF_SPEED}",  # Set the AVIF compression speed
                str(avif_path),                    # Output AVIF file
            ],
            check=True,                            # Raise an exception if the command fails
            stdout=subprocess.PIPE,                # Capture standard output (not used here)
            stderr=subprocess.PIPE,                # Capture standard error (for error messages)
        )
        # If the command succeeds, return True
        return True
    except subprocess.CalledProcessError as e:
        # If the command fails, print an error message with details
        print(f"Error compressing {png_path} to AVIF: {e}")
        # Return False to indicate failure
        return False

def extract_metadata(image_path: Path) -> Dict[str, Any]:
    """
    Extract metadata from an image using ExifTool.

    Args:
        image_path (Path): Path to the image file.

    Returns:
        Dict[str, Any]: A dictionary containing the image metadata.

    ---

    Example of Exiftool output for a PNG that contains a comfyui workflow:

    [Example Start]
    C:\\Photos>exiftool ComfyUI_00003_.png
    ExifTool Version Number         : 13.03
    File Name                       : ComfyUI_00003_.png
    Directory                       : .
    File Size                       : 1196 kB
    File Modification Date/Time     : 2024:10:21 01:53:16-04:00
    File Access Date/Time           : 2024:11:18 19:22:49-05:00
    File Creation Date/Time         : 2024:11:18 00:24:09-05:00
    File Permissions                : -rw-rw-rw-
    File Type                       : PNG
    File Type Extension             : png
    MIME Type                       : image/png
    Image Width                     : 768
    Image Height                    : 1344
    Bit Depth                       : 8
    Color Type                      : RGB
    Compression                     : Deflate/Inflate
    Filter                          : Adaptive
    Interlace                       : Noninterlaced
    Prompt                          : {"6": {"inputs": {"text": "photo of a man.", "clip": ["50", 1]}, "class_type": "CLIPTextEncode"}, "8": {"inputs": {"samples": ["13", 0], "vae": ["10", 0]}, "class_type": "VAEDecode"}, "9": {"inputs": {"filename_prefix": "ComfyUI", "images": ["8", 0]}, "class_type": "SaveImage"}, "10": {"inputs": {"vae_name": "FLUX1\\ae.safetensors"}, "class_type": "VAELoader"}, "13": {"inputs": {"noise": ["25", 0], "guider": ["22", 0], "sampler": ["16", 0], "sigmas": ["17", 0], "latent_image": ["27", 0]}, "class_type": "SamplerCustomAdvanced"}, "16": {"inputs": {"sampler_name": "euler"}, "class_type": "KSamplerSelect"}, "17": {"inputs": {"scheduler": "normal", "steps": 8, "denoise": 1.0, "model": ["50", 0]}, "class_type": "BasicScheduler"}, "22": {"inputs": {"model": ["50", 0], "conditioning": ["26", 0]}, "class_type": "BasicGuider"}, "25": {"inputs": {"noise_seed": 976408652294932}, "class_type": "RandomNoise"}, "26": {"inputs": {"guidance": 3.5, "conditioning": ["6", 0]}, "class_type": "FluxGuidance"}, "27": {"inputs": {"width": 768, "height": 1344, "batch_size": 1}, "class_type": "EmptySD3LatentImage"}, "46": {"inputs": {"unet_name": "FLUX1\\flux1-dev.safetensors", "weight_dtype": "fp8_e4m3fn_fast"}, "class_type": "UNETLoader"}, "47": {"inputs": {"clip_name1": "ViT-L-14-TEXT-detail-improved-hiT-GmP-TE-only-HF.safetensors", "clip_name2": "t5\\google_t5-v1_1-xxl_encoderonly-fp16.safetensors", "type": "flux"}, "class_type": "DualCLIPLoader"}, "50": {"inputs": {"PowerLoraLoaderHeaderWidget": {"type": "PowerLoraLoaderHeaderWidget"}, "lora_1": {"on": true, "lora": "Turbo\\flux_turbo.safetensors", "strength": 1}, "\u2795 Add Lora": "", "model": ["46", 0], "clip": ["47", 0]}, "class_type": "Power Lora Loader (rgthree)"}}
    Workflow                        : {"last_node_id": 51, "last_link_id": 142, "nodes": [{"id": 9, "type": "SaveImage", "pos": {"0": 1112, "1": 117}, "size": {"0": 736.6519165039062, "1": 907.8062744140625}, "flags": {}, "order": 18, "mode": 0, "inputs": [{"name": "images", "type": "IMAGE", "link": 9}], "outputs": [], "properties": {"Node name for S&R": "SaveImage"}, "widgets_values": ["ComfyUI"]}, {"id": 26, "type": "FluxGuidance", "pos": {"0": 390, "1": 138}, "size": {"0": 317.4000244140625, "1": 58}, "flags": {}, "order": 14, "mode": 0, "inputs": [{"name": "conditioning", "type": "CONDITIONING", "link": 41}], "outputs": [{"name": "CONDITIONING", "type": "CONDITIONING", "links": [42], "slot_index": 0, "shape": 3}], "properties": {"Node name for S&R": "FluxGuidance"}, "widgets_values": [3.5], "color": "#233", "bgcolor": "#355"}, {"id": 35, "type": "PrimitiveNode", "pos": {"0": 620, "1": 484}, "size": {"0": 210, "1": 82}, "flags": {}, "order": 0, "mode": 0, "inputs": [], "outputs": [{"name": "INT", "type": "INT", "links": [113, 114], "slot_index": 0, "widget": {"name": "height"}}], "title": "height", "properties": {"Run widget replace on values": false}, "widgets_values": [1344, "fixed"], "color": "#323", "bgcolor": "#535"}, {"id": 34, "type": "PrimitiveNode", "pos": {"0": 394, "1": 477}, "size": {"0": 210.0775909423828, "1": 94.05860900878906}, "flags": {}, "order": 1, "mode": 0, "inputs": [], "outputs": [{"name": "INT", "type": "INT", "links": [112, 115], "slot_index": 0, "widget": {"name": "width"}}], "title": "width", "properties": {"Run widget replace on values": false}, "widgets_values": [768, "fixed"], "color": "#323", "bgcolor": "#535"}, {"id": 22, "type": "BasicGuider", "pos": {"0": 729, "1": 142}, "size": {"0": 222.3482666015625, "1": 46}, "flags": {}, "order": 15, "mode": 0, "inputs": [{"name": "model", "type": "MODEL", "link": 54, "slot_index": 0}, {"name": "conditioning", "type": "CONDITIONING", "link": 42, "slot_index": 1}], "outputs": [{"name": "GUIDER", "type": "GUIDER", "links": [30], "slot_index": 0, "shape": 3}], "properties": {"Node name for S&R": "BasicGuider"}, "widgets_values": []}, {"id": 27, "type": "EmptySD3LatentImage", "pos": {"0": 399, "1": 616}, "size": {"0": 424.8544006347656, "1": 99.15755462646484}, "flags": {}, "order": 9, "mode": 0, "inputs": [{"name": "width", "type": "INT", "link": 112, "widget": {"name": "width"}}, {"name": "height", "type": "INT", "link": 113, "widget": {"name": "height"}}], "outputs": [{"name": "LATENT", "type": "LATENT", "links": [116], "slot_index": 0, "shape": 3}], "properties": {"Node name for S&R": "EmptySD3LatentImage"}, "widgets_values": [768, 1344, 1]}, {"id": 25, "type": "RandomNoise", "pos": {"0": 404, "1": 761}, "size": {"0": 412.7810363769531, "1": 82}, "flags": {}, "order": 2, "mode": 0, "inputs": [], "outputs": [{"name": "NOISE", "type": "NOISE", "links": [37], "shape": 3}], "properties": {"Node name for S&R": "RandomNoise"}, "widgets_values": [976408652294932, "randomize"], "color": "#2a363b", "bgcolor": "#3f5159"}, {"id": 17, "type": "BasicScheduler", "pos": {"0": 413, "1": 1007}, "size": {"0": 398.4141845703125, "1": 106}, "flags": {}, "order": 11, "mode": 0, "inputs": [{"name": "model", "type": "MODEL", "link": 141, "slot_index": 0}], "outputs": [{"name": "SIGMAS", "type": "SIGMAS", "links": [20], "shape": 3}], "properties": {"Node name for S&R": "BasicScheduler"}, "widgets_values": ["normal", 8, 1]}, {"id": 16, "type": "KSamplerSelect", "pos": {"0": 408, "1": 896}, "size": {"0": 394.4875793457031, "1": 58.668025970458984}, "flags": {}, "order": 3, "mode": 0, "inputs": [], "outputs": [{"name": "SAMPLER", "type": "SAMPLER", "links": [19], "shape": 3}], "properties": {"Node name for S&R": "KSamplerSelect"}, "widgets_values": ["euler"]}, {"id": 30, "type": "ModelSamplingFlux", "pos": {"0": 425, "1": 1158}, "size": {"0": 382.2674560546875, "1": 124.22319030761719}, "flags": {}, "order": 12, "mode": 4, "inputs": [{"name": "model", "type": "MODEL", "link": 142, "slot_index": 0}, {"name": "width", "type": "INT", "link": 115, "slot_index": 1, "widget": {"name": "width"}}, {"name": "height", "type": "INT", "link": 114, "slot_index": 2, "widget": {"name": "height"}}], "outputs": [{"name": "MODEL", "type": "MODEL", "links": [54], "slot_index": 0, "shape": 3}], "properties": {"Node name for S&R": "ModelSamplingFlux"}, "widgets_values": [1.15, 0.5, 768, 1344]}, {"id": 37, "type": "Note", "pos": {"0": 826, "1": 1160}, "size": {"0": 314.99755859375, "1": 117.98363494873047}, "flags": {}, "order": 4, "mode": 0, "inputs": [], "outputs": [], "properties": {"text": ""}, "widgets_values": ["The reference sampling implementation auto adjusts the shift value based on the resolution, if you don't want this you can just bypass (CTRL-B) this ModelSamplingFlux node.\n"], "color": "#432", "bgcolor": "#653"}, {"id": 13, "type": "SamplerCustomAdvanced", "pos": {"0": 827, "1": 239}, "size": {"0": 236.8000030517578, "1": 128.12550354003906}, "flags": {}, "order": 16, "mode": 0, "inputs": [{"name": "noise", "type": "NOISE", "link": 37, "slot_index": 0}, {"name": "guider", "type": "GUIDER", "link": 30, "slot_index": 1}, {"name": "sampler", "type": "SAMPLER", "link": 19, "slot_index": 2}, {"name": "sigmas", "type": "SIGMAS", "link": 20, "slot_index": 3}, {"name": "latent_image", "type": "LATENT", "link": 116, "slot_index": 4}], "outputs": [{"name": "output", "type": "LATENT", "links": [24], "slot_index": 0, "shape": 3}, {"name": "denoised_output", "type": "LATENT", "links": null, "shape": 3}], "properties": {"Node name for S&R": "SamplerCustomAdvanced"}, "widgets_values": []}, {"id": 8, "type": "VAEDecode", "pos": {"0": 832, "1": 407}, "size": {"0": 233.40155029296875, "1": 46}, "flags": {}, "order": 17, "mode": 0, "inputs": [{"name": "samples", "type": "LATENT", "link": 24}, {"name": "vae", "type": "VAE", "link": 12}], "outputs": [{"name": "IMAGE", "type": "IMAGE", "links": [9], "slot_index": 0}], "properties": {"Node name for S&R": "VAEDecode"}, "widgets_values": []}, {"id": 51, "type": "Note", "pos": {"0": 329, "1": -95}, "size": {"0": 463.29266357421875, "1": 166.00962829589844}, "flags": {}, "order": 5, "mode": 0, "inputs": [], "outputs": [], "properties": {}, "widgets_values": ["     \u2588\u2588\u2557 \u2588\u2588\u2588\u2588\u2588\u2588\u2557  \u2588\u2588\u2588\u2588\u2588\u2588\u2557\u2588\u2588\u2557  \u2588\u2588\u2557\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2557\u2588\u2588\u2588\u2588\u2588\u2588\u2557     \u2588\u2588\u2588\u2588\u2588\u2557 \u2588\u2588\u2557\n     \u2588\u2588\u2551\u2588\u2588\u2554\u2550\u2550\u2550\u2588\u2588\u2557\u2588\u2588\u2554\u2550\u2550\u2550\u2550\u255d\u2588\u2588\u2551 \u2588\u2588\u2554\u255d\u2588\u2588\u2554\u2550\u2550\u2550\u2550\u255d\u2588\u2588\u2554\u2550\u2550\u2588\u2588\u2557   \u2588\u2588\u2554\u2550\u2550\u2588\u2588\u2557\u2588\u2588\u2551\n     \u2588\u2588\u2551\u2588\u2588\u2551   \u2588\u2588\u2551\u2588\u2588\u2551     \u2588\u2588\u2588\u2588\u2588\u2554\u255d \u2588\u2588\u2588\u2588\u2588\u2557  \u2588\u2588\u2588\u2588\u2588\u2588\u2554\u255d   \u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2551\u2588\u2588\u2551\n\u2588\u2588   \u2588\u2588\u2551\u2588\u2588\u2551   \u2588\u2588\u2551\u2588\u2588\u2551     \u2588\u2588\u2554\u2550\u2588\u2588\u2557 \u2588\u2588\u2554\u2550\u2550\u255d  \u2588\u2588\u2554\u2550\u2550\u2588\u2588\u2557   \u2588\u2588\u2554\u2550\u2550\u2588\u2588\u2551\u2588\u2588\u2551\n\u255a\u2588\u2588\u2588\u2588\u2588\u2554\u255d\u255a\u2588\u2588\u2588\u2588\u2588\u2588\u2554\u255d\u255a\u2588\u2588\u2588\u2588\u2588\u2588\u2557\u2588\u2588\u2551  \u2588\u2588\u2557\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2557\u2588\u2588\u2551  \u2588\u2588\u2551\u2588\u2588\u2557\u2588\u2588\u2551  \u2588\u2588\u2551\u2588\u2588\u2551\n \u255a\u2550\u2550\u2550\u2550\u255d  \u255a\u2550\u2550\u2550\u2550\u2550\u255d  \u255a\u2550\u2550\u2550\u2550\u2550\u255d\u255a\u2550\u255d  \u255a\u2550\u255d\u255a\u2550\u2550\u2550\u2550\u2550\u2550\u255d\u255a\u2550\u255d  \u255a\u2550\u255d\u255a\u2550\u255d\u255a\u2550\u255d  \u255a\u2550\u255d\u255a\u2550\u255d\n
                                    \nhttps://instagram.com/"], "color": "#432", "bgcolor": "#653"}, {"id": 47, "type": "DualCLIPLoader", "pos": {"0": -322, "1": 296}, "size": {"0": 312.69696044921875, "1": 106}, "flags": {}, "order": 6, "mode": 0, "inputs": [], "outputs": [{"name": "CLIP", "type": "CLIP", "links": [139], "slot_index": 0, "shape": 3}], "properties": {"Node name for S&R": "DualCLIPLoader"}, "widgets_values": ["ViT-L-14-TEXT-detail-improved-hiT-GmP-TE-only-HF.safetensors", "t5\\google_t5-v1_1-xxl_encoderonly-fp16.safetensors", "flux"]}, {"id": 10, "type": "VAELoader", "pos": {"0": 30, "1": 177}, "size": {"0": 319.9231872558594, "1": 60.98368453979492}, "flags": {}, "order": 7, "mode": 0, "inputs": [], "outputs": [{"name": "VAE", "type": "VAE", "links": [12], "slot_index": 0, "shape": 3}], "properties": {"Node name for S&R": "VAELoader"}, "widgets_values": ["FLUX1\\ae.safetensors"]}, {"id": 50, "type": "Power Lora Loader (rgthree)", "pos": {"0": 19, "1": 288}, "size": {"0": 334.2002868652344, "1": 142}, "flags": {}, "order": 10, "mode": 0, "inputs": [{"name": "model", "type": "MODEL", "link": 138, "dir": 3}, {"name": "clip", "type": "CLIP", "link": 139, "dir": 3}], "outputs": [{"name": "MODEL", "type": "MODEL", "links": [141, 142], "slot_index": 0, "shape": 3, "dir": 4}, {"name": "CLIP", "type": "CLIP", "links": [140], "slot_index": 1, "shape": 3, "dir": 4}], "properties": {"Show Strengths": "Single Strength"}, "widgets_values": [null, {"type": "PowerLoraLoaderHeaderWidget"}, {"on": true, "lora": "Turbo\\flux_turbo.safetensors", "strength": 1, "strengthTwo": null}, null, ""]}, {"id": 46, "type": "UNETLoader", "pos": {"0": -319, "1": 166}, "size": {"0": 315, "1": 82}, "flags": {}, "order": 8, "mode": 0, "inputs": [], "outputs": [{"name": "MODEL", "type": "MODEL", "links": [138], "slot_index": 0, "shape": 3}], "properties": {"Node name for S&R": "UNETLoader"}, "widgets_values": ["FLUX1\\flux1-dev.safetensors", "fp8_e4m3fn_fast"]}, {"id": 6, "type": "CLIPTextEncode", "pos": {"0": 384, "1": 240}, "size": {"0": 428.4508972167969, "1": 207.69332885742188}, "flags": {}, "order": 13, "mode": 0, "inputs": [{"name": "clip", "type": "CLIP", "link": 140}], "outputs": [{"name": "CONDITIONING", "type": "CONDITIONING", "links": [41], "slot_index": 0}], "title": "CLIP Text Encode (Positive Prompt)", "properties": {"Node name for S&R": "CLIPTextEncode"}, "widgets_values": ["photo of a man."], "color": "#232", "bgcolor": "#353"}], "links": [[9, 8, 0, 9, 0, "IMAGE"], [12, 10, 0, 8, 1, "VAE"], [19, 16, 0, 13, 2, "SAMPLER"], [20, 17, 0, 13, 3, "SIGMAS"], [24, 13, 0, 8, 0, "LATENT"], [30, 22, 0, 13, 1, "GUIDER"], [37, 25, 0, 13, 0, "NOISE"], [41, 6, 0, 26, 0, "CONDITIONING"], [42, 26, 0, 22, 1, "CONDITIONING"], [54, 30, 0, 22, 0, "MODEL"], [112, 34, 0, 27, 0, "INT"], [113, 35, 0, 27, 1, "INT"], [114, 35, 0, 30, 2, "INT"], [115, 34, 0, 30, 1, "INT"], [116, 27, 0, 13, 4, "LATENT"], [138, 46, 0, 50, 0, "MODEL"], [139, 47, 0, 50, 1, "CLIP"], [140, 50, 1, 6, 0, "CLIP"], [141, 50, 0, 17, 0, "MODEL"], [142, 50, 0, 30, 0, "MODEL"]], "groups": [], "config": {}, "extra": {"ds": {"scale": 0.7513148009015777, "offset": [633.1895566406254, -41.92843025346228]}, "groupNodes": {}}, "version": 0.4}
    Image Size                      : 768x1344
    Megapixels                      : 1.0
    [Example End]

    ---

    """
    try:
        # Run ExifTool to extract metadata in JSON format
        result = subprocess.run(
            ["exiftool", "-j", str(image_path)],   # Command and arguments
            stdout=subprocess.PIPE,                # Capture standard output
            stderr=subprocess.PIPE,                # Capture standard error
            text=True,                             # Return output as strings (not bytes)
        )
        # Check if ExifTool ran successfully
        if result.returncode != 0:
            # If ExifTool failed, print the error message
            print(f"ExifTool error for {image_path}: {result.stderr}")
            # Return an empty dictionary to signify failure
            return {}
        # Load the JSON output into a Python list of dictionaries
        metadata_list = json.loads(result.stdout)
        # ExifTool outputs a list; return the first item (should be the only one)
        return metadata_list[0] if metadata_list else {}
    except Exception as e:
        # Catch any exceptions that occurred during the process
        print(f"Error extracting metadata for {image_path}: {e}")
        # Return an empty dictionary to signify failure
        return {}

def save_metadata(file_path: Path, metadata, extension: str) -> None:
    """
    Save metadata to a file with the same base name as the image.

    Args:
        file_path (Path): The original image file path.
        metadata: The metadata to save (can be a dictionary or a string).
        extension (str): The file extension to use (e.g., '.json' or '.txt').

    Returns:
        None
    """
    # Construct the new file path with the desired extension
    save_path = file_path.with_suffix(extension)
    # Generate a unique filename if the file already exists
    save_path = ensure_unique_filename(save_path)
    # Open the file in write mode with UTF-8 encoding
    with open(save_path, "w", encoding="utf-8") as file:
        if extension == ".json":
            try:
                # Attempt to write the metadata as formatted JSON
                json.dump(metadata, file, ensure_ascii=False, indent=4)
                print(f"Saved metadata to {save_path}")
            except TypeError as e:
                # If the metadata is not JSON-serializable, print an error
                print(f"Error saving JSON metadata for {file_path}: {e}")
        else:
            # Write metadata as raw text
            file.write(metadata if isinstance(metadata, str) else str(metadata))
            print(f"Saved metadata to {save_path}")

def ensure_unique_filename(file_path: Path) -> Path:
    """
    Generate a unique file path by appending a counter if the file already exists.

    Args:
        file_path (Path): The desired file path.

    Returns:
        Path: A unique file path that does not exist yet.
    """
    counter = 1
    unique_path = file_path
    # Loop until a unique file name is found
    while unique_path.exists():
        # Append a counter to the file stem (base name without suffix)
        new_stem = f"{file_path.stem}_{counter}"
        # Create a new file path with the modified stem
        unique_path = file_path.with_name(f"{new_stem}{file_path.suffix}")
        # Increment the counter for the next iteration if needed
        counter += 1
    # Return the unique file path
    return unique_path

def move_file_with_structure(file_path: Path, root_folder: Path, destination_folder: Path) -> None:
    """
    Move a file to the destination folder, preserving its relative directory structure.

    Args:
        file_path (Path): The original file path.
        root_folder (Path): The root folder containing all files.
        destination_folder (Path): The destination folder where the file will be moved.

    Returns:
        None
    """
    # Calculate the relative path from the root folder to the file
    relative_path = file_path.relative_to(root_folder)
    # Construct the destination path by joining the destination folder and relative path
    destination_path = destination_folder / relative_path
    # Ensure that all parent directories of the destination path exist
    destination_path.parent.mkdir(parents=True, exist_ok=True)
    # Move the file to the destination path
    shutil.move(str(file_path), str(destination_path))

def process_png_file(image_path: Path, root_folder: Path, review_folder: Path) -> None:
    """
    Process a single PNG file:
        - Extract metadata ('Workflow' or 'Parameters') and save appropriately.
        - Convert the PNG image to AVIF format.
        - Move the original PNG file to the review folder.

    Args:
        image_path (Path): Path to the PNG image file.
        root_folder (Path): Root directory containing all images.
        review_folder (Path): Directory to store the original PNG files for review.

    Returns:
        None
    """
    # Extract metadata from the image
    metadata = extract_metadata(image_path)

    # Check for 'Workflow' metadata (ComfyUI)
    if "Workflow" in metadata:
        data = metadata["Workflow"]         # Get the 'Workflow' data
        try:
            # Try to parse the 'Workflow' data as JSON
            json_data = json.loads(data)
            # Save the parsed JSON data to a .json file
            save_metadata(image_path, json_data, ".json")
        except json.JSONDecodeError as e:
            # If parsing fails, save the raw data to a .json file
            print(f"Error parsing 'Workflow' metadata in {image_path}: {e}")
            save_metadata(image_path, data, ".json")
    # If 'Workflow' is not present, check for 'Parameters' metadata (Automatic1111)
    elif "Parameters" in metadata:
        params = metadata["Parameters"]     # Get the 'Parameters' data
        # Save the parameters to a .txt file
        save_metadata(image_path, params, ".txt")
    else:
        # If neither 'Workflow' nor 'Parameters' metadata is found, proceed without saving metadata
        print(f"No 'Workflow' or 'Parameters' metadata found for: {image_path}")

    # Convert the PNG image to AVIF format
    avif_path = image_path.with_suffix(".avif")   # Define the output file path
    if compress_to_avif(image_path, avif_path):
        # If conversion succeeds, move the original PNG file to the review folder
        move_file_with_structure(image_path, root_folder, review_folder)

def process_images_concurrently(folder_path: Path, review_folder: Path) -> None:
    """
    Process all PNG files in a folder and its subfolders concurrently.

    Args:
        folder_path (Path): Path to the folder containing PNG files.
        review_folder (Path): Path to the folder where original PNG files will be moved.

    Returns:
        None
    """
    # Recursively find all PNG files in the folder and its subfolders
    png_files = list(folder_path.rglob("*.png"))
    # Check if any PNG files were found
    if not png_files:
        print("No PNG files found in the specified directory.")
        return
    # Use a ThreadPoolExecutor to process files concurrently
    with ThreadPoolExecutor() as executor:
        # Map each PNG file to a future task
        future_to_file = {
            executor.submit(process_png_file, file, folder_path, review_folder): file
            for file in png_files
        }
        # Use tqdm to display a progress bar
        with tqdm(
            total=len(png_files),            # Total number of files to process
            desc="Processing PNG files",     # Description displayed in the progress bar
            dynamic_ncols=True,              # Adjust the progress bar width dynamically
            smoothing=0.3                    # Smoothing factor for progress bar updates
        ) as progress_bar:
            # Iterate over the futures as they complete
            for future in as_completed(future_to_file):
                file = future_to_file[future]    # Get the corresponding file
                try:
                    # Retrieve the result to catch any exceptions
                    future.result()
                except Exception as e:
                    # If an exception occurred, print an error message
                    print(f"Error processing file {file}: {e}")
                finally:
                    # Update the progress bar
                    progress_bar.update(1)

def main() -> None:
    """
    Main function to execute the script:
        - Checks for required dependencies.
        - Prompts the user for input and output directories.
        - Initiates concurrent processing of images.

    Returns:
        None
    """
    try:
        # Check that required external tools are installed
        check_dependencies()
    except EnvironmentError as e:
        # If dependencies are missing, print the error message and exit
        print(e)
        return

    # Prompt the user for the path to the images folder
    images_folder_input = input("Path to images folder: ").strip()
    # Resolve the absolute path of the images folder
    images_folder = Path(images_folder_input).resolve()
    # Check if the provided path is a directory
    if not images_folder.is_dir():
        print(f"Invalid path: {images_folder} is not a directory.")
        return

    # Prompt the user for the path to the review folder (optional)
    review_folder_input = input("Path to review folder (leave blank for default): ").strip()
    if review_folder_input:
        # Use the user-provided path for the review folder
        review_folder = Path(review_folder_input).resolve()
    else:
        # Default to a 'Review' folder inside the images folder
        review_folder = images_folder / "Review"
    # Create the review folder if it doesn't exist
    review_folder.mkdir(parents=True, exist_ok=True)
    # Inform the user where the review folder is located
    print(f"Review folder set to: {review_folder}")

    # Start processing images concurrently
    process_images_concurrently(images_folder, review_folder)
    # Inform the user that processing is complete
    print("Processing complete.")

if __name__ == "__main__":
    # Entry point of the script
    main()