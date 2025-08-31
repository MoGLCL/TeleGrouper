📝 Telegram Group Creator Web App
🔗 Connect with Developers
MoGlitch
Manona
🚀 Core Features
✅ Telegram Login: Secure login via phone number, code, and two-factor authentication.

✅ Bulk Group Creation: Create multiple Telegram groups with sequential titles effortlessly.

✅ Custom Messaging: Send a unique, custom message to each newly created group.

✅ Flood Control: Set a delay between group creations to avoid Telegram's flood limits.

✅ User Dashboard: View your profile information (username, phone, and photo) after logging in.

✅ Robust Error Handling: Manages common Telethon errors like invalid codes, flood waits, and more.

✅ Session Management: Handles multiple user sessions securely.

✨ Login Page Features
Our login page is designed to be modern, user-friendly, and secure.

🎨 Animated Background: A sleek, animated gradient background provides a modern aesthetic.

🔒 Security Warning: A prominent modal appears on the first visit, warning users that their sensitive data is stored locally in browser cookies and advising them to protect their session.

📱 International Phone Input: A user-friendly phone number field with a dropdown for all country codes and flags, defaulting to Egypt.

🇪🇬 Smart Validation: Includes automatic formatting and validation for Egyptian phone numbers, ensuring data accuracy.

✒️ Floating Labels: Input fields feature floating labels for a clean and intuitive user experience.

🌐 Developer Socials: Interactive Floating Action Buttons (FABs) provide quick access to the developers' social media profiles with a smooth animation.

📱 Fully Responsive: The entire page is designed to work seamlessly on all devices, from desktops to mobile phones.

🛠️ Technologies
Python 3.11+

Flask – Lightweight web framework

Telethon – Async Telegram client library

Nest Asyncio – For running async functions in Flask

HTML5 & CSS3 – For the frontend structure and styling.

JavaScript – To handle interactive elements like the security modal, social FABs, and phone validation.

intl-tel-input – A JavaScript plugin for international telephone number input.

📦 Installation
Clone this repository:

git clone [https://github.com/MoGLCL/TeleGrouper.git](https://github.com/MoGLCL/TeleGrouper.git)
cd TeleGrouper

Create a virtual environment and activate it:

# For Linux / macOS
python3 -m venv venv
source venv/bin/activate

# For Windows
python -m venv venv
venv\Scripts\activate

Install dependencies:

pip install -r requirements.txt

▶️ How to Run
After installation, start the Flask application by running:

python app.py

The application will be accessible at http://127.0.0.1:5000.

📸 Screenshots
(A screenshot of the main login page, showing the input fields, animated background, and developer FABs)

🤝 Contributing
Contributions, issues, and feature requests are welcome! Feel free to check the issues page.

📄 License
This project is licensed under the MIT License. See the LICENSE file for more details.
