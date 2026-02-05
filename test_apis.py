#!/usr/bin/env python3
"""Test script to verify all API endpoints are working correctly"""

import requests
import json
from typing import Dict, Any

BASE_URL = "http://localhost:8000/api/v1"

def test_auth():
    """Test authentication endpoints"""
    print("=" * 50)
    print("Testing Authentication Endpoints")
    print("=" * 50)
    
    # Test login
    login_data = {
        "username": "testuser",
        "password": "test123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
        print(f"✓ Login: {response.status_code}")
        token_data = response.json()
        token = token_data.get("access_token")
        print(f"  Token: {token[:20]}...")
        return token
    except Exception as e:
        print(f"✗ Login failed: {e}")
        return None

def test_goals(token: str):
    """Test goal endpoints"""
    print("\n" + "=" * 50)
    print("Testing Goal Endpoints")
    print("=" * 50)
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # List goals
    try:
        response = requests.get(f"{BASE_URL}/goals", headers=headers)
        print(f"✓ List Goals: {response.status_code}")
        goals = response.json()
        print(f"  Found {len(goals)} goals")
        if goals:
            return goals[0]["id"]
    except Exception as e:
        print(f"✗ List Goals failed: {e}")
        return None

def test_tasks(token: str):
    """Test task endpoints"""
    print("\n" + "=" * 50)
    print("Testing Task Endpoints")
    print("=" * 50)
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # List tasks
    try:
        response = requests.get(f"{BASE_URL}/tasks", headers=headers)
        print(f"✓ List Tasks: {response.status_code}")
        tasks = response.json()
        print(f"  Found {len(tasks)} tasks")
        if tasks:
            return tasks[0]["id"]
    except Exception as e:
        print(f"✗ List Tasks failed: {e}")
        return None

def test_achievements(token: str):
    """Test achievement endpoints"""
    print("\n" + "=" * 50)
    print("Testing Achievement Endpoints")
    print("=" * 50)
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # List achievements
    try:
        response = requests.get(f"{BASE_URL}/achievements", headers=headers)
        print(f"✓ List Achievements: {response.status_code}")
        achievements = response.json()
        print(f"  Found {len(achievements)} achievements")
    except Exception as e:
        print(f"✗ List Achievements failed: {e}")
    
    # Get achievement stats
    try:
        response = requests.get(f"{BASE_URL}/achievements/stats", headers=headers)
        print(f"✓ Achievement Stats: {response.status_code}")
        stats = response.json()
        print(f"  Total Points: {stats.get('total_points')}")
        print(f"  Unlocked: {stats.get('total_unlocked')}")
    except Exception as e:
        print(f"✗ Achievement Stats failed: {e}")

def main():
    print("Testing High-Performance API\n")
    
    # Test authentication
    token = test_auth()
    if not token:
        print("\nCannot continue without authentication token")
        return
    
    # Test other endpoints
    goal_id = test_goals(token)
    task_id = test_tasks(token)
    test_achievements(token)
    
    print("\n" + "=" * 50)
    print("Testing Complete!")
    print("=" * 50)
    print(f"\nFrontend: http://localhost:5173")
    print(f"API Docs: http://localhost:8000/docs")
    print(f"ReDoc: http://localhost:8000/redoc")

if __name__ == "__main__":
    main()
