require('dotenv').config();
const express = require('express');
const path = require('path');
const fs = require('fs');
const crypto = require('crypto');
const bcrypt = require('bcryptjs');
const jwt = require('jsonwebtoken');
const multer = require('multer');
const helmet = require('helmet');
const compression = require('compression');
const rateLimit = require('express-rate-limit');
const nodemailer = require('nodemailer');

let Anthropic, anthropic;
try {
  Anthropic = require('@anthropic-ai/sdk');
  if (process.env.ANTHROPIC_API_KEY) {
    anthropic = new Anthropic({ apiKey: process.env.ANTHROPIC_API_KEY });
    console.log('[INIT] Anthropic SDK loaded, API key set');
  } else {
    console.log('[INIT] Anthropic SDK loaded, but no ANTHROPIC_API_KEY env var');
  }
} catch (e) {
  console.log('[INIT] Anthropic SDK not available:', e.message);
}

const app = express();
const PORT = process.env.PORT || 3000;
const DATA_DIR = process.env.RAILWAY_VOLUME_MOUNT_PATH || process.env.DATA_PATH || path.join(__dirname, 'data');
const SEED_DIR = path.join(__dirname, 'data');
const UPLOADS_DIR = process.env.UPLOADS_PATH || (process.env.RAILWAY_VOLUME_MOUNT_PATH ? path.join(process.env.RAILWAY_VOLUME_MOUNT_PATH, 'uploads') : path.join(__dirname, 'public', 'uploads'));

// B4: JWT_SECRET — use random fallback so sessions expire on restart (forces admin to set env var)
if (!process.env.JWT_SECRET) {
  console.warn('[SECURITY] JWT_SECRET env var not set! Using a random secret — all admin sessions will be invalidated on every server restart. Add JWT_SECRET to Railway Variables immediately.');
}
const JWT_SECRET = process.env.JWT_SECRET || crypto.randomBytes(32).toString('hex');

// Ensure directories exist
if (!fs.existsSync(DATA_DIR)) fs.mkdirSync(DATA_DIR, { recursive: true });
if (!fs.existsSync(UPLOADS_DIR)) fs.mkdirSync(UPLOADS_DIR, { recursive: true });

// Seed persistent volume from git data on first deploy (if volume is empty)
if (DATA_DIR !== SEED_DIR && fs.existsSync(SEED_DIR)) {
  for (const file of fs.readdirSync(SEED_DIR)) {
    const dest = path.join(DATA_DIR, file);
    if (!fs.existsSync(dest)) {
      fs.copyFileSync(path.join(SEED_DIR, file), dest);
      console.log(`[INIT] Seeded ${file} to persistent storage`);
    }
  }
}

// Multer config for image uploads
const storage = multer.diskStorage({
  destination: (req, file, cb) => cb(null, UPLOADS_DIR),
  filename: (req, file, cb) => {
    const ext = path.extname(file.originalname).toLowerCase();
    cb(null, 'prod-' + Date.now() + ext);
  }
});
const upload = multer({
  storage,
  limits: { fileSize: 5 * 1024 * 1024 },
  fileFilter: (req, file, cb) => {
    const allowed = ['.jpg', '.jpeg', '.png', '.gif', '.webp'];
    const ext = path.extname(file.originalname).toLowerCase();
    if (allowed.includes(ext)) cb(null, true);
    else cb(new Error('Only jpg, png, gif, webp images are allowed'));
  }
});

app.use(compression());
// IMPORTANT: Do NOT change these Helmet settings without testing Google & Facebook login.
// crossOriginOpenerPolicy MUST be false — setting it to 'same-origin' will break
// Firebase signInWithPopup for both Google and Facebook by killing window.opener
// in the OAuth popup, causing silent auth failures.
app.use(helmet({
  contentSecurityPolicy: {
    directives: {
      defaultSrc: ["'self'"],
      scriptSrc: ["'self'", "'unsafe-inline'", "https://www.gstatic.com", "https://cdn.jsdelivr.net", "https://apis.google.com", "https://connect.facebook.net"],
      scriptSrcAttr: ["'unsafe-inline'"],
      styleSrc: ["'self'", "'unsafe-inline'", "https://fonts.googleapis.com"],
      fontSrc: ["'self'", "https://fonts.gstatic.com"],
      imgSrc: ["'self'", "data:", "blob:", "https:"],
      connectSrc: ["'self'", "https://identitytoolkit.googleapis.com", "https://securetoken.googleapis.com", "https://www.googleapis.com", "https://firebase.googleapis.com", "https://firebaseinstallations.googleapis.com", "https://whitelabel-ai-production.up.railway.app"],
      frameSrc: ["https://accounts.google.com", "https://www.facebook.com", "https://web.facebook.com", "https://maps.google.com"],
      objectSrc: ["'none'"],
      baseUri: ["'self'"],
      formAction: ["'self'"],
      upgradeInsecureRequests: null
    }
  },
  crossOriginEmbedderPolicy: false,
  crossOriginOpenerPolicy: false
}));
app.use(express.json({ limit: '10mb' }));

// H2: Rate limiters
const loginLimiter = rateLimit({
  windowMs: 15 * 60 * 1000,
  max: 10,
  standardHeaders: true,
  legacyHeaders: false,
  message: { error: 'Too many login attempts. Try again in 15 minutes.' }
});
const orderLimiter = rateLimit({
  windowMs: 10 * 60 * 1000,
  max: 5,
  standardHeaders: true,
  legacyHeaders: false,
  message: { error: 'Too many orders submitted. Try again later.' }
});
const contactLimiter = rateLimit({
  windowMs: 60 * 60 * 1000,
  max: 5,
  standardHeaders: true,
  legacyHeaders: false,
  message: { error: 'Too many messages sent. Try again in an hour.' }
});

// Static files: long cache for assets, no-cache for HTML so updates show immediately
const assetCacheOptions = { maxAge: '7d', etag: true, lastModified: true };
app.use(express.static(path.join(__dirname, 'public'), {
  etag: true, lastModified: true,
  setHeaders(res, filePath) {
    if (filePath.endsWith('.html')) {
      res.setHeader('Cache-Control', 'no-cache, must-revalidate');
    } else {
      res.setHeader('Cache-Control', 'public, max-age=604800');
    }
  }
}));
// M9: Always serve /uploads from UPLOADS_DIR (not just when UPLOADS_PATH is set)
app.use('/uploads', express.static(UPLOADS_DIR, assetCacheOptions));

// ── Helpers ──────────────────────────────────────────────────────

// In-memory cache to avoid reading from disk on every request
const jsonCache = {};

function readJSON(filename) {
  if (jsonCache[filename]) return JSON.parse(JSON.stringify(jsonCache[filename]));
  const file = path.join(DATA_DIR, filename);
  try {
    const data = JSON.parse(fs.readFileSync(file, 'utf8'));
    jsonCache[filename] = data;
    return JSON.parse(JSON.stringify(data));
  } catch { return []; }
}

function writeJSON(filename, data) {
  const json = JSON.stringify(data, null, 2);
  jsonCache[filename] = JSON.parse(json);
  fs.writeFileSync(path.join(DATA_DIR, filename), json);
}

function appendToFile(filename, entry) {
  const arr = readJSON(filename);
  arr.push({ ...entry, timestamp: new Date().toISOString() });
  writeJSON(filename, arr);
  return arr[arr.length - 1];
}

// H5: Strip HTML tags, encode dangerous chars, and trim/limit string length to prevent XSS in stored data
function sanitizeInput(str, maxLen = 500) {
  if (typeof str !== 'string') return str;
  return str
    .replace(/<[^>]*>?/g, '')       // strip HTML tags (including unclosed)
    .replace(/&/g, '&amp;')         // encode ampersand first
    .replace(/</g, '&lt;')          // encode any remaining angle brackets
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#x27;')
    .trim()
    .slice(0, maxLen);
}

// H1: CSRF protection — require custom header on public state-changing endpoints
// Browser fetch() can set this; plain HTML form submissions and cross-origin requests cannot
function csrfCheck(req, res, next) {
  if (req.get('X-Requested-With') !== 'XMLHttpRequest') {
    return res.status(403).json({ error: 'Invalid request' });
  }
  next();
}

// ── Points System Helpers ────────────────────────────────────────

function readPoints() {
  const data = readJSON('points.json');
  return Array.isArray(data) ? {} : data;
}

function getCustomerPoints(uid) {
  const points = readPoints();
  if (!points[uid]) return { balance: 0, history: [] };
  return points[uid];
}

function creditPoints(uid, amount, note, meta) {
  const points = readPoints();
  if (!points[uid]) points[uid] = { balance: 0, history: [] };
  points[uid].balance += amount;
  points[uid].history.push({
    type: 'earn',
    points: amount,
    note: note || '',
    ...meta,
    ts: new Date().toISOString()
  });
  writeJSON('points.json', points);
  return points[uid];
}

function redeemPoints(uid, pointsToRedeem, note, meta) {
  const points = readPoints();
  if (!points[uid] || points[uid].balance < pointsToRedeem) return null;
  points[uid].balance -= pointsToRedeem;
  points[uid].history.push({
    type: 'redeem',
    points: pointsToRedeem,
    pesoValue: pointsToRedeem / 100,
    note: note || '',
    ...meta,
    ts: new Date().toISOString()
  });
  writeJSON('points.json', points);
  return points[uid];
}

function generateQRToken(uid) {
  const hmac = crypto.createHmac('sha256', JWT_SECRET).update(uid).digest('hex');
  return uid + ':' + hmac;
}

