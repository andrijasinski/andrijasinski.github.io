"""
Test B&W detection algorithm against labeled portfolio data.
Scans markdown files for images with 'black-and-white' or 'color' tags
and compares algorithm predictions with actual labels.
"""
import re
from pathlib import Path
from collections import defaultdict
from image_utils import is_black_and_white

PORTFOLIO_PATH = Path("content/portfolio")
ASSETS_PATH = Path("assets")


def parse_markdown_file(md_file: Path) -> list[tuple[str, str]]:
    """
    Parse a markdown file and extract image paths and their tags.
    
    Returns:
        List of tuples: (image_path, tag) where tag is 'black-and-white' or 'color'
    """
    results = []
    try:
        content = md_file.read_text()
        
        # Check if file has black-and-white or color tag
        has_bw = 'black-and-white' in content.lower()
        has_color = '- color' in content or 'tags:\n- color' in content
        
        if not (has_bw or has_color):
            return results
        
        # Extract image paths
        image_pattern = r'images:\s*\n((?:- /images/[^\n]+\n?)+)'
        match = re.search(image_pattern, content)
        if not match:
            return results
        
        images_section = match.group(1)
        image_paths = re.findall(r'- (/images/[^\n]+)', images_section)
        
        # Determine tag
        tag = 'black-and-white' if has_bw else 'color'
        
        for img_path in image_paths:
            results.append((img_path, tag))
    
    except Exception as e:
        print(f"Error parsing {md_file}: {e}")
    
    return results


def get_actual_image_path(markdown_path: str) -> Path:
    """
    Convert markdown image path to actual file system path.
    /images/2025/November/... -> assets/images/2025/November/...
    """
    if markdown_path.startswith('/images/'):
        relative_path = markdown_path[8:]  # Remove '/images/'
        return ASSETS_PATH / 'images' / relative_path
    return Path(markdown_path)


def test_algorithm():
    """Test B&W detection algorithm against labeled data."""
    print("Scanning portfolio markdown files...")
    
    # Collect all labeled images
    labeled_images = []
    md_files = list(PORTFOLIO_PATH.rglob('*.md'))
    
    for md_file in md_files:
        images = parse_markdown_file(md_file)
        labeled_images.extend(images)
    
    print(f"Found {len(labeled_images)} labeled images\n")
    
    # Test algorithm
    results = {
        'correct': {'bw': 0, 'color': 0},
        'incorrect': {'bw': [], 'color': []},
        'not_found': []
    }
    
    bw_stats = {'saturation': [], 'channel_diff': []}
    color_stats = {'saturation': [], 'channel_diff': []}
    
    for img_path, label in labeled_images:
        actual_path = get_actual_image_path(img_path)
        
        if not actual_path.exists():
            results['not_found'].append((img_path, label))
            continue
        
        # Get prediction with debug info
        prediction, diagnostics = is_black_and_white(actual_path, debug=True)
        is_bw_pred = prediction
        
        # Determine expected label
        expected_bw = (label == 'black-and-white')
        
        # Collect statistics
        if diagnostics.get('saturation') is not None:
            if expected_bw:
                bw_stats['saturation'].append(diagnostics['saturation'])
                bw_stats['channel_diff'].append(diagnostics.get('channel_diff', 0))
            else:
                color_stats['saturation'].append(diagnostics['saturation'])
                color_stats['channel_diff'].append(diagnostics.get('channel_diff', 0))
        
        # Compare prediction with label
        label_key = 'bw' if label == 'black-and-white' else 'color'
        
        if is_bw_pred == expected_bw:
            results['correct'][label_key] += 1
        else:
            # Determine which incorrect category
            # If predicted B&W but was Color -> incorrect['bw']
            # If predicted Color but was B&W -> incorrect['color']
            incorrect_key = 'bw' if is_bw_pred else 'color'
            results['incorrect'][incorrect_key].append({
                'path': img_path,
                'expected': label,
                'predicted': 'black-and-white' if is_bw_pred else 'color',
                'saturation': diagnostics.get('saturation'),
                'channel_diff': diagnostics.get('channel_diff')
            })
    
    # Print results
    total_correct = sum(results['correct'].values())
    total_tested = total_correct + sum(len(v) for v in results['incorrect'].values())
    accuracy = (total_correct / total_tested * 100) if total_tested > 0 else 0
    
    print("=" * 60)
    print("TEST RESULTS")
    print("=" * 60)
    print(f"Total images tested: {total_tested}")
    print(f"Correct predictions: {total_correct}")
    print(f"Accuracy: {accuracy:.2f}%\n")
    
    print(f"Correct B&W: {results['correct']['bw']}")
    print(f"Correct Color: {results['correct']['color']}")
    print(f"Incorrect B&W (predicted B&W but was Color): {len(results['incorrect']['bw'])}")
    print(f"Incorrect Color (predicted Color but was B&W): {len(results['incorrect']['color'])}")
    
    if results['not_found']:
        print(f"\nImages not found: {len(results['not_found'])}")
    
    # Statistics
    if bw_stats['saturation']:
        print(f"\nB&W Images Statistics:")
        print(f"  Avg Saturation: {sum(bw_stats['saturation'])/len(bw_stats['saturation']):.2f}")
        print(f"  Avg Channel Diff: {sum(bw_stats['channel_diff'])/len(bw_stats['channel_diff']):.2f}")
        print(f"  Min Saturation: {min(bw_stats['saturation']):.2f}")
        print(f"  Max Saturation: {max(bw_stats['saturation']):.2f}")
    
    if color_stats['saturation']:
        print(f"\nColor Images Statistics:")
        print(f"  Avg Saturation: {sum(color_stats['saturation'])/len(color_stats['saturation']):.2f}")
        print(f"  Avg Channel Diff: {sum(color_stats['channel_diff'])/len(color_stats['channel_diff']):.2f}")
        print(f"  Min Saturation: {min(color_stats['saturation']):.2f}")
        print(f"  Max Saturation: {max(color_stats['saturation']):.2f}")
    
    # Show misclassifications
    if results['incorrect']['bw'] or results['incorrect']['color']:
        print("\n" + "=" * 60)
        print("MISCLASSIFICATIONS")
        print("=" * 60)
        
        if results['incorrect']['bw']:
            print("\nPredicted B&W but was Color:")
            for item in results['incorrect']['bw'][:10]:  # Show first 10
                print(f"  {item['path']}")
                print(f"    Sat: {item['saturation']:.2f}, Channel Diff: {item['channel_diff']:.2f}")
        
        if results['incorrect']['color']:
            print("\nPredicted Color but was B&W:")
            for item in results['incorrect']['color'][:10]:  # Show first 10
                print(f"  {item['path']}")
                print(f"    Sat: {item['saturation']:.2f}, Channel Diff: {item['channel_diff']:.2f}")


if __name__ == '__main__':
    test_algorithm()

