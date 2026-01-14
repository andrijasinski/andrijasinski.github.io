"""
Utility functions for image analysis, particularly for detecting black and white photos.
"""
from PIL import Image
from pathlib import Path
from typing import Union, Tuple


def is_black_and_white(image_path: Union[str, Path], threshold: float = 15.0, debug: bool = False) -> Union[bool, Tuple[bool, dict]]:
    """
    Determine if an image is black and white (grayscale).
    
    Uses multiple detection methods:
    1. Checks if image mode is grayscale (L, LA)
    2. For RGB images, analyzes channel similarity and saturation
    
    Args:
        image_path: Path to the image file
        threshold: Saturation threshold (0-255). Lower values = stricter detection.
                  Default 15.0 works well for most cases.
        debug: If True, return diagnostic information
    
    Returns:
        If debug=False: bool indicating if image is B&W
        If debug=True: tuple of (bool, dict) with diagnostic info
    """
    img = Image.open(image_path)
    diagnostics = {'mode': img.mode, 'saturation': None, 'channel_diff': None}
    
    # Method 1: Check image mode - true grayscale images
    if img.mode in ('L', 'LA'):
        if debug:
            return True, diagnostics
        return True
    
    # Method 2: For RGB images, check if they're actually grayscale
    if img.mode == 'RGB':
        # Convert to HSV to analyze saturation
        hsv = img.convert('HSV')
        h, s, v = hsv.split()
        
        # Get saturation values - B&W images have very low saturation
        saturation_values = list(s.getdata())
        avg_saturation = sum(saturation_values) / len(saturation_values)
        diagnostics['saturation'] = avg_saturation
        
        # Method 3: Check RGB channel similarity
        r, g, b = img.split()
        r_data = list(r.getdata())
        g_data = list(g.getdata())
        b_data = list(b.getdata())
        
        # Sample pixels for efficiency (every 50th pixel)
        sample_size = min(5000, len(r_data))
        step = max(1, len(r_data) // sample_size)
        
        channel_diffs = []
        for i in range(0, len(r_data), step):
            r_val, g_val, b_val = r_data[i], g_data[i], b_data[i]
            # Calculate maximum difference between channels
            max_diff = max(abs(r_val - g_val), abs(r_val - b_val), abs(g_val - b_val))
            channel_diffs.append(max_diff)
        
        avg_channel_diff = sum(channel_diffs) / len(channel_diffs) if channel_diffs else 255
        diagnostics['channel_diff'] = avg_channel_diff
        
        # B&W images have:
        # - Low saturation (typically < threshold) OR
        # - Very similar RGB channels (avg difference < 8) - strong indicator
        # Based on testing: B&W images avg sat=25.34, channel_diff=4.58
        # Color images avg sat=102.00, channel_diff=41.39
        if avg_channel_diff < 8:
            # Very similar channels = strong B&W indicator, allow higher saturation
            is_bw = avg_saturation < 35  # Very lenient for very similar channels
        elif avg_channel_diff < 12:
            # Moderate channel similarity (8-12), allow moderate saturation
            is_bw = avg_saturation < 25  # More lenient for moderate channel similarity
        elif avg_channel_diff < 15:
            # Higher channel similarity (12-15), require lower saturation
            is_bw = avg_saturation < threshold
        else:
            # High channel difference = definitely color
            is_bw = False
        
        if debug:
            return is_bw, diagnostics
        return is_bw
    
    # For other modes (RGBA, P, etc.), assume color
    if debug:
        return False, diagnostics
    return False


def count_bw_photos(directory: Union[str, Path], threshold: float = 15.0, debug: bool = False) -> tuple[int, int, list[str]]:
    """
    Count black and white photos in a directory.
    
    Args:
        directory: Path to directory containing images
        threshold: Saturation threshold for B&W detection
        debug: If True, print diagnostic information for each image
    
    Returns:
        Tuple of (bw_count, total_count, bw_file_names)
    """
    directory = Path(directory)
    image_files = sorted(directory.glob('*.jpg')) + sorted(directory.glob('*.JPG'))
    
    bw_count = 0
    bw_files = []
    
    for img_file in image_files:
        result = is_black_and_white(img_file, threshold, debug=debug)
        if debug:
            is_bw, diag = result  # type: ignore
            status = "B&W" if is_bw else "Color"
            print(f"{img_file.name}: {status} (sat: {diag.get('saturation', 'N/A'):.1f}, "
                  f"channel_diff: {diag.get('channel_diff', 'N/A'):.2f})")
        else:
            is_bw = result  # type: ignore
        
        if is_bw:
            bw_count += 1
            bw_files.append(img_file.name)
    
    return bw_count, len(image_files), bw_files


if __name__ == '__main__':
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python image_utils.py <image_path_or_directory> [threshold] [--debug]")
        sys.exit(1)
    
    path = Path(sys.argv[1])
    threshold = float(sys.argv[2]) if len(sys.argv) > 2 and sys.argv[2] != '--debug' else 15.0
    debug = '--debug' in sys.argv
    
    if path.is_file():
        result = is_black_and_white(path, threshold, debug=debug)
        if debug:
            is_bw, diag = result  # type: ignore
            status = "B&W" if is_bw else "Color"
            print(f"{path.name}: {status}")
            print(f"  Mode: {diag['mode']}")
            if diag['saturation'] is not None:
                print(f"  Avg Saturation: {diag['saturation']:.2f}")
            if diag['channel_diff'] is not None:
                print(f"  Avg Channel Diff: {diag['channel_diff']:.2f}")
        else:
            is_bw = result  # type: ignore
            print(f"{path.name}: {'B&W' if is_bw else 'Color'}")
    elif path.is_dir():
        bw_count, total, bw_files = count_bw_photos(path, threshold, debug=debug)
        print(f"\nBlack and white photos: {bw_count} out of {total}")
        if bw_files:
            print("B&W files:")
            for f in bw_files:
                print(f"  - {f}")
    else:
        print(f"Error: {path} is not a valid file or directory")
        sys.exit(1)