function verifyQRToken(token) {
  const parts = token.split(':');
  if (parts.length < 2) return null;
  const uid = parts.slice(0, -1).join(':');
  const sig = parts[parts.length - 1];
  const expected = crypto.createHmac('sha256', JWT_SECRET).update(uid).digest('hex');
  if (sig !== expected) return null;
  return uid;
}

function deriveStockStatus(stock) {
  if (typeof stock === 'string') {
    return stock === 'in' ? 'in' : stock === 'low' ? 'low' : 'out';
  }
  const n = Number(stock);
  if (isNaN(n) || n <= 0) return 'out';
  if (n <= 10) return 'low';
  return 'in';
}

// ── Inventory & Audit Log Helpers ─────────────────────────────────

function logInventory(productId, productName, type, qty, prevStock, newStock, note, by) {
  const entry = {
    id: 'inv-' + Date.now(),
    productId, productName, type, qty, prevStock, newStock,
    note: note || '', by: by || 'system',
    timestamp: new Date().toISOString()
  };
  const log = readJSON('inventory-log.json');
  log.push(entry);
  writeJSON('inventory-log.json', log);
}

function logAudit(action, target, details, by) {
  const entry = {
    action, target: target || '',
    details: details || '', by: by || 'system',
    timestamp: new Date().toISOString()
  };
  const log = readJSON('audit.json');
  log.push(entry);
  writeJSON('audit.json', log);
}

// ── Auth Middleware ───────────────────────────────────────────────

function authMiddleware(req, res, next) {
  const authHeader = req.headers.authorization;
  if (!authHeader || !authHeader.startsWith('Bearer ')) {
    return res.status(401).json({ error: 'No token provided' });
  }
  try {
    const decoded = jwt.verify(authHeader.split(' ')[1], JWT_SECRET);
    req.admin = decoded;
    next();
  } catch {
    return res.status(401).json({ error: 'Invalid or expired token' });
  }
}

function ownerOnly(req, res, next) {
  if (req.admin.role !== 'owner' && req.admin.role !== 'admin') {
    return res.status(403).json({ error: 'Admin access required' });
  }
  next();
}

// ── Email ─────────────────────────────────────────────────────────

// H3: Email notifications — opt-in via SMTP env vars
let emailTransporter = null;
if (process.env.SMTP_HOST && process.env.SMTP_USER && process.env.SMTP_PASS) {
  emailTransporter = nodemailer.createTransport({
    host: process.env.SMTP_HOST,
    port: parseInt(process.env.SMTP_PORT) || 587,
    secure: parseInt(process.env.SMTP_PORT) === 465,
    auth: { user: process.env.SMTP_USER, pass: process.env.SMTP_PASS }
  });
  console.log('[EMAIL] SMTP configured:', process.env.SMTP_HOST);
} else {
  console.log('[EMAIL] SMTP not configured — email notifications disabled. Set SMTP_HOST, SMTP_USER, SMTP_PASS to enable.');
}

const STORE_EMAIL = process.env.STORE_EMAIL || process.env.SMTP_USER || 'hub@email.com';
const OWNER_EMAIL = process.env.OWNER_EMAIL;

async function sendOrderEmails(order) {
  if (!emailTransporter) return;

  const shippingLabel = {
    local: 'Local Delivery (Valenzuela City)',
    metro: 'Metro Manila Delivery',
    provincial: 'Provincial / Outside NCR',
    pickup: 'Store Pickup'
  }[order.shipping] || order.shipping;

  const itemsHtml = order.items.map(i =>
    `<tr><td style="padding:6px 8px;border-bottom:1px solid #e2e8f0">${i.name} × ${i.qty}</td><td style="padding:6px 8px;border-bottom:1px solid #e2e8f0;text-align:right;font-weight:600">₱${(i.price * i.qty).toLocaleString('en-PH')}</td></tr>`
  ).join('');

  const itemsText = order.items.map(i =>
    `  ${i.name} x${i.qty} — ₱${(i.price * i.qty).toLocaleString('en-PH')}`
  ).join('\n');

  const totalFormatted = `₱${Number(order.total).toLocaleString('en-PH')}`;

  // Customer confirmation email
  if (order.customer.email) {
    try {
      await emailTransporter.sendMail({
        from: `"H.U.B Store" <${STORE_EMAIL}>`,
        to: order.customer.email,
        subject: `Order Received — ${order.id} | H.U.B Store`,
        html: `
<!DOCTYPE html><html><body style="margin:0;padding:0;background:#f1f5f9;font-family:'Segoe UI',Arial,sans-serif">
<div style="max-width:560px;margin:32px auto;background:#fff;border-radius:12px;overflow:hidden;box-shadow:0 2px 12px rgba(0,0,0,0.08)">
  <div style="background:linear-gradient(135deg,#1255c0,#1a6ee8);padding:28px 32px;text-align:center">
    <h1 style="margin:0;color:#fff;font-size:22px;letter-spacing:0.5px">H.U.B Store</h1>
    <p style="margin:6px 0 0;color:rgba(255,255,255,0.85);font-size:13px">Hanap.Usap.Build — Valenzuela City</p>
  </div>
  <div style="padding:28px 32px">
    <h2 style="margin:0 0 6px;color:#1e293b;font-size:18px">Your order has been received!</h2>
    <p style="color:#64748b;margin:0 0 20px;font-size:14px">Hi ${order.customer.firstName}, we've received your order and will process it once payment is verified.</p>
    <div style="background:#f8fafc;border-radius:8px;padding:14px 16px;margin-bottom:20px">
      <p style="margin:0 0 4px;font-size:12px;color:#94a3b8;text-transform:uppercase;letter-spacing:0.5px">Order ID</p>
      <p style="margin:0;font-size:16px;font-weight:700;color:#1a6ee8">${order.id}</p>
    </div>
    <table style="width:100%;border-collapse:collapse;font-size:14px;margin-bottom:16px">
      <thead><tr style="background:#f1f5f9"><th style="padding:8px;text-align:left;color:#64748b;font-weight:600">Item</th><th style="padding:8px;text-align:right;color:#64748b;font-weight:600">Subtotal</th></tr></thead>
      <tbody>${itemsHtml}</tbody>
    </table>
    <div style="display:flex;justify-content:space-between;padding:12px 8px;border-top:2px solid #1a6ee8;margin-bottom:20px">
      <span style="font-weight:700;color:#1e293b">Total</span>
      <span style="font-weight:800;color:#1a6ee8;font-size:16px">${totalFormatted}</span>
    </div>
    <table style="width:100%;font-size:13px;color:#64748b;margin-bottom:20px">
      <tr><td style="padding:3px 0;font-weight:600;color:#475569;width:110px">Shipping</td><td>${shippingLabel}</td></tr>
      <tr><td style="padding:3px 0;font-weight:600;color:#475569">Payment</td><td>${order.payment}</td></tr>
      ${order.paymentRef ? `<tr><td style="padding:3px 0;font-weight:600;color:#475569">Ref No.</td><td>${order.paymentRef}</td></tr>` : ''}
    </table>
    <div style="background:#fef9c3;border:1px solid #fde047;border-radius:8px;padding:12px 14px;font-size:13px;color:#854d0e;margin-bottom:20px">
      ⚠️ Please <strong>send your payment screenshot</strong> to our <a href="https://www.facebook.com/messages/t/HUBValenzuela" style="color:#1a6ee8">Facebook Messenger</a> to complete your order.
    </div>
    <p style="font-size:12px;color:#94a3b8;margin:0">Questions? Message us on <a href="https://www.facebook.com/HUBValenzuela" style="color:#1a6ee8">Facebook</a> or email <a href="mailto:${STORE_EMAIL}" style="color:#1a6ee8">${STORE_EMAIL}</a></p>
  </div>
  <div style="background:#f8fafc;padding:14px 32px;text-align:center;font-size:11px;color:#94a3b8">
    H.U.B | 3/F Unit 306 Arbortowne Plaza II, Karuhatan Road, Valenzuela, Philippines 1442
  </div>
</div>
</body></html>`,
        text: `Hi ${order.customer.firstName},\n\nYour order has been received!\n\nOrder ID: ${order.id}\n\nItems:\n${itemsText}\n\nTotal: ${totalFormatted}\nShipping: ${shippingLabel}\nPayment: ${order.payment}${order.paymentRef ? '\nRef No.: ' + order.paymentRef : ''}\n\nIMPORTANT: Please send your payment screenshot to our Facebook Messenger to complete your order.\nhttps://www.facebook.com/messages/t/HUBValenzuela\n\n— H.U.B Store`
      });
      console.log(`[EMAIL] Confirmation sent to ${order.customer.email}`);
    } catch (err) {
      console.error('[EMAIL] Customer confirmation failed:', err.message);
    }
  }

  // Owner new-order alert
  if (OWNER_EMAIL) {
    try {
      await emailTransporter.sendMail({
        from: `"H.U.B Store" <${STORE_EMAIL}>`,
        to: OWNER_EMAIL,
        subject: `🛒 New Order: ${order.id} — ${order.customer.firstName} ${order.customer.lastName}`,
        html: `
<!DOCTYPE html><html><body style="margin:0;padding:0;background:#f1f5f9;font-family:'Segoe UI',Arial,sans-serif">
<div style="max-width:560px;margin:32px auto;background:#fff;border-radius:12px;overflow:hidden;box-shadow:0 2px 12px rgba(0,0,0,0.08)">
  <div style="background:linear-gradient(135deg,#1255c0,#1a6ee8);padding:20px 28px">
    <h2 style="margin:0;color:#fff;font-size:17px">New Order Received</h2>
    <p style="margin:4px 0 0;color:rgba(255,255,255,0.8);font-size:13px">${order.id}</p>
  </div>
  <div style="padding:24px 28px">
    <h3 style="margin:0 0 12px;color:#1e293b;font-size:15px">Customer</h3>
    <table style="font-size:13px;color:#475569;margin-bottom:20px">
      <tr><td style="padding:2px 12px 2px 0;font-weight:600">Name</td><td>${order.customer.firstName} ${order.customer.lastName}</td></tr>
      <tr><td style="padding:2px 12px 2px 0;font-weight:600">Email</td><td><a href="mailto:${order.customer.email}" style="color:#1a6ee8">${order.customer.email}</a></td></tr>
      <tr><td style="padding:2px 12px 2px 0;font-weight:600">Phone</td><td>${order.customer.phone}</td></tr>
      <tr><td style="padding:2px 12px 2px 0;font-weight:600">Address</td><td>${order.customer.street}${order.customer.street2 ? ', ' + order.customer.street2 : ''}, ${order.customer.city}${order.customer.province ? ', ' + order.customer.province : ''}</td></tr>
    </table>
    <h3 style="margin:0 0 8px;color:#1e293b;font-size:15px">Items</h3>
    <table style="width:100%;border-collapse:collapse;font-size:13px;margin-bottom:16px">
      <thead><tr style="background:#f1f5f9"><th style="padding:6px 8px;text-align:left;color:#64748b">Item</th><th style="padding:6px 8px;text-align:right;color:#64748b">Subtotal</th></tr></thead>
      <tbody>${itemsHtml}</tbody>
    </table>
    <table style="font-size:13px;color:#475569;margin-bottom:20px">
      <tr><td style="padding:2px 12px 2px 0;font-weight:600">Total</td><td style="color:#1a6ee8;font-weight:700;font-size:15px">${totalFormatted}</td></tr>
      <tr><td style="padding:2px 12px 2px 0;font-weight:600">Shipping</td><td>${shippingLabel}</td></tr>
      <tr><td style="padding:2px 12px 2px 0;font-weight:600">Payment</td><td>${order.payment}</td></tr>
      ${order.paymentRef ? `<tr><td style="padding:2px 12px 2px 0;font-weight:600">Ref No.</td><td><strong>${order.paymentRef}</strong></td></tr>` : '<tr><td style="padding:2px 12px 2px 0;font-weight:600">Ref No.</td><td style="color:#ef4444">Not provided — ask for screenshot</td></tr>'}
      ${order.customer.notes ? `<tr><td style="padding:2px 12px 2px 0;font-weight:600">Notes</td><td>${order.customer.notes}</td></tr>` : ''}
    </table>
    <a href="https://hubstore.ph/admin" style="display:inline-block;background:linear-gradient(135deg,#1255c0,#1a6ee8);color:#fff;text-decoration:none;padding:10px 20px;border-radius:8px;font-size:13px;font-weight:600">View in Admin Panel →</a>
  </div>
</div>
</body></html>`,
        text: `New Order: ${order.id}\n\nCustomer: ${order.customer.firstName} ${order.customer.lastName}\nEmail: ${order.customer.email}\nPhone: ${order.customer.phone}\nAddress: ${order.customer.street}, ${order.customer.city}\n\nItems:\n${itemsText}\n\nTotal: ${totalFormatted}\nShipping: ${shippingLabel}\nPayment: ${order.payment}${order.paymentRef ? '\nRef No.: ' + order.paymentRef : '\nRef No.: NOT PROVIDED'}\n\nView in admin: https://hubstore.ph/admin`
      });
      console.log(`[EMAIL] Owner notification sent to ${OWNER_EMAIL}`);
    } catch (err) {
      console.error('[EMAIL] Owner notification failed:', err.message);
    }
  }
}

