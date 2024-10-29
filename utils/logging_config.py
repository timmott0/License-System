import logging
import logging.handlers
from pathlib import Path
from datetime import datetime

def setup_logging(log_dir: Path = Path("logs"), 
                 log_level: int = logging.INFO) -> None:
    """Configure application logging
    
    Args:
        log_dir: Directory for log files
        log_level: Logging level (default: INFO)
    """
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # Create formatters
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_formatter = logging.Formatter(
        '%(levelname)s: %(message)s'
    )
    
    # File handler with rotation
    log_file = log_dir / f"app_{datetime.now():%Y%m%d}.log"
    file_handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    file_handler.setFormatter(file_formatter)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(console_formatter)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)
    
    # Log startup information
    logging.info("Logging initialized")
    logging.info(f"Log file: {log_file}") 