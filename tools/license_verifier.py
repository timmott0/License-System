# Standard library imports for argument parsing and JSON handling
import argparse
import json
from pathlib import Path
# Custom utility imports for license verification and host identification
from utils.validation import LicenseVerifier
from utils.host_identifier import HostIdentifier

def main():
    """
    Main function to verify software licenses and display host information.
    Handles command-line arguments and outputs verification results.
    """
    # Set up command line argument parser with description
    parser = argparse.ArgumentParser(description='License Verification Tool')
    # Required argument for the license file path
    parser.add_argument('license_file', help='Path to the license file')
    # Optional argument for custom public key location
    parser.add_argument('--public-key', default='config/rsa_keys/public_key.pem',
                      help='Path to the public key file')
    # Optional flag to display host information
    parser.add_argument('--show-host-info', action='store_true',
                      help='Show current host information')
    
    args = parser.parse_args()
    
    # If requested, collect and display host information
    if args.show_host_info:
        host_info = HostIdentifier.get_host_identifiers()
        print("\nCurrent Host Information:")
        print(json.dumps(host_info, indent=2))
        print("\n")
    
    # Verify the license file using the provided public key
    valid, message, license_data = LicenseVerifier.verify_license_file(
        args.license_file,
        args.public_key
    )
    
    # Display verification results
    print(f"License Status: {'Valid' if valid else 'Invalid'}")
    print(f"Message: {message}")
    
    # If license data was successfully extracted, display it
    if license_data:
        print("\nLicense Details:")
        print(json.dumps(license_data, indent=2))

# Standard Python idiom to ensure main() only runs if script is executed directly
if __name__ == "__main__":
    main()
