# transfer/tests/test_progress_reporter.py

# All tests should only write files to the test/tmp directory,
# which will be cleaned up automatically at the end of each test.

from journal_transporter import cli
from journal_transporter.progress.cli_progress_reporter import CliProgressReporter

# Constants

INIT_MESSAGE = "Init Message"

MAJOR_LENGTH = 10
MAJOR_MESSAGE = "Major Update Message"

MINOR_LENGTH = 20
MINOR_MESSAGE = "Minor Update Message"
MINOR_PROGRESS = 1

DETAIL_PROGRESS = 5
DETAIL_UNWEIGHTED_MESSAGE = "Unweighted Detail Update Message"
DETAIL_WEIGHTED_MESSAGE = "Weighted Detail Update Message"


# Helpers


DEFAULT_PR_OPTS = {
    "interface": cli.typer,
    "init_message": INIT_MESSAGE,
    "start": 0,
    "verbose": False,
    "debug": False,
    "log": "n",
    "on_error": "i",
}


def build_progress_reporter(**opts):
    return CliProgressReporter(**{**DEFAULT_PR_OPTS, **opts})


def mock_debug(message, type):
    return message


# Tests


def test_setup():
    build_progress_reporter()


def test_major(progress=build_progress_reporter()):
    progress.major(MAJOR_MESSAGE, MAJOR_LENGTH)

    assert progress.message == MAJOR_MESSAGE
    assert progress.progress_length == MAJOR_LENGTH


def test_major_verbose(progress=build_progress_reporter(verbose=True)):
    progress.major(MAJOR_MESSAGE, MAJOR_LENGTH)

    assert progress.message == INIT_MESSAGE
    assert progress.progress_length != MAJOR_LENGTH


def test_minor(progress=build_progress_reporter()):
    test_major(progress)
    progress.minor(MINOR_PROGRESS, MINOR_MESSAGE, MINOR_LENGTH)

    assert progress.message == MINOR_MESSAGE
    assert progress.progress == MINOR_PROGRESS
    assert progress.subtask_length == MINOR_LENGTH


def test_minor_verbose(progress=build_progress_reporter(verbose=True)):
    test_major_verbose(progress)
    progress.minor(MINOR_PROGRESS, MINOR_MESSAGE, MINOR_LENGTH)

    assert progress.message == MINOR_MESSAGE
    assert progress.progress_length == MINOR_LENGTH


def test_detail_unweighted(progress=build_progress_reporter()):
    test_major(progress)
    progress.detail(DETAIL_PROGRESS, DETAIL_UNWEIGHTED_MESSAGE)

    assert progress.progress == DETAIL_PROGRESS
    assert progress.message != DETAIL_UNWEIGHTED_MESSAGE


def test_detail_weighted(progress=build_progress_reporter()):
    test_major(progress)
    test_minor(progress)
    progress.detail(DETAIL_PROGRESS, DETAIL_WEIGHTED_MESSAGE)

    assert progress.progress == (DETAIL_PROGRESS / MINOR_LENGTH)


def test_detail_verbose(progress=build_progress_reporter(verbose=True)):
    test_major_verbose(progress)
    test_minor_verbose(progress)
    progress.detail(DETAIL_PROGRESS, DETAIL_UNWEIGHTED_MESSAGE)

    assert progress.progress == DETAIL_PROGRESS
    assert progress.progress_length == MINOR_LENGTH


def test_debug(monkeypatch, progress=build_progress_reporter(debug=True)):
    monkeypatch.setattr(progress, "_handle_debug", mock_debug)

    assert progress.debug_mode is True

    debug = progress.major(MAJOR_MESSAGE, MAJOR_LENGTH)

    # Should not update anything - only print debug messages
    assert progress.message != MAJOR_MESSAGE
    assert progress.progress_length != MAJOR_LENGTH
    assert debug == MAJOR_MESSAGE
