# Standard library imports for CLI and data handling
import argparse
import json
from pathlib import Path
from datetime import datetime, timedelta

# Custom module imports for core functionality
from core.template_manager import TemplateManager
from core.revocation_manager import RevocationManager
from core.usage_tracker import UsageTracker
import logging
import yaml

def setup_logging(log_file: str):
    """
    Configure logging to both file and console output
    
    Args:
        log_file: Path to the log file where messages will be stored
    """
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),    # Write logs to file
            logging.StreamHandler()           # Also output to console
        ]
    )

def handle_template_commands(args, template_manager):
    """
    Process all template-related commands (create, list, delete)
    
    Args:
        args: Parsed command line arguments
        template_manager: Instance of TemplateManager for template operations
    """
    if args.template_action == "create":
        # Load template definition from YAML file
        with open(args.template_file, 'r') as f:
            template_data = yaml.safe_load(f)
        template = template_manager.create_template(template_data)
        print(f"Created template: {template.name}")
        
    elif args.template_action == "list":
        # Display all available templates
        templates = template_manager.list_templates()
        print("\nAvailable Templates:")
        for template in templates:
            print(f"- {template}")
            
    elif args.template_action == "delete":
        # Remove specified template
        template_manager.delete_template(args.template_name)
        print(f"Deleted template: {args.template_name}")

def handle_revocation_commands(args, revocation_manager):
    """
    Process all revocation-related commands (revoke, check, publish)
    
    Args:
        args: Parsed command line arguments
        revocation_manager: Instance of RevocationManager for license revocation
    """
    if args.revocation_action == "revoke":
        # Parse optional metadata and revoke the license
        metadata = json.loads(args.metadata) if args.metadata else {}
        revocation_manager.revoke_license(
            args.license_id,
            args.customer_id,
            args.reason,
            metadata
        )
        print(f"Revoked license: {args.license_id}")
        
    elif args.revocation_action == "check":
        # Check if a license is revoked and show details
        is_revoked = revocation_manager.is_revoked(args.license_id)
        if is_revoked:
            info = revocation_manager.get_revocation_info(args.license_id)
            print(f"\nLicense {args.license_id} is revoked:")
            print(json.dumps(info, indent=2))
        else:
            print(f"\nLicense {args.license_id} is valid")
            
    elif args.revocation_action == "publish":
        # Generate and display the revocation list
        revocation_list = revocation_manager.publish_revocation_list()
        print("\nPublished Revocation List:")
        print(revocation_list)

def handle_usage_commands(args, usage_tracker):
    """
    Process usage-related commands (currently only reporting)
    
    Args:
        args: Parsed command line arguments
        usage_tracker: Instance of UsageTracker for monitoring license usage
    """
    if args.usage_action == "report":
        # Calculate date range and generate usage report
        start_date = datetime.now() - timedelta(days=args.days) if args.days else None
        report = usage_tracker.get_usage_report(args.license_id, start_date)
        print("\nUsage Report:")
        print(json.dumps(report, indent=2))

def main():
    """
    Main entry point for the license management CLI tool
    Sets up argument parsing and handles command routing
    """
    # Create main parser with subcommands
    parser = argparse.ArgumentParser(description='License Management Tool')
    subparsers = parser.add_subparsers(dest='command')
    
    # Template management command group
    template_parser = subparsers.add_parser('template')
    template_parser.add_argument('template_action', choices=['create', 'list', 'delete'])
    template_parser.add_argument('--template-file', help='Template definition file')
    template_parser.add_argument('--template-name', help='Template name')
    
    # Revocation management command group
    revoke_parser = subparsers.add_parser('revocation')
    revoke_parser.add_argument('revocation_action', choices=['revoke', 'check', 'publish'])
    revoke_parser.add_argument('--license-id', help='License ID')
    revoke_parser.add_argument('--customer-id', help='Customer ID')
    revoke_parser.add_argument('--reason', help='Revocation reason')
    revoke_parser.add_argument('--metadata', help='Additional metadata (JSON)')
    
    # Usage tracking command group
    usage_parser = subparsers.add_parser('usage')
    usage_parser.add_argument('usage_action', choices=['report'])
    usage_parser.add_argument('--license-id', help='License ID')
    usage_parser.add_argument('--days', type=int, help='Number of days to report')
    
    # Parse arguments
    args = parser.parse_args()
    
    # Initialize core components with appropriate paths
    template_manager = TemplateManager(Path('config/templates'))
    revocation_manager = RevocationManager(Path('data/revocation.db'))
    usage_tracker = UsageTracker(Path('data/usage.db'))
    
    # Route to appropriate handler based on command
    if args.command == 'template':
        handle_template_commands(args, template_manager)
    elif args.command == 'revocation':
        handle_revocation_commands(args, revocation_manager)
    elif args.command == 'usage':
        handle_usage_commands(args, usage_tracker)

# Script entry point
if __name__ == '__main__':
    main()
