"""Progress reporter for CLI app"""
# cdl_journal_transfer/progress/cli_progress_reporter.py

from cdl_journal_transfer.progress.abstract_progress_reporter import AbstractProgressReporter

class CliProgressReporter(AbstractProgressReporter):

    def set_progress(self, progress):
        # Typer/Click takes progress updates as an amount to be added to current progress,
        # not a total value.
        if hasattr(self, "progress"):
            self.progress = progress - self.progress
        else:
            self.progress = progress


    def update_ui(self):
        self.interface.update(self.progress)


    def set_message(self, message):
        self.interface.label = message
        self.interface.update(0)
