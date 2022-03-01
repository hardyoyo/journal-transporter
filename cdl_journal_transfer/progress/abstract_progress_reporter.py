"""Abstract superclass for progress reporters"""
# cdl_journal_transfer/progress/abstract_progress_reporter.py

from abc import ABC, abstractmethod

class AbstractProgressReporter(ABC):

    def __init__(self, interface, init_message="Initializing...", length=100, start=0):
        self.interface = interface
        self.label = init_message
        self.length = length
        self.set_progress(start)


    def update(self, progress: int = None, message: str = None) -> None:
        """
        Updates progress and message, and updates the UI
        """
        if message : self.set_message(message)
        if progress : self.set_progress(progress)
        self.update_ui()


    def set_progress(self, progress: int) -> None:
        """
        Sets the current progress.
        """
        self.progress = progress


    def set_message(self, message: str):
        """
        Updates the application-specific UI with a progress message
        """
        self.message = message


    @abstractmethod
    def update_ui(self):
        """
        Updates the application-specific UI based on current progress
        """
        pass
