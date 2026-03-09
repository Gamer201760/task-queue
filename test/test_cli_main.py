import sys

import pytest

from adapter.cli.main import main
from repository.api import mock as mock_module


def test_main_runs_with_default_args(
    monkeypatch: pytest.MonkeyPatch, valid_json_file
) -> None:
    monkeypatch.setattr(
        sys, 'argv', ['main', '--file', str(valid_json_file), '--seed', '42']
    )
    monkeypatch.setattr(mock_module.time, 'sleep', lambda _: None)

    main()


def test_main_runs_with_custom_seed(
    monkeypatch: pytest.MonkeyPatch, valid_json_file
) -> None:
    monkeypatch.setattr(
        sys, 'argv', ['main', '--file', str(valid_json_file), '--seed', '99']
    )
    monkeypatch.setattr(mock_module.time, 'sleep', lambda _: None)

    main()
