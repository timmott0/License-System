import logging
from pathlib import Path
from typing import Dict, List
import json
from datetime import datetime

class KeyHealthChecker:
    def __init__(self, install_path: Path):
        self.install_path = install_path
        self.logger = logging.getLogger(__name__)
        
    def run_health_check(self) -> Dict:
        """Run a comprehensive health check on the license system"""
        results = {
            'timestamp': datetime.now().isoformat(),
            'status': 'pass',
            'checks': []
        }
        
        # Check directory structure
        dir_check = self.check_directories()
        results['checks'].append(dir_check)
        
        # Check key files
        key_check = self.check_keys()
        results['checks'].append(key_check)
        
        # Check permissions
        perm_check = self.check_permissions()
        results['checks'].append(perm_check)
        
        # Update overall status
        if any(check['status'] == 'fail' for check in results['checks']):
            results['status'] = 'fail'
        elif any(check['status'] == 'warning' for check in results['checks']):
            results['status'] = 'warning'
            
        return results
        
    def check_directories(self) -> Dict:
        """Check if all required directories exist and are accessible"""
        required_dirs = [
            'config/keys',
            'licenses',
            'logs'
        ]
        
        missing_dirs = []
        for dir_path in required_dirs:
            full_path = self.install_path / dir_path
            if not full_path.exists():
                missing_dirs.append(dir_path)
                
        return {
            'name': 'Directory Structure Check',
            'status': 'fail' if missing_dirs else 'pass',
            'details': {
                'missing_directories': missing_dirs
            }
        }
        
    def check_keys(self) -> Dict:
        """Check key files for validity and expiration"""
        key_dir = self.install_path / 'config/keys'
        issues = []
        
        if not key_dir.exists():
            return {
                'name': 'Key Files Check',
                'status': 'fail',
                'details': {'error': 'Key directory not found'}
            }
            
        public_key = key_dir / 'public_key.pem'
        if not public_key.exists():
            issues.append('Public key not found')
            
        # Add more key-specific checks here
        
        return {
            'name': 'Key Files Check',
            'status': 'fail' if issues else 'pass',
            'details': {'issues': issues}
        }
        
    def check_permissions(self) -> Dict:
        """Check file and directory permissions"""
        issues = []
        
        # Check key directory permissions
        key_dir = self.install_path / 'config/keys'
        if key_dir.exists():
            try:
                # Try to create a test file
                test_file = key_dir / '.test'
                test_file.touch()
                test_file.unlink()
            except Exception as e:
                issues.append(f'Key directory not writable: {e}')
                
        return {
            'name': 'Permissions Check',
            'status': 'fail' if issues else 'pass',
            'details': {'issues': issues}
        }

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='License System Health Check')
    parser.add_argument('--install-path', required=True, help='Installation path to check')
    parser.add_argument('--output', help='Output file for results (JSON)')
    
    args = parser.parse_args()
    
    checker = KeyHealthChecker(Path(args.install_path))
    results = checker.run_health_check()
    
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(results, f, indent=2)
    else:
        print(json.dumps(results, indent=2))

if __name__ == "__main__":
    main()
