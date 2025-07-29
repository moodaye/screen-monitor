import os
import logging
import threading
import time
import base64
from io import BytesIO
from flask import Flask, render_template, jsonify, request, Response
from screen_capture import ScreenCaptureService
from config import Config

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key-change-in-production")

# Initialize screen capture service
capture_service = ScreenCaptureService()

@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('index.html', 
                         is_capturing=capture_service.is_capturing(),
                         config=capture_service.get_config())

@app.route('/api/start', methods=['POST'])
def start_capture():
    """Start screen capture"""
    try:
        data = request.get_json() or {}
        interval = data.get('interval', 1.0)
        quality = data.get('quality', 85)
        
        success = capture_service.start_capture(interval=interval, quality=quality)
        
        if success:
            logger.info(f"Screen capture started with interval {interval}s, quality {quality}")
            return jsonify({
                'success': True, 
                'message': 'Screen capture started successfully',
                'config': capture_service.get_config()
            })
        else:
            return jsonify({
                'success': False, 
                'message': 'Failed to start screen capture'
            }), 500
            
    except Exception as e:
        logger.error(f"Error starting capture: {str(e)}")
        return jsonify({
            'success': False, 
            'message': f'Error starting capture: {str(e)}'
        }), 500

@app.route('/api/stop', methods=['POST'])
def stop_capture():
    """Stop screen capture"""
    try:
        capture_service.stop_capture()
        logger.info("Screen capture stopped")
        return jsonify({
            'success': True, 
            'message': 'Screen capture stopped successfully'
        })
    except Exception as e:
        logger.error(f"Error stopping capture: {str(e)}")
        return jsonify({
            'success': False, 
            'message': f'Error stopping capture: {str(e)}'
        }), 500

@app.route('/api/status')
def get_status():
    """Get current capture status"""
    try:
        status = {
            'is_capturing': capture_service.is_capturing(),
            'config': capture_service.get_config(),
            'stats': capture_service.get_stats(),
            'last_error': capture_service.get_last_error()
        }
        return jsonify(status)
    except Exception as e:
        logger.error(f"Error getting status: {str(e)}")
        return jsonify({
            'error': f'Error getting status: {str(e)}'
        }), 500

@app.route('/api/image/latest')
def get_latest_image():
    """Get the latest captured image"""
    try:
        image_data = capture_service.get_latest_image()
        
        if image_data is None:
            return jsonify({
                'success': False,
                'message': 'No image available'
            }), 404
        
        # Convert PIL Image to base64
        buffer = BytesIO()
        image_data.save(buffer, format='JPEG', quality=capture_service.get_config().get('quality', 85))
        img_str = base64.b64encode(buffer.getvalue()).decode()
        
        return jsonify({
            'success': True,
            'image': f'data:image/jpeg;base64,{img_str}',
            'timestamp': capture_service.get_last_capture_time(),
            'size': image_data.size
        })
        
    except Exception as e:
        logger.error(f"Error getting latest image: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Error getting image: {str(e)}'
        }), 500

@app.route('/api/image/stream')
def image_stream():
    """Stream images for real-time viewing"""
    def generate():
        while capture_service.is_capturing():
            try:
                image_data = capture_service.get_latest_image()
                if image_data:
                    buffer = BytesIO()
                    image_data.save(buffer, format='JPEG', quality=capture_service.get_config().get('quality', 85))
                    
                    yield (b'--frame\r\n'
                           b'Content-Type: image/jpeg\r\n\r\n' + 
                           buffer.getvalue() + b'\r\n')
                
                time.sleep(capture_service.get_config().get('interval', 1.0))
                
            except Exception as e:
                logger.error(f"Error in image stream: {str(e)}")
                break
    
    return Response(generate(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/api/config', methods=['GET', 'POST'])
def handle_config():
    """Get or update configuration"""
    if request.method == 'GET':
        return jsonify(capture_service.get_config())
    
    elif request.method == 'POST':
        try:
            data = request.get_json()
            success = capture_service.update_config(data)
            
            if success:
                return jsonify({
                    'success': True,
                    'message': 'Configuration updated successfully',
                    'config': capture_service.get_config()
                })
            else:
                return jsonify({
                    'success': False,
                    'message': 'Failed to update configuration'
                }), 400
                
        except Exception as e:
            logger.error(f"Error updating config: {str(e)}")
            return jsonify({
                'success': False,
                'message': f'Error updating configuration: {str(e)}'
            }), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal server error: {str(error)}")
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    logger.info("Starting Screen Monitor application...")
    app.run(host='0.0.0.0', port=5000, debug=True, threaded=True)
