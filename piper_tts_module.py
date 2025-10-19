#!/usr/bin/env python3
"""
Piper TTS Module for AI Brain
Handles text-to-speech conversion using Piper
"""

import os
import sys
import subprocess
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class PiperTTS:
    """Piper Text-to-Speech handler"""

    def __init__(self, model_path=None, piper_command='piper'):
        """
        Initialize Piper TTS

        Args:
            model_path: Path to Piper ONNX model (optional, will use default if not provided)
            piper_command: Command to run piper (default: 'piper')
        """
        self.piper_command = piper_command

        # Default model location
        if model_path is None:
            # Try to find model in common locations
            possible_paths = [
                Path.home() / 'piper-tts-workflow' / 'models' / 'en_US-lessac-medium.onnx',
                Path('/usr/share/piper/models/en_US-lessac-medium.onnx'),
                Path.home() / '.local/share/piper/models/en_US-lessac-medium.onnx'
            ]

            for path in possible_paths:
                if path.exists():
                    self.model_path = path
                    logger.info(f"Using Piper model: {self.model_path}")
                    break
            else:
                logger.warning("No Piper model found in default locations")
                self.model_path = None
        else:
            self.model_path = Path(model_path)

        # Verify Piper is installed
        self.piper_available = self._check_piper_installation()

    def _check_piper_installation(self):
        """Check if Piper is installed and available"""
        try:
            result = subprocess.run(
                [self.piper_command, '--help'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                logger.info("Piper TTS is available")
                return True
            else:
                logger.warning("Piper command found but returned error")
                return False
        except FileNotFoundError:
            logger.warning("Piper TTS not found. Install with: pip install piper-tts")
            return False
        except Exception as e:
            logger.error(f"Error checking Piper installation: {e}")
            return False

    def text_to_speech(self, text, output_file, max_length=500):
        """
        Convert text to speech using Piper

        Args:
            text: Text to convert to speech
            output_file: Path to save output WAV file
            max_length: Maximum text length (truncate if longer for safety)

        Returns:
            Path to generated audio file, or None if failed
        """
        if not self.piper_available:
            logger.error("Piper TTS not available")
            return None

        if not self.model_path or not self.model_path.exists():
            logger.error(f"Piper model not found: {self.model_path}")
            return None

        # Truncate text if too long (for safety and better speech quality)
        if len(text) > max_length:
            text = text[:max_length] + "..."
            logger.info(f"Text truncated to {max_length} characters for TTS")

        # Remove markdown formatting for better speech
        text = self._clean_text_for_speech(text)

        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            # Run piper command
            cmd = [
                self.piper_command,
                '--model', str(self.model_path),
                '--output_file', str(output_path)
            ]

            # Pass text via stdin
            process = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            stdout, stderr = process.communicate(input=text, timeout=30)

            if process.returncode != 0:
                logger.error(f"Piper error: {stderr}")
                return None

            if output_path.exists():
                logger.info(f"Audio generated successfully: {output_path}")
                return str(output_path)
            else:
                logger.error("Audio file was not created")
                return None

        except subprocess.TimeoutExpired:
            logger.error("Piper TTS timeout")
            process.kill()
            return None
        except Exception as e:
            logger.error(f"Error during TTS conversion: {e}")
            return None

    def _clean_text_for_speech(self, text):
        """
        Clean text for better speech synthesis
        Remove markdown, emojis, and other formatting
        """
        import re

        # Remove markdown headers
        text = re.sub(r'#{1,6}\s+', '', text)

        # Remove markdown bold/italic
        text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)
        text = re.sub(r'\*(.+?)\*', r'\1', text)
        text = re.sub(r'__(.+?)__', r'\1', text)
        text = re.sub(r'_(.+?)_', r'\1', text)

        # Remove markdown links [text](url) -> text
        text = re.sub(r'\[(.+?)\]\(.+?\)', r'\1', text)

        # Remove emojis (basic removal)
        text = re.sub(r'[\U00010000-\U0010ffff]', '', text)
        text = re.sub(r'[\u2600-\u26FF\u2700-\u27BF]', '', text)

        # Remove bullet points and dashes at start of lines
        text = re.sub(r'^\s*[•\-\*]\s+', '', text, flags=re.MULTILINE)

        # Replace multiple newlines with single space
        text = re.sub(r'\n+', ' ', text)

        # Replace multiple spaces with single space
        text = re.sub(r'\s+', ' ', text)

        # Clean up
        text = text.strip()

        return text

    def get_status(self):
        """Get TTS system status"""
        return {
            'piper_available': self.piper_available,
            'model_path': str(self.model_path) if self.model_path else None,
            'model_exists': self.model_path.exists() if self.model_path else False
        }


# Singleton instance
_piper_instance = None


def get_piper_tts():
    """Get or create Piper TTS singleton instance"""
    global _piper_instance
    if _piper_instance is None:
        _piper_instance = PiperTTS()
    return _piper_instance


# Test function
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    print("Testing Piper TTS Module...")
    piper = PiperTTS()

    print(f"Status: {piper.get_status()}")

    if piper.piper_available:
        test_text = "Hello! This is a test of the Piper text to speech system. Your network is working well."
        output_file = "/tmp/piper_test.wav"

        result = piper.text_to_speech(test_text, output_file)

        if result:
            print(f"Success! Audio saved to: {result}")
        else:
            print("Failed to generate audio")
    else:
        print("Piper TTS is not available")
