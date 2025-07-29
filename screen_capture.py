import threading
import time
import logging
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
import os

# Screen capture library selection
try:
    import mss
    CAPTURE_LIBRARY = 'mss'
except ImportError:
    try:
        import pyautogui
        CAPTURE_LIBRARY = 'pyautogui'
    except ImportError:
        CAPTURE_LIBRARY = None

logger = logging.getLogger(__name__)

class ScreenCaptureService:
    def __init__(self):
        self._capturing = False
        self._capture_thread = None
        self._latest_image = None
        self._last_capture_time = None
        self._last_error = None
        self._stats = {
            'total_captures': 0,
            'failed_captures': 0,
            'start_time': None
        }
        self._config = {
            'interval': 1.0,  # seconds
            'quality': 85,    # JPEG quality
            'resize_factor': 1.0,  # scale factor for resizing
            'add_timestamp': True,  # add timestamp to image
            'monitor': 0      # monitor index for multi-monitor setups
        }
        
        # Check if screen capture is available
        if CAPTURE_LIBRARY is None:
            logger.error("No screen capture library available. Install 'mss' or 'pyautogui'")
        else:
            logger.info(f"Using {CAPTURE_LIBRARY} for screen capture")

    def is_capturing(self):
        """Check if currently capturing"""
        return self._capturing

    def get_config(self):
        """Get current configuration"""
        return self._config.copy()

    def get_stats(self):
        """Get capture statistics"""
        stats = self._stats.copy()
        if stats['start_time'] and self._capturing:
            stats['uptime_seconds'] = (datetime.now() - stats['start_time']).total_seconds()
        return stats

    def get_last_error(self):
        """Get last error message"""
        return self._last_error

    def get_latest_image(self):
        """Get the latest captured image"""
        return self._latest_image

    def get_last_capture_time(self):
        """Get timestamp of last capture"""
        return self._last_capture_time
    
    def feed_external_image(self, image):
        """Accept an external image and process it as if it was captured"""
        try:
            processed_image = self._process_image(image)
            self._latest_image = processed_image
            self._last_capture_time = datetime.now().isoformat()
            self._stats['total_captures'] += 1
            return True
        except Exception as e:
            logger.error(f"Error feeding external image: {str(e)}")
            self._last_error = str(e)
            self._stats['failed_captures'] += 1
            return False

    def update_config(self, new_config):
        """Update configuration"""
        try:
            # Validate configuration values
            if 'interval' in new_config:
                interval = float(new_config['interval'])
                if interval <= 0:
                    raise ValueError("Interval must be positive")
                self._config['interval'] = interval

            if 'quality' in new_config:
                quality = int(new_config['quality'])
                if not 1 <= quality <= 100:
                    raise ValueError("Quality must be between 1 and 100")
                self._config['quality'] = quality

            if 'resize_factor' in new_config:
                resize_factor = float(new_config['resize_factor'])
                if resize_factor <= 0:
                    raise ValueError("Resize factor must be positive")
                self._config['resize_factor'] = resize_factor

            if 'add_timestamp' in new_config:
                self._config['add_timestamp'] = bool(new_config['add_timestamp'])

            if 'monitor' in new_config:
                monitor = int(new_config['monitor'])
                if monitor < 0:
                    raise ValueError("Monitor index must be non-negative")
                self._config['monitor'] = monitor

            logger.info(f"Configuration updated: {self._config}")
            return True

        except (ValueError, TypeError) as e:
            logger.error(f"Invalid configuration: {str(e)}")
            self._last_error = f"Invalid configuration: {str(e)}"
            return False

    def start_capture(self, interval=None, quality=None):
        """Start screen capture"""
        if CAPTURE_LIBRARY is None:
            self._last_error = "No screen capture library available"
            return False

        if self._capturing:
            logger.warning("Capture already running")
            return True

        # Update config if provided
        if interval is not None:
            self._config['interval'] = float(interval)
        if quality is not None:
            self._config['quality'] = int(quality)

        try:
            self._capturing = True
            self._stats['start_time'] = datetime.now()
            self._stats['total_captures'] = 0
            self._stats['failed_captures'] = 0
            self._last_error = None

            # Start capture thread
            self._capture_thread = threading.Thread(target=self._capture_loop, daemon=True)
            self._capture_thread.start()

            logger.info("Screen capture started successfully")
            return True

        except Exception as e:
            logger.error(f"Failed to start capture: {str(e)}")
            self._last_error = str(e)
            self._capturing = False
            return False

    def stop_capture(self):
        """Stop screen capture"""
        if not self._capturing:
            logger.warning("Capture not running")
            return

        self._capturing = False
        
        # Wait for thread to finish
        if self._capture_thread and self._capture_thread.is_alive():
            self._capture_thread.join(timeout=5.0)

        logger.info("Screen capture stopped")

    def _capture_loop(self):
        """Main capture loop running in separate thread"""
        logger.info("Starting capture loop")
        
        while self._capturing:
            try:
                # Capture screenshot
                image = self._capture_screenshot()
                
                if image:
                    # Process image
                    processed_image = self._process_image(image)
                    
                    # Update latest image
                    self._latest_image = processed_image
                    self._last_capture_time = datetime.now().isoformat()
                    self._stats['total_captures'] += 1
                    
                    logger.debug(f"Captured image: {processed_image.size}")
                else:
                    self._stats['failed_captures'] += 1
                    logger.warning("Failed to capture screenshot")

            except Exception as e:
                logger.error(f"Error in capture loop: {str(e)}")
                self._last_error = str(e)
                self._stats['failed_captures'] += 1

            # Wait for next capture
            time.sleep(self._config['interval'])

        logger.info("Capture loop ended")

    def _capture_screenshot(self):
        """Capture screenshot using available library"""
        try:
            if CAPTURE_LIBRARY == 'mss':
                # Check if we're in a headless environment
                import os
                if not os.environ.get('DISPLAY') and not os.environ.get('WAYLAND_DISPLAY'):
                    # Create a simple test image for demonstration in headless environment
                    logger.warning("No display available - creating test image")
                    return self._create_test_image()
                
                with mss.mss() as sct:
                    # Get monitor info
                    monitors = sct.monitors
                    monitor_index = min(self._config['monitor'], len(monitors) - 1)
                    monitor = monitors[monitor_index + 1] if monitor_index < len(monitors) - 1 else monitors[1]
                    
                    # Capture screenshot
                    screenshot = sct.grab(monitor)
                    image = Image.frombytes('RGB', screenshot.size, screenshot.bgra, 'raw', 'BGRX')
                    return image

            elif CAPTURE_LIBRARY == 'pyautogui':
                # Check if we're in a headless environment
                import os
                if not os.environ.get('DISPLAY') and not os.environ.get('WAYLAND_DISPLAY'):
                    # Create a simple test image for demonstration in headless environment
                    logger.warning("No display available - creating test image")
                    return self._create_test_image()
                
                # pyautogui doesn't support monitor selection easily
                screenshot = pyautogui.screenshot()
                return screenshot

            else:
                raise RuntimeError("No capture library available")

        except Exception as e:
            logger.error(f"Screenshot capture failed: {str(e)}")
            # If screen capture fails, create a test image to demonstrate functionality
            logger.info("Creating test image due to capture failure")
            return self._create_test_image()
    
    def _create_test_image(self):
        """Create a test image for demonstration purposes"""
        from datetime import datetime
        
        # Create a 800x600 test image
        image = Image.new('RGB', (800, 600), color=(45, 55, 72))  # Dark blue-gray background
        draw = ImageDraw.Draw(image)
        
        # Draw some test content
        try:
            font = ImageFont.load_default()
        except:
            font = None
        
        # Draw title
        title = "Screen Monitor - Test Mode"
        title_bbox = draw.textbbox((0, 0), title, font=font)
        title_width = title_bbox[2] - title_bbox[0]
        draw.text(((800 - title_width) // 2, 200), title, fill=(255, 255, 255), font=font)
        
        # Draw timestamp
        timestamp = datetime.now().strftime("Captured: %Y-%m-%d %H:%M:%S")
        timestamp_bbox = draw.textbbox((0, 0), timestamp, font=font)
        timestamp_width = timestamp_bbox[2] - timestamp_bbox[0]
        draw.text(((800 - timestamp_width) // 2, 250), timestamp, fill=(200, 200, 200), font=font)
        
        # Draw info message
        info = "Running in headless environment - showing test image"
        info_bbox = draw.textbbox((0, 0), info, font=font)
        info_width = info_bbox[2] - info_bbox[0]
        draw.text(((800 - info_width) // 2, 300), info, fill=(150, 150, 150), font=font)
        
        # Draw some geometric shapes for visual interest
        draw.rectangle([100, 400, 200, 500], fill=(52, 152, 219), outline=(255, 255, 255))  # Blue square
        draw.ellipse([250, 400, 350, 500], fill=(231, 76, 60), outline=(255, 255, 255))    # Red circle
        draw.polygon([(450, 400), (500, 450), (450, 500), (400, 450)], fill=(46, 204, 113), outline=(255, 255, 255))  # Green diamond
        draw.rectangle([550, 400, 650, 500], fill=(155, 89, 182), outline=(255, 255, 255))  # Purple square
        
        return image

    def _process_image(self, image):
        """Process captured image"""
        try:
            # Resize if needed
            if self._config['resize_factor'] != 1.0:
                new_size = (
                    int(image.width * self._config['resize_factor']),
                    int(image.height * self._config['resize_factor'])
                )
                image = image.resize(new_size, Image.Resampling.LANCZOS)

            # Add timestamp if enabled
            if self._config['add_timestamp']:
                image = self._add_timestamp(image)

            return image

        except Exception as e:
            logger.error(f"Image processing failed: {str(e)}")
            return image  # Return original image if processing fails

    def _add_timestamp(self, image):
        """Add timestamp to image"""
        try:
            # Create a copy to avoid modifying original
            img_copy = image.copy()
            draw = ImageDraw.Draw(img_copy)
            
            # Get timestamp
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Try to use a default font, fallback to default if not available
            try:
                font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 20)
            except:
                try:
                    font = ImageFont.load_default()
                except:
                    font = None

            # Position timestamp at bottom-right
            text_bbox = draw.textbbox((0, 0), timestamp, font=font)
            text_width = text_bbox[2] - text_bbox[0]
            text_height = text_bbox[3] - text_bbox[1]
            
            x = image.width - text_width - 10
            y = image.height - text_height - 10

            # Draw background rectangle
            draw.rectangle([x-5, y-5, x+text_width+5, y+text_height+5], 
                         fill=(0, 0, 0, 128))
            
            # Draw timestamp text
            draw.text((x, y), timestamp, fill=(255, 255, 255), font=font)
            
            return img_copy

        except Exception as e:
            logger.error(f"Failed to add timestamp: {str(e)}")
            return image  # Return original if timestamp addition fails
