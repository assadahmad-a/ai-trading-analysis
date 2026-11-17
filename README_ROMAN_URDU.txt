AI TRADING ANALYSIS WEB APP - V1
=================================

Yeh mobile-friendly web app hai. Android Chrome se open ho sakti hai aur
"Add to Home screen" karke app jaisi shortcut ban sakti hai.

IMPORTANT:
- Forex analysis Twelve Data ke 1-minute OHLC candles par rule-based hai.
- Is version mein trained AI/ML model nahi; EMA 9/21, RSI 14 aur MACD rules hain.
- Score (e.g. 2/3) confidence percentage nahi hota.
- Quotex OTC ke liye verified official public API/feed configured nahi. OTC option
  filhal UNAVAILABLE show karta hai; koi fake signal nahi banata.
- Yeh next candle ki guarantee nahi deta aur trade execute nahi karta.
- Twelve Data Basic free plan has daily/minute credit restrictions and trial-symbol
  limitations. Check your own account's symbol access and data terms.
- Render free web services sleep after 15 minutes without inbound traffic and may
  restart; this is a demo/testing host, not reliable 24/7 live signal hosting.

DEPLOY (PHONE SE):
1) GitHub par account banayein aur new repository create karein.
2) ZIP ke andar ki tamam files repository mein upload karein.
3) Render.com par sign up karein, New > Blueprint ya Web Service choose karein,
   GitHub repo connect karein.
4) Environment variable add karein:
   TWELVE_DATA_API_KEY = apni Twelve Data key
5) Deploy complete hone par Render URL Chrome mein kholein.
6) Chrome menu > Add to Home screen.

API KEY:
Twelve Data: https://twelvedata.com/
API key ko HTML ya public GitHub files mein kabhi paste na karein. Sirf Render
Environment Variables mein add karein.

LOCAL TEST (computer required):
pip install -r requirements.txt
set TWELVE_DATA_API_KEY=your_key
uvicorn main:app --reload

Hosting aur API account aapke apne honge. ZIP ko deploy karne se pehle apni key
khud add karni hogi. Free hosting always-on guarantee nahi deti.
