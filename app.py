import os
import sqlite3
from flask import Flask, request, redirect, render_template_string

app = Flask(__name__)

# Secret password and hidden admin route
ADMIN_PASSWORD = "EliteWash2026!"
SECRET_ADMIN_PATH = "/elite-admin-panel"
GOOGLE_BUSINESS_LINK = "https://share.google/CxgjWPXmTkbV3VZaz"

# --- CLOUDINARY CONFIGURATION ---
try:
    import cloudinary
    import cloudinary.uploader
    cloudinary.config( 
      cloud_name = "ple2ovph", 
      api_key = "775655745774232", 
      api_secret = "i-iRyEvgCTxrLBDGbYF3E8EvRkk",
      secure = True
    )
    HAS_CLOUDINARY = True
except ImportError:
    HAS_CLOUDINARY = False

# --- DATABASE SETUP ---
def init_db():
    conn = sqlite3.connect('laundry.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS media_posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            media_type TEXT NOT NULL,
            media_url TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# --- COMMON CSS STYLES ---
BASE_CSS = """
  :root {
    --primary: #0077b6;
    --primary-dark: #023e8a;
    --accent: #00b4d8;
    --bg-light: #f8fafc;
    --card-bg: #ffffff;
    --text-main: #0f172a;
    --text-muted: #475569;
  }

  * { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }
  html { scroll-behavior: smooth; }
  body { background-color: var(--bg-light); color: var(--text-main); line-height: 1.6; overflow-x: hidden; }

  /* Keyframe Animations */
  @keyframes float {
    0%, 100% { transform: translateY(0px); }
    50% { transform: translateY(-8px); }
  }

  @keyframes pulseGreenGlow {
    0% { box-shadow: 0 0 0 0 rgba(37, 211, 102, 0.5); }
    70% { box-shadow: 0 0 0 14px rgba(37, 211, 102, 0); }
    100% { box-shadow: 0 0 0 0 rgba(37, 211, 102, 0); }
  }

  @keyframes rippleEffect {
    0% { box-shadow: 0 0 0 0 rgba(0, 180, 216, 0.4), 0 0 0 10px rgba(0, 180, 216, 0.2); }
    50% { box-shadow: 0 0 0 15px rgba(0, 180, 216, 0.2), 0 0 0 25px rgba(0, 180, 216, 0); }
    100% { box-shadow: 0 0 0 0 rgba(0, 180, 216, 0), 0 0 0 0 rgba(0, 180, 216, 0); }
  }

  /* Hero Banner Background Slideshow Animation */
  @keyframes laundrySlideshow {
    0%, 28% {
      background-image: linear-gradient(rgba(2, 62, 138, 0.78), rgba(0, 119, 182, 0.82)),
                        url('https://images.unsplash.com/photo-1517677208171-0bc6725a3e60?auto=format&fit=crop&w=1200&q=80');
    }
    33%, 61% {
      background-image: linear-gradient(rgba(2, 62, 138, 0.78), rgba(0, 119, 182, 0.82)),
                        url('https://images.unsplash.com/photo-1545173168-9f1947eebb7f?auto=format&fit=crop&w=1200&q=80');
    }
    66%, 95% {
      background-image: linear-gradient(rgba(2, 62, 138, 0.78), rgba(0, 119, 182, 0.82)),
                        url('https://images.unsplash.com/photo-1582735689369-4fe89db7114c?auto=format&fit=crop&w=1200&q=80');
    }
    100% {
      background-image: linear-gradient(rgba(2, 62, 138, 0.78), rgba(0, 119, 182, 0.82)),
                        url('https://images.unsplash.com/photo-1517677208171-0bc6725a3e60?auto=format&fit=crop&w=1200&q=80');
    }
  }

  /* Header & Nav */
  .top-bar { background: var(--primary-dark); color: white; padding: 8px 15px; font-size: 0.85rem; text-align: center; }
  .top-bar a { color: #38bdf8; text-decoration: underline; font-weight: bold; margin-left: 6px; }
  
  header { background: white; box-shadow: 0 2px 10px rgba(0,0,0,0.05); position: sticky; top: 0; z-index: 1000; }
  .nav-container { max-width: 1100px; margin: 0 auto; display: flex; justify-content: space-between; align-items: center; padding: 15px; }
  .logo { font-size: 1.25rem; font-weight: 800; color: var(--primary-dark); text-decoration: none; }
  .btn-nav { background: var(--primary); color: white; padding: 9px 16px; border-radius: 8px; text-decoration: none; font-weight: 600; font-size: 0.85rem; animation: float 3s ease-in-out infinite; }

  /* Hero Section */
  .hero {
    animation: laundrySlideshow 15s infinite ease-in-out;
    background-size: cover;
    background-position: center;
    color: white; 
    padding: 75px 20px 85px; 
    text-align: center; 
    border-bottom-left-radius: 32px; 
    border-bottom-right-radius: 32px; 
    position: relative;
    transition: background-image 1s ease-in-out;
  }
  .hero h1 { 
    font-size: 2.3rem; 
    font-weight: 800; 
    margin-bottom: 15px; 
    line-height: 1.25; 
    animation: float 3.5s ease-in-out infinite; 
    text-shadow: 0 4px 10px rgba(0,0,0,0.3);
  }
  .hero p { 
    font-size: 1.1rem; 
    opacity: 0.95; 
    max-width: 620px; 
    margin: 0 auto 30px; 
    animation: float 4s ease-in-out infinite;
  }
  .hero-btns { display: flex; gap: 14px; justify-content: center; flex-wrap: wrap; }
  .btn-hero-primary { 
    background: white; 
    color: var(--primary-dark); 
    font-weight: bold; 
    padding: 14px 28px; 
    border-radius: 30px; 
    text-decoration: none; 
    animation: float 2.5s ease-in-out infinite, rippleEffect 2.5s infinite; 
  }
  .btn-hero-secondary { 
    border: 2px solid white; 
    color: white; 
    font-weight: bold; 
    padding: 12px 26px; 
    border-radius: 30px; 
    text-decoration: none; 
    animation: float 3.2s ease-in-out infinite;
  }

  /* Okpanam & Asaba Delivery Notice Banner */
  .delivery-notice-bar { 
    max-width: 900px; 
    margin: 25px auto 30px; 
    background: #e0f2fe; 
    border: 1px solid #bae6fd; 
    color: #0369a1; 
    padding: 14px 20px; 
    border-radius: 14px; 
    text-align: center; 
    font-weight: 600; 
    font-size: 0.95rem; 
    animation: float 4.2s ease-in-out infinite;
  }

  /* Container & Cards */
  .container { max-width: 1000px; margin: 0 auto 40px; padding: 0 15px; }
  .card { background: var(--card-bg); border-radius: 20px; padding: 30px; box-shadow: 0 8px 25px rgba(0,0,0,0.04); margin-bottom: 35px; }
  .section-title { text-align: center; margin-bottom: 28px; }
  .section-title h2 { font-size: 1.6rem; color: var(--primary-dark); }
  .section-title p { color: var(--text-muted); font-size: 0.95rem; }

  /* Booking Form Styles */
  .booking-form-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 18px; margin-bottom: 25px; }
  .form-group { display: flex; flex-direction: column; }
  .form-group label { font-size: 0.9rem; font-weight: 700; color: var(--primary-dark); margin-bottom: 6px; }
  .form-group input, .form-group select, .form-group textarea { padding: 12px; border: 1px solid #cbd5e1; border-radius: 8px; font-size: 0.95rem; outline: none; }
  .form-group input:focus, .form-group select:focus, .form-group textarea:focus { border-color: var(--primary); box-shadow: 0 0 0 3px rgba(0,119,182,0.15); }

  /* 4-Step Grid */
  .steps-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 18px; text-align: center; }
  .step-box { background: #f1f5f9; padding: 22px 14px; border-radius: 14px; border: 1px solid #e2e8f0; animation: float 5s ease-in-out infinite; }
  .step-number { background: var(--primary); color: white; width: 40px; height: 40px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: bold; margin: 0 auto 12px; animation: rippleEffect 3.5s infinite; }

  /* Item Quantities */
  .calculator-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 12px; }
  .item-row { display: flex; justify-content: space-between; align-items: center; padding: 12px 15px; background: #f8fafc; border-radius: 10px; border: 1px solid #e2e8f0; }
  .item-row input[type="number"] { width: 65px; padding: 6px; font-size: 0.95rem; text-align: center; border: 1px solid #cbd5e1; border-radius: 6px; }
  .total-container { text-align: center; margin-top: 25px; padding-top: 20px; border-top: 2px dashed #cbd5e1; }
  .total-price { font-size: 2.2rem; color: var(--primary); font-weight: 800; margin: 8px 0 18px; }
  .btn-whatsapp { background: #25d366; color: white; border: none; padding: 16px; font-size: 1.05rem; font-weight: bold; border-radius: 12px; width: 100%; max-width: 420px; cursor: pointer; animation: float 3s ease-in-out infinite, pulseGreenGlow 2s infinite; }

  /* Media Feed */
  .media-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 20px; }
  .media-card { background: white; border-radius: 14px; overflow: hidden; border: 1px solid #e2e8f0; }
  .media-wrapper { width: 100%; height: 250px; background: #000; }
  .media-wrapper video, .media-wrapper img { width: 100%; height: 100%; object-fit: contain; }
  .media-info { padding: 15px; }

  /* Legal Page Styling */
  .legal-page { max-width: 850px; margin: 30px auto; background: white; padding: 35px; border-radius: 16px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); }
  .legal-page h1 { color: var(--primary-dark); margin-bottom: 15px; border-bottom: 2px solid #e2e8f0; padding-bottom: 10px; }
  .legal-page h2 { color: var(--primary); margin: 20px 0 10px; font-size: 1.2rem; }
  .legal-page p, .legal-page li { font-size: 0.95rem; color: var(--text-muted); margin-bottom: 12px; }
  .btn-maps { display: inline-block; background: #ea4335; color: white; padding: 10px 18px; border-radius: 8px; text-decoration: none; font-weight: bold; margin-top: 10px; }

  /* Footer */
  footer { background: #0f172a; color: white; padding: 40px 20px 20px; }
  .footer-content { max-width: 950px; margin: 0 auto 30px; display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 25px; }
  .footer-section h4 { color: var(--accent); margin-bottom: 12px; font-size: 0.95rem; text-transform: uppercase; letter-spacing: 0.5px; }
  .footer-section ul { list-style: none; }
  .footer-section ul li { margin-bottom: 8px; }
  .footer-section ul li a { color: #94a3b8; text-decoration: none; font-size: 0.88rem; }
  .footer-section ul li a:hover { color: white; }
  .footer-bottom { border-top: 1px solid #334155; max-width: 950px; margin: 0 auto; padding-top: 20px; text-align: center; font-size: 0.8rem; color: #64748b; }

  /* Floating WhatsApp Widget */
  .floating-whatsapp-widget { position: fixed; bottom: 20px; right: 20px; background: #25d366; color: white; width: 58px; height: 58px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 28px; text-decoration: none; box-shadow: 0 4px 15px rgba(0,0,0,0.25); z-index: 9999; animation: float 2.5s ease-in-out infinite, pulseGreenGlow 2s infinite; }
"""

# --- MAIN PAGE TEMPLATE ---
MAIN_HTML = f"""
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>ELITE WASH & FOLD | Laundry Marketplace</title>
  <style>{BASE_CSS}</style>
</head>
<body>

  <a href="https://wa.me/2347061270962?text=Hello%20ELITE%20WASH%20%26%20FOLD!" target="_blank" class="floating-whatsapp-widget">💬</a>

  <div class="top-bar">
    📍 SMAK SHOPPING PLAZA, OPP THE CONVENT, OKPANAM BY PASS | <a href="{GOOGLE_BUSINESS_LINK}" target="_blank">View on Google Maps 📍</a>
  </div>

  <header>
    <div class="nav-container">
      <a href="/" class="logo">🧼 ELITE WASH & FOLD</a>
      <a href="#booking" class="btn-nav">Book Pickup</a>
    </div>
  </header>

  <!-- Hero Section -->
  <section class="hero">
    <h1>Freshly Cleaned.<br>Carefully Delivered.</h1>
    <p>Experience the joy of receiving perfectly cleaned and neatly folded clothes right at your doorstep.</p>
    <div class="hero-btns">
      <a href="#booking" class="btn-hero-primary">Book a Pickup</a>
      <a href="#gallery" class="btn-hero-secondary">Watch Videos</a>
    </div>
  </section>

  <!-- Delivery Coverage Notice -->
  <div class="delivery-notice-bar">
    🚚 Fast Doorstep Pickup & Delivery available across <strong>Okpanam</strong> and <strong>Asaba</strong>!
  </div>

  <main class="container">

    <!-- 4-STEP PROCESS -->
    <section class="card">
      <div class="section-title">
        <h2>From your door to your closet</h2>
        <p>Four easy steps to hassle-free laundry</p>
      </div>
      <div class="steps-grid">
        <div class="step-box"><div class="step-number">01</div><h3>Book Online</h3><p>Select your items and schedule your pickup time online.</p></div>
        <div class="step-box"><div class="step-number">02</div><h3>We Collect</h3><p>Our driver collects your laundry right from your doorstep.</p></div>
        <div class="step-box"><div class="step-number">03</div><h3>We Clean</h3><p>Garments are washed, dried, and ironed professionally.</p></div>
        <div class="step-box"><div class="step-number">04</div><h3>Delivered Fresh</h3><p>Neatly packaged laundry delivered back to your home.</p></div>
      </div>
    </section>

    <!-- BOOKING / ORDER FORM SECTION -->
    <section class="card" id="booking">
      <div class="section-title">
        <h2>Booking / Order Form</h2>
        <p>Fill in your details and select your laundry items to order via WhatsApp</p>
      </div>

      <!-- Customer Contact & Delivery Info -->
      <div class="booking-form-grid">
        <div class="form-group">
          <label for="cust_name">Full Name *</label>
          <input type="text" id="cust_name" placeholder="e.g. Chukwuma Obi" required>
        </div>

        <div class="form-group">
          <label for="cust_phone">Phone Number *</label>
          <input type="tel" id="cust_phone" placeholder="e.g. 08012345678" required>
        </div>

        <div class="form-group">
          <label for="cust_address">Delivery Address (Okpanam / Asaba) *</label>
          <input type="text" id="cust_address" placeholder="e.g. No 12 Okpanam Road, Asaba" required>
        </div>

        <div class="form-group">
          <label for="pickup_date">Pickup Date *</label>
          <input type="date" id="pickup_date" required>
        </div>

        <div class="form-group">
          <label for="service_type">Choose Service *</label>
          <select id="service_type">
            <option value="Wash & Fold">Wash & Fold</option>
            <option value="Wash & Iron">Wash & Iron</option>
            <option value="Dry Cleaning">Dry Cleaning</option>
            <option value="Express Same-Day Service">Express Same-Day Service</option>
          </select>
        </div>

        <div class="form-group">
          <label for="approx_clothes">Approx. Number of Clothes *</label>
          <input type="number" id="approx_clothes" placeholder="e.g. 10" min="1">
        </div>
      </div>

      <hr style="border: 0; border-top: 1px solid #e2e8f0; margin: 25px 0;">

      <!-- Itemized Calculator -->
      <h3 style="color: var(--primary-dark); margin-bottom: 15px; text-align: center;">Select Clothes Breakdown</h3>
      <div class="calculator-grid">
        <div class="item-row"><label>Polo (White) - ₦800</label><input type="number" class="item-qty" data-name="Polo (White)" data-price="800" min="0" value="0" onchange="calculateTotal()"></div>
        <div class="item-row"><label>Polo (Coloured) - ₦600</label><input type="number" class="item-qty" data-name="Polo (Coloured)" data-price="600" min="0" value="0" onchange="calculateTotal()"></div>
        <div class="item-row"><label>Short Jeans - ₦700</label><input type="number" class="item-qty" data-name="Short Jeans" data-price="700" min="0" value="0" onchange="calculateTotal()"></div>
        <div class="item-row"><label>Long Jeans - ₦800</label><input type="number" class="item-qty" data-name="Long Jeans" data-price="800" min="0" value="0" onchange="calculateTotal()"></div>
        <div class="item-row"><label>Boxers / Singlet - ₦400</label><input type="number" class="item-qty" data-name="Boxers / Singlet" data-price="400" min="0" value="0" onchange="calculateTotal()"></div>
        <div class="item-row"><label>Gown - ₦800</label><input type="number" class="item-qty" data-name="Gown" data-price="800" min="0" value="0" onchange="calculateTotal()"></div>
        <div class="item-row"><label>Two-Piece (Up & Down) - ₦1,000</label><input type="number" class="item-qty" data-name="Two-Piece (Up & Down)" data-price="1000" min="0" value="0" onchange="calculateTotal()"></div>
        <div class="item-row"><label>Express Service (+₦2,000/item)</label><input type="number" class="item-qty" data-name="Express Fee" data-price="2000" min="0" value="0" onchange="calculateTotal()"></div>
      </div>

      <div class="total-container">
        <p style="font-weight: bold; color: var(--text-muted);">Estimated Total:</p>
        <div class="total-price" id="total-price">₦0</div>
        <button class="btn-whatsapp" onclick="sendWhatsAppOrder()">📲 Send Booking via WhatsApp</button>
      </div>
    </section>

    <!-- CLOUDINARY MEDIA FEED -->
    <section class="card" id="gallery">
      <div class="section-title">
        <h2>Store Gallery & Live Videos</h2>
        <p>Watch clips showing how we handle and wash clothes</p>
      </div>

      {{% if posts %}}
        <div class="media-grid">
          {{% for post in posts %}}
            <div class="media-card">
              <div class="media-wrapper">
                {{% if post[3] == 'image' %}}
                  <img src="{{{{ post[4] }}}}" alt="{{{{ post[1] }}}}">
                {{% elif post[3] == 'video' %}}
                  <video controls preload="metadata">
                    <source src="{{{{ post[4] }}}}">
                  </video>
                {{% endif %}}
              </div>
              <div class="media-info">
                <h3>{{{{ post[1] }}}}</h3>
                <p>{{{{ post[2] }}}}</p>
                <small style="color: #94a3b8;">Posted: {{{{ post[5] }}}}</small>
              </div>
            </div>
          {{% endfor %}}
        </div>
      {{% else %}}
        <p style="text-align: center; color: #64748b; padding: 25px 0;">Our store videos are coming soon!</p>
      {{% endif %}}
    </section>

  </main>

  <footer>
    <div class="footer-content">
      <div class="footer-section">
        <h4>Services</h4>
        <ul>
          <li><a href="#booking">Laundry Booking</a></li>
          <li><a href="#booking">Pickup & Delivery (Okpanam & Asaba)</a></li>
          <li><a href="#booking">Express Cleaning</a></li>
        </ul>
      </div>
      <div class="footer-section">
        <h4>Location & Maps</h4>
        <ul>
          <li><a href="{GOOGLE_BUSINESS_LINK}" target="_blank">📍 Open in Google Maps</a></li>
        </ul>
      </div>
      <div class="footer-section">
        <h4>Help & Legal</h4>
        <ul>
          <li><a href="/faq">FAQ</a></li>
          <li><a href="/contact">Contact Us</a></li>
          <li><a href="/privacy-policy">Privacy Policy</a></li>
          <li><a href="/terms-of-service">Terms of Service</a></li>
        </ul>
      </div>
    </div>
    <div class="footer-bottom">
      &copy; 2026 ELITE WASH & FOLD Ltd. All rights reserved. | Serving Okpanam & Asaba, Delta State.
    </div>
  </footer>

  <script>
    function calculateTotal() {{
      let inputs = document.querySelectorAll('.item-qty');
      let total = 0;
      inputs.forEach(input => {{
        let count = parseInt(input.value) || 0;
        let price = parseInt(input.getAttribute('data-price'));
        total += count * price;
      }});
      document.getElementById('total-price').innerText = '₦' + total.toLocaleString();
    }}

    function sendWhatsAppOrder() {{
      let name = document.getElementById('cust_name').value.trim();
      let phone = document.getElementById('cust_phone').value.trim();
      let address = document.getElementById('cust_address').value.trim();
      let pickupDate = document.getElementById('pickup_date').value;
      let service = document.getElementById('service_type').value;
      let approxClothes = document.getElementById('approx_clothes').value;

      if (!name || !phone || !address || !pickupDate) {{
        alert("Please complete your Name, Phone, Address, and Pickup Date.");
        return;
      }}

      let inputs = document.querySelectorAll('.item-qty');
      let orderDetails = `*NEW LAUNDRY BOOKING*%0A%0A`;
      orderDetails += `👤 *Name:* ${{encodeURIComponent(name)}}%0A`;
      orderDetails += `📞 *Phone:* ${{encodeURIComponent(phone)}}%0A`;
      orderDetails += `📍 *Address:* ${{encodeURIComponent(address)}}%0A`;
      orderDetails += `📅 *Pickup Date:* ${{encodeURIComponent(pickupDate)}}%0A`;
      orderDetails += `🧺 *Service:* ${{encodeURIComponent(service)}}%0A`;
      if (approxClothes) {{
        orderDetails += `👕 *Total Clothes Count:* ${{encodeURIComponent(approxClothes)}}%0A`;
      }}
      orderDetails += `%0A*CLOTHES BREAKDOWN:*%0A`;

      let hasItems = false;
      let total = 0;

      inputs.forEach(input => {{
        let count = parseInt(input.value) || 0;
        if (count > 0) {{
          hasItems = true;
          let itemName = input.getAttribute('data-name');
          let price = parseInt(input.getAttribute('data-price'));
          let itemTotal = count * price;
          total += itemTotal;
          orderDetails += `• ${{encodeURIComponent(itemName)}}: ${{count}} pcs (₦${{itemTotal.toLocaleString()}})%0A`;
        }}
      }});

      if (total > 0) {{
        orderDetails += `%0A*Estimated Total:* ₦${{total.toLocaleString()}}`;
      }}

      window.open(`https://wa.me/2347061270962?text=${{orderDetails}}`, '_blank');
    }}
  </script>
</body>
</html>
"""

# --- LEGAL & POLICY PAGE TEMPLATE ---
LEGAL_PAGE_HTML = f"""
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>(( title )) | ELITE WASH & FOLD</title>
  <style>{BASE_CSS}</style>
</head>
<body>
  <header>
    <div class="nav-container">
      <a href="/" class="logo">🧼 ELITE WASH & FOLD</a>
      <a href="/" class="btn-nav">← Back to Home</a>
    </div>
  </header>

  <div class="legal-page">
    <h1>(( title ))</h1>
    (( content | safe ))
  </div>

  <footer>
    <div class="footer-bottom">
      &copy; 2026 ELITE WASH & FOLD Ltd. All rights reserved.
    </div>
  </footer>
</body>
</html>
"""

# --- ADMIN PANEL TEMPLATE ---
ADMIN_HTML = f"""
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Admin Media Upload</title>
  <style>
    body {{ font-family: Arial, sans-serif; background: #0f172a; color: white; padding: 20px; }}
    .box {{ max-width: 450px; margin: 30px auto; background: #1e293b; padding: 25px; border-radius: 12px; }}
    h2 {{ color: #38bdf8; text-align: center; margin-bottom: 20px; }}
    label {{ font-size: 0.85rem; color: #94a3b8; display: block; margin-top: 10px; margin-bottom: 4px; }}
    input, select, textarea {{ width: 100%; padding: 12px; border-radius: 6px; border: 1px solid #334155; background: #0f172a; color: white; box-sizing: border-box; }}
    button {{ background: #38bdf8; color: #0f172a; font-weight: bold; padding: 12px; width: 100%; border: none; border-radius: 6px; margin-top: 20px; cursor: pointer; }}
    .error {{ color: #f87171; text-align: center; margin-bottom: 10px; }}
  </style>
</head>
<body>
  <div class="box">
    <h2>Upload Media to Gallery</h2>
    {{% if error %}}<p class="error">{{{{ error }}}}</p>{{% endif %}}
    <form action="/upload-media" method="POST" enctype="multipart/form-data">
      <label>Admin Password</label>
      <input type="password" name="password" required>

      <label>Post Title</label>
      <input type="text" name="title" placeholder="e.g. Ironing two-piece outfit" required>

      <label>Description</label>
      <textarea name="description" rows="3"></textarea>

      <label>Media Type</label>
      <select name="media_type">
        <option value="video">Video (MP4 / MOV)</option>
        <option value="image">Image (Photo)</option>
      </select>

      <label>Pick File from Gallery</label>
      <input type="file" name="media_file" accept="image/*,video/*" required>

      <button type="submit">Upload File</button>
    </form>
  </div>
</body>
</html>
"""

# --- ROUTES ---

@app.route('/')
def home():
    conn = sqlite3.connect('laundry.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, description, media_type, media_url, created_at FROM media_posts ORDER BY id DESC")
    posts = cursor.fetchall()
    conn.close()
    return render_template_string(MAIN_HTML, posts=posts)

@app.route('/privacy-policy')
def privacy_policy():
    content = """
    <p>Last updated: September 2026</p>
    <h2>1. Information We Collect</h2>
    <p>We collect personal information that you voluntarily provide to us when placing a laundry pickup order, including your name, phone number, delivery address, and garment specifications.</p>
    <h2>2. How We Use Your Information</h2>
    <p>Your details are strictly used to fulfill your laundry orders, communicate pickup/delivery status updates via WhatsApp, and improve our services across Okpanam and Asaba.</p>
    <h2>3. Data Protection</h2>
    <p>We do not sell or rent your personal information to third parties. All order transactions and communications are processed securely.</p>
    """
    return render_template_string(LEGAL_PAGE_HTML.replace('(( title ))', 'Privacy Policy').replace('(( content | safe ))', content))

@app.route('/terms-of-service')
def terms_of_service():
    content = """
    <h2>1. Service Agreement</h2>
    <p>By scheduling a laundry pickup with ELITE WASH & FOLD, you agree to our processing terms. Garments are handled with high professional care according to care label specifications.</p>
    <h2>2. Pickup & Delivery</h2>
    <p>We provide doorstep pickup and delivery across Okpanam and Asaba. Customers must ensure garments are ready at the designated pickup slot.</p>
    """
    return render_template_string(LEGAL_PAGE_HTML.replace('(( title ))', 'Terms of Service').replace('(( content | safe ))', content))

@app.route('/faq')
def faq():
    content = """
    <h2>Frequently Asked Questions</h2>
    <p><strong>Q: Where do you deliver?</strong><br>A: We provide full pickup and delivery coverage across all areas in Okpanam and Asaba.</p>
    <p><strong>Q: How long does standard washing take?</strong><br>A: Standard orders are delivered within 24 to 48 hours.</p>
    <p><strong>Q: Do you offer express same-day washing?</strong><br>A: Yes! Select the Express option on our order menu for same-day service.</p>
    """
    return render_template_string(LEGAL_PAGE_HTML.replace('(( title ))', 'Frequently Asked Questions (FAQ)').replace('(( content | safe ))', content))

@app.route('/contact')
def contact():
    content = f"""
    <h2>Get in Touch</h2>
    <p><strong>Store Address:</strong> SMAK SHOPPING PLAZA, OPP THE CONVENT, OKPANAM BY PASS, OKPANAM, Asaba 320242, Delta State</p>
    <p><strong>Phone / WhatsApp:</strong> 07061270962</p>
    <p><strong>Coverage Areas:</strong> Okpanam and Asaba</p>
    <p><strong>Operating Hours:</strong> Monday – Saturday: 8:00 AM – 8:00 PM</p>
    <br>
    <a href="{GOOGLE_BUSINESS_LINK}" target="_blank" class="btn-maps">📍 Open Store on Google Maps</a>
    """
    return render_template_string(LEGAL_PAGE_HTML.replace('(( title ))', 'Contact Us').replace('(( content | safe ))', content))

@app.route(SECRET_ADMIN_PATH)
def secret_admin():
    return render_template_string(ADMIN_HTML)

@app.route('/upload-media', methods=['POST'])
def upload_media():
    pwd = request.form.get('password')
    title = request.form.get('title')
    description = request.form.get('description')
    media_type = request.form.get('media_type')

    if pwd != ADMIN_PASSWORD:
        return render_template_string(ADMIN_HTML, error="Incorrect Password!")

    if 'media_file' not in request.files:
        return render_template_string(ADMIN_HTML, error="No file attached!")

    file = request.files['media_file']

    if file.filename == '':
        return render_template_string(ADMIN_HTML, error="No file selected!")

    try:
        if HAS_CLOUDINARY:
            upload_result = cloudinary.uploader.upload(file, resource_type="video" if media_type == "video" else "image")
            media_url = upload_result.get('secure_url')
        else:
            media_url = "https://images.unsplash.com/photo-1517677208171-0bc6725a3e60?w=600"

        conn = sqlite3.connect('laundry.db')
        cursor = conn.cursor()
        cursor.execute("INSERT INTO media_posts (title, description, media_type, media_url) VALUES (?, ?, ?, ?)",
                       (title, description, media_type, media_url))
        conn.commit()
        conn.close()

        return redirect('/')

    except Exception as e:
        return render_template_string(ADMIN_HTML, error=f"Upload Failed: {str(e)}")

if __name__ == '__main__':
    print("-------------------------------------------------------")
    print("Server starting... Open http://127.0.0.1:5000 in Chrome")
    print("-------------------------------------------------------")
    app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)