// ── Public API ───────────────────────────────────────────────────

// GET /api/products — public storefront
app.get('/api/products', (req, res) => {
  const products = readJSON('products.json')
    .map(p => ({
      id: p.id, cat: p.cat, label: p.label, name: p.name, price: p.price,
      priceTiers: p.priceTiers || null, img: p.img, brand: p.brand || null,
      description: p.description || null, weight: p.weight || null,
      warranty: p.warranty || null, originalPrice: p.originalPrice || p.comparePrice || null,
      salePrice: p.salePrice || null, stock: p.stock, specs: p.specs || null,
      condition: p.condition || 'new', badge: p.badge || null,
      stockStatus: deriveStockStatus(p.stock)
    }));
  res.json(products);
});

// M1: Contact form submission with server-side email validation + H5: sanitize inputs
app.post('/api/contact', contactLimiter, csrfCheck, (req, res) => {
  const { name, email, phone, message } = req.body;
  if (!name || !email || !message) {
    return res.status(400).json({ error: 'Name, email, and message are required' });
  }
  const emailRe = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  if (!emailRe.test(email)) {
    return res.status(400).json({ error: 'Valid email address is required' });
  }
  const entry = {
    name: sanitizeInput(name),
    email: sanitizeInput(email),
    phone: sanitizeInput(phone || ''),
    message: sanitizeInput(message, 2000)
  };
  appendToFile('contacts.json', entry);
  console.log(`[CONTACT] New contact form submission received`);
  res.json({ success: true });
});

// Customer registration (from Firebase Auth logins)
app.post('/api/customers', csrfCheck, (req, res) => {
  const { uid, name, email, provider, photoURL } = req.body;
  if (!uid || !name) {
    return res.status(400).json({ error: 'uid and name are required' });
  }
  const customers = readJSON('customers.json');
  const existing = customers.find(c => c.uid === uid);
  if (existing) {
    existing.lastLogin = new Date().toISOString();
    if (email && !existing.email) existing.email = sanitizeInput(email);
    if (name) existing.name = sanitizeInput(name);
    if (photoURL) existing.photoURL = photoURL;
    existing.loginCount = (existing.loginCount || 1) + 1;
    writeJSON('customers.json', customers);
    return res.json({ success: true, updated: true });
  }
  const customer = {
    uid,
    name: sanitizeInput(name),
    email: email ? sanitizeInput(email) : null,
    provider: provider || 'unknown',
    photoURL: photoURL || null,
    loginCount: 1,
    firstLogin: new Date().toISOString(),
    lastLogin: new Date().toISOString()
  };
  customers.push(customer);
  writeJSON('customers.json', customers);
  console.log(`[CUSTOMER] New customer registered via ${provider}`);
  res.json({ success: true, new: true });
});

// Duplicate order prevention
const recentOrderHashes = new Map();
setInterval(() => {
  const cutoff = Date.now() - 60000;
  for (const [hash, ts] of recentOrderHashes) {
    if (ts < cutoff) recentOrderHashes.delete(hash);
  }
}, 30000);

// B1+H4+B5: Order submission with server-side price verification and stock management
app.post('/api/order', orderLimiter, csrfCheck, (req, res) => {
  const { customer, items, shipping, payment, paymentRef, total } = req.body;

  // Validate customer fields
  if (!customer || typeof customer !== 'object') {
    return res.status(400).json({ error: 'Customer info is required' });
  }
  const { firstName, lastName, email, phone, street, city } = customer;
  if (!firstName || !lastName || !street || !city) {
    return res.status(400).json({ error: 'Name, street, and city are required' });
  }
  const emailRe = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  if (!email || !emailRe.test(email)) {
    return res.status(400).json({ error: 'Valid email is required' });
  }
  const phoneRe = /^(\+?63|0)9\d{9}$/;
  if (!phone || !phoneRe.test(phone.replace(/[\s\-]/g, ''))) {
    return res.status(400).json({ error: 'Valid Philippine phone number is required' });
  }

  // Validate items
  if (!Array.isArray(items) || !items.length) {
    return res.status(400).json({ error: 'At least one item is required' });
  }
  for (const item of items) {
    if (!item.name || item.price == null || !item.qty) {
      return res.status(400).json({ error: 'Each item must have name, price, and qty' });
    }
  }

  // Validate shipping & payment (must match checkout.html values)
  const validShipping = ['local', 'metro', 'provincial', 'pickup'];
  if (!shipping || !validShipping.includes(shipping)) {
    return res.status(400).json({ error: 'Invalid shipping method' });
  }
  const validPayment = ['GCash', 'Maya', 'Bank Transfer'];
  if (!payment || !validPayment.includes(payment)) {
    return res.status(400).json({ error: 'Invalid payment method' });
  }

  // H4: Server-side price verification — override client prices with catalog prices
  const products = readJSON('products.json');
  const verifiedItems = [];
  for (const item of items) {
    const product = products.find(p =>
      p.name && p.name.toLowerCase() === (item.name || '').toLowerCase()
    );
    if (!product) {
      return res.status(400).json({ error: `"${item.name}" is not available in our catalog` });
    }
    if (Number(product.price) !== Number(item.price)) {
      console.warn(`[ORDER] Price mismatch for "${item.name}": client=${item.price}, catalog=${product.price}`);
    }
    verifiedItems.push({ ...item, price: product.price, productId: product.id });
  }

  // B5: Stock availability check before accepting order
  for (const item of verifiedItems) {
    if (!item.productId) continue;
    const product = products.find(p => p.id === item.productId);
    if (!product) continue;
    const stockNum = Number(product.stock);
    if (!isNaN(stockNum) && stockNum < (item.qty || 1)) {
      return res.status(400).json({ error: `"${item.name}" has insufficient stock (${stockNum} available)` });
    }
    if (deriveStockStatus(product.stock) === 'out') {
      return res.status(400).json({ error: `"${item.name}" is currently out of stock` });
    }
  }

  // B1: Recalculate server-side total (ignore client-submitted total)
  const shippingFees = { local: 79, metro: 0, provincial: 0, pickup: 0 };
  const itemsTotal = verifiedItems.reduce((sum, item) => sum + (Number(item.price) * (item.qty || 1)), 0);
  const shippingFee = shippingFees[shipping] || 0;
  const serverTotal = itemsTotal + shippingFee;

  // Validate server-calculated total (not client-submitted)
  if (serverTotal <= 0) {
    return res.status(400).json({ error: 'Order total must be greater than 0' });
  }

  // H5: Sanitize all customer fields before storage
  const sanitizedCustomer = {
    firstName: sanitizeInput(firstName),
    lastName: sanitizeInput(lastName),
    email: sanitizeInput(email),
    phone: sanitizeInput(phone),
    street: sanitizeInput(street),
    street2: sanitizeInput(customer.street2 || ''),
    city: sanitizeInput(city),
    province: sanitizeInput(customer.province || ''),
    zip: sanitizeInput(customer.zip || ''),
    notes: sanitizeInput(customer.notes || '', 1000)
  };

  // Duplicate order prevention (same content within 60s)
  const orderHash = crypto.createHash('md5')
    .update(JSON.stringify({
      customer: { firstName: sanitizedCustomer.firstName, lastName: sanitizedCustomer.lastName, email: sanitizedCustomer.email },
      items: verifiedItems,
      serverTotal
    }))
    .digest('hex');
  if (recentOrderHashes.has(orderHash)) {
    return res.status(409).json({ error: 'Duplicate order detected. Please wait before resubmitting.' });
  }
  recentOrderHashes.set(orderHash, Date.now());

  // Generate unique order ID
  const orderId = 'HUB-' + Date.now() + '-' + crypto.randomBytes(3).toString('hex');
  const order = {
    id: orderId,
    customer: sanitizedCustomer,
    items: verifiedItems,
    shipping,
    payment,
    paymentRef: sanitizeInput(paymentRef || ''),
    total: serverTotal,
    customerUid: req.body.customerUid || null,
    status: 'Pending'
  };
  appendToFile('orders.json', order);
  console.log(`[ORDER] ${order.id} - ${verifiedItems.length} item(s) - Total: ₱${serverTotal}`);

  // B5: Decrement stock after order is saved
  let productsUpdated = false;
  const productsCopy = readJSON('products.json');
  for (const item of verifiedItems) {
    if (!item.productId) continue;
    const pidx = productsCopy.findIndex(p => p.id === item.productId);
    if (pidx === -1) continue;
    const stockNum = Number(productsCopy[pidx].stock);
    if (!isNaN(stockNum) && stockNum > 0) {
      const qty = item.qty || 1;
      const newStock = Math.max(0, stockNum - qty);
      logInventory(item.productId, productsCopy[pidx].name, 'online-order', -qty, stockNum, newStock, `Order ${orderId}`, 'system');
      productsCopy[pidx].stock = newStock;
      productsUpdated = true;
    }
  }
  if (productsUpdated) {
    writeJSON('products.json', productsCopy);
    console.log(`[ORDER] Stock decremented for order ${orderId}`);
  }

  // H3: Send emails non-blocking (don't delay response)
  sendOrderEmails(order).catch(err => console.error('[EMAIL] Unexpected error:', err.message));

  res.json({ success: true, orderId: order.id, total: serverTotal });
});

