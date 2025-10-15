"""
Environment variable validation
Ensures all required environment variables are set before application starts
"""
import os
import sys
import logging

logger = logging.getLogger(__name__)


class EnvironmentValidator:
    """Validates required environment variables"""
    
    # Required environment variables for production
    REQUIRED_PROD_VARS = [
        'SECRET_KEY',
        'JWT_SECRET_KEY',
    ]
    
    # Recommended environment variables
    RECOMMENDED_VARS = [
        'DATABASE_URL',
        'CORS_ORIGINS',
        'AI_API_URL',
        'AI_MODEL',
    ]
    
    # Optional environment variables with defaults
    OPTIONAL_VARS = {
        'LOG_LEVEL': 'INFO',
        'AI_TIMEOUT': '30',
        'RATELIMIT_STORAGE_URL': 'memory://',
    }
    
    @classmethod
    def validate(cls, environment='development'):
        """
        Validate environment variables based on environment
        
        Args:
            environment (str): The environment (development, production, testing)
            
        Returns:
            bool: True if validation passes, False otherwise
        """
        errors = []
        warnings = []
        
        # Check required variables for production
        if environment == 'production':
            for var in cls.REQUIRED_PROD_VARS:
                value = os.getenv(var)
                if not value:
                    errors.append(f"Required environment variable '{var}' is not set")
                elif var in ['SECRET_KEY', 'JWT_SECRET_KEY']:
                    # Check if using default/weak keys
                    if len(str(value)) < 32:
                        warnings.append(f"Environment variable '{var}' should be at least 32 characters long")
        
        # Check recommended variables
        for var in cls.RECOMMENDED_VARS:
            if not os.getenv(var):
                warnings.append(f"Recommended environment variable '{var}' is not set, using default")
        
        # Log results
        if errors:
            logger.error("Environment validation failed:")
            for error in errors:
                logger.error(f"  ❌ {error}")
            return False
        
        if warnings:
            logger.warning("Environment validation warnings:")
            for warning in warnings:
                logger.warning(f"  ⚠️  {warning}")
        
        logger.info("✅ Environment validation passed")
        return True
    
    @classmethod
    def validate_or_exit(cls, environment='development'):
        """
        Validate environment variables and exit if validation fails
        
        Args:
            environment (str): The environment (development, production, testing)
        """
        if not cls.validate(environment):
            logger.critical("Application cannot start due to environment validation errors")
            sys.exit(1)
    
    @classmethod
    def get_env_info(cls):
        """
        Get information about current environment configuration
        
        Returns:
            dict: Environment configuration information
        """
        info = {
            'required': {},
            'recommended': {},
            'optional': {}
        }
        
        for var in cls.REQUIRED_PROD_VARS:
            info['required'][var] = '✅ Set' if os.getenv(var) else '❌ Not set'
        
        for var in cls.RECOMMENDED_VARS:
            info['recommended'][var] = '✅ Set' if os.getenv(var) else '⚠️ Using default'
        
        for var, default in cls.OPTIONAL_VARS.items():
            value = os.getenv(var, default)
            info['optional'][var] = f'✅ {value}'
        
        return info


def validate_environment(environment='development'):
    """
    Convenience function to validate environment
    
    Args:
        environment (str): The environment to validate for
        
    Returns:
        bool: True if validation passes
    """
    return EnvironmentValidator.validate(environment)


def validate_environment_or_exit(environment='development'):
    """
    Convenience function to validate environment and exit on failure
    
    Args:
        environment (str): The environment to validate for
    """
    EnvironmentValidator.validate_or_exit(environment)

