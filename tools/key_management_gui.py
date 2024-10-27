import sys
from pathlib import Path

# Add the project root directory to Python path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import json
import shutil
import logging
from typing import Dict, Optional
from core.key_manager import KeyManager

class KeyManagementDashboard:
    def __init__(self, root):
        self.root = root
        self.root.title("License Key Management")
        
        # Initialize key manager
        self.key_manager = KeyManager(
            private_key_path='config/keys/private_key.pem',
            public_key_path='config/keys/public_key.pem'
        )
        
        # Load application config
        self.config = self.load_config()
        self.key_paths = self.config.get('paths', {}).get('keys', {})
        
        if not self.key_paths:
            self.key_paths = {
                'private_key_path': 'config/keys/private_key.pem',
                'public_key_path': 'config/keys/public_key.pem'
            }
        
        self.setup_ui()
        
    def load_config(self):
        """Load the application configuration"""
        try:
            config_path = Path('config/config.json')
            if config_path.exists():
                with open(config_path) as f:
                    return json.load(f)
        except Exception as e:
            logging.error(f"Failed to load config: {e}")
        return {}
    
    def setup_ui(self):
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Key Information Section
        ttk.Label(main_frame, text="Current Key Information", style='Header.TLabel').grid(row=0, column=0, pady=10)
        
        self.key_info = ttk.Treeview(main_frame, columns=('Location', 'Status'), show='headings')
        self.key_info.heading('Location', text='Key Location')
        self.key_info.heading('Status', text='Status')
        self.key_info.grid(row=1, column=0, pady=5, sticky=(tk.W, tk.E))
        
        # Actions Section
        actions_frame = ttk.LabelFrame(main_frame, text="Actions", padding="10")
        actions_frame.grid(row=2, column=0, pady=10, sticky=(tk.W, tk.E))
        
        ttk.Button(actions_frame, text="Import New Key", command=self.import_key).grid(row=0, column=0, padx=5)
        ttk.Button(actions_frame, text="Validate Keys", command=self.validate_keys).grid(row=0, column=1, padx=5)
        ttk.Button(actions_frame, text="Backup Keys", command=self.backup_keys).grid(row=0, column=2, padx=5)
        
        # Status Section
        self.status_var = tk.StringVar()
        ttk.Label(main_frame, textvariable=self.status_var).grid(row=3, column=0, pady=5)
        
        # Load initial key information
        self.refresh_key_info()
        
    def refresh_key_info(self):
        """Update the key information display"""
        self.key_info.delete(*self.key_info.get_children())
        
        # Scan for keys
        keys = self.scan_for_keys()
        for key_type, info in keys.items():
            if info['path']:
                status = "Valid" if info['valid'] else "Invalid"
                self.key_info.insert('', 'end', values=(str(info['path']), status))
                
    def scan_for_keys(self) -> Dict[str, Dict]:
        """Scan for license keys and validate them"""
        common_locations = [
            Path('config/keys'),
            Path.home() / '.keys',
            Path('C:/ProgramData/YourApp/keys') if sys.platform == 'win32' else Path('/etc/yourapp/keys'),
        ]
        
        keys = {
            'public_key': {'path': None, 'valid': False},
            'private_key': {'path': None, 'valid': False}
        }
        
        for location in common_locations:
            if location.exists():
                for key_file in location.glob('*.pem'):
                    is_valid = self.validate_key(key_file)
                    key_type = 'public_key' if 'public' in key_file.name.lower() else 'private_key'
                    if is_valid and not keys[key_type]['valid']:  # Only update if we haven't found a valid key yet
                        keys[key_type] = {'path': key_file, 'valid': True}
        
        return keys
        
    def validate_key(self, key_path: Path) -> bool:
        """Validate a key file using KeyManager"""
        return self.key_manager.validate_key(key_path)
            
    def import_key(self):
        """Import a new key file"""
        file_path = filedialog.askopenfilename(
            title="Select Key File",
            filetypes=[("PEM files", "*.pem"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                # Determine if it's a public or private key
                is_public = 'public' in Path(file_path).name.lower()
                key_type = 'public_key' if is_public else 'private_key'
                
                # Create keys directory if it doesn't exist
                target_dir = Path('config/keys')
                target_dir.mkdir(parents=True, exist_ok=True)
                
                # Copy key to appropriate location
                target_path = target_dir / f"{'public' if is_public else 'private'}_key.pem"
                shutil.copy2(file_path, target_path)
                
                # Update config
                self.key_paths[key_type] = str(target_path)
                self.save_config()
                
                self.status_var.set(f"Successfully imported {key_type}")
                self.refresh_key_info()
                
            except Exception as e:
                messagebox.showerror("Import Error", f"Failed to import key: {e}")
    
    def save_config(self):
        """Save the updated configuration"""
        try:
            config_path = Path('config/config.json')
            config_path.parent.mkdir(parents=True, exist_ok=True)
            
            config = self.load_config()
            config.setdefault('paths', {})['keys'] = self.key_paths
            
            with open(config_path, 'w') as f:
                json.dump(config, f, indent=4)
                
        except Exception as e:
            logging.error(f"Failed to save config: {e}")
    
    def validate_keys(self):
        """Validate all known keys"""
        keys = self.scan_for_keys()
        valid_count = sum(1 for k in keys.values() if k['valid'])
        
        messagebox.showinfo(
            "Validation Results",
            f"Found {valid_count} valid keys out of {len(keys)} total keys."
        )
        
    def backup_keys(self):
        """Backup all keys to a user-specified location"""
        backup_dir = filedialog.askdirectory(title="Select Backup Location")
        if backup_dir:
            try:
                backup_path = Path(backup_dir) / 'key_backup'
                backup_path.mkdir(exist_ok=True)
                
                keys = self.scan_for_keys()
                backed_up = 0
                
                for key_info in keys.values():
                    if key_info['path']:
                        shutil.copy2(key_info['path'], backup_path)
                        backed_up += 1
                
                self.status_var.set(f"Successfully backed up {backed_up} keys to {backup_path}")
            except Exception as e:
                messagebox.showerror("Backup Error", f"Failed to backup keys: {e}")

def main():
    root = tk.Tk()
    app = KeyManagementDashboard(root)
    root.mainloop()

if __name__ == "__main__":
    main()
