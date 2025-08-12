import sys
import os
import uuid
from PyQt5.QtWidgets import (
    QApplication, QWidget, QComboBox, QTextEdit, QPushButton,
    QVBoxLayout, QHBoxLayout, QLabel, QMessageBox, QGraphicsOpacityEffect,
    QFrame, QShortcut, QProgressBar
)
from PyQt5.QtGui import QFont, QKeySequence
from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve, QRect, QTimer, QUrl

try:
    from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
    HAS_QT_MEDIA = True
except Exception:
    HAS_QT_MEDIA = False

import speech_recognition as sr
from gtts import gTTS
from playsound import playsound
from deep_translator import GoogleTranslator

LANGUAGES = {
    "English": "en",
    "French": "fr",
    "German": "de",
    "Spanish": "es",
    "Hindi": "hi",
    "Italian": "it",
    "Russian": "ru",
    "Arabic": "ar",
    "Chinese": "zh-CN",
    "Sanskrit": "sa"
}

TTS_LANGS = {
    "English": "en",
    "French": "fr",
    "German": "de",
    "Spanish": "es",
    "Hindi": "hi",
    "Italian": "it",
    "Russian": "ru",
    "Arabic": "ar",
    "Chinese": "zh-CN",
    "Sanskrit": "hi"
}

DARK_QSS = """
QWidget { background-color: #1e222a; color: #ececec; }
QFrame#Header {
    background-color: #191c23;
    border-radius: 12px;
}
QLabel#Title { color: #ffd369; font-size: 20px; font-weight: 600; }
QLabel#Subtitle { color: #aab2bf; font-size: 12px; }
QTextEdit, QComboBox {
    background-color: #232833;
    border-radius: 10px;
    padding: 6px;
    border: 2px solid #ffd369;
}
QPushButton {
    background-color: #2b313d; color: #ffd369;
    border-radius: 10px; padding: 8px 12px;
}
QPushButton:hover { background-color: #ffd369; color: #1f232b; }
QLabel#Status { color: #9aa3af; }
"""

class BusyOverlay(QFrame):
    def __init__(self, parent=None, text="Working..."):
        super().__init__(parent)
        self.setStyleSheet("""
            QFrame {
                background-color: rgba(0, 0, 0, 120);
                border-radius: 12px;
            }
            QLabel {
                color: #ececec;
                font-size: 13px;
            }
            QProgressBar {
                background-color: rgba(255,255,255,40);
                color: #ececec;
                border: 1px solid rgba(255,255,255,60);
                border-radius: 6px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #ffd369;
                width: 10px;
                margin: 0.5px;
            }
        """)
        self.setVisible(False)

        layout = QVBoxLayout(self)
        self.label = QLabel(text)
        self.label.setAlignment(Qt.AlignCenter)
        self.bar = QProgressBar()
        self.bar.setRange(0, 0)
        layout.addStretch(1)
        layout.addWidget(self.label)
        layout.addWidget(self.bar)
        layout.addStretch(1)

    def resizeEvent(self, event):
        if self.parent():
            self.setGeometry(self.parent().rect())
        super().resizeEvent(event)


class TranslatorApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Translator By Vinayak")
        self.setGeometry(200, 200, 740, 520)
        self.media_player = QMediaPlayer(self) if HAS_QT_MEDIA else None

        self.setup_ui()
        self.install_shortcuts()
        self.fade_in_widget(self, duration=600)

    def setup_ui(self):
        font = QFont("Segoe UI", 11)
        self.setFont(font)

        header = QFrame(objectName="Header")
        header_layout = QVBoxLayout(header)
        header_layout.setContentsMargins(16, 12, 16, 12)
        title = QLabel("Translator By Vinayak", objectName="Title")
        subtitle = QLabel("Voice + Text — Translate between languages with a click", objectName="Subtitle")
        header_layout.addWidget(title)
        header_layout.addWidget(subtitle)

        self.source_label = QLabel("Source")
        self.source_lang = QComboBox()
        self.source_lang.addItems(LANGUAGES.keys())

        self.target_label = QLabel("Target")
        self.target_lang = QComboBox()
        self.target_lang.addItems(LANGUAGES.keys())
        self.target_lang.setCurrentIndex(1)

        self.source_lang.currentIndexChanged.connect(self.on_language_changed)
        self.target_lang.currentIndexChanged.connect(self.on_language_changed)

        lang_layout = QHBoxLayout()
        lang_layout.addWidget(self.source_label)
        lang_layout.addWidget(self.source_lang, 1)
        lang_layout.addWidget(self.target_label)
        lang_layout.addWidget(self.target_lang, 1)
        swap_btn = QPushButton("⇄ Swap")
        swap_btn.clicked.connect(self.swap_languages)
        lang_layout.addWidget(swap_btn)

        self.input_text = QTextEdit()
        self.input_text.setPlaceholderText("Enter or speak text here...")
        self.apply_card_style(self.input_text)

        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)
        self.output_text.setPlaceholderText("Translated text will appear here...")
        self.apply_card_style(self.output_text)

        self.voice_in_btn = QPushButton("🎤 Voice Input", clicked=self.voice_input)
        self.translate_btn = QPushButton("Translate", clicked=self.translate_text)
        self.voice_out_btn = QPushButton("🔊 Voice Output", clicked=self.voice_output)

        buttons_layout = QHBoxLayout()
        buttons_layout.addWidget(self.voice_in_btn)
        buttons_layout.addWidget(self.translate_btn, 1)
        buttons_layout.addWidget(self.voice_out_btn)

        self.status = QLabel("", objectName="Status")

        main_layout = QVBoxLayout(self)
        main_layout.addWidget(header)
        main_layout.addLayout(lang_layout)
        main_layout.addWidget(self.input_text, 1)
        main_layout.addLayout(buttons_layout)
        main_layout.addWidget(self.output_text, 1)
        main_layout.addWidget(self.status)

        self.overlay = BusyOverlay(self, text="Working...")
        self.overlay.raise_()

        for b in [self.voice_in_btn, self.translate_btn, self.voice_out_btn]:
            self.add_button_animation(b)

    def apply_card_style(self, widget):
        widget.setGraphicsEffect(QGraphicsOpacityEffect(widget))
        widget.graphicsEffect().setOpacity(0.0)
        self.fade_in_widget(widget, duration=500, delay=150)

    def add_button_animation(self, button):
        def enterEvent(e): self.animate_geometry_pulse(button, 1.03, 120)
        def leaveEvent(e): self.animate_geometry_pulse(button, 1.0, 120, return_to=True)
        button.enterEvent = enterEvent
        button.leaveEvent = leaveEvent

    def animate_geometry_pulse(self, widget, scale, duration, return_to=False):
        rect = widget.geometry()
        cx, cy = rect.center().x(), rect.center().y()
        new_w, new_h = int(rect.width()*scale), int(rect.height()*scale)
        new_rect = QRect(cx - new_w//2, cy - new_h//2, new_w, new_h)
        anim = QPropertyAnimation(widget, b"geometry")
        anim.setDuration(duration)
        anim.setStartValue(rect)
        anim.setEndValue(new_rect)
        anim.setEasingCurve(QEasingCurve.OutCubic)
        if return_to:
            anim.finished.connect(lambda: self.animate_geometry_pulse(widget, 1.0, duration))
        anim.start()
        widget._anim = anim

    def fade_in_widget(self, widget, duration=400, start=0.0, end=1.0, delay=0):
        effect = widget.graphicsEffect()
        if not effect:
            effect = QGraphicsOpacityEffect(widget)
            widget.setGraphicsEffect(effect)
        anim = QPropertyAnimation(effect, b"opacity")
        anim.setDuration(duration)
        anim.setStartValue(start)
        anim.setEndValue(end)
        if delay:
            QTimer.singleShot(delay, anim.start)
        else:
            anim.start()
        widget._fade_anim = anim

    def install_shortcuts(self):
        QShortcut(QKeySequence("Ctrl+I"), self, activated=self.voice_input)
        QShortcut(QKeySequence("Ctrl+T"), self, activated=self.translate_text)
        QShortcut(QKeySequence("Ctrl+O"), self, activated=self.voice_output)
        QShortcut(QKeySequence("Ctrl+Q"), self, activated=self.close)

    def set_busy(self, on=True, message="Working..."):
        self.overlay.label.setText(message)
        self.overlay.setVisible(on)
        QApplication.setOverrideCursor(Qt.WaitCursor if on else Qt.ArrowCursor)
        QApplication.processEvents()

    def swap_languages(self):
        s_idx, t_idx = self.source_lang.currentIndex(), self.target_lang.currentIndex()
        self.source_lang.setCurrentIndex(t_idx)
        self.target_lang.setCurrentIndex(s_idx)
        self.translate_text()

    def popup(self, title, text, icon=QMessageBox.Information):
        QMessageBox(icon, title, text, QMessageBox.Ok, self).exec_()

    def translate_text(self):
        src_code = LANGUAGES[self.source_lang.currentText()]
        tgt_code = LANGUAGES[self.target_lang.currentText()]
        text = self.input_text.toPlainText().strip()
        if not text:
            self.popup("Error", "Please enter text to translate", QMessageBox.Warning)
            return
        if src_code == tgt_code:
            self.popup("Error", "Source and target language are the same", QMessageBox.Warning)
            return
        try:
            self.set_busy(True, "Translating...")
            translated = GoogleTranslator(source=src_code, target=tgt_code).translate(text)
            self.output_text.setText(translated)
        except Exception as e:
            print("[Translation Error]", e)
            self.popup("Translation error", str(e), QMessageBox.Critical)
        finally:
            self.set_busy(False)
            self.setStyleSheet(DARK_QSS)  # keep dark theme locked

    def on_language_changed(self):
        if self.input_text.toPlainText().strip() and \
           self.source_lang.currentIndex() != self.target_lang.currentIndex():
            self.translate_text()

    def voice_input(self):
        recognizer = sr.Recognizer()
        try:
            with sr.Microphone() as source:
                self.set_busy(True, "Listening...")
                recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio = recognizer.listen(source, timeout=5, phrase_time_limit=10)
            self.set_busy(True, "Recognizing...")
            text = recognizer.recognize_google(audio)
            self.input_text.setText(text)
        except Exception as e:
            print("[Speech Recognition Error]", e)
            self.popup("Speech recognition error", str(e), QMessageBox.Critical)
        finally:
            self.set_busy(False)
            self.setStyleSheet(DARK_QSS)

    def voice_output(self):
        text = self.output_text.toPlainText().strip()
        if not text:
            self.popup("Error", "No text to speak", QMessageBox.Warning)
            return

        # unique temp file to prevent caching
        filename = f"temp_voice_{uuid.uuid4().hex}.mp3"
        try:
            self.set_busy(True, "Generating speech...")
            lang_code = TTS_LANGS[self.target_lang.currentText()].lower()
            tts = gTTS(text=text, lang=lang_code)
            tts.save(filename)

            def safe_remove():
                if os.path.exists(filename):
                    try:
                        os.remove(filename)
                    except Exception as e:
                        print("[File Delete Error]", e)

            if HAS_QT_MEDIA and self.media_player:
                self.media_player.setMedia(QMediaContent(QUrl.fromLocalFile(os.path.abspath(filename))))
                self.media_player.play()
                try:
                    self.media_player.mediaStatusChanged.disconnect()
                except Exception:
                    pass

                def cleanup(status):
                    if status == QMediaPlayer.EndOfMedia:
                        safe_remove()
                        try:
                            self.media_player.mediaStatusChanged.disconnect(cleanup)
                        except Exception:
                            pass

                self.media_player.mediaStatusChanged.connect(cleanup)
            else:
                playsound(filename)
                safe_remove()

        except Exception as e:
            print("[Voice Output Error]", e)
            self.popup("Voice output error", str(e), QMessageBox.Critical)
        finally:
            self.set_busy(False)
            self.setStyleSheet(DARK_QSS)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet(DARK_QSS)  # Apply globally so it never reverts
    window = TranslatorApp()
    window.show()
    sys.exit(app.exec_())
