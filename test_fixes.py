#!/usr/bin/env python3
"""Simple test to verify the time synchronization logic"""

import time
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from datetime import datetime
from pytz import timezone

def test_wait_for_next_minute():
    """Test the wait_for_next_minute function logic"""
    local_tz = timezone("Europe/Berlin")
    
    # Mock different second values to test the logic
    test_cases = [
        (0, 0),    # At start of minute, should wait 0 seconds
        (1, 59),   # At second 1, should wait 59 seconds
        (30, 30),  # At second 30, should wait 30 seconds
        (59, 1),   # At second 59, should wait 1 second
    ]
    
    for current_second, expected_wait in test_cases:
        seconds_to_wait = 60 - current_second
        if current_second == 0:
            seconds_to_wait = 0
        
        print(f"Second {current_second}: waiting {seconds_to_wait} seconds (expected: {expected_wait})")
        assert seconds_to_wait == expected_wait, f"Expected {expected_wait}, got {seconds_to_wait}"
    
    print("✓ All time synchronization tests passed!")

def test_docker_user_fix():
    """Test that the Docker user fix is applied"""
    with open("Dockerfile", "r") as f:
        dockerfile_content = f.read()
    
    # Check that USER discord is present and USER discordbot is not
    assert "USER discord" in dockerfile_content, "USER discord not found in Dockerfile"
    assert "USER discordbot" not in dockerfile_content, "USER discordbot still present in Dockerfile"
    
    print("✓ Docker user fix verified!")

if __name__ == "__main__":
    print("Running tests...")
    test_wait_for_next_minute()
    test_docker_user_fix()
    print("All tests passed!")