"""
Settings dialog for Screen Translator
"""

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QTextEdit, QPushButton, QComboBox, 
                             QGroupBox, QFormLayout, QMessageBox, QInputDialog)
from PyQt6.QtCore import Qt, pyqtSignal
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
        self.setMinimumHeight(600)
        
        self.config_path = os.path.join(os.path.dirname(__file__), '..', '..', 'config.json')
        self.config = self.load_config()
        
        # Load saved contexts or initialize defaults
        self.saved_contexts = self.config.get('saved_contexts', {
            "Tự nhiên": "Dịch văn bản sau sang tiếng Việt một cách tự nhiên và dễ hiểu:",
            "Kiếm hiệp": "Dịch văn bản sau với văn phong kiếm hiệp, hào hùng:",
            "Kỹ thuật": "Dịch văn bản kỹ thuật sau sang tiếng Việt chuyên nghiệp, chính xác:",
            "Hài hước": "Dịch văn bản sau một cách hài hước, dễ hiểu:",
            "Tóm tắt": "Tóm tắt nội dung văn bản sau bằng tiếng Việt:"
        })
        
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
            'target_lang': 'vi',
            'saved_contexts': {}
        }
    
    def save_config(self):
        """Save configuration to file"""
        try:
            # Update contexts in config
            self.config['saved_contexts'] = self.saved_contexts
            
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
        
        # Gemini Mode Selection
        mode_layout = QHBoxLayout()
        mode_label = QLabel("Gemini Mode:")
        self.gemini_mode_combo = QComboBox()
        self.gemini_mode_combo.addItems([
            "Vision (Gửi ảnh - Chính xác hơn)",
            "Text (Gửi text OCR - Nhanh hơn)"
        ])
        current_mode = self.config.get('gemini_mode', 'vision')
        self.gemini_mode_combo.setCurrentIndex(0 if current_mode == 'vision' else 1)
        
        mode_layout.addWidget(mode_label)
        mode_layout.addWidget(self.gemini_mode_combo)
        gemini_layout.addLayout(mode_layout)
        
        # Context Management
        context_label = QLabel("Context (Ngữ cảnh dịch):")
        gemini_layout.addWidget(context_label)
        
        context_controls = QHBoxLayout()
        
        self.context_combo = QComboBox()
        self.context_combo.addItems(list(self.saved_contexts.keys()))
        self.context_combo.setPlaceholderText("Chọn ngữ cảnh...")
        self.context_combo.currentTextChanged.connect(self.on_context_changed)
        
        add_context_btn = QPushButton("➕ Thêm")
        add_context_btn.clicked.connect(self.add_context)
        
        del_context_btn = QPushButton("🗑 Xóa")
        del_context_btn.clicked.connect(self.delete_context)
        
        context_controls.addWidget(self.context_combo, 1)
        context_controls.addWidget(add_context_btn)
        context_controls.addWidget(del_context_btn)
        
        gemini_layout.addLayout(context_controls)
        
        # Custom Prompt Input
        self.prompt_input = QTextEdit()
        self.prompt_input.setPlaceholderText("Nhập prompt cho AI...")
        self.prompt_input.setMaximumHeight(100)
        self.prompt_input.setText(self.config.get('custom_prompt', ''))
        self.prompt_input.textChanged.connect(self.save_current_context_text)
        
        gemini_layout.addWidget(self.prompt_input)
        
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
        save_btn.setFixedWidth(120)
        save_btn.setFixedHeight(40)
        
        cancel_btn = QPushButton("❌ Hủy")
        cancel_btn.clicked.connect(self.reject)
        cancel_btn.setStyleSheet("padding: 8px;")
        cancel_btn.setFixedWidth(120)
        cancel_btn.setFixedHeight(40)
        
        button_layout.addStretch()
        button_layout.addWidget(save_btn)
        button_layout.addWidget(cancel_btn)
        button_layout.addStretch()
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        
        # Update UI based on engine
        self.on_engine_changed()
        
        # Set initial context selection if matches current prompt
        current_prompt = self.config.get('custom_prompt', '')
        for name, prompt in self.saved_contexts.items():
            if prompt == current_prompt:
                self.context_combo.setCurrentText(name)
                break
    
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
    
    def on_context_changed(self, text):
        """Handle context selection change"""
        if text in self.saved_contexts:
            self.prompt_input.setText(self.saved_contexts[text])
    
    def save_current_context_text(self):
        """Update the text of the currently selected context"""
        current_context = self.context_combo.currentText()
        if current_context and current_context in self.saved_contexts:
            self.saved_contexts[current_context] = self.prompt_input.toPlainText()
    
    def add_context(self):
        """Add a new context"""
        name, ok = QInputDialog.getText(self, "Thêm Context", "Nhập tên ngữ cảnh mới:")
        if ok and name:
            if name in self.saved_contexts:
                QMessageBox.warning(self, "Lỗi", "Tên ngữ cảnh đã tồn tại!")
                return
            
            # Add new context with current prompt text or default
            current_text = self.prompt_input.toPlainText()
            self.saved_contexts[name] = current_text if current_text else "Nhập prompt cho ngữ cảnh này..."
            
            # Update combo box
            self.context_combo.addItem(name)
            self.context_combo.setCurrentText(name)
    
    def delete_context(self):
        """Delete current context"""
        current_context = self.context_combo.currentText()
        if not current_context:
            return
            
        reply = QMessageBox.question(self, "Xác nhận", 
                                   f"Bạn có chắc muốn xóa ngữ cảnh '{current_context}'?",
                                   QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            del self.saved_contexts[current_context]
            self.context_combo.removeItem(self.context_combo.currentIndex())
            
            # Clear input if no items left
            if self.context_combo.count() == 0:
                self.prompt_input.clear()
    
    settings_saved = pyqtSignal()

    def save_settings(self):
        """Save settings and close dialog"""
        # Update config
        self.config['translation_engine'] = 'gemini' if self.engine_combo.currentIndex() == 1 else 'google'
        self.config['gemini_api_key'] = self.api_key_input.text().strip()
        self.config['gemini_mode'] = 'vision' if self.gemini_mode_combo.currentIndex() == 0 else 'text'
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
            # Emit signal to notify app to reload settings
            self.settings_saved.emit()
            
            QMessageBox.information(self, "Thành công", 
                                  "✓ Cài đặt đã được lưu và áp dụng!")
            self.accept()
        else:
            QMessageBox.critical(self, "Lỗi", "Không thể lưu cài đặt!")
