"""
Settings dialog for Screen Translator
"""

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QTextEdit, QPushButton, QComboBox, 
                             QGroupBox, QFormLayout, QMessageBox)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
import json
import os


class SettingsDialog(QDialog):
    """
    Settings dialog for configuring translation options
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings - Screen Translator")
        self.setMinimumWidth(600)
        self.setMinimumHeight(500)
        
        self.config_path = os.path.join(os.path.dirname(__file__), '..', '..', 'config.json')
        self.config = self.load_config()
        
        self.init_ui()
    
    def load_config(self):
        """Load configuration from file"""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Error loading config: {e}")
        
        return {
            'translation_engine': 'google',
            'gemini_api_key': '',
            'custom_prompt': 'Dịch văn bản sau sang tiếng Việt một cách tự nhiên và dễ hiểu:',
            'source_lang': 'en',
            'target_lang': 'vi'
        }
    
    def save_config(self):
        """Save configuration to file"""
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error saving config: {e}")
            return False
    
    def init_ui(self):
        """Initialize UI components"""
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("⚙️ Cài đặt dịch thuật")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Translation Engine Group
        engine_group = QGroupBox("Translation Engine")
        engine_layout = QFormLayout()
        
        self.engine_combo = QComboBox()
        self.engine_combo.addItems(["Google Translate (Miễn phí)", "Gemini AI (Chất lượng cao)"])
        self.engine_combo.setCurrentIndex(0 if self.config.get('translation_engine') == 'google' else 1)
        self.engine_combo.currentIndexChanged.connect(self.on_engine_changed)
        
        engine_layout.addRow("Chọn engine:", self.engine_combo)
        engine_group.setLayout(engine_layout)
        layout.addWidget(engine_group)
        
        # Gemini Settings Group
        self.gemini_group = QGroupBox("Gemini AI Settings")
        gemini_layout = QVBoxLayout()
        
        # API Key
        api_key_layout = QHBoxLayout()
        api_key_label = QLabel("API Key:")
        self.api_key_input = QLineEdit()
        self.api_key_input.setPlaceholderText("Nhập Gemini API key...")
        self.api_key_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.api_key_input.setText(self.config.get('gemini_api_key', ''))
        
        self.show_key_btn = QPushButton("👁")
        self.show_key_btn.setMaximumWidth(40)
        self.show_key_btn.clicked.connect(self.toggle_api_key_visibility)
        
        get_key_btn = QPushButton("Lấy API Key")
        get_key_btn.clicked.connect(self.open_api_key_page)
        
        api_key_layout.addWidget(api_key_label)
        api_key_layout.addWidget(self.api_key_input)
        api_key_layout.addWidget(self.show_key_btn)
        api_key_layout.addWidget(get_key_btn)
        
        gemini_layout.addLayout(api_key_layout)
        
        # Custom Prompt
        prompt_label = QLabel("Custom Prompt (Context cho AI):")
        self.prompt_input = QTextEdit()
        self.prompt_input.setPlaceholderText("Ví dụ:\n- Dịch văn bản sau với văn phong kiếm hiệp:\n- Dịch văn bản kỹ thuật sau sang tiếng Việt chuyên nghiệp:")
        self.prompt_input.setMaximumHeight(100)
        self.prompt_input.setText(self.config.get('custom_prompt', ''))
        
        gemini_layout.addWidget(prompt_label)
        gemini_layout.addWidget(self.prompt_input)
        
        # Prompt examples
        examples_label = QLabel("💡 Gợi ý prompts:")
        examples_label.setFont(QFont("Arial", 9))
        gemini_layout.addWidget(examples_label)
        
        examples_layout = QHBoxLayout()
        
        example_btns = [
            ("Tự nhiên", "Dịch văn bản sau sang tiếng Việt một cách tự nhiên và dễ hiểu:"),
            ("Kiếm hiệp", "Dịch văn bản sau với văn phong kiếm hiệp, hào hùng:"),
            ("Kỹ thuật", "Dịch văn bản kỹ thuật sau sang tiếng Việt chuyên nghiệp, chính xác:"),
            ("Hài hước", "Dịch văn bản sau một cách hài hước, dễ hiểu:")
        ]
        
        for label, prompt in example_btns:
            btn = QPushButton(label)
            btn.clicked.connect(lambda checked, p=prompt: self.prompt_input.setText(p))
            examples_layout.addWidget(btn)
        
        gemini_layout.addLayout(examples_layout)
        
        self.gemini_group.setLayout(gemini_layout)
        layout.addWidget(self.gemini_group)
        
        # Language Settings Group
        lang_group = QGroupBox("Ngôn ngữ")
        lang_layout = QFormLayout()
        
        self.source_lang_input = QLineEdit()
        self.source_lang_input.setText(self.config.get('source_lang', 'en'))
        self.source_lang_input.setPlaceholderText("en, vi, ja, ko, zh...")
        
        self.target_lang_input = QLineEdit()
        self.target_lang_input.setText(self.config.get('target_lang', 'vi'))
        self.target_lang_input.setPlaceholderText("en, vi, ja, ko, zh...")
        
        lang_layout.addRow("Ngôn ngữ nguồn:", self.source_lang_input)
        lang_layout.addRow("Ngôn ngữ đích:", self.target_lang_input)
        
        lang_group.setLayout(lang_layout)
        layout.addWidget(lang_group)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        save_btn = QPushButton("💾 Lưu")
        save_btn.clicked.connect(self.save_settings)
        save_btn.setStyleSheet("background-color: #4CAF50; color: white; padding: 8px; font-weight: bold;")
        
        cancel_btn = QPushButton("❌ Hủy")
        cancel_btn.clicked.connect(self.reject)
        
        button_layout.addWidget(save_btn)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        
        # Update UI based on engine
        self.on_engine_changed()
    
    def on_engine_changed(self):
        """Handle engine selection change"""
        is_gemini = self.engine_combo.currentIndex() == 1
        self.gemini_group.setEnabled(is_gemini)
    
    def toggle_api_key_visibility(self):
        """Toggle API key visibility"""
        if self.api_key_input.echoMode() == QLineEdit.EchoMode.Password:
            self.api_key_input.setEchoMode(QLineEdit.EchoMode.Normal)
            self.show_key_btn.setText("🙈")
        else:
            self.api_key_input.setEchoMode(QLineEdit.EchoMode.Password)
            self.show_key_btn.setText("👁")
    
    def open_api_key_page(self):
        """Open Gemini API key page in browser"""
        import webbrowser
        webbrowser.open("https://makersuite.google.com/app/apikey")
        QMessageBox.information(self, "Hướng dẫn", 
                               "1. Tạo API key mới\n"
                               "2. Copy API key\n"
                               "3. Paste vào ô bên trái")
    
    def save_settings(self):
        """Save settings and close dialog"""
        # Update config
        self.config['translation_engine'] = 'gemini' if self.engine_combo.currentIndex() == 1 else 'google'
        self.config['gemini_api_key'] = self.api_key_input.text().strip()
        self.config['custom_prompt'] = self.prompt_input.toPlainText().strip()
        self.config['source_lang'] = self.source_lang_input.text().strip()
        self.config['target_lang'] = self.target_lang_input.text().strip()
        
        # Validate
        if self.config['translation_engine'] == 'gemini' and not self.config['gemini_api_key']:
            QMessageBox.warning(self, "Thiếu API Key", 
                              "Bạn cần nhập Gemini API key hoặc chọn Google Translate!")
            return
        
        # Save to file
        if self.save_config():
            QMessageBox.information(self, "Thành công", 
                                  "✓ Cài đặt đã được lưu!\n\n"
                                  "⚠ Vui lòng khởi động lại ứng dụng để áp dụng thay đổi.")
            self.accept()
        else:
            QMessageBox.critical(self, "Lỗi", "Không thể lưu cài đặt!")
