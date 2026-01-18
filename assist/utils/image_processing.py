"""
Image processing utilities for Assist

Provides automatic background removal and image enhancement features
for camera-based item addition.
"""

import io
import base64
import requests
from typing import Optional, Union
from PIL import Image


def remove_background(
    image_input: Union[str, bytes, Image.Image],
    return_base64: bool = True,
    use_altlokalt_api: bool = False
) -> Union[str, bytes, Image.Image]:
    """
    Remove background from an image using AI-powered background removal.
    
    Args:
        image_input: Can be:
            - Base64 encoded string
            - Raw bytes
            - PIL Image object
            - File path
        return_base64: If True, returns base64 string; otherwise returns PIL Image
        use_altlokalt_api: If True, uses receipt-ocr.altlokalt.com API; otherwise uses rembg
    
    Returns:
        Processed image with background removed (format based on return_base64)
    """
    try:
        # Convert input to base64 for API or PIL Image for rembg
        if isinstance(image_input, str):
            if image_input.startswith('data:image'):
                # Handle data URI
                header, encoded = image_input.split(',', 1)
                image_data = base64.b64decode(encoded)
                image = Image.open(io.BytesIO(image_data))
                image_base64 = encoded
            elif image_input.startswith('/'):
                # File path
                image = Image.open(image_input)
                buffer = io.BytesIO()
                image.save(buffer, format='PNG')
                buffer.seek(0)
                image_base64 = base64.b64encode(buffer.read()).decode('utf-8')
            else:
                # Base64 string
                image_data = base64.b64decode(image_input)
                image = Image.open(io.BytesIO(image_data))
                image_base64 = image_input
        elif isinstance(image_input, bytes):
            image = Image.open(io.BytesIO(image_input))
            image_base64 = base64.b64encode(image_input).decode('utf-8')
        elif isinstance(image_input, Image.Image):
            image = image_input
            buffer = io.BytesIO()
            image.save(buffer, format='PNG')
            buffer.seek(0)
            image_base64 = base64.b64encode(buffer.read()).decode('utf-8')
        else:
            raise ValueError("Unsupported image input type")
        
        # Use altlokalt API if requested
        if use_altlokalt_api:
            try:
                response = requests.post(
                    'https://receipt-ocr.altlokalt.com/remove-background',
                    json={'image': image_base64},
                    headers={'Content-Type': 'application/json'},
                    timeout=30
                )
                
                if response.status_code == 200:
                    result = response.json()
                    processed_base64 = result.get('image_no_background', image_base64)
                    
                    if return_base64:
                        return processed_base64
                    else:
                        image_data = base64.b64decode(processed_base64)
                        return Image.open(io.BytesIO(image_data))
                else:
                    print(f"API returned status {response.status_code}, falling back to rembg")
                    # Fall through to rembg
            except Exception as api_error:
                print(f"API error: {str(api_error)}, falling back to rembg")
                # Fall through to rembg
        
        # Use rembg (default or fallback)
        from rembg import remove
        output_image = remove(image)
        
        # Return in requested format
        if return_base64:
            buffer = io.BytesIO()
            output_image.save(buffer, format='PNG')
            buffer.seek(0)
            return base64.b64encode(buffer.read()).decode('utf-8')
        else:
            return output_image
            
    except ImportError:
        # Fallback if rembg is not available
        print("Warning: rembg not installed. Background removal disabled.")
        if isinstance(image_input, str) and not image_input.startswith('/'):
            return image_input
        elif isinstance(image_input, Image.Image):
            if return_base64:
                buffer = io.BytesIO()
                image_input.save(buffer, format='PNG')
                buffer.seek(0)
                return base64.b64encode(buffer.read()).decode('utf-8')
            return image_input
        else:
            raise ValueError("Cannot process image without rembg library")
    except Exception as e:
        print(f"Error removing background: {str(e)}")
        raise


