"""
Secrets Manager for ServiceNow Monitor

Securely retrieves API keys from 1Password or environment variables.
"""

import os
import subprocess
import logging
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SecretsManager:
    """Manages secure retrieval of API keys from 1Password or environment variables."""

    def __init__(self, use_1password: bool = True):
        """
        Initialize the secrets manager.

        Args:
            use_1password: Whether to try 1Password CLI first (default: True)
        """
        self.use_1password = use_1password
        self._check_1password_availability()

    def _check_1password_availability(self):
        """Check if 1Password CLI is available and user is signed in."""
        if not self.use_1password:
            return

        try:
            # Check if op CLI is installed
            result = subprocess.run(
                ['which', 'op'],
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode != 0:
                logger.warning("1Password CLI (op) not found. Falling back to environment variables.")
                self.use_1password = False
                return

            # Check if user is signed in
            result = subprocess.run(
                ['op', 'whoami'],
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode != 0:
                logger.warning("Not signed in to 1Password. Run: eval $(op signin)")
                logger.info("Falling back to environment variables.")
                self.use_1password = False
            else:
                logger.info(f"1Password CLI available. Signed in as: {result.stdout.strip()}")

        except Exception as e:
            logger.warning(f"Error checking 1Password availability: {e}")
            self.use_1password = False

    def get_secret(self,
                   secret_name: str,
                   env_var_name: str = None,
                   item_name: str = None,
                   vault: str = None,
                   field: str = None) -> str:
        """
        Get a secret from 1Password or environment variable.

        Args:
            secret_name: Descriptive name for logging
            env_var_name: Environment variable name to check
            item_name: 1Password item name (e.g., "Anthropic API Key")
            vault: 1Password vault name (optional, uses default if not specified)
            field: Field name in the 1Password item (default: tries common fields)

        Returns:
            The secret value or None if not found

        Examples:
            # Get from 1Password item "Anthropic API Key" in default vault
            api_key = manager.get_secret(
                secret_name="Claude API Key",
                env_var_name="ANTHROPIC_API_KEY",
                item_name="Anthropic API Key"
            )

            # Get from specific vault and field
            api_key = manager.get_secret(
                secret_name="News API Key",
                env_var_name="NEWS_API_KEY",
                item_name="NewsAPI",
                vault="Development",
                field="api_key"
            )
        """
        # Try 1Password first
        if self.use_1password and item_name:
            secret = self._get_from_1password(secret_name, item_name, vault, field)
            if secret:
                return secret

        # Fall back to environment variable
        if env_var_name:
            secret = os.environ.get(env_var_name)
            if secret:
                logger.info(f"{secret_name}: Retrieved from environment variable {env_var_name}")
                return secret

        logger.warning(f"{secret_name}: Not found in 1Password or environment variables")
        return None

    def _get_from_1password(self,
                           secret_name: str,
                           item_name: str,
                           vault: str = None,
                           field: str = None) -> str:
        """
        Retrieve a secret from 1Password using the CLI.

        Args:
            secret_name: Descriptive name for logging
            item_name: 1Password item name
            vault: Vault name (optional)
            field: Field name (optional, tries common fields if not specified)

        Returns:
            The secret value or None if not found
        """
        try:
            # Build the op command
            # Using 'op item get' for 1Password CLI 2.0+
            cmd = ['op', 'item', 'get', item_name, '--format', 'json']

            if vault:
                cmd.extend(['--vault', vault])

            # Execute command
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode != 0:
                logger.warning(f"{secret_name}: 1Password item '{item_name}' not found")
                logger.debug(f"Error: {result.stderr}")
                return None

            # Parse JSON response
            item_data = json.loads(result.stdout)

            # If specific field requested, look for it
            if field:
                for item_field in item_data.get('fields', []):
                    if item_field.get('label', '').lower() == field.lower() or \
                       item_field.get('id', '').lower() == field.lower():
                        value = item_field.get('value')
                        if value:
                            logger.info(f"{secret_name}: Retrieved from 1Password item '{item_name}'")
                            return value

                logger.warning(f"{secret_name}: Field '{field}' not found in 1Password item '{item_name}'")
                return None

            # Otherwise, try common field names
            common_fields = ['credential', 'password', 'api key', 'api_key', 'token', 'secret']

            for item_field in item_data.get('fields', []):
                label = item_field.get('label', '').lower()
                field_id = item_field.get('id', '').lower()

                if any(common in label or common in field_id for common in common_fields):
                    value = item_field.get('value')
                    if value:
                        logger.info(f"{secret_name}: Retrieved from 1Password item '{item_name}' field '{item_field.get('label')}'")
                        return value

            logger.warning(f"{secret_name}: Could not find API key field in 1Password item '{item_name}'")
            return None

        except subprocess.TimeoutExpired:
            logger.error(f"{secret_name}: 1Password CLI command timed out")
            return None
        except json.JSONDecodeError as e:
            logger.error(f"{secret_name}: Failed to parse 1Password response: {e}")
            return None
        except Exception as e:
            logger.error(f"{secret_name}: Error retrieving from 1Password: {e}")
            return None


def get_api_keys(use_1password: bool = True) -> dict:
    """
    Convenience function to get all required API keys.

    Args:
        use_1password: Whether to use 1Password CLI (default: True)

    Returns:
        Dictionary with API keys: {'anthropic': '...', 'newsapi': '...'}
    """
    manager = SecretsManager(use_1password=use_1password)

    api_keys = {
        'anthropic': manager.get_secret(
            secret_name="Claude API Key",
            env_var_name="ANTHROPIC_API_KEY",
            item_name="Anthropic API Key"  # Adjust to match your 1Password item name
        ),
        'newsapi': manager.get_secret(
            secret_name="NewsAPI Key",
            env_var_name="NEWS_API_KEY",
            item_name="NewsAPI"  # Adjust to match your 1Password item name
        )
    }

    return api_keys


if __name__ == "__main__":
    """Test the secrets manager."""
    print("Testing Secrets Manager...")
    print("=" * 60)

    manager = SecretsManager()

    # Test retrieving API keys
    print("\nTesting API key retrieval:")

    anthropic_key = manager.get_secret(
        secret_name="Claude API Key",
        env_var_name="ANTHROPIC_API_KEY",
        item_name="Anthropic API Key"
    )

    if anthropic_key:
        print(f"✓ Anthropic API Key: {anthropic_key[:10]}..." if len(anthropic_key) > 10 else f"✓ Anthropic API Key: Found")
    else:
        print("✗ Anthropic API Key: Not found")

    newsapi_key = manager.get_secret(
        secret_name="NewsAPI Key",
        env_var_name="NEWS_API_KEY",
        item_name="NewsAPI"
    )

    if newsapi_key:
        print(f"✓ NewsAPI Key: {newsapi_key[:10]}..." if len(newsapi_key) > 10 else f"✓ NewsAPI Key: Found")
    else:
        print("✗ NewsAPI Key: Not found")

    print("\n" + "=" * 60)
