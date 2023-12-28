def bot_welcome(name):
    return f"""
👋 Welcome to RapidNotifyBot!

Hey {name}! 🌟

Get ready to supercharge your notification experience with RapidNotifyBot – your ultimate notification companion! We're not just about keeping you in the loop; we're here to elevate your notification game to new heights! 🚀

🔔 **Key Features:**
- **Instant Notifications:** Receive lightning-fast alerts on Telegram for seamless updates.
- **Customizable Alerts:** Tailor notifications to match your preferences.
- **Real-time Updates:** Stay connected and informed with timely notifications.

✨ **How to Get Started:**
- Use /subscribe to obtain your personalized API key.

🌐 **Connect with Us:**
Have questions or brilliant suggestions? Reach out to our support team via t.me/amitdas99. Your feedback is the secret sauce in making RapidNotifyBot even more awesome!

🚀 **Ready to Dive In?**
Type /help to access our command list and unveil the plethora of amazing features at your fingertips.

Thank you for choosing RapidNotifyBot! We're here to simplify your life and keep you organized. Happy notifying! 🚀✉️

Best regards,
The RapidNotifyBot Team
"""


def bot_help(name):
    return f"""
👋 Need Help? We've Got Your Back!

Hello {name}! 🌟

If you ever find yourself in a bit of a pickle or just want to explore the full potential of RapidNotifyBot, you're in the right place! Our support team is here to assist you every step of the way.

🛠️ **How We Can Help:**
   - **Technical Assistance:** Encountering issues? We'll troubleshoot with you.
   - **Feature Exploration:** Learn how to make the most of RapidNotifyBot's capabilities.
   - **General Inquiries:** Have questions? We've got answers!

💡 **Quick Tips:**
   - /start - Begin your RapidNotifyBot journey.
   - /help - Access the command list and get assistance.
   - /subscribe - Obtain your personalized API key.

🌐 **Connect with Us:**
Your feedback and questions are valuable to us. Don't hesitate to reach out via t.me/amitdas99. – we're here to make your RapidNotifyBot experience smooth and enjoyable!

Thank you for choosing RapidNotifyBot! We're committed to ensuring you have the best experience possible. Happy exploring! 🚀✉️

Best regards,
The RapidNotifyBot Team
"""


def bot_subscribe(name, api_key):
    return f"""
🌟 **Thank You for Subscribing to RapidNotifyBot!**

Hello {name}! We appreciate you joining the RapidNotifyBot community. Your personalized API key is ready to roll! 🎉

🔑 **Your API Key:**
API Key: {api_key}


✨ **How to Get Started:**
To receive notifications via telegram, send a POST request with your API key in the message body. Here's an example using cURL:
```bash
curl -X POST -d "api_key=[YourAPIKey]" [YourAPIEndpoint]
```
Replace [YourAPIKey] with your generated API key and [YourAPIEndpoint] with your API endpoint.

🌐 Connect with Us:
Have any questions or need assistance? Reach out to our support team via t.me/amitdas99. We're here to ensure you make the most of RapidNotifyBot!

🎉 Ready to Get Notified?
Simply use your API key in your POST requests and let the notifications flow. Thank you for choosing RapidNotifyBot. Happy notifying! 🚀✉️

Best regards,
The RapidNotifyBot Team
"""