// ── Admin Auth ───────────────────────────────────────────────────

app.post('/api/admin/login', loginLimiter, (req, res) => {
  const { username, password } = req.body;
  if (!username || !password) {
    return res.status(400).json({ error: 'Username and password required' });
  }
  const admins = readJSON('admins.json');
  const admin = admins.find(a => a.username === username);
  if (!admin || !bcrypt.compareSync(password, admin.password)) {
    return res.status(401).json({ error: 'Invalid credentials' });
  }
  const role = admin.role || 'employee';
  const token = jwt.sign({ username: admin.username, role }, JWT_SECRET, { expiresIn: '24h' });
  res.json({ success: true, token, username: admin.username, role });
});

app.get('/api/admin/verify', authMiddleware, (req, res) => {
  const admins = readJSON('admins.json');
  const admin = admins.find(a => a.username === req.admin.username);
  const role = admin ? admin.role || 'employee' : req.admin.role || 'employee';
  res.json({ valid: true, username: req.admin.username, role });
});

// ── Admin: Dashboard Stats ───────────────────────────────────────

app.get('/api/admin/stats', authMiddleware, ownerOnly, (req, res) => {
  const products = readJSON('products.json');
  const orders = readJSON('orders.json');
  const contacts = readJSON('contacts.json');
  const customers = readJSON('customers.json');

  const totalRevenue = orders.reduce((sum, o) => sum + (parseFloat(o.total) || 0), 0);
  const lowStock = products.filter(p => deriveStockStatus(p.stock) === 'low').length;
  const outOfStock = products.filter(p => deriveStockStatus(p.stock) === 'out').length;
  const recentOrders = orders.slice(-5).reverse();

  // Revenue by day (last 30 days)
  const now = new Date();
  const revenueByDay = [];
  for (let i = 29; i >= 0; i--) {
    const d = new Date(now);
    d.setDate(d.getDate() - i);
    const dateStr = d.toISOString().slice(0, 10);
    const dayRevenue = orders
      .filter(o => o.timestamp && o.timestamp.slice(0, 10) === dateStr)
      .reduce((sum, o) => sum + (parseFloat(o.total) || 0), 0);
    revenueByDay.push({ date: dateStr, revenue: dayRevenue });
  }

  // Orders by status
  const ordersByStatus = {};
  orders.forEach(o => {
    const s = (o.status || 'Pending');
    ordersByStatus[s] = (ordersByStatus[s] || 0) + 1;
  });

  // Top 5 products by order frequency
  const productCounts = {};
  orders.forEach(o => {
    (o.items || []).forEach(item => {
      const name = item.name || item.product || 'Unknown';
      productCounts[name] = (productCounts[name] || 0) + (item.qty || item.quantity || 1);
    });
  });
  const topProducts = Object.entries(productCounts)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 5)
    .map(([name, qty]) => ({ name, qty }));

  // Enhanced stats: today's revenue, sales count, monthly profit
  const sales = readJSON('sales.json');
  const expenses = readJSON('expenses.json');
  const todayStr = now.toISOString().slice(0, 10);
  const monthStr = now.toISOString().slice(0, 7);

  const todayOnlineRev = orders
    .filter(o => o.timestamp && o.timestamp.slice(0, 10) === todayStr && o.status === 'Completed')
    .reduce((sum, o) => sum + (parseFloat(o.total) || 0), 0);
  const todayWalkinRev = sales
    .filter(s => !s.voided && s.timestamp && s.timestamp.slice(0, 10) === todayStr)
    .reduce((sum, s) => sum + (s.total || 0), 0);
  const todayRevenue = todayOnlineRev + todayWalkinRev;
  const todaySalesCount = sales.filter(s => !s.voided && s.timestamp && s.timestamp.slice(0, 10) === todayStr).length
    + orders.filter(o => o.timestamp && o.timestamp.slice(0, 10) === todayStr).length;

  // Yesterday comparison
  const yesterday = new Date(now);
  yesterday.setDate(yesterday.getDate() - 1);
  const yesterdayStr = yesterday.toISOString().slice(0, 10);
  const yesterdayRev = orders.filter(o => o.timestamp && o.timestamp.slice(0, 10) === yesterdayStr && o.status === 'Completed').reduce((sum, o) => sum + (parseFloat(o.total) || 0), 0)
    + sales.filter(s => !s.voided && s.timestamp && s.timestamp.slice(0, 10) === yesterdayStr).reduce((sum, s) => sum + (s.total || 0), 0);
  const revenueChange = yesterdayRev > 0 ? Number((((todayRevenue - yesterdayRev) / yesterdayRev) * 100).toFixed(1)) : 0;

  // Monthly expense total
  const monthExpenses = expenses.filter(e => e.date && e.date.startsWith(monthStr)).reduce((sum, e) => sum + (e.amount || 0), 0);

  // Monthly revenue
  const monthOnlineRev = orders.filter(o => o.timestamp && o.timestamp.slice(0, 7) === monthStr && o.status === 'Completed').reduce((sum, o) => sum + (parseFloat(o.total) || 0), 0);
  const monthWalkinRev = sales.filter(s => !s.voided && s.timestamp && s.timestamp.slice(0, 7) === monthStr).reduce((sum, s) => sum + (s.total || 0), 0);
  const monthRevenue = monthOnlineRev + monthWalkinRev;
  const monthProfit = monthRevenue - monthExpenses;

  // Recent walk-in sales
  const recentSales = sales.filter(s => !s.voided).slice(-5).reverse();

  res.json({
    totalProducts: products.length,
    totalOrders: orders.length,
    totalContacts: contacts.length,
    totalCustomers: customers.length,
    totalRevenue,
    lowStock,
    outOfStock,
    recentOrders,
    revenueByDay,
    ordersByStatus,
    topProducts,
    todayRevenue,
    todaySalesCount,
    revenueChange,
    monthProfit,
    monthExpenses,
    monthRevenue,
    recentSales
  });
});

// ── Admin: Delete Category ────────────────────────────────────────

app.delete('/api/admin/categories/:cat', authMiddleware, (req, res) => {
  const cat = req.params.cat;
  let products = readJSON('products.json');
  const matching = products.filter(p => p.cat === cat);
  if (!matching.length) {
    return res.status(404).json({ error: 'No products found in this category' });
  }
  const removed = matching.length;
  products = products.filter(p => p.cat !== cat);
  writeJSON('products.json', products);
  console.log(`[ADMIN] Category "${cat}" deleted (${removed} product(s) removed)`);
  res.json({ success: true, removed });
});

// ── Admin: Products CRUD ─────────────────────────────────────────

app.get('/api/admin/products', authMiddleware, (req, res) => {
  res.json(readJSON('products.json'));
});

