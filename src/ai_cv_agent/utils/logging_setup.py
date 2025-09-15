import logging
import os
import sys
from typing import Optional

RESET = "\x1b[0m"
DIM = "\x1b[2m"
BOLD = "\x1b[1m"

PALETTE = {
    "INFO": "\x1b[38;5;39m",  # Cyan
    "WARNING": "\x1b[38;5;214m",  # Orange
    "ERROR": "\x1b[38;5;196m",  # Red
    "DEBUG": "\x1b[38;5;244m",  # Grey
}

ICONS = {
    "INFO": "",
    "WARNING": "⚠",
    "ERROR": "✗",
    "DEBUG": "·",
}


def _supports_color(stream) -> bool:
    if not hasattr(stream, "isatty") or not stream.isatty():
        return False
    if os.name == "nt":
        return True
    return True


class CompactFormatter(logging.Formatter):
    def __init__(self, use_color: bool):
        super().__init__("%(asctime)s │ %(level)s %(message)s", datefmt="%H:%M:%S")
        self.use_color = use_color

    def format(self, record: logging.LogRecord) -> str:
        level = record.levelname
        icon = ICONS.get(level, " ")
        if self.use_color and level in PALETTE:
            colored = f"{PALETTE[level]}{icon} {level:<7}{RESET}"
        else:
            colored = f"{icon} {level:<7}"
        record.level = colored
        return super().format(record)


def configure_logging(verbosity: int = 0, httpx_level: Optional[int] = logging.WARNING):
    root = logging.getLogger()
    # Avoid duplicate handlers if reconfigured
    if getattr(root, "_cv_logging_configured", False):
        return
    root.handlers.clear()

    level = logging.INFO
    if verbosity >= 2:
        level = logging.DEBUG
    elif verbosity == 1:
        level = logging.INFO

    handler = logging.StreamHandler(sys.stdout)
    use_color = _supports_color(sys.stdout) and os.environ.get("NO_COLOR") is None
    handler.setFormatter(CompactFormatter(use_color=use_color))
    root.addHandler(handler)
    root.setLevel(level)

    # Quiet down noisy libs
    logging.getLogger("httpx").setLevel(httpx_level)
    logging.getLogger("playwright").setLevel(logging.WARNING)

    root._cv_logging_configured = True


def banner(text: str, char: str = "═", width: int = 60):
    line = char * width
    logging.info(line)
    logging.info(f"{text}")
    logging.info(line)


def step(number: int, title: str):
    logging.info("")
    logging.info(f"{BOLD}[Step {number}] {title}{RESET}")


def success(msg: str):
    logging.info(f"✓ {msg}")


def fail(msg: str):
    logging.error(f"✗ {msg}")
