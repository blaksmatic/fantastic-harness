from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    db_path: str = "harness.db"

    # LLM defaults
    default_provider: str = "anthropic"
    decision_model: str = "claude-opus-4-20250514"
    validation_model: str = "claude-sonnet-4-20250514"
    adversary_model: str = "claude-sonnet-4-20250514"
    executor_model: str = "claude-haiku-4-5-20251001"
    hunter_model: str = "claude-haiku-4-5-20251001"
    auditor_model: str = "claude-sonnet-4-20250514"

    # Schedules (seconds)
    miles_loop_interval: int = 30
    shadow_loop_interval: int = 30
    maurissa_interval: int = 600
    rimu_interval: int = 1800
    hunter_interval: int = 3600

    # Succession
    context_pressure_threshold: float = 0.85
    max_decisions_before_retire: int = 200

    # API
    anthropic_api_key: str = ""

    model_config = {"env_prefix": "HARNESS_"}


settings = Settings()