app.post('/api/admin/products', authMiddleware, (req, res) => {
  const products = readJSON('products.json');
  const { cat, label, name, price, costPrice, priceTiers, img, brand, description, weight, warranty, stock, condition, badge, specs, shopee } = req.body;
  if (!cat || !name || !price || isNaN(Number(price)) || Number(price) <= 0) {
    return res.status(400).json({ error: 'Category, name, and valid price are required' });
  }
  // Generate next ID
  const maxNum = products.reduce((max, p) => {
    const n = parseInt(p.id.replace('prod-', ''));
    return n > max ? n : max;
  }, 0);
  const product = {
    id: 'prod-' + (maxNum + 1),
    cat, label: label || cat, name, price: Number(price),
    costPrice: Number(costPrice) || 0,
    priceTiers: priceTiers || null,
    img: img || '', brand: brand || null, description: description || null,
    weight: weight ? Number(weight) : null, warranty: warranty || null,
    stock: stock !== undefined ? Number(stock) : 50, condition: condition || 'new',
    badge: badge || null, specs: specs || {}, shopee: !!shopee
  };
  products.push(product);
  writeJSON('products.json', products);
  logAudit('product_create', product.id, `Created product: ${name}`, req.admin.username);
  console.log(`[ADMIN] Product added: ${name}`);
  res.json({ success: true, product });
});

app.put('/api/admin/products/:id', authMiddleware, (req, res) => {
  const products = readJSON('products.json');
  const idx = products.findIndex(p => p.id === req.params.id);
  if (idx === -1) return res.status(404).json({ error: 'Product not found' });

  const { cat, label, name, price, costPrice, priceTiers, img, brand, description, weight, warranty, stock, condition, badge, specs, shopee } = req.body;
  const changes = [];
  if (cat !== undefined) products[idx].cat = cat;
  if (label !== undefined) products[idx].label = label;
  if (name !== undefined) products[idx].name = name;
  if (price !== undefined) { if (products[idx].price !== Number(price)) changes.push(`price ${products[idx].price}→${Number(price)}`); products[idx].price = Number(price); }
  if (costPrice !== undefined) { products[idx].costPrice = Number(costPrice) || 0; }
  if (priceTiers !== undefined) products[idx].priceTiers = priceTiers;
  if (img !== undefined) products[idx].img = img;
  if (brand !== undefined) products[idx].brand = brand || null;
  if (description !== undefined) products[idx].description = description || null;
  if (weight !== undefined) products[idx].weight = weight ? Number(weight) : null;
  if (warranty !== undefined) products[idx].warranty = warranty || null;
  if (stock !== undefined) {
    const prevStock = products[idx].stock;
    products[idx].stock = Number(stock);
    if (prevStock !== Number(stock)) {
      logInventory(products[idx].id, products[idx].name, 'adjustment', Number(stock) - prevStock, prevStock, Number(stock), 'Manual stock edit', req.admin.username);
      changes.push(`stock ${prevStock}→${Number(stock)}`);
    }
  }
  if (condition !== undefined) products[idx].condition = condition;
  if (badge !== undefined) products[idx].badge = badge || null;
  if (specs !== undefined) products[idx].specs = specs;
  if (shopee !== undefined) products[idx].shopee = !!shopee;

  writeJSON('products.json', products);
  logAudit('product_update', products[idx].id, `Updated ${products[idx].name}${changes.length ? ': ' + changes.join(', ') : ''}`, req.admin.username);
  console.log(`[ADMIN] Product updated: ${products[idx].name}`);
  res.json({ success: true, product: products[idx] });
});

app.delete('/api/admin/products/:id', authMiddleware, ownerOnly, (req, res) => {
  let products = readJSON('products.json');
  const idx = products.findIndex(p => p.id === req.params.id);
  if (idx === -1) return res.status(404).json({ error: 'Product not found' });

  const removed = products.splice(idx, 1)[0];
  writeJSON('products.json', products);
  logAudit('product_delete', removed.id, `Deleted product: ${removed.name}`, req.admin.username);
  console.log(`[ADMIN] Product deleted: ${removed.name}`);
  res.json({ success: true });
});

// ── Admin: Image Upload ──────────────────────────────────────────

app.post('/api/admin/upload', authMiddleware, (req, res, next) => {
  upload.single('image')(req, res, (err) => {
    if (err) {
      if (err instanceof multer.MulterError) {
        return res.status(400).json({ error: err.code === 'LIMIT_FILE_SIZE' ? 'File too large (max 5MB)' : err.message });
      }
      return res.status(400).json({ error: err.message });
    }
    if (!req.file) return res.status(400).json({ error: 'No file uploaded' });
    const url = '/uploads/' + req.file.filename;
    console.log(`[ADMIN] Image uploaded: ${url}`);
    res.json({ success: true, url });
  });
});

// ── Admin: Analyze Image (Upload + AI Detection) ─────────────────

app.post('/api/admin/analyze-image', authMiddleware, (req, res, next) => {
  upload.single('image')(req, res, async (err) => {
    if (err) {
      if (err instanceof multer.MulterError) {
        return res.status(400).json({ error: err.code === 'LIMIT_FILE_SIZE' ? 'File too large (max 5MB)' : err.message });
      }
      return res.status(400).json({ error: err.message });
    }
    if (!req.file) return res.status(400).json({ error: 'No file uploaded' });

    const url = '/uploads/' + req.file.filename;
    console.log(`[ADMIN] Image uploaded: ${url}`);

    // Try lazy-init if key was added after startup
    if (!anthropic && Anthropic && process.env.ANTHROPIC_API_KEY) {
      anthropic = new Anthropic({ apiKey: process.env.ANTHROPIC_API_KEY });
      console.log('[ADMIN] Anthropic client lazy-initialized');
    }

    // If still no client, behave like plain upload
    if (!anthropic) {
      console.log('[ADMIN] No Anthropic client — skipping detection. KEY set:', !!process.env.ANTHROPIC_API_KEY, 'SDK:', !!Anthropic);
      return res.json({ success: true, url, detected: null });
    }

    try {
      const imgPath = path.join(UPLOADS_DIR, req.file.filename);
      const imgBuffer = fs.readFileSync(imgPath);
      const base64 = imgBuffer.toString('base64');
      const ext = path.extname(req.file.filename).toLowerCase();
      const mediaType = ext === '.png' ? 'image/png'
        : ext === '.gif' ? 'image/gif'
        : ext === '.webp' ? 'image/webp'
        : 'image/jpeg';

      const response = await anthropic.messages.create({
        model: 'claude-haiku-4-5-20251001',
        max_tokens: 2048,
        messages: [{
          role: 'user',
          content: [
            {
              type: 'image',
              source: { type: 'base64', media_type: mediaType, data: base64 }
            },
            {
              type: 'text',
              text: `You are analyzing a product promotional image for a PC parts store called H.U.B (Hanap.Usap.Build) in Valenzuela, Philippines.

1. First, extract any info visible in the image.
2. Then, based on the product you identified, use your knowledge to provide additional technical specs that a buyer would want to know (e.g. resolution, response time, ports, TDP, core count, etc. depending on the product type). Do NOT repeat specs already found in the image.

Return this JSON structure:
{
  "product_name": "Full product name (brand + model + key variant info)",
  "category": "one of: gpu, cpu, mobo, ram, psu, monitor, case, cooler, peripheral, storage, builds",
  "label": "Human-readable category (e.g. Video Card, Processor, Monitor, Peripherals, Storage)",
  "price": null or number in PHP (no currency symbol),
  "image_specs": { "key": "value" pairs found IN the image },
  "researched_specs": { "key": "value" pairs from your knowledge about this product }
}

Return ONLY valid JSON, no markdown, no code fences.`
            }
          ]
        }]
      });

      if (!response.content || !response.content[0] || !response.content[0].text) throw new Error('Empty AI response');
      let text = response.content[0].text.trim();
      // Strip markdown code fences if present
      text = text.replace(/^```(?:json)?\s*/i, '').replace(/\s*```$/,'');
      const detected = JSON.parse(text);
      console.log(`[ADMIN] AI detected: ${detected.product_name || 'unknown'}`);
      res.json({ success: true, url, detected });
    } catch (aiErr) {
      console.error('[ADMIN] AI detection failed:', aiErr.message);
      // Still return the uploaded image — don't waste the upload
      res.json({ success: true, url, detected: null });
    }
  });
});

// ── Admin: Bulk Product Actions ──────────────────────────────────

app.post('/api/admin/products/bulk', authMiddleware, (req, res) => {
  const { action, ids, value } = req.body;
  if (!ids || !ids.length) return res.status(400).json({ error: 'No products selected' });

  let products = readJSON('products.json');

  if (action === 'delete') {
    const before = products.length;
    products = products.filter(p => !ids.includes(p.id));
    writeJSON('products.json', products);
    console.log(`[ADMIN] Bulk deleted ${before - products.length} products`);
    return res.json({ success: true, deleted: before - products.length });
  }

  if (action === 'set-stock') {
    const stockVal = Number(value);
    if (isNaN(stockVal) || stockVal < 0) return res.status(400).json({ error: 'Invalid stock value' });
    let count = 0;
    products.forEach(p => {
      if (ids.includes(p.id)) { p.stock = stockVal; count++; }
    });
    writeJSON('products.json', products);
    console.log(`[ADMIN] Bulk set stock to ${stockVal} for ${count} products`);
    return res.json({ success: true, updated: count });
  }

  if (action === 'set-badge') {
    const badge = value || null;
    let count = 0;
    products.forEach(p => {
      if (ids.includes(p.id)) { p.badge = badge; count++; }
    });
    writeJSON('products.json', products);
    console.log(`[ADMIN] Bulk set badge to "${badge}" for ${count} products`);
    return res.json({ success: true, updated: count });
  }

  res.status(400).json({ error: 'Unknown action' });
});

// ── Admin: Orders ────────────────────────────────────────────────

app.get('/api/admin/orders', authMiddleware, (req, res) => {
  const orders = readJSON('orders.json');
  res.json(orders.reverse());
});

app.put('/api/admin/orders/:id/status', authMiddleware, (req, res) => {
  const orders = readJSON('orders.json');
  const order = orders.find(o => o.id === req.params.id);
  if (!order) return res.status(404).json({ error: 'Order not found' });

  const validStatuses = ['Pending', 'Confirmed', 'Shipped', 'Completed', 'Cancelled'];
  if (!req.body.status || !validStatuses.includes(req.body.status)) {
    return res.status(400).json({ error: 'Invalid status. Must be: ' + validStatuses.join(', ') });
  }

  if (req.body.status === 'Cancelled' && !req.body.reason) {
    return res.status(400).json({ error: 'Cancellation reason is required' });
  }

  const prevStatus = order.status;
  order.status = req.body.status;
  if (req.body.reason) order.cancelReason = sanitizeInput(req.body.reason, 500);
  writeJSON('orders.json', orders);
  console.log(`[ADMIN] Order ${order.id} status → ${order.status}`);

  // Restore stock when order is cancelled
  if (req.body.status === 'Cancelled' && prevStatus !== 'Cancelled') {
    const products = readJSON('products.json');
    let restored = false;
    for (const item of (order.items || [])) {
      const pid = item.productId;
      if (!pid) continue;
      const pidx = products.findIndex(p => p.id === pid);
      if (pidx === -1) continue;
      const prevStock = Number(products[pidx].stock) || 0;
      const qty = item.qty || item.quantity || 1;
      products[pidx].stock = prevStock + qty;
      logInventory(pid, products[pidx].name, 'return', qty, prevStock, products[pidx].stock, `Order ${order.id} cancelled`, req.admin.username);
      restored = true;
    }
    if (restored) {
      writeJSON('products.json', products);
      console.log(`[ADMIN] Stock restored for cancelled order ${order.id}`);
    }
  }

  logAudit('order_status', order.id, `Status ${prevStatus}→${order.status}${order.cancelReason ? ' (reason: ' + order.cancelReason + ')' : ''}`, req.admin.username);

  // Auto-credit points when order is completed
  let pointsCredited = 0;
  if (req.body.status === 'Completed' && prevStatus !== 'Completed' && order.customerUid) {
    const subtotal = (order.items || []).reduce((sum, item) => sum + ((parseFloat(item.price) || 0) * (item.qty || item.quantity || 1)), 0);
    if (subtotal > 0) {
      const pointsEarned = Math.floor(subtotal / 2); // 1 pt per ₱2
      const existing = getCustomerPoints(order.customerUid);
      const alreadyCredited = existing.history.some(h => h.orderId === order.id);
      if (!alreadyCredited) {
        creditPoints(order.customerUid, pointsEarned, 'Online order ' + order.id, { orderId: order.id, staffId: req.admin.username });
        pointsCredited = pointsEarned;
        console.log(`[POINTS] Auto-credited ${pointsEarned} pts for order ${order.id}`);
      }
    }
  }

  res.json({ success: true, order, pointsCredited });
});

// ── Admin: Contacts ──────────────────────────────────────────────

app.get('/api/admin/contacts', authMiddleware, (req, res) => {
  const contacts = readJSON('contacts.json');
  res.json(contacts.reverse());
});

// ── Admin: Customers ─────────────────────────────────────────────

app.get('/api/admin/customers', authMiddleware, (req, res) => {
  const customers = readJSON('customers.json');
  res.json(customers.reverse());
});

app.post('/api/admin/customers', authMiddleware, (req, res) => {
  const { name, email, phone, provider, notes } = req.body;
  if (!name) return res.status(400).json({ error: 'Name is required' });
  const customers = readJSON('customers.json');
  const customer = {
    uid: 'manual-' + Date.now(),
    name: sanitizeInput(name),
    email: email ? sanitizeInput(email) : null,
    phone: phone ? sanitizeInput(phone) : null,
    provider: provider || 'Manual',
    photoURL: null,
    notes: notes ? sanitizeInput(notes, 1000) : null,
    loginCount: 0,
    firstLogin: new Date().toISOString(),
    lastLogin: new Date().toISOString()
  };
  customers.push(customer);
  writeJSON('customers.json', customers);
  console.log(`[CUSTOMER] Manual add: ${customer.name} (${customer.email || 'no email'})`);
  res.json({ success: true, customer });
});

app.put('/api/admin/customers/:uid', authMiddleware, (req, res) => {
  const customers = readJSON('customers.json');
  const idx = customers.findIndex(c => c.uid === req.params.uid);
  if (idx === -1) return res.status(404).json({ error: 'Customer not found' });
  const { name, email, phone, notes } = req.body;
  if (name) customers[idx].name = sanitizeInput(name);
  if (email !== undefined) customers[idx].email = email ? sanitizeInput(email) : null;
  if (phone !== undefined) customers[idx].phone = phone ? sanitizeInput(phone) : null;
  if (notes !== undefined) customers[idx].notes = notes ? sanitizeInput(notes, 1000) : null;
  writeJSON('customers.json', customers);
  res.json({ success: true });
});

app.delete('/api/admin/customers/:uid', authMiddleware, (req, res) => {
  let customers = readJSON('customers.json');
  const before = customers.length;
  customers = customers.filter(c => c.uid !== req.params.uid);
  if (customers.length === before) return res.status(404).json({ error: 'Customer not found' });
  writeJSON('customers.json', customers);
  res.json({ success: true });
});

// ── Admin: Export ────────────────────────────────────────────────

app.get('/api/admin/export/products', authMiddleware, (req, res) => {
  const file = path.join(DATA_DIR, 'products.json');
  res.download(file, 'products-backup.json');
});

// ── Trade-In Estimator ──────────────────────────────────────────

// Public: get trade-in data for storefront estimator
app.get('/api/tradein', (req, res) => {
  const data = readJSON('tradein.json');
  if (!data || (!data.types && !Array.isArray(data))) {
    return res.status(404).json({ error: 'Trade-in data not configured' });
  }
  res.json(data);
});

// Admin: get trade-in data
app.get('/api/admin/tradein', authMiddleware, (req, res) => {
  const data = readJSON('tradein.json');
  res.json(data && data.types ? data : { conditions: {}, types: {} });
});

// Admin: update trade-in data
app.put('/api/admin/tradein', authMiddleware, (req, res) => {
  const { conditions, types } = req.body;
  if (!conditions || typeof conditions !== 'object') {
    return res.status(400).json({ error: 'Conditions object is required' });
  }
  if (!types || typeof types !== 'object') {
    return res.status(400).json({ error: 'Types object is required' });
  }
  for (const [key, cond] of Object.entries(conditions)) {
    if (typeof cond.multiplier !== 'number' || cond.multiplier < 0 || cond.multiplier > 1) {
      return res.status(400).json({ error: `Invalid multiplier for condition "${key}"` });
    }
  }
  for (const [key, type] of Object.entries(types)) {
    if (!type.label || !Array.isArray(type.models)) {
      return res.status(400).json({ error: `Invalid type "${key}": needs label and models array` });
    }
    for (const model of type.models) {
      if (!model.name || !Array.isArray(model.val) || model.val.length !== 2) {
        return res.status(400).json({ error: `Invalid model in "${key}": needs name and val [low, high]` });
      }
    }
  }
  writeJSON('tradein.json', { conditions, types });
  console.log(`[ADMIN] Trade-in data updated (${Object.keys(types).length} types)`);
  res.json({ success: true });
});

// ── Points System (Customer) ─────────────────────────────────────

// Get QR token for a customer
app.get('/api/points/qr-token/:uid', (req, res) => {
  const token = generateQRToken(req.params.uid);
  res.json({ token });
});

// Get own points balance
app.get('/api/points/:uid', (req, res) => {
  const data = getCustomerPoints(req.params.uid);
  res.json({
    balance: data.balance,
    pesoValue: (data.balance / 100).toFixed(2),
    history: data.history.slice(-50).reverse()
  });
});

// ── Admin: Points ────────────────────────────────────────────────

// Verify QR token and look up customer
app.post('/api/admin/points/verify-qr', authMiddleware, (req, res) => {
  const { token } = req.body;
  if (!token) return res.status(400).json({ error: 'Token required' });
  const uid = verifyQRToken(token);
  if (!uid) return res.status(400).json({ error: 'Invalid QR code' });
  const customers = readJSON('customers.json');
  const customer = customers.find(c => c.uid === uid);
  if (!customer) return res.status(404).json({ error: 'Customer not found' });
  const points = getCustomerPoints(uid);
  res.json({ customer, balance: points.balance, pesoValue: (points.balance / 100).toFixed(2), history: points.history.slice(-50).reverse() });
});

// Lookup customer points by uid or email
app.post('/api/admin/points/lookup', authMiddleware, (req, res) => {
  const { uid, email } = req.body;
  const customers = readJSON('customers.json');
  let customer;
  if (uid) customer = customers.find(c => c.uid === uid);
  else if (email) customer = customers.find(c => c.email && c.email.toLowerCase() === email.toLowerCase());
  if (!customer) return res.status(404).json({ error: 'Customer not found' });
  const points = getCustomerPoints(customer.uid);
  res.json({ customer, balance: points.balance, pesoValue: (points.balance / 100).toFixed(2), history: points.history.slice(-50).reverse() });
});

// Credit points (in-store purchase) — duplicate-safe via 30s dedup window
const recentCreditHashes = new Map();
setInterval(() => {
  const cutoff = Date.now() - 30000;
  for (const [hash, ts] of recentCreditHashes) {
    if (ts < cutoff) recentCreditHashes.delete(hash);
  }
}, 15000);

app.post('/api/admin/points/credit', authMiddleware, (req, res) => {
  const { uid, amount, note } = req.body;
  if (!uid || !amount || isNaN(Number(amount)) || Number(amount) <= 0) {
    return res.status(400).json({ error: 'Valid uid and purchase amount required' });
  }
  const purchaseAmount = Number(amount);
  const pointsEarned = Math.floor(purchaseAmount / 2); // 1 pt per ₱2

  // Duplicate guard: same uid + amount within 30 seconds
  const dedupKey = uid + ':' + purchaseAmount;
  if (recentCreditHashes.has(dedupKey)) {
    return res.status(409).json({ error: 'Duplicate credit detected. Please wait before crediting the same amount again.' });
  }
  recentCreditHashes.set(dedupKey, Date.now());

  const result = creditPoints(uid, pointsEarned, note || 'In-store purchase', { purchaseAmount, staffId: req.admin.username });
  console.log(`[POINTS] Credited ${pointsEarned} pts to ${uid} (₱${purchaseAmount} purchase by ${req.admin.username})`);
  res.json({ success: true, pointsEarned, balance: result.balance, pesoValue: (result.balance / 100).toFixed(2) });
});

// Redeem points
app.post('/api/admin/points/redeem', authMiddleware, (req, res) => {
  const { uid, points } = req.body;
  if (!uid || !points || isNaN(Number(points)) || Number(points) <= 0) {
    return res.status(400).json({ error: 'Valid uid and points required' });
  }
  const pointsToRedeem = Math.floor(Number(points));
  const result = redeemPoints(uid, pointsToRedeem, 'In-store redemption', { staffId: req.admin.username });
  if (!result) return res.status(400).json({ error: 'Insufficient points' });
  console.log(`[POINTS] Redeemed ${pointsToRedeem} pts (₱${(pointsToRedeem / 100).toFixed(2)}) from ${uid} by ${req.admin.username}`);
  res.json({ success: true, redeemed: pointsToRedeem, pesoValue: (pointsToRedeem / 100).toFixed(2), balance: result.balance });
});

// Get all customer points (admin overview)
app.get('/api/admin/points', authMiddleware, (req, res) => {
  const points = readPoints();
  const customers = readJSON('customers.json');
  const result = Object.entries(points).map(([uid, data]) => {
    const customer = customers.find(c => c.uid === uid);
    return {
      uid,
      name: customer ? customer.name : 'Unknown',
      email: customer ? customer.email : null,
      balance: data.balance,
      pesoValue: (data.balance / 100).toFixed(2),
      totalEarned: data.history.filter(h => h.type === 'earn').reduce((s, h) => s + h.points, 0),
      totalRedeemed: data.history.filter(h => h.type === 'redeem').reduce((s, h) => s + h.points, 0)
    };
  }).filter(r => r.balance > 0 || r.totalEarned > 0);
  res.json(result);
});

// ── Site Settings ────────────────────────────────────────────────

function readSettings() {
  const file = path.join(DATA_DIR, 'settings.json');
  try {
    return JSON.parse(fs.readFileSync(file, 'utf8'));
  } catch { return { showUrgencyCTA: true }; }
}

// GET /api/settings — public (frontend needs this)
app.get('/api/settings', (req, res) => {
  res.json(readSettings());
});

// SSE: real-time settings stream
const settingsClients = new Set();
app.get('/api/settings/stream', (req, res) => {
  res.writeHead(200, {
    'Content-Type': 'text/event-stream',
    'Cache-Control': 'no-cache',
    Connection: 'keep-alive'
  });
  res.write('data: ' + JSON.stringify(readSettings()) + '\n\n');
  settingsClients.add(res);
  req.on('close', () => settingsClients.delete(res));
});

function broadcastSettings(settings) {
  const msg = 'data: ' + JSON.stringify(settings) + '\n\n';
  for (const client of settingsClients) {
    client.write(msg);
  }
}

// PUT /api/admin/settings — admin only
app.put('/api/admin/settings', authMiddleware, ownerOnly, (req, res) => {
  const allowedKeys = ['showUrgencyCTA'];
  const current = readSettings();
  const filtered = {};
  for (const key of allowedKeys) {
    if (req.body[key] !== undefined) filtered[key] = req.body[key];
  }
  if (!Object.keys(filtered).length) {
    return res.status(400).json({ error: 'No valid settings provided' });
  }
  const updated = { ...current, ...filtered };
  writeJSON('settings.json', updated);
  broadcastSettings(updated);
  logAudit('settings_update', 'settings', `Updated: ${Object.keys(req.body).join(', ')}`, req.admin.username);
  res.json({ success: true, settings: updated });
});

// ── Admin: Expenses CRUD ──────────────────────────────────────────

app.get('/api/admin/expenses', authMiddleware, (req, res) => {
  let expenses = readJSON('expenses.json');
  const { from, to } = req.query;
  if (from) expenses = expenses.filter(e => e.date >= from);
  if (to) expenses = expenses.filter(e => e.date <= to);
  res.json(expenses.reverse().slice(0, 500));
});

app.post('/api/admin/expenses', authMiddleware, ownerOnly, (req, res) => {
  const { date, category, description, amount, paymentMethod } = req.body;
  if (!category || !amount || isNaN(Number(amount)) || Number(amount) <= 0) {
    return res.status(400).json({ error: 'Category and valid amount are required' });
  }
  const expenses = readJSON('expenses.json');
  const expense = {
    id: 'exp-' + Date.now(),
    date: date || new Date().toISOString().slice(0, 10),
    category: sanitizeInput(category),
    description: sanitizeInput(description || ''),
    amount: Number(amount),
    paymentMethod: sanitizeInput(paymentMethod || 'Cash'),
    timestamp: new Date().toISOString()
  };
  expenses.push(expense);
  writeJSON('expenses.json', expenses);
  logAudit('expense_create', expense.id, `${category}: ₱${Number(amount).toLocaleString()}`, req.admin.username);
  console.log(`[ADMIN] Expense added: ${category} ₱${amount}`);
  res.json({ success: true, expense });
});

app.put('/api/admin/expenses/:id', authMiddleware, ownerOnly, (req, res) => {
  const expenses = readJSON('expenses.json');
  const idx = expenses.findIndex(e => e.id === req.params.id);
  if (idx === -1) return res.status(404).json({ error: 'Expense not found' });
  const { date, category, description, amount, paymentMethod } = req.body;
  if (date !== undefined) expenses[idx].date = date;
  if (category !== undefined) expenses[idx].category = sanitizeInput(category);
  if (description !== undefined) expenses[idx].description = sanitizeInput(description);
  if (amount !== undefined) {
    if (isNaN(Number(amount)) || Number(amount) <= 0) {
      return res.status(400).json({ error: 'Amount must be greater than 0' });
    }
    expenses[idx].amount = Number(amount);
  }
  if (paymentMethod !== undefined) expenses[idx].paymentMethod = sanitizeInput(paymentMethod);
  writeJSON('expenses.json', expenses);
  logAudit('expense_update', expenses[idx].id, `Updated: ${expenses[idx].category} ₱${expenses[idx].amount}`, req.admin.username);
  res.json({ success: true, expense: expenses[idx] });
});

app.delete('/api/admin/expenses/:id', authMiddleware, ownerOnly, (req, res) => {
  let expenses = readJSON('expenses.json');
  const idx = expenses.findIndex(e => e.id === req.params.id);
  if (idx === -1) return res.status(404).json({ error: 'Expense not found' });
  const removed = expenses.splice(idx, 1)[0];
  writeJSON('expenses.json', expenses);
  logAudit('expense_delete', removed.id, `Deleted: ${removed.category} ₱${removed.amount}`, req.admin.username);
  res.json({ success: true });
});

// ── Admin: Walk-in Sales / POS ────────────────────────────────────

app.get('/api/admin/sales', authMiddleware, (req, res) => {
  let sales = readJSON('sales.json');
  const { from, to } = req.query;
  if (from) sales = sales.filter(s => s.timestamp && s.timestamp.slice(0, 10) >= from);
  if (to) sales = sales.filter(s => s.timestamp && s.timestamp.slice(0, 10) <= to);
  res.json(sales.reverse().slice(0, 500));
});

app.post('/api/admin/sales', authMiddleware, (req, res) => {
  const { items, discount, paymentMethod, customerName, notes } = req.body;
  if (!Array.isArray(items) || !items.length) {
    return res.status(400).json({ error: 'At least one item is required' });
  }

  const products = readJSON('products.json');
  const saleItems = [];

  for (const item of items) {
    if (!item.productId || !item.qty || item.qty < 1) {
      return res.status(400).json({ error: 'Each item needs productId and qty' });
    }
    const product = products.find(p => p.id === item.productId);
    if (!product) return res.status(400).json({ error: `Product ${item.productId} not found` });
    const stockNum = Number(product.stock) || 0;
    if (stockNum < item.qty) {
      return res.status(400).json({ error: `"${product.name}" insufficient stock (${stockNum} available)` });
    }
    saleItems.push({
      productId: product.id,
      name: product.name,
      price: product.price,
      costPrice: product.costPrice || 0,
      qty: item.qty
    });
  }

  const subtotal = saleItems.reduce((sum, i) => sum + (i.price * i.qty), 0);
  const discountAmt = Number(discount) || 0;
  const total = Math.max(0, subtotal - discountAmt);

  const sale = {
    id: 'sale-' + Date.now(),
    items: saleItems,
    subtotal,
    discount: discountAmt,
    total,
    paymentMethod: sanitizeInput(paymentMethod || 'Cash'),
    customerName: sanitizeInput(customerName || 'Walk-in'),
    notes: sanitizeInput(notes || ''),
    soldBy: req.admin.username,
    timestamp: new Date().toISOString()
  };

  // Decrement stock
  for (const item of saleItems) {
    const pidx = products.findIndex(p => p.id === item.productId);
    if (pidx === -1) continue;
    const prevStock = Number(products[pidx].stock) || 0;
    products[pidx].stock = prevStock - item.qty;
    logInventory(item.productId, item.name, 'sale', -item.qty, prevStock, products[pidx].stock, `Sale ${sale.id}`, req.admin.username);
  }
  writeJSON('products.json', products);

  const sales = readJSON('sales.json');
  sales.push(sale);
  writeJSON('sales.json', sales);
  logAudit('sale_create', sale.id, `Walk-in sale: ₱${total.toLocaleString()} (${saleItems.length} items)`, req.admin.username);
  console.log(`[ADMIN] Walk-in sale: ${sale.id} ₱${total}`);
  res.json({ success: true, sale });
});

