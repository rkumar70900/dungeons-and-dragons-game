import logging

# Configure the logger
logging.basicConfig(
    filename='api.log',
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def log_success(endpoint_name, data):
    logger.info(f"Endpoint '{endpoint_name}' succeeded with data: {data}")

def log_failure(endpoint_name, error):
    logger.error(f"Endpoint '{endpoint_name}' failed with error: {error}")