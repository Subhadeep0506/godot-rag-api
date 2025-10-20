import os

from typing import Any
from infisical_sdk import InfisicalSDKClient
from api.services.logger_service import LoggerService

logger = LoggerService.get_logger(__name__)


class InfisicalManagedCredentials:
    def __init__(self) -> None:
        try:
            self.client = InfisicalSDKClient(
                host="https://app.infisical.com",
                cache_ttl=1,
            )
            self.client.auth.universal_auth.login(
                client_id=os.getenv("INFISICAL_CLIENT_ID"),
                 client_secret=os.getenv("INFISICAL_SECRET"),
            )
            self()
            logger.info("Infisical Managed Credentials initialized")
        except Exception as e:
            logger.error(f"Error initializing Infisical client: {e}")

    def __call__(self, *args: Any, **kwds: Any) -> Any:
        """
        Fetch secrets from Infisical and populate os.environ with each secret.

        - Supports secret items that are either objects with attributes (e.g. BaseSecret.secretKey /
          BaseSecret.secretValue) or dict-like items with keys 'secretKey'/'secretValue' or
          'key'/'value'.
        - Does NOT log secret values. Logs only which keys were set.
        - By default this uses os.environ.setdefault so existing environment variables won't be
          overwritten. Change to assignment if you want to force overwrite.

        Returns:
            Dict[str, bool]: mapping of secret key -> True if set, False if skipped/empty
        """
        set_keys: dict[str, bool] = {}
        try:
            result = self.client.secrets.list_secrets(
                project_id=os.getenv("INFISICAL_PROJECT_ID"),
                environment_slug="dev",
                secret_path="/"
            )
            # SDK may return an object with a .secrets list or return the list directly
            secrets = getattr(result, "secrets", result)
            logger.info("Fetched secrets metadata from Infisical (values not logged)")

            for s in secrets or []:
                # support both object attributes and dict-like items
                if isinstance(s, dict):
                    key = s.get("secretKey") or s.get("key")
                    value = s.get("secretValue") or s.get("value")
                else:
                    key = getattr(s, "secretKey", None) or getattr(s, "key", None)
                    value = getattr(s, "secretValue", None) or getattr(s, "value", None)

                if not key:
                    logger.debug("Skipping a secret without a key")
                    continue

                if value is None or value == "":
                    logger.warning("Secret '%s' has empty value; skipping", key)
                    set_keys[key] = False
                    continue

                # Do not overwrite existing env vars by default; use assignment if overwrite is desired
                os.environ.setdefault(key, str(value))
                set_keys[key] = True

            logger.info("Infisical Managed Credentials loaded into environment (keys set: %s)", list(set_keys.keys()))
            return set_keys
        except Exception as e:
            logger.error(f"Error occured while fetching secrets: {e}")
            raise e
