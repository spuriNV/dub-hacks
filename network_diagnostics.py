#!/usr/bin/env python3
"""
Network Diagnostics Module
Runs real-time network tests to gather actual performance data
"""

import subprocess
import re
import time
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class NetworkDiagnostics:
    """Run network diagnostics and analysis"""

    def __init__(self):
        self.speedtest_available = self._check_speedtest()

    def _check_speedtest(self) -> bool:
        """Check if speedtest-cli is available"""
        try:
            result = subprocess.run(
                ['speedtest-cli', '--version'],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0
        except:
            return False

    def run_ping_test(self, host='8.8.8.8', count=5) -> Dict[str, Any]:
        """
        Run ping test to measure latency and packet loss

        Returns:
            dict with avg_latency, min_latency, max_latency, packet_loss
        """
        try:
            result = subprocess.run(
                ['ping', '-c', str(count), host],
                capture_output=True,
                text=True,
                timeout=count + 5
            )

            if result.returncode == 0:
                output = result.stdout

                # Parse average latency
                avg_match = re.search(r'rtt min/avg/max/mdev = ([\d.]+)/([\d.]+)/([\d.]+)/([\d.]+)', output)
                if avg_match:
                    return {
                        'success': True,
                        'min_latency': float(avg_match.group(1)),
                        'avg_latency': float(avg_match.group(2)),
                        'max_latency': float(avg_match.group(3)),
                        'mdev': float(avg_match.group(4)),
                        'packet_loss': 0
                    }

                # Check for packet loss
                loss_match = re.search(r'(\d+)% packet loss', output)
                if loss_match:
                    packet_loss = int(loss_match.group(1))
                    return {
                        'success': True,
                        'avg_latency': 0,
                        'min_latency': 0,
                        'max_latency': 0,
                        'mdev': 0,
                        'packet_loss': packet_loss
                    }

            return {
                'success': False,
                'error': 'Ping failed',
                'packet_loss': 100
            }

        except Exception as e:
            logger.error(f"Ping test error: {e}")
            return {
                'success': False,
                'error': str(e),
                'packet_loss': 100
            }

    def test_dns_resolution(self, domains=None) -> Dict[str, Any]:
        """
        Test DNS resolution for common domains

        Returns:
            dict with success rate and avg resolution time
        """
        if domains is None:
            domains = ['google.com', 'cloudflare.com', 'github.com']

        results = {
            'total': len(domains),
            'successful': 0,
            'failed': 0,
            'avg_time': 0,
            'details': []
        }

        total_time = 0

        for domain in domains:
            start_time = time.time()
            try:
                import socket
                socket.gethostbyname(domain)
                resolution_time = (time.time() - start_time) * 1000  # Convert to ms

                results['successful'] += 1
                total_time += resolution_time
                results['details'].append({
                    'domain': domain,
                    'success': True,
                    'time_ms': resolution_time
                })

            except Exception as e:
                results['failed'] += 1
                results['details'].append({
                    'domain': domain,
                    'success': False,
                    'error': str(e)
                })

        if results['successful'] > 0:
            results['avg_time'] = total_time / results['successful']

        results['success_rate'] = (results['successful'] / results['total']) * 100

        return results

    def analyze_wifi_quality(self, current_network_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze WiFi quality using live tests

        Args:
            current_network_data: Current network data from get_network_data()

        Returns:
            Comprehensive analysis with quality score and recommendations
        """
        analysis = {
            'timestamp': time.time(),
            'quality_score': 0,
            'overall_status': 'unknown',
            'issues': [],
            'recommendations': []
        }

        # Run ping test
        logger.info("🔍 Running ping test...")
        ping_results = self.run_ping_test()
        analysis['ping_test'] = ping_results

        # Run DNS test
        logger.info("🔍 Running DNS test...")
        dns_results = self.test_dns_resolution()
        analysis['dns_test'] = dns_results

        # Calculate quality scores
        signal_score = 0
        latency_score = 0
        reliability_score = 0
        dns_score = 0

        # WiFi Signal Score (30 points max)
        wifi = current_network_data.get('wifi', {})
        signal_strength = wifi.get('signal_strength', 'unknown')

        if signal_strength != 'unknown':
            try:
                signal_dbm = int(signal_strength)
                analysis['signal_strength_dbm'] = signal_dbm

                if signal_dbm >= -30:
                    signal_score = 30
                    analysis['signal_quality'] = 'excellent'
                elif signal_dbm >= -50:
                    signal_score = 25
                    analysis['signal_quality'] = 'good'
                elif signal_dbm >= -70:
                    signal_score = 15
                    analysis['signal_quality'] = 'fair'
                else:
                    signal_score = 5
                    analysis['signal_quality'] = 'poor'

                if signal_dbm < -70:
                    analysis['issues'].append('Weak WiFi signal detected')
                    analysis['recommendations'].append('Move closer to router or use WiFi extender')
            except:
                pass

        # Latency Score (30 points max)
        if ping_results.get('success'):
            avg_latency = ping_results.get('avg_latency', 999)

            if avg_latency < 20:
                latency_score = 30
                analysis['latency_quality'] = 'excellent'
            elif avg_latency < 50:
                latency_score = 25
                analysis['latency_quality'] = 'good'
            elif avg_latency < 100:
                latency_score = 15
                analysis['latency_quality'] = 'fair'
            else:
                latency_score = 5
                analysis['latency_quality'] = 'poor'

            if avg_latency > 100:
                analysis['issues'].append('High latency detected')
                analysis['recommendations'].append('Check for network congestion or try restarting router')

        # Reliability Score (20 points max)
        packet_loss = ping_results.get('packet_loss', 100)

        if packet_loss == 0:
            reliability_score = 20
            analysis['reliability'] = 'excellent'
        elif packet_loss < 5:
            reliability_score = 15
            analysis['reliability'] = 'good'
        elif packet_loss < 10:
            reliability_score = 10
            analysis['reliability'] = 'fair'
        else:
            reliability_score = 5
            analysis['reliability'] = 'poor'

        if packet_loss > 5:
            analysis['issues'].append(f'Packet loss detected ({packet_loss}%)')
            analysis['recommendations'].append('Check WiFi interference or router stability')

        # DNS Score (20 points max)
        dns_success_rate = dns_results.get('success_rate', 0)

        if dns_success_rate == 100:
            dns_score = 20
            analysis['dns_quality'] = 'excellent'
        elif dns_success_rate >= 66:
            dns_score = 15
            analysis['dns_quality'] = 'good'
        elif dns_success_rate >= 33:
            dns_score = 10
            analysis['dns_quality'] = 'fair'
        else:
            dns_score = 5
            analysis['dns_quality'] = 'poor'

        if dns_success_rate < 100:
            analysis['issues'].append('DNS resolution issues detected')
            analysis['recommendations'].append('Try using alternative DNS (8.8.8.8 or 1.1.1.1)')

        # Calculate total quality score
        analysis['quality_score'] = signal_score + latency_score + reliability_score + dns_score

        # Overall assessment
        if analysis['quality_score'] >= 80:
            analysis['overall_status'] = 'excellent'
        elif analysis['quality_score'] >= 60:
            analysis['overall_status'] = 'good'
        elif analysis['quality_score'] >= 40:
            analysis['overall_status'] = 'fair'
        else:
            analysis['overall_status'] = 'poor'

        return analysis


# Singleton instance
_diagnostics_instance = None

def get_diagnostics() -> NetworkDiagnostics:
    """Get singleton instance of NetworkDiagnostics"""
    global _diagnostics_instance
    if _diagnostics_instance is None:
        _diagnostics_instance = NetworkDiagnostics()
    return _diagnostics_instance
