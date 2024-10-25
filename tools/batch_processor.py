# Standard library imports for file handling and concurrent processing
import argparse
import csv
import json
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict
from concurrent.futures import ThreadPoolExecutor, as_completed

# Custom module imports for license generation and encryption
from core.license_generator import LicenseGenerator
from encryption.key_management import KeyManager
from encryption.license_signing import LicenseSigner

# Set up logging for this module
logger = logging.getLogger(__name__)

class BatchLicenseProcessor:
    """
    Handles bulk processing of license requests from CSV files.
    Manages concurrent license generation with thread pooling.
    """
    def __init__(self, config_path: Path, output_dir: Path):
        # Initialize paths and core components
        self.config_path = config_path
        self.output_dir = output_dir
        # Set up encryption and signing infrastructure
        self.key_manager = KeyManager(Path('config/rsa_keys'))
        self.signer = LicenseSigner(self.key_manager)
        self.generator = LicenseGenerator(self.signer)

    def process_csv(self, csv_path: Path, max_workers: int = 4) -> Dict[str, str]:
        """
        Process multiple license requests from a CSV file concurrently
        
        Args:
            csv_path: Path to the input CSV file
            max_workers: Maximum number of concurrent threads
        
        Returns:
            Dictionary mapping customer IDs to processing results
        """
        results = {}
        
        # Read all tasks from CSV file
        with open(csv_path, 'r') as f:
            reader = csv.DictReader(f)
            tasks = list(reader)

        # Process licenses concurrently using thread pool
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Create future objects for each license task
            future_to_task = {
                executor.submit(self.process_single_license, task): task
                for task in tasks
            }

            # Process completed tasks as they finish
            for future in as_completed(future_to_task):
                task = future_to_task[future]
                try:
                    customer_id = task['customer_id']
                    result = future.result()
                    results[customer_id] = result
                except Exception as e:
                    # Log any errors and store them in results
                    logger.error(f"Error processing license for {task.get('customer_id')}: {e}")
                    results[task.get('customer_id')] = f"Error: {str(e)}"

        return results

    def process_single_license(self, data: Dict) -> str:
        """
        Generate a single license file from the provided data
        
        Args:
            data: Dictionary containing license request details
        
        Returns:
            Success message with output path or error message
        """
        try:
            # Extract customer information
            customer_info = {
                'name': data['customer_name'],
                'id': data['customer_id'],
                'email': data['email']
            }

            # Calculate license validity periods
            validity_days = int(data.get('validity_days', 365))  # Default 1 year
            maintenance_days = int(data.get('maintenance_days', 90))  # Default 90 days
            
            expiration_date = datetime.now() + timedelta(days=validity_days)
            maintenance_date = datetime.now() + timedelta(days=maintenance_days)

            # Prepare license configuration
            license_info = {
                'type': data.get('license_type', 'node_locked'),
                'expiration_date': expiration_date,
                'maintenance_date': maintenance_date,
                'platforms': data.get('platforms', '').split(',')
            }

            # Parse product information from JSON string
            products = json.loads(data.get('products', '[]'))

            # Generate the license using core generator
            license_data = self.generator.generate_license(
                customer_info,
                license_info,
                products,
                {}  # Empty host info - will be collected during activation
            )

            # Save license to output directory
            output_path = self.output_dir / f"{data['customer_id']}.lic"
            self.generator.save_license(license_data, output_path)

            return f"Success: License saved to {output_path}"

        except Exception as e:
            raise Exception(f"Failed to process license: {str(e)}")

def main():
    """
    Command-line interface for batch license processing
    Handles argument parsing and high-level process flow
    """
    # Set up command line argument parser
    parser = argparse.ArgumentParser(description='Batch License Processor')
    parser.add_argument('csv_file', help='Path to CSV file containing license requests')
    parser.add_argument('--output-dir', default='licenses/batch',
                      help='Output directory for generated licenses')
    parser.add_argument('--config', default='config/settings.json',
                      help='Path to configuration file')
    parser.add_argument('--workers', type=int, default=4,
                      help='Number of worker threads')
    parser.add_argument('--log-file', default='logs/batch_processor.log',
                      help='Log file path')

    args = parser.parse_args()

    # Configure logging to both file and console
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(args.log_file),
            logging.StreamHandler()
        ]
    )

    # Ensure output directory exists
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Initialize processor and generate licenses
    processor = BatchLicenseProcessor(Path(args.config), output_dir)
    results = processor.process_csv(Path(args.csv_file), args.workers)

    # Save processing results to JSON file
    results_path = output_dir / 'processing_results.json'
    with open(results_path, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"Processing complete. Results saved to {results_path}")

# Entry point for script execution
if __name__ == "__main__":
    main()