function handleVoidSale(req, res) {
  const sales = readJSON('sales.json');
  const idx = sales.findIndex(s => s.id === req.params.id);
  if (idx === -1) return res.status(404).json({ error: 'Sale not found' });

  const { reason } = req.body;
  if (!reason) return res.status(400).json({ error: 'Void reason is required' });

  const sale = sales[idx];
  // Restore stock
  const products = readJSON('products.json');
  for (const item of (sale.items || [])) {
    const pidx = products.findIndex(p => p.id === item.productId);
    if (pidx === -1) continue;
    const prevStock = Number(products[pidx].stock) || 0;
    products[pidx].stock = prevStock + item.qty;
    logInventory(item.productId, item.name, 'void', item.qty, prevStock, products[pidx].stock, `Voided sale ${sale.id}: ${sanitizeInput(reason)}`, req.admin.username);
  }
  writeJSON('products.json', products);

  sale.voided = true;
  sale.voidReason = sanitizeInput(reason);
  sale.voidedBy = req.admin.username;
  sale.voidedAt = new Date().toISOString();
  writeJSON('sales.json', sales);
  logAudit('sale_void', sale.id, `Voided: ${reason}`, req.admin.username);
  console.log(`[ADMIN] Sale voided: ${sale.id}`);
  res.json({ success: true });
}
app.post('/api/admin/sales/:id/void', authMiddleware, ownerOnly, handleVoidSale);
app.delete('/api/admin/sales/:id', authMiddleware, ownerOnly, handleVoidSale);

// ── Admin: Inventory Log ──────────────────────────────────────────

app.get('/api/admin/inventory-log', authMiddleware, (req, res) => {
  let log = readJSON('inventory-log.json');
  const { productId, type, from, to } = req.query;
  if (productId) log = log.filter(e => e.productId === productId);
  if (type) log = log.filter(e => e.type === type);
  if (from) log = log.filter(e => e.timestamp && e.timestamp.slice(0, 10) >= from);
  if (to) log = log.filter(e => e.timestamp && e.timestamp.slice(0, 10) <= to);
  res.json(log.reverse().slice(0, 500));
});

app.post('/api/admin/inventory/restock', authMiddleware, (req, res) => {
  const { productId, qty, note } = req.body;
  if (!productId || !qty || isNaN(Number(qty)) || Number(qty) <= 0) {
    return res.status(400).json({ error: 'Product ID and valid quantity required' });
  }
  const products = readJSON('products.json');
  const idx = products.findIndex(p => p.id === productId);
  if (idx === -1) return res.status(404).json({ error: 'Product not found' });

  const prevStock = Number(products[idx].stock) || 0;
  const addQty = Number(qty);
  products[idx].stock = prevStock + addQty;
  writeJSON('products.json', products);
  logInventory(productId, products[idx].name, 'restock', addQty, prevStock, products[idx].stock, sanitizeInput(note || 'Restock'), req.admin.username);
  logAudit('restock', productId, `Restocked ${products[idx].name}: +${addQty} (${prevStock}→${products[idx].stock})`, req.admin.username);
  console.log(`[ADMIN] Restocked ${products[idx].name}: +${addQty}`);
  res.json({ success: true, product: products[idx] });
});

// ── Admin: Reports / P&L ──────────────────────────────────────────

app.get('/api/admin/reports', authMiddleware, ownerOnly, (req, res) => {
  const now = new Date();
  const from = req.query.from || new Date(now.getFullYear(), now.getMonth(), 1).toISOString().slice(0, 10);
  const to = req.query.to || now.toISOString().slice(0, 10);

  const orders = readJSON('orders.json');
  const sales = readJSON('sales.json');
  const expenses = readJSON('expenses.json');

  // Online revenue (completed orders in range)
  const completedOrders = orders.filter(o =>
    o.status === 'Completed' && o.timestamp && o.timestamp.slice(0, 10) >= from && o.timestamp.slice(0, 10) <= to
  );
  const onlineRevenue = completedOrders.reduce((sum, o) => sum + (parseFloat(o.total) || 0), 0);

  // Walk-in revenue (non-voided sales in range)
  const validSales = sales.filter(s =>
    !s.voided && s.timestamp && s.timestamp.slice(0, 10) >= from && s.timestamp.slice(0, 10) <= to
  );
  const walkinRevenue = validSales.reduce((sum, s) => sum + (s.total || 0), 0);

  // COGS
  const products = readJSON('products.json');
  let cogs = 0;
  // From walk-in sales
  for (const sale of validSales) {
    for (const item of (sale.items || [])) {
      cogs += (item.costPrice || 0) * (item.qty || 1);
    }
  }
  // From completed online orders
  for (const order of completedOrders) {
    for (const item of (order.items || [])) {
      const product = products.find(p => p.id === item.productId);
      const costPrice = product ? (product.costPrice || 0) : 0;
      cogs += costPrice * (item.qty || item.quantity || 1);
    }
  }

  // Expenses in range
  const periodExpenses = expenses.filter(e => e.date >= from && e.date <= to);
  const expenseByCategory = {};
  let totalExpenses = 0;
  for (const e of periodExpenses) {
    expenseByCategory[e.category] = (expenseByCategory[e.category] || 0) + e.amount;
    totalExpenses += e.amount;
  }

  const totalRevenue = onlineRevenue + walkinRevenue;
  const grossProfit = totalRevenue - cogs;
  const netProfit = grossProfit - totalExpenses;

  // Daily revenue breakdown
  const dailyRevenue = [];
  const startDate = new Date(from + 'T00:00:00');
  const endDate = new Date(to + 'T00:00:00');
  for (let d = new Date(startDate); d <= endDate; d.setDate(d.getDate() + 1)) {
    const dateStr = d.toISOString().slice(0, 10);
    const dayOnline = completedOrders
      .filter(o => o.timestamp && o.timestamp.slice(0, 10) === dateStr)
      .reduce((sum, o) => sum + (parseFloat(o.total) || 0), 0);
    const dayWalkin = validSales
      .filter(s => s.timestamp && s.timestamp.slice(0, 10) === dateStr)
      .reduce((sum, s) => sum + (s.total || 0), 0);
    dailyRevenue.push({ date: dateStr, online: dayOnline, walkin: dayWalkin, total: dayOnline + dayWalkin });
  }

  // Top products
  const productCounts = {};
  for (const sale of validSales) {
    for (const item of (sale.items || [])) {
      productCounts[item.name] = (productCounts[item.name] || 0) + item.qty;
    }
  }
  for (const order of completedOrders) {
    for (const item of (order.items || [])) {
      const name = item.name || item.product || 'Unknown';
      productCounts[name] = (productCounts[name] || 0) + (item.qty || item.quantity || 1);
    }
  }
  const topProducts = Object.entries(productCounts)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 10)
    .map(([name, qty]) => ({ name, qty }));

  res.json({
    period: { from, to },
    revenue: { online: onlineRevenue, walkin: walkinRevenue, total: totalRevenue },
    cogs,
    grossProfit,
    grossMargin: totalRevenue > 0 ? Number(((grossProfit / totalRevenue) * 100).toFixed(1)) : 0,
    expenses: { ...expenseByCategory, total: totalExpenses },
    netProfit,
    netMargin: totalRevenue > 0 ? Number(((netProfit / totalRevenue) * 100).toFixed(1)) : 0,
    orderCount: { online: completedOrders.length, walkin: validSales.length, total: completedOrders.length + validSales.length },
    topProducts,
    dailyRevenue
  });
});

// ── Admin: Audit Log ──────────────────────────────────────────────

app.get('/api/admin/audit', authMiddleware, (req, res) => {
  let log = readJSON('audit.json');
  const { action, from, to, by } = req.query;
  if (action) log = log.filter(e => e.action === action);
  if (by) log = log.filter(e => e.by === by);
  if (from) log = log.filter(e => e.timestamp && e.timestamp.slice(0, 10) >= from);
  if (to) log = log.filter(e => e.timestamp && e.timestamp.slice(0, 10) <= to);
  res.json(log.reverse().slice(0, 200));
});

// ── API 404 handler ──────────────────────────────────────────────

app.all('/api/*', (req, res) => {
  res.status(404).json({ error: 'Not found' });
});

// Serve admin panel
app.get('/admin', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'admin.html'));
});

// Serve privacy and data deletion pages
app.get('/privacy', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'privacy.html'));
});
app.get('/data-deletion', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'data-deletion.html'));
});

// Catch-all: serve index.html for SPA
app.get('*', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

app.listen(PORT, () => {
  console.log(`H.U.B server running on port ${PORT}`);
});
