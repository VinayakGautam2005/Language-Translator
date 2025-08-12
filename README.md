***

# AI Translator App

A powerful multi-language translator app built with **Python** and **PyQt5**, offering seamless text and voice translation with an intuitive graphical interface.

## Overview

This desktop application facilitates real-time translation and voice interaction across various languages, including popular global languages and regional classics such as **Sanskrit**. It combines modern translation APIs with speech recognition and text-to-speech to provide a smooth and accessible user experience.

## Features

- 🌐 **Multi-language translation:**  
  Supports English, French, German, Spanish, Hindi, Italian, Russian, Arabic, Chinese, Sanskrit.

- 🎤 **Voice input:**  
  Speak text directly into the app using speech recognition for hands-free convenience.

- 🔊 **Voice output:**  
  Hear translated text with natural-sounding voices using Google Text-to-Speech (gTTS). For Sanskrit, Hindi TTS voice is used for clear pronunciation.

- 🔄 **Language swap & auto-translate:**  
  Quickly switch source and target languages with one click and enjoy automatic retranslation on language changes.

- 🎨 **Sleek, animated UI:**  
  Built with PyQt5 featuring smooth button animations, busy overlays, and progress bars for effective user feedback.


## Installation

1. Ensure Python 3.7+ is installed on your system.
2. Install the required dependencies:

   ```bash
   pip install PyQt5 gtts playsound speechrecognition deep-translator
   ```

3. Run the script:

   ```bash
   python TranslatorBot.py
   ```

## Usage

- Select the source and target languages from the dropdown menus.
- Enter text manually or use the voice input button to speak.
- Click **Translate** to see the translated output.
- Use the **Voice Output** button to hear the translation.
- Swap languages at any time with the swap button.

## Notes

- Sanskrit voice outputs utilize the Hindi voice due to current TTS limitations.
- The app gracefully handles unsupported languages to avoid voice output errors.

## Contributing

Feel free to open issues or submit pull requests to help improve language support, UI design, or add new features.

## License

This project is open source and available under the MIT License.

***