def enhance_image(
    image_input: Union[str, bytes, Image.Image],
    enhance_brightness: float = 1.0,
    enhance_contrast: float = 1.0,
    enhance_sharpness: float = 1.0,
    return_base64: bool = True
) -> Union[str, bytes, Image.Image]:
    """
    Enhance image quality with brightness, contrast, and sharpness adjustments.
    
    Args:
        image_input: Image in various formats (base64, bytes, PIL Image, or path)
        enhance_brightness: Brightness factor (1.0 = no change, >1.0 = brighter)
        enhance_contrast: Contrast factor (1.0 = no change, >1.0 = more contrast)
        enhance_sharpness: Sharpness factor (1.0 = no change, >1.0 = sharper)
        return_base64: If True, returns base64 string; otherwise returns PIL Image
    
    Returns:
        Enhanced image
    """
    try:
        from PIL import ImageEnhance
        
        # Convert input to PIL Image
        if isinstance(image_input, str):
            if image_input.startswith('data:image'):
                header, encoded = image_input.split(',', 1)
                image_data = base64.b64decode(encoded)
                image = Image.open(io.BytesIO(image_data))
            elif image_input.startswith('/'):
                image = Image.open(image_input)
            else:
                image_data = base64.b64decode(image_input)
                image = Image.open(io.BytesIO(image_data))
        elif isinstance(image_input, bytes):
            image = Image.open(io.BytesIO(image_input))
        elif isinstance(image_input, Image.Image):
            image = image_input
        else:
            raise ValueError("Unsupported image input type")
        
        # Apply enhancements
        if enhance_brightness != 1.0:
            enhancer = ImageEnhance.Brightness(image)
            image = enhancer.enhance(enhance_brightness)
        
        if enhance_contrast != 1.0:
            enhancer = ImageEnhance.Contrast(image)
            image = enhancer.enhance(enhance_contrast)
        
        if enhance_sharpness != 1.0:
            enhancer = ImageEnhance.Sharpness(image)
            image = enhancer.enhance(enhance_sharpness)
        
        # Return in requested format
        if return_base64:
            buffer = io.BytesIO()
            image.save(buffer, format='PNG')
            buffer.seek(0)
            return base64.b64encode(buffer.read()).decode('utf-8')
        else:
            return image
            
    except Exception as e:
        print(f"Error enhancing image: {str(e)}")
        raise


def process_camera_image(
    image_input: Union[str, bytes],
    remove_bg: bool = True,
    enhance: bool = True,
    return_base64: bool = True,
    use_altlokalt_api: bool = False
) -> Union[str, Image.Image]:
    """
    Complete image processing pipeline for camera-captured images.
    Removes background and enhances image quality.
    
    Args:
        image_input: Input image (base64 or bytes)
        remove_bg: Whether to remove background
        enhance: Whether to enhance image quality
        return_base64: If True, returns base64 string
        use_altlokalt_api: If True, uses receipt-ocr.altlokalt.com API for background removal
    
    Returns:
        Processed image ready for item attachment
    """
    try:
        # Start with original image
        processed_image = image_input
        
        # Remove background if requested
        if remove_bg:
            processed_image = remove_background(
                processed_image,
                return_base64=False,
                use_altlokalt_api=use_altlokalt_api
            )
        elif not isinstance(processed_image, Image.Image):
            # Convert to PIL Image for enhancement
            if isinstance(processed_image, str):
                if processed_image.startswith('data:image'):
                    header, encoded = processed_image.split(',', 1)
                    image_data = base64.b64decode(encoded)
                    processed_image = Image.open(io.BytesIO(image_data))
                else:
                    image_data = base64.b64decode(processed_image)
                    processed_image = Image.open(io.BytesIO(image_data))
            elif isinstance(processed_image, bytes):
                processed_image = Image.open(io.BytesIO(processed_image))
        
        # Enhance image if requested
        if enhance:
            processed_image = enhance_image(
                processed_image,
                enhance_brightness=1.1,
                enhance_contrast=1.1,
                enhance_sharpness=1.2,
                return_base64=False
            )
        
        # Return in requested format
        if return_base64:
            buffer = io.BytesIO()
            processed_image.save(buffer, format='PNG')
            buffer.seek(0)
            return base64.b64encode(buffer.read()).decode('utf-8')
        else:
            return processed_image
            
    except Exception as e:
        print(f"Error processing camera image: {str(e)}")
        raise
