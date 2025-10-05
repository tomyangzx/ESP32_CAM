"""
Diagnostic CLI tool for ESP32-CAM connections.

This module provides command-line diagnostic utilities for testing
camera connectivity and performance.
"""

import click
import logging
import json
import sys
from pathlib import Path
from typing import Optional

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from core import get_config, CameraDiagnostics, NetworkDiagnostics
from utils import test_url_reachable, test_stream_endpoint

logger = logging.getLogger(__name__)


@click.group()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
def cli(verbose):
    """ESP32-CAM Diagnostic Tools"""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )


@cli.command()
@click.option('--camera', '-c', default='ESP32_CAM_1', help='Camera name to test')
def test_camera(camera):
    """Test connection to a specific camera."""
    click.echo(f"Testing camera: {camera}")
    
    config = get_config()
    cam_config = config.get_camera(camera)
    
    if not cam_config:
        click.echo(f"❌ Camera {camera} not found in configuration", err=True)
        return
    
    click.echo(f"Camera IP: {cam_config.ip}")
    click.echo(f"Stream URL: {cam_config.stream_url}")
    click.echo("")
    
    # Run diagnostics
    click.echo("Running diagnostics...")
    results = CameraDiagnostics.run_full_diagnostics(cam_config.ip, cam_config.port)
    
    # Display results
    click.echo(f"\n{'='*50}")
    click.echo("Diagnostic Results:")
    click.echo(f"{'='*50}")
    
    click.echo(f"\n📡 Ping Test: {'✅ PASS' if results['ping_test'] else '❌ FAIL'}")
    
    http_status = results['http_status']
    if http_status['reachable']:
        click.echo(f"🌐 HTTP Status: ✅ {http_status['status_code']} ({http_status['response_time']}ms)")
    else:
        click.echo(f"🌐 HTTP Status: ❌ {http_status.get('error', 'Failed')}")
    
    stream_status = results['stream_status']
    if stream_status['reachable']:
        click.echo(f"📹 Stream Status: ✅ {stream_status['status_code']} ({stream_status['response_time']}ms)")
    else:
        click.echo(f"📹 Stream Status: ❌ {stream_status.get('error', 'Failed')}")
    
    if 'stream_quality' in results and 'error' not in results['stream_quality']:
        quality = results['stream_quality']
        click.echo(f"\n📊 Stream Quality:")
        click.echo(f"   Frames received: {quality['frames_received']}")
        click.echo(f"   Average FPS: {quality['avg_fps']}")
        click.echo(f"   Stable: {'✅ Yes' if quality['stable'] else '❌ No'}")


@cli.command()
def test_all():
    """Test all configured cameras."""
    click.echo("Testing all configured cameras...")
    
    config = get_config()
    cameras = config.get_all_cameras()
    
    if not cameras:
        click.echo("❌ No cameras configured", err=True)
        return
    
    for name, cam_config in cameras.items():
        click.echo(f"\n{'='*50}")
        click.echo(f"Testing: {name}")
        click.echo(f"{'='*50}")
        
        results = CameraDiagnostics.run_full_diagnostics(cam_config.ip, cam_config.port)
        
        # Summary
        ping_ok = results['ping_test']
        http_ok = results['http_status']['reachable']
        stream_ok = results['stream_status']['reachable']
        
        if ping_ok and http_ok and stream_ok:
            click.echo(f"✅ {name}: All tests passed")
        else:
            click.echo(f"❌ {name}: Some tests failed")
            if not ping_ok:
                click.echo("   - Ping failed")
            if not http_ok:
                click.echo("   - HTTP connection failed")
            if not stream_ok:
                click.echo("   - Stream connection failed")


@cli.command()
@click.option('--output', '-o', type=click.Path(), help='Output file for results (JSON)')
def full_report(output: Optional[str]):
    """Generate full diagnostic report for all cameras."""
    click.echo("Generating full diagnostic report...")
    
    config = get_config()
    cameras = config.get_all_cameras()
    
    report = {
        'timestamp': CameraDiagnostics.run_full_diagnostics("127.0.0.1")['timestamp'],
        'cameras': {}
    }
    
    for name, cam_config in cameras.items():
        click.echo(f"Testing {name}...")
        results = CameraDiagnostics.run_full_diagnostics(cam_config.ip, cam_config.port)
        report['cameras'][name] = results
    
    # Output results
    if output:
        with open(output, 'w') as f:
            json.dump(report, f, indent=2)
        click.echo(f"\n✅ Report saved to: {output}")
    else:
        click.echo("\n" + "="*50)
        click.echo("DIAGNOSTIC REPORT")
        click.echo("="*50)
        click.echo(json.dumps(report, indent=2))


@cli.command()
@click.option('--subnet', '-s', default='192.168.2', help='Subnet to scan (e.g., 192.168.2)')
def scan_network(subnet):
    """Scan network for ESP32-CAM devices."""
    click.echo(f"Scanning subnet {subnet}.0/24 for devices...")
    click.echo("This may take a few minutes...")
    
    devices = NetworkDiagnostics.scan_subnet(subnet, port=80, timeout=0.5)
    
    if devices:
        click.echo(f"\n✅ Found {len(devices)} device(s):")
        for ip in devices:
            click.echo(f"   📹 {ip}")
    else:
        click.echo("\n❌ No devices found")


@cli.command()
def network_info():
    """Display network interface information."""
    click.echo("Network Interface Information:")
    click.echo("="*50)
    
    interfaces = NetworkDiagnostics.get_network_interfaces()
    
    for key, value in interfaces.items():
        click.echo(f"{key}: {value}")
    
    local_ip = NetworkDiagnostics.get_local_ip()
    click.echo(f"\nLocal IP: {local_ip}")


@cli.command()
@click.argument('url')
def test_url(url):
    """Test if a URL is reachable."""
    click.echo(f"Testing URL: {url}")
    
    result = test_stream_endpoint(url)
    
    if result['accessible']:
        click.echo(f"✅ URL is accessible")
        click.echo(f"   Content-Type: {result['content_type']}")
    else:
        click.echo(f"❌ URL is not accessible")
        if result['error']:
            click.echo(f"   Error: {result['error']}")


if __name__ == '__main__':
    cli()
