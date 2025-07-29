# Screen Monitor Application

## Overview

This is a real-time screen capture and monitoring web application built with Flask and Python. The system provides a web-based dashboard for capturing, viewing, and managing screen recordings with configurable parameters like capture interval, image quality, and monitor selection.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture
- **Framework**: Traditional server-side rendered Flask templates with Bootstrap 5 dark theme
- **Templates**: Jinja2 templating with base template inheritance
- **Styling**: Bootstrap CSS with custom overrides for dark theme consistency
- **JavaScript**: Vanilla JavaScript class-based architecture for real-time monitoring
- **Icons**: Feather Icons for consistent iconography

### Backend Architecture
- **Framework**: Flask web framework with threaded request handling
- **Structure**: Modular design with separate services for screen capture functionality
- **API Design**: RESTful JSON API endpoints for frontend communication
- **Threading**: Dedicated background threads for continuous screen capture operations

### Data Storage Solutions
- **In-Memory Storage**: Captured images stored temporarily in memory for real-time display
- **No Persistent Database**: Application uses in-memory state management for capture statistics and configuration
- **Session Management**: Flask sessions for user state (minimal usage)

## Key Components

### ScreenCaptureService (`screen_capture.py`)
- **Purpose**: Core service handling screen capture operations
- **Technology**: Supports multiple capture libraries (mss, pyautogui) with fallback detection
- **Features**: 
  - Configurable capture intervals and image quality
  - Multi-monitor support
  - Image processing with PIL (timestamps, resizing)
  - Thread-safe capture statistics

### Flask Application (`app.py`)
- **Purpose**: Web server and API endpoint management
- **Routes**: Dashboard rendering and capture control endpoints
- **Error Handling**: Comprehensive logging and error response management
- **Configuration**: Environment-based configuration with sensible defaults

### Configuration Management (`config.py`)
- **Purpose**: Centralized application configuration
- **Features**: Environment variable support with fallback defaults
- **Settings**: Capture parameters, Flask settings, logging configuration

### Frontend Dashboard
- **Real-time Updates**: JavaScript-based status monitoring and image refresh
- **Controls**: Start/stop capture, configuration adjustment, manual refresh
- **Status Display**: Live capture statistics and system status indicators

## Data Flow

1. **Capture Initiation**: User configures parameters via web interface
2. **API Request**: Frontend sends configuration to `/api/start` endpoint
3. **Service Activation**: ScreenCaptureService starts background capture thread
4. **Image Processing**: Captured screens processed (resize, timestamp, quality adjustment)
5. **Memory Storage**: Latest image stored in service memory
6. **Frontend Polling**: JavaScript periodically requests latest image via API
7. **Real-time Display**: Dashboard updates with current capture and statistics

## External Dependencies

### Required Python Packages
- **Flask**: Web framework for server and API
- **Pillow (PIL)**: Image processing and manipulation
- **mss** or **pyautogui**: Screen capture libraries (with fallback detection)

### Frontend Dependencies
- **Bootstrap 5**: UI framework with dark theme support
- **Feather Icons**: Icon library for consistent UI elements

### System Dependencies
- **Screen Access**: Requires system permissions for screen capture
- **Multi-platform Support**: Compatible with Windows, macOS, Linux via capture library abstraction

## Deployment Strategy

### Development Setup
- **Entry Point**: `main.py` for local development server
- **Configuration**: Environment variables with development defaults
- **Debug Mode**: Enabled by default with comprehensive logging

### Production Considerations
- **Threading**: Flask threaded mode enabled for concurrent request handling
- **Security**: Session secret configuration via environment variables
- **Host Binding**: Configured for `0.0.0.0:5000` for container compatibility

### Environment Configuration
- **Configurable Parameters**: Capture interval, image quality, resize factor
- **Logging**: Adjustable log levels via environment variables
- **Security**: Production session secrets via environment variables

### Architecture Rationale

**Problem Addressed**: Need for real-time screen monitoring with web-based interface
**Solution Chosen**: Flask-based web application with background capture service
**Key Benefits**:
- Platform independence through web interface
- Real-time monitoring without desktop application requirements
- Configurable capture parameters for different use cases
- Lightweight architecture with minimal dependencies

**Trade-offs**:
- In-memory storage limits historical data retention
- Single-user focused (no multi-user authentication)
- Requires screen permissions which may be restricted in some environments