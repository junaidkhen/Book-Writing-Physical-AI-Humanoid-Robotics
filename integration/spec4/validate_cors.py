#!/usr/bin/env python3
"""
Script to validate CORS headers for cross-origin requests from GitHub Pages domain
"""
import requests
import sys
import json
from urllib.parse import urlparse

def validate_cors_headers(api_base_url, github_pages_domain):
    """
    Validate CORS headers by making a preflight request
    """
    print(f"Validating CORS headers for {api_base_url} with origin {github_pages_domain}")

    try:
        # Make a preflight OPTIONS request to simulate CORS
        headers = {
            'Origin': github_pages_domain,
            'Access-Control-Request-Method': 'POST',
            'Access-Control-Request-Headers': 'Content-Type',
        }

        # Test the /ask endpoint
        response = requests.options(f"{api_base_url}/ask", headers=headers)

        print(f"Status Code: {response.status_code}")

        # Check CORS headers
        cors_headers = {
            'Access-Control-Allow-Origin': response.headers.get('Access-Control-Allow-Origin'),
            'Access-Control-Allow-Methods': response.headers.get('Access-Control-Allow-Methods'),
            'Access-Control-Allow-Headers': response.headers.get('Access-Control-Allow-Headers'),
            'Access-Control-Allow-Credentials': response.headers.get('Access-Control-Allow-Credentials'),
        }

        print("CORS Headers received:")
        for header, value in cors_headers.items():
            print(f"  {header}: {value}")

        # Validate the headers
        success = True

        # Check if our GitHub Pages domain is allowed
        allowed_origin = cors_headers['Access-Control-Allow-Origin']
        if allowed_origin == github_pages_domain or allowed_origin == "*" or (
            isinstance(allowed_origin, str) and github_pages_domain in allowed_origin
        ):
            print("✅ GitHub Pages domain is allowed in CORS")
        else:
            print(f"❌ GitHub Pages domain {github_pages_domain} is not allowed in CORS: {allowed_origin}")
            success = False

        # Check allowed methods
        allowed_methods = cors_headers['Access-Control-Allow-Methods']
        if allowed_methods and 'POST' in allowed_methods:
            print("✅ POST method is allowed in CORS")
        else:
            print("❌ POST method is not allowed in CORS")
            success = False

        # Check allowed headers
        allowed_headers = cors_headers['Access-Control-Allow-Headers']
        if allowed_headers and 'Content-Type' in allowed_headers:
            print("✅ Content-Type header is allowed in CORS")
        else:
            print("❌ Content-Type header is not allowed in CORS")
            success = False

        if success:
            print("\n✅ CORS validation PASSED")
            return True
        else:
            print("\n❌ CORS validation FAILED")
            return False

    except requests.exceptions.RequestException as e:
        print(f"❌ Error making request: {e}")
        return False
    except Exception as e:
        print(f"❌ Error validating CORS: {e}")
        return False

def main():
    # Default values - these would be configured based on your setup
    api_base_url = "http://localhost:8000"  # Replace with your actual API URL
    github_pages_domain = "https://your-username.github.io"  # Replace with your GitHub Pages domain

    print("CORS Validation Script")
    print("=" * 50)

    success = validate_cors_headers(api_base_url, github_pages_domain)

    if success:
        print("\nCORS validation completed successfully!")
        sys.exit(0)
    else:
        print("\nCORS validation failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()