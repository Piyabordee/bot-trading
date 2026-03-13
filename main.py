#!/usr/bin/env python3
"""Main entry point for paper trading bot.

This is a DEMO bot for paper trading only.
No live trading will be executed.
"""

import logging
import sys
from pathlib import Path
from decimal import Decimal

from bot_trading.config import get_config
from bot_trading.providers.alpaca import AlpacaProvider
from bot_trading.risk.limits import RiskLimits
from bot_trading.execution.executor import Executor

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def main() -> int:
    """Main entry point."""
    config = get_config()

    logger.info("=" * 60)
    logger.info("Paper Trading Bot - DEMO ONLY")
    logger.info("=" * 60)
    logger.info(f"Trading Mode: {config.trading_mode.upper()}")
    logger.info(f"Max Position Size: ${config.max_position_size}")
    logger.info(f"Max Portfolio Exposure: {config.max_portfolio_exposure * 100}%")
    logger.info(f"Daily Loss Limit: ${config.daily_loss_limit}")
    logger.info("=" * 60)

    # Safety verification
    if not config.is_paper_mode:
        logger.error("REFUSING TO RUN: This is a paper-trading-only demo bot")
        logger.error("Set TRADING_MODE=paper in environment")
        return 1

    try:
        # Initialize provider (will fail without credentials)
        logger.info("Initializing Alpaca Paper Trading provider...")
        provider = AlpacaProvider()
        logger.info(f"Provider initialized: {provider.base_url}")

        # Initialize risk limits
        risk_limits = RiskLimits(
            max_position_size=Decimal(str(config.max_position_size)),
            max_portfolio_exposure=Decimal(str(config.max_portfolio_exposure)),
            daily_loss_limit=Decimal(str(config.daily_loss_limit)),
        )
        logger.info("Risk limits initialized")

        # Initialize executor
        executor = Executor(provider=provider, risk_limits=risk_limits)
        logger.info("Executor initialized")

        logger.info("Bot ready - TODO: Implement main trading loop")
        logger.info("Currently in scaffold mode - no actual trading will occur")

        return 0

    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        logger.error("Please check your .env file")
        return 1
    except ImportError as e:
        logger.error(f"Dependency error: {e}")
        logger.error("Install dependencies: pip install -e '.[dev]'")
        return 1
    except Exception as e:
        logger.exception(f"Unexpected error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
