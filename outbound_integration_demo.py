#!/usr/bin/env python3
"""
Outbound Integration Demo for Screen Monitor
Demonstrates how to configure the screen monitor to send images to external systems.
"""

import requests
import json
import time

BASE_URL = "http://localhost:5000"

def demo_configure_webhooks():
    """Demonstrate configuring webhook URLs"""
    print("=== Demo: Configuring Outbound Webhooks ===")
    
    # Example webhook URLs (you can replace these with real endpoints)
    webhook_urls = [
        "http://localhost:8000/webhook/base64",
        "http://localhost:8000/webhook/multipart", 
        "https://webhook.site/your-unique-id",  # Example public webhook service
        "https://httpbin.org/post"  # Example test endpoint
    ]
    
    for url in webhook_urls[:2]:  # Only add the first two for demo
        try:
            response = requests.post(f"{BASE_URL}/api/webhooks", 
                                   json={"add_url": url})
            result = response.json()
            
            if result['success']:
                print(f"✓ Added webhook: {url}")
            else:
                print(f"✗ Failed to add webhook: {result['message']}")
        except Exception as e:
            print(f"✗ Error adding webhook {url}: {e}")

def demo_enable_external_sending():
    """Demonstrate enabling external sending"""
    print("\n=== Demo: Enabling External Sending ===")
    
    try:
        # Enable external sending
        response = requests.post(f"{BASE_URL}/api/webhooks", 
                               json={"enable_external": True})
        result = response.json()
        
        if result['success']:
            print(f"✓ {result['message']}")
        else:
            print(f"✗ Failed to enable: {result['message']}")
            
        # Set format to base64
        response = requests.post(f"{BASE_URL}/api/webhooks", 
                               json={"external_format": "base64"})
        result = response.json()
        
        if result['success']:
            print(f"✓ {result['message']}")
        else:
            print(f"✗ Failed to set format: {result['message']}")
            
    except Exception as e:
        print(f"✗ Error enabling external sending: {e}")

def demo_start_capture_with_webhooks():
    """Demonstrate starting capture that will send to webhooks"""
    print("\n=== Demo: Starting Capture with Webhook Integration ===")
    
    try:
        # Start capture
        response = requests.post(f"{BASE_URL}/api/start", 
                               json={
                                   "interval": 5.0,  # 5 second intervals
                                   "quality": 90
                               })
        result = response.json()
        
        if result['success']:
            print(f"✓ Capture started: {result['message']}")
            print("📸 Screen monitor will now send images to configured webhooks every 5 seconds")
        else:
            print(f"✗ Failed to start: {result['message']}")
            
    except Exception as e:
        print(f"✗ Error starting capture: {e}")

def demo_check_webhook_status():
    """Demonstrate checking webhook configuration"""
    print("\n=== Demo: Checking Webhook Configuration ===")
    
    try:
        response = requests.get(f"{BASE_URL}/api/webhooks")
        result = response.json()
        
        if result['success']:
            print(f"✓ Webhook Status:")
            print(f"  External sending: {'Enabled' if result['external_sending_enabled'] else 'Disabled'}")
            print(f"  Format: {result['external_format']}")
            print(f"  Configured webhooks ({len(result['webhooks'])}):")
            
            for i, url in enumerate(result['webhooks'], 1):
                print(f"    {i}. {url}")
                
            if not result['webhooks']:
                print("    None configured")
        else:
            print(f"✗ Failed to get status: {result.get('message', 'Unknown error')}")
            
    except Exception as e:
        print(f"✗ Error checking status: {e}")

def demo_test_webhook():
    """Demonstrate testing a webhook URL"""
    print("\n=== Demo: Testing Webhook URL ===")
    
    test_url = "http://localhost:8000/webhook/base64"
    
    try:
        response = requests.post(f"{BASE_URL}/api/test-webhook", 
                               json={"url": test_url})
        result = response.json()
        
        if result['success']:
            print(f"✓ Test successful: {result['message']}")
        else:
            print(f"✗ Test failed: {result['message']}")
            
    except Exception as e:
        print(f"✗ Error testing webhook: {e}")

def main():
    """Run the outbound integration demonstration"""
    print("Screen Monitor - Outbound Integration Demo")
    print("==========================================")
    
    try:
        # Check if the monitor is running
        response = requests.get(f"{BASE_URL}/api/status", timeout=5)
        if response.status_code != 200:
            print("✗ Screen Monitor is not running. Start the application first.")
            return
            
        print("✓ Screen Monitor is running\n")
        
        # Run demonstrations
        demo_configure_webhooks()
        demo_enable_external_sending()
        demo_check_webhook_status()
        demo_test_webhook()
        demo_start_capture_with_webhooks()
        
        print("\n=== Next Steps ===")
        print("1. Start the webhook receiver: python3 webhook_receiver_demo.py")
        print("2. The screen monitor will automatically send captures to your webhooks")
        print("3. Check the received_images folder for saved images")
        print("4. Monitor the webhook receiver console for incoming images")
        
        print("\n=== Integration Guide ===")
        print("• Configure webhook URLs: POST /api/webhooks with {'add_url': 'your-url'}")
        print("• Enable sending: POST /api/webhooks with {'enable_external': true}")
        print("• Set format: POST /api/webhooks with {'external_format': 'base64' or 'multipart'}")
        print("• Test URLs: POST /api/test-webhook with {'url': 'test-url'}")
        print("• Start capture: POST /api/start (images will be sent automatically)")
        
    except requests.ConnectionError:
        print("✗ Cannot connect to Screen Monitor. Make sure it's running on port 5000.")
    except Exception as e:
        print(f"✗ Error: {e}")

if __name__ == "__main__":
    main()