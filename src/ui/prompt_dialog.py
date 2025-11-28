from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QTextEdit, QDialogButtonBox
from PyQt6.QtCore import Qt

class PromptDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Ask Gemini")
        self.resize(400, 200)
        
        # Make it stay on top
        self.setWindowFlags(self.windowFlags() | Qt.WindowType.WindowStaysOnTopHint)
        
        layout = QVBoxLayout()
        
        layout.addWidget(QLabel("Enter your prompt for this capture:"))
        
        self.input_text = QTextEdit()
        self.input_text.setPlaceholderText("E.g., Explain this code, Summarize this, Translate to French...")
        self.input_text.setTabChangesFocus(True)
        layout.addWidget(self.input_text)
        
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        
        self.setLayout(layout)
        
    def get_prompt(self):
        return self.input_text.toPlainText().strip()
