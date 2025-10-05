"""
Main CLI entry point for ESP32-CAM applications.

This module provides the main command-line interface for running
various camera viewing and diagnostic operations.
"""

import click
import logging
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from viewers import DualCameraViewer, SingleCameraViewer
from core import get_config

logger = logging.getLogger(__name__)


@click.group()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.option('--config', '-c', type=click.Path(exists=True), help='Path to configuration file')
@click.pass_context
def cli(ctx, verbose, config):
    """
    ESP32-CAM OpenCV Application CLI
    
    Manage and view ESP32-CAM camera streams with various tools and utilities.
    """
    # Setup logging
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Store config in context
    ctx.ensure_object(dict)
    ctx.obj['config_file'] = config
    ctx.obj['verbose'] = verbose


@cli.command()
@click.pass_context
def view(ctx):
    """Launch dual camera viewer (GUI)."""
    click.echo("🎥 Launching Dual Camera Viewer...")
    click.echo("Press 'q' to quit, 's' to save frame pair, 'a' to save annotated frames")
    
    try:
        viewer = DualCameraViewer(config_file=ctx.obj.get('config_file'))
        viewer.run()
    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        if ctx.obj.get('verbose'):
            raise


@cli.command()
@click.option('--camera', '-c', default='ESP32_CAM_1', 
              help='Camera name to view (default: ESP32_CAM_1)')
@click.pass_context
def view_single(ctx, camera):
    """Launch single camera viewer (GUI)."""
    click.echo(f"🎥 Launching Single Camera Viewer for {camera}...")
    click.echo("Press 'q' to quit, 's' to save frame, 'a' to save annotated frame")
    
    try:
        viewer = SingleCameraViewer(camera, config_file=ctx.obj.get('config_file'))
        viewer.run()
    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        if ctx.obj.get('verbose'):
            raise


@cli.command()
@click.option('--host', '-h', default='0.0.0.0', help='Host to bind to (default: 0.0.0.0)')
@click.option('--port', '-p', default=5000, help='Port to listen on (default: 5000)')
@click.option('--debug', is_flag=True, help='Enable debug mode')
def web(host, port, debug):
    """Launch web-based viewer."""
    click.echo(f"🌐 Launching Web Viewer...")
    click.echo(f"Access at: http://{host}:{port}")
    
    try:
        from viewers.web_viewer import main as web_main
        web_main(host=host, port=port, debug=debug)
    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        raise


@cli.command()
@click.pass_context
def diagnose(ctx):
    """Run diagnostic tests on cameras."""
    click.echo("🔍 Running camera diagnostics...")
    
    from diagnostic_cli import cli as diag_cli
    
    # Pass control to diagnostic CLI
    sys.argv = ['diagnostic_cli', 'test-all']
    if ctx.obj.get('verbose'):
        sys.argv.append('--verbose')
    
    diag_cli()


@cli.command()
@click.pass_context
def config_info(ctx):
    """Display current configuration."""
    click.echo("⚙️  Configuration Information")
    click.echo("="*50)
    
    try:
        config = get_config(ctx.obj.get('config_file'))
        cameras = config.get_all_cameras()
        
        click.echo(f"\nConfigured Cameras: {len(cameras)}")
        
        for name, cam_config in cameras.items():
            click.echo(f"\n📹 {name}:")
            click.echo(f"   IP Address: {cam_config.ip}")
            click.echo(f"   Port: {cam_config.port}")
            click.echo(f"   Stream URL: {cam_config.stream_url}")
            click.echo(f"   Status URL: {cam_config.status_url}")
    except Exception as e:
        click.echo(f"❌ Error loading configuration: {e}", err=True)


@cli.command()
@click.option('--name', '-n', required=True, help='Camera name')
@click.option('--ip', '-i', required=True, help='Camera IP address')
@click.option('--port', '-p', default=80, help='Camera port (default: 80)')
def add_camera(name, ip, port):
    """Add a new camera to configuration."""
    click.echo(f"Adding camera: {name} ({ip}:{port})")
    
    try:
        from core import get_config
        config = get_config()
        config.add_camera(name, ip, port)
        
        click.echo(f"✅ Camera {name} added successfully")
        click.echo(f"   Stream URL: http://{ip}:{port}/stream")
    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)


@cli.command()
def list_cameras():
    """List all configured cameras."""
    click.echo("📋 Configured Cameras:")
    click.echo("="*50)
    
    try:
        config = get_config()
        cameras = config.get_all_cameras()
        
        if not cameras:
            click.echo("No cameras configured")
            return
        
        for name, cam_config in cameras.items():
            click.echo(f"\n{name}:")
            click.echo(f"  IP: {cam_config.ip}:{cam_config.port}")
            click.echo(f"  Stream: {cam_config.stream_url}")
    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)


@cli.command()
def version():
    """Display version information."""
    click.echo("ESP32-CAM OpenCV Application")
    click.echo("Version: 1.0.0")
    click.echo("A professional framework for ESP32-CAM camera management")


if __name__ == '__main__':
    cli()
