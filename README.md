# Posture Guardian Desktop App 🌿

A gentle companion that watches your posture and sends system-wide overlay alerts, no matter what you're doing.

## Installation

### Step 1: Install Python
If you don't have Python installed:
- **Windows**: Download from https://www.python.org/downloads/ (get Python 3.10 or newer)
- **Mac**: Python usually comes pre-installed, or use `brew install python3`
- **Linux**: Usually pre-installed, or use `sudo apt install python3 python3-pip`

### Step 2: Install Dependencies
Open Terminal (Mac/Linux) or Command Prompt (Windows) and run:

```bash
pip install -r requirements.txt
```

Or install individually:
```bash
pip install opencv-python mediapipe numpy Pillow
```

### Step 3: Run the App
```bash
python posture_guardian.py
```

## How to Use

1. **Launch the app** - A window will open showing your webcam feed
2. **Calibrate** - Sit with perfect posture and click "Calibrate Good Posture"
3. **Wait 3 seconds** - The app captures your good posture
4. **Work freely** - The app now monitors you in the background
5. **Get alerts** - When you slouch, a red overlay appears over EVERYTHING

## Features

- ✨ **System-wide alerts** - Overlay appears over any application
- 🎯 **Smart detection** - Uses AI to track your shoulders, neck, and head position
- ⚙️ **Adjustable sensitivity** - Make it stricter or more lenient
- ⏱️ **Custom alert duration** - Control how long warnings stay visible
- 🪞 **Mirror view** - Camera feed is flipped for natural viewing

## Settings

- **Alert Sensitivity**: Lower numbers = stricter posture requirements (5-20°) default = 8°
- **Alert Duration**: How long the warning stays visible (1-10 seconds) default = 3 seconds 

## Tips

- Keep the app window open (you can minimize it after calibration)
- Calibrate in your normal working position
- Adjust sensitivity if you get too many or too few alerts
- The app works best with good lighting

## Troubleshooting

**Camera not working?**
- Make sure no other app is using your webcam
- Grant camera permissions when prompted
- Try unplugging/replugging external webcams

**No alerts appearing?**
- Make sure you clicked "Calibrate Good Posture" first
- Try lowering the sensitivity setting
- Check that you're slouching noticeably

**App won't start?**
- Make sure all dependencies are installed
- Check that you have Python 3.10 or newer: `python --version`

---

Made with 💚 for your wellbeing

## 💫 Let's connect
- 💌 [Email](mailto:marisombra@proton.me)
- 🎮 [Twitch](https://www.twitch.tv/marissombra)    
- 🧵 [TikTok](https://www.tiktok.com/@marissombra)
- 🪩 [Itch.io](https://marisombra.itch.io/) (for games)

