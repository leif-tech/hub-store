import re

with open('public/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# ── 1. NEW WHITE CSS ────────────────────────────────────────────────────────────
NEW_CSS = """
    *,*::before,*::after{margin:0;padding:0;box-sizing:border-box}
    html{scroll-behavior:smooth;scroll-padding-top:116px}
    body{font-family:'Plus Jakarta Sans',sans-serif;background:#fff;color:#374151;line-height:1.65;overflow-x:hidden}
    a{color:inherit;text-decoration:none}
    img{max-width:100%;display:block}
    ul{list-style:none}
    button{cursor:pointer;border:none;font-family:inherit;background:none}
    .container{max-width:1240px;margin:0 auto;padding:0 24px}

    :root{
      --blue:#1a6ee8;
      --blue-dark:#1255c0;
      --blue-light:#eff6ff;
      --blue-mid:#dbeafe;
      --orange:#f97316;
      --gold:#f59e0b;
      --bg:#ffffff;
      --bg-soft:#f4f7ff;
      --card:#ffffff;
      --border:#e5eaf3;
      --border-blue:#c7d9f8;
      --text:#374151;
      --text-dim:#9ca3af;
      --heading:#0f172a;
      --grad:linear-gradient(135deg,#1255c0 0%,#1a6ee8 55%,#3b9dfd 100%);
      --grad-orange:linear-gradient(135deg,#f97316,#fb923c);
      --shadow-xs:0 1px 3px rgba(15,23,42,0.06);
      --shadow-sm:0 2px 8px rgba(15,23,42,0.08);
      --shadow:0 4px 20px rgba(15,23,42,0.1);
      --shadow-lg:0 12px 40px rgba(15,23,42,0.12);
      --shadow-blue:0 6px 24px rgba(26,110,232,0.22);
      --r:10px;
      --r-lg:16px;
      --r-xl:24px;
    }

    /* ===== ANNOUNCEMENT BAR ===== */
    .topbar-announce{background:var(--grad);color:#fff;padding:9px 0;font-size:0.78rem;font-weight:600;text-align:center;letter-spacing:0.2px}
    .topbar-announce a{color:#fff;text-decoration:underline;margin-left:6px;opacity:.9}
    .topbar-announce .sep{margin:0 12px;opacity:0.5}

    /* ===== BUTTONS ===== */
    .btn{display:inline-flex;align-items:center;gap:8px;padding:12px 28px;border-radius:8px;font-weight:700;font-size:0.875rem;letter-spacing:0.3px;transition:all .22s;cursor:pointer;border:none}
    .btn-primary{background:var(--grad);color:#fff;box-shadow:var(--shadow-blue)}
    .btn-primary:hover{transform:translateY(-2px);box-shadow:0 10px 32px rgba(26,110,232,0.35)}
    .btn-outline{background:#fff;color:var(--blue);border:2px solid var(--border-blue)}
    .btn-outline:hover{border-color:var(--blue);background:var(--blue-light)}
    .btn-orange{background:var(--grad-orange);color:#fff;box-shadow:0 4px 16px rgba(249,115,22,0.3)}
    .btn-orange:hover{transform:translateY(-2px);box-shadow:0 8px 28px rgba(249,115,22,0.4)}

    /* ===== NAVBAR ===== */
    .navbar{position:sticky;top:0;z-index:1000;background:rgba(255,255,255,0.97);backdrop-filter:blur(20px);border-bottom:2px solid var(--border-blue);box-shadow:var(--shadow-sm)}
    .navbar .container{display:flex;align-items:center;justify-content:space-between;height:64px;gap:12px}
    .nav-logo img{height:38px;width:auto}
    .nav-links{display:flex;align-items:center;margin-left:auto;margin-right:auto}
    .nav-links a{padding:20px 14px;font-size:0.8rem;font-weight:700;color:var(--text);text-transform:uppercase;letter-spacing:0.8px;transition:color .2s;position:relative}
    .nav-links a:hover,.nav-links a.active{color:var(--blue)}
    .nav-links a::after{content:'';position:absolute;bottom:0;left:14px;right:14px;height:3px;background:var(--grad);transform:scaleX(0);transition:transform .25s;border-radius:3px 3px 0 0}
    .nav-links a:hover::after,.nav-links a.active::after{transform:scaleX(1)}
    .nav-links .shop-link{color:var(--orange);font-weight:800}
    .nav-links .nav-cta{margin-left:8px;padding:9px 20px;border-radius:8px;background:var(--grad);color:#fff !important;box-shadow:var(--shadow-blue);font-size:0.8rem}
    .nav-links .nav-cta::after{display:none}
    .nav-links .nav-cta:hover{transform:translateY(-1px);box-shadow:0 6px 22px rgba(26,110,232,0.4)}
    .nav-search{position:relative;flex:1;max-width:280px}
    .nav-search input{width:100%;padding:9px 36px 9px 14px;background:var(--bg-soft);border:1.5px solid var(--border);border-radius:8px;font-size:0.82rem;color:var(--heading);transition:all .2s;outline:none}
    .nav-search input::placeholder{color:var(--text-dim)}
    .nav-search input:focus{border-color:var(--blue);background:#fff;box-shadow:0 0 0 3px rgba(26,110,232,0.1)}
    .nav-search-icon{position:absolute;right:12px;top:50%;transform:translateY(-50%);color:var(--text-dim);pointer-events:none}
    .nav-suggest{position:absolute;top:calc(100% + 8px);left:0;right:0;background:#fff;border:1px solid var(--border);border-radius:12px;box-shadow:var(--shadow-lg);overflow:hidden;z-index:100}
    .nav-suggest-item{padding:11px 16px;font-size:0.84rem;cursor:pointer;transition:background .15s;color:var(--heading);display:flex;align-items:center;gap:8px}
    .nav-suggest-item:hover{background:var(--blue-light)}
    .nav-icons{display:flex;align-items:center;gap:4px}
    .nav-icon-btn{position:relative;width:40px;height:40px;border-radius:10px;display:flex;align-items:center;justify-content:center;color:var(--text);background:var(--bg-soft);transition:all .2s;border:1px solid var(--border)}
    .nav-icon-btn svg{width:18px;height:18px}
    .nav-icon-btn:hover{background:var(--blue-light);color:var(--blue);border-color:var(--border-blue)}
    .nav-badge{position:absolute;top:4px;right:4px;background:var(--orange);color:#fff;border-radius:50%;width:16px;height:16px;font-size:0.6rem;font-weight:700;display:none;align-items:center;justify-content:center;border:2px solid #fff}
    .nav-badge.show{display:flex}
    .nav-user-area{display:flex;align-items:center;gap:8px;position:relative}
    .nav-login-btn{display:flex;align-items:center;gap:7px;padding:8px 16px;border-radius:8px;border:1.5px solid var(--border);color:var(--heading);font-size:0.82rem;font-weight:600;transition:all .2s;background:#fff}
    .nav-login-btn:hover{border-color:var(--blue);color:var(--blue);background:var(--blue-light)}
    .nav-user-avatar{width:36px;height:36px;border-radius:50%;object-fit:cover;cursor:pointer;border:2.5px solid var(--blue)}
    .nav-user-name{font-size:0.82rem;font-weight:700;color:var(--heading);cursor:pointer}
    .nav-user-dropdown{position:absolute;top:calc(100% + 12px);right:0;background:#fff;border:1px solid var(--border);border-radius:14px;box-shadow:var(--shadow-lg);min-width:220px;overflow:hidden;z-index:200;display:none}
    .nav-user-dropdown.open{display:block}
    .ud-header{padding:16px 18px 12px;border-bottom:1px solid var(--border)}
    .ud-name{font-weight:700;font-size:0.92rem;color:var(--heading)}
    .ud-email{font-size:0.78rem;color:var(--text-dim);margin-top:2px}
    .ud-points{font-size:0.78rem;color:var(--blue);font-weight:600;margin-top:6px}
    .ud-signout{display:block;width:100%;padding:12px 18px;text-align:left;font-size:0.84rem;font-weight:600;color:#ef4444;transition:background .15s}
    .ud-signout:hover{background:#fef2f2}
    .hamburger{display:none;flex-direction:column;gap:5px;padding:8px;cursor:pointer}
    .hamburger span{display:block;width:22px;height:2px;background:var(--heading);border-radius:2px;transition:all .3s}

    /* ===== MOBILE MENU ===== */
    .mobile-menu{display:none;flex-direction:column;background:#fff;border-bottom:1px solid var(--border);box-shadow:var(--shadow);padding:8px 0;position:sticky;top:64px;z-index:999}
    .mobile-menu.open{display:flex}
    .mobile-menu a{padding:13px 24px;font-size:0.88rem;font-weight:600;color:var(--text);border-bottom:1px solid var(--bg-soft);transition:color .2s}
    .mobile-menu a:hover{color:var(--blue);background:var(--blue-light)}

    /* ===== AUTH OVERLAY ===== */
    .auth-overlay{position:fixed;inset:0;background:rgba(15,23,42,0.5);backdrop-filter:blur(8px);z-index:2000;display:none;align-items:center;justify-content:center}
    .auth-overlay.open{display:flex}
    .auth-modal{background:#fff;border-radius:20px;padding:40px 36px;max-width:400px;width:90%;box-shadow:var(--shadow-lg);position:relative;text-align:center}
    .auth-modal-close{position:absolute;top:16px;right:20px;font-size:1.5rem;color:var(--text-dim);transition:color .2s}
    .auth-modal-close:hover{color:var(--heading)}
    .auth-modal h2{font-family:'Exo 2',sans-serif;font-size:1.5rem;font-weight:800;color:var(--heading);margin-bottom:8px}
    .auth-sub{font-size:0.84rem;color:var(--text-dim);margin-bottom:28px}
    .auth-btn{display:flex;align-items:center;justify-content:center;gap:10px;width:100%;padding:13px 20px;border-radius:10px;font-size:0.88rem;font-weight:600;transition:all .2s;border:1.5px solid var(--border);cursor:pointer;margin-bottom:12px;color:var(--heading);background:#fff}
    .auth-btn:hover{border-color:var(--blue);background:var(--blue-light)}
    .auth-btn-google:hover{border-color:#4285f4;background:#f0f4ff}
    .auth-btn-facebook{border-color:#1877f2;background:#1877f2;color:#fff}
    .auth-btn-facebook:hover{background:#0e66d0;border-color:#0e66d0}
    .auth-divider{display:flex;align-items:center;gap:12px;margin:4px 0 12px;font-size:0.78rem;color:var(--text-dim)}
    .auth-divider::before,.auth-divider::after{content:'';flex:1;height:1px;background:var(--border)}

    /* ===== HERO ===== */
    .hero{background:linear-gradient(150deg,#0a1628 0%,#0f2042 40%,#0d1b3e 100%);overflow:hidden;position:relative;min-height:600px}
    .hero-bg-img{position:absolute;inset:0;background-image:url('/hero-bg.jpg');background-size:cover;background-position:center;opacity:0.07;pointer-events:none}
    .hero::before{content:'';position:absolute;inset:0;background:radial-gradient(ellipse 60% 100% at 100% 50%,rgba(26,110,232,0.2) 0%,transparent 65%);pointer-events:none}
    .hero-slides{position:relative;z-index:2}
    .hero-slide{position:absolute;inset:0;opacity:0;display:flex;align-items:center;transition:opacity .6s ease}
    .hero-slide.active{opacity:1;position:relative}
    .hero-slide .container{padding-top:72px;padding-bottom:72px}
    .hero-split{display:grid;grid-template-columns:1fr 1fr;gap:48px;align-items:center}
    .hero-inner{max-width:580px}
    .hero-eyebrow{display:flex;align-items:center;gap:10px;margin-bottom:20px}
    .hero-badge{display:inline-flex;align-items:center;gap:8px;background:rgba(249,115,22,0.15);border:1px solid rgba(249,115,22,0.4);color:#fb923c;padding:5px 14px;border-radius:100px;font-size:0.75rem;font-weight:700;letter-spacing:0.8px;text-transform:uppercase}
    .hero-badge .dot{width:6px;height:6px;background:#fb923c;border-radius:50%;animation:pulse 2s infinite}
    @keyframes pulse{0%,100%{opacity:1;transform:scale(1)}50%{opacity:0.5;transform:scale(1.4)}}
    .hero-inner h1{font-family:'Exo 2',sans-serif;font-size:clamp(2.6rem,5.5vw,4.4rem);font-weight:900;color:#fff;line-height:1.06;margin-bottom:18px;letter-spacing:-0.5px}
    .hero-desc{font-size:1.02rem;color:rgba(255,255,255,0.55);line-height:1.75;margin-bottom:34px;max-width:500px}
    .hero-buttons{display:flex;flex-wrap:wrap;gap:12px}
    .hero-trust{display:flex;align-items:center;gap:16px;margin-top:28px;padding-top:24px;border-top:1px solid rgba(255,255,255,0.1)}
    .hero-trust-item{display:flex;align-items:center;gap:7px;font-size:0.78rem;color:rgba(255,255,255,0.55);font-weight:600}
    .hero-trust-icon{font-size:1rem}
    .hero-img-col{position:relative;display:flex;align-items:center;justify-content:center}
    .hero-img-frame{position:relative;border-radius:20px;overflow:hidden;box-shadow:0 32px 80px rgba(0,0,0,0.4)}
    .hero-img-frame img{width:100%;max-height:420px;object-fit:cover;display:block}
    .hero-img-frame::after{content:'';position:absolute;inset:0;background:linear-gradient(to top,rgba(10,22,40,0.4) 0%,transparent 50%);pointer-events:none}
    .hero-float-badge{position:absolute;bottom:-16px;left:-16px;background:#fff;border-radius:14px;padding:14px 18px;box-shadow:var(--shadow-lg);display:flex;align-items:center;gap:10px;z-index:3}
    .hero-float-badge .fb-num{font-family:'Exo 2',sans-serif;font-size:1.4rem;font-weight:900;color:var(--blue);line-height:1}
    .hero-float-badge .fb-lbl{font-size:0.72rem;color:var(--text-dim);font-weight:600;line-height:1.4}
    .hero-float-badge2{position:absolute;top:-16px;right:-16px;background:var(--grad-orange);border-radius:14px;padding:12px 16px;box-shadow:0 8px 24px rgba(249,115,22,0.4);z-index:3;text-align:center}
    .hero-float-badge2 .fb2-label{font-size:0.68rem;color:rgba(255,255,255,0.8);font-weight:700;text-transform:uppercase;letter-spacing:0.5px}
    .hero-float-badge2 .fb2-val{font-family:'Exo 2',sans-serif;font-size:1.1rem;font-weight:900;color:#fff;line-height:1.2}
    .hero-dots{display:flex;justify-content:center;gap:8px;padding:20px;position:relative;z-index:2}
    .hero-dot{width:8px;height:8px;border-radius:50%;background:rgba(255,255,255,0.25);cursor:pointer;transition:all .3s;border:none}
    .hero-dot.active{background:#fff;width:24px;border-radius:4px}
    .hero-arrow{position:absolute;top:50%;transform:translateY(-50%);width:44px;height:44px;border-radius:50%;background:rgba(255,255,255,0.1);backdrop-filter:blur(10px);border:1px solid rgba(255,255,255,0.2);color:#fff;display:flex;align-items:center;justify-content:center;font-size:1rem;transition:all .2s;z-index:10}
    .hero-arrow:hover{background:rgba(255,255,255,0.2)}
    .hero-arrow.prev{left:20px}
    .hero-arrow.next{right:20px}

    /* ===== STATS BAR ===== */
    .stats-bar{background:#fff;border-bottom:1px solid var(--border)}
    .stats-inner{display:grid;grid-template-columns:repeat(5,1fr);border-left:1px solid var(--border)}
    .stat-item{padding:22px 24px;text-align:center;border-right:1px solid var(--border);position:relative}
    .stat-item:first-child{background:var(--grad);border-right:none}
    .stat-item:first-child .stat-num,.stat-item:first-child .stat-label{color:#fff !important}
    .stat-num{font-family:'Exo 2',sans-serif;font-size:1.8rem;font-weight:900;color:var(--blue);line-height:1}
    .stat-label{font-size:0.7rem;color:var(--text-dim);text-transform:uppercase;letter-spacing:0.8px;margin-top:4px;font-weight:600}

    /* ===== SHARED SECTION STYLES ===== */
    .section{padding:88px 0;background:var(--bg)}
    .section-alt{background:var(--bg-soft)}
    .section-header{margin-bottom:52px}
    .section-header.center{text-align:center}
    .section-eyebrow{display:flex;align-items:center;gap:10px;margin-bottom:12px}
    .section-eyebrow.center{justify-content:center}
    .section-line{width:32px;height:3px;background:var(--grad);border-radius:3px}
    .section-tag{font-size:0.72rem;font-weight:700;letter-spacing:1.8px;text-transform:uppercase;color:var(--blue)}
    .section-title{font-family:'Exo 2',sans-serif;font-size:clamp(1.75rem,3vw,2.4rem);font-weight:800;color:var(--heading);letter-spacing:0.2px;line-height:1.18;margin-bottom:14px}
    .section-desc{font-size:0.96rem;color:var(--text-dim);line-height:1.72;max-width:580px}
    .section-header.center .section-desc{margin:0 auto}
    .grad{background:var(--grad);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text}
    .glass{background:#fff;border:1px solid var(--border);box-shadow:var(--shadow-sm)}
    .fade-in{opacity:0;transform:translateY(20px);transition:opacity .55s ease,transform .55s ease}
    .fade-in.visible{opacity:1;transform:translateY(0)}

    /* ===== BRAND TICKER ===== */
    .brand-ticker{background:var(--bg-soft);border-top:1px solid var(--border);border-bottom:1px solid var(--border);overflow:hidden;padding:14px 0}
    .brand-track{display:flex;gap:0;white-space:nowrap;animation:ticker 30s linear infinite}
    @keyframes ticker{0%{transform:translateX(0)}100%{transform:translateX(-50%)}}
    .brand-item{display:inline-flex;align-items:center;gap:8px;padding:0 28px;font-size:0.75rem;font-weight:700;color:var(--text-dim);letter-spacing:1px;text-transform:uppercase}
    .brand-item .dot{width:4px;height:4px;background:var(--blue);border-radius:50%}

    /* ===== CATEGORY TILES ===== */
    .cat-tiles-section{padding:80px 0;background:var(--bg)}
    .cat-tiles-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(150px,1fr));gap:14px}
    .cat-tile{border-radius:14px;overflow:hidden;cursor:pointer;background:#fff;border:1.5px solid var(--border);transition:all .25s;text-align:center;padding-bottom:14px}
    .cat-tile:hover{transform:translateY(-5px);box-shadow:var(--shadow);border-color:var(--border-blue)}
    .cat-tile-img{width:100%;aspect-ratio:1;object-fit:cover;display:block;background:var(--bg-soft)}
    .cat-tile-label{padding:10px 8px 0;font-size:0.78rem;font-weight:700;color:var(--heading);text-transform:uppercase;letter-spacing:0.5px}

    /* ===== PRODUCT CARDS ===== */
    .product-card{background:#fff;border:1.5px solid var(--border);border-radius:var(--r-lg);overflow:hidden;transition:all .25s;box-shadow:var(--shadow-xs);display:flex;flex-direction:column}
    .product-card:hover{transform:translateY(-5px);box-shadow:var(--shadow-lg);border-color:var(--border-blue)}
    .product-img-wrap{position:relative;overflow:hidden;aspect-ratio:1;background:var(--bg-soft)}
    .product-img-wrap img{width:100%;height:100%;object-fit:contain;padding:16px;transition:transform .4s ease}
    .product-card:hover .product-img-wrap img{transform:scale(1.06)}
    .product-badge{position:absolute;top:10px;left:10px;background:var(--grad-orange);color:#fff;font-size:0.65rem;font-weight:700;letter-spacing:0.5px;padding:4px 10px;border-radius:100px;text-transform:uppercase}
    .product-wish-btn{position:absolute;top:10px;right:10px;width:34px;height:34px;border-radius:8px;background:rgba(255,255,255,0.95);display:flex;align-items:center;justify-content:center;color:var(--text-dim);transition:all .2s;border:1px solid var(--border)}
    .product-wish-btn svg{width:16px;height:16px}
    .product-wish-btn:hover,.product-wish-btn.wished{color:#ef4444;background:#fff;border-color:#fca5a5}
    .product-wish-btn.wished svg{fill:#ef4444}
    .product-info{padding:16px 18px;flex:1;display:flex;flex-direction:column}
    .product-cat{font-size:0.67rem;font-weight:700;text-transform:uppercase;letter-spacing:1px;color:var(--blue);margin-bottom:5px}
    .product-name{font-size:0.88rem;font-weight:700;color:var(--heading);line-height:1.45;margin-bottom:10px;flex:1}
    .product-price{font-size:1.1rem;font-weight:800;color:var(--heading);margin-bottom:12px}
    .product-price-orig{font-size:0.78rem;font-weight:500;color:var(--text-dim);text-decoration:line-through;margin-left:6px}
    .product-actions{display:flex;gap:8px}
    .product-add-btn{flex:1;padding:10px 14px;background:var(--grad);color:#fff;border-radius:8px;font-size:0.82rem;font-weight:700;transition:all .2s;box-shadow:0 2px 8px rgba(26,110,232,0.2)}
    .product-add-btn:hover{transform:translateY(-1px);box-shadow:0 5px 18px rgba(26,110,232,0.35)}
    .product-compare-btn{padding:10px 12px;border-radius:8px;border:1.5px solid var(--border);color:var(--text-dim);font-size:0.75rem;font-weight:600;transition:all .2s;background:#fff}
    .product-compare-btn:hover{border-color:var(--blue);color:var(--blue);background:var(--blue-light)}
    .featured-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(240px,1fr));gap:22px}

    /* ===== SHOP PAGE ===== */
    .shop-page{position:fixed;inset:0;z-index:900;background:var(--bg-soft);overflow-y:auto;transform:translateX(100%);transition:transform .35s cubic-bezier(0.4,0,0.2,1)}
    .shop-page.open{transform:translateX(0)}
    .shop-topbar{position:sticky;top:0;z-index:10;background:rgba(255,255,255,0.97);backdrop-filter:blur(16px);border-bottom:1px solid var(--border);box-shadow:var(--shadow-sm)}
    .shop-back{font-size:0.82rem;font-weight:600;color:var(--text);padding:8px 14px;border-radius:8px;background:var(--bg-soft);border:1px solid var(--border);transition:all .2s}
    .shop-back:hover{color:var(--blue);border-color:var(--blue);background:var(--blue-light)}
    .topbar-cart{display:flex;align-items:center;gap:8px;padding:8px 18px;border-radius:8px;background:var(--grad);color:#fff;font-size:0.82rem;font-weight:700;transition:all .2s;box-shadow:var(--shadow-blue)}
    .topbar-cart:hover{transform:translateY(-1px);box-shadow:0 6px 22px rgba(26,110,232,0.4)}
    .topbar-cart-count{font-size:0.7rem;background:rgba(255,255,255,0.2);padding:1px 6px;border-radius:100px}
    .topbar-cart-total{font-size:0.8rem}
    .shop-body{padding:24px 0 80px}
    .shop-layout{display:grid;grid-template-columns:260px 1fr;gap:28px;align-items:start}
    .shop-sidebar{background:#fff;border:1px solid var(--border);border-radius:var(--r-lg);padding:24px;position:sticky;top:80px;box-shadow:var(--shadow-xs)}
    .filter-overlay{display:none;position:fixed;inset:0;background:rgba(0,0,0,0.45);z-index:100}
    .filter-overlay.open{display:block}
    .filter-overlay-close{display:none;justify-content:space-between;align-items:center;margin-bottom:16px}
    .filter-overlay-close h3{font-size:1rem;font-weight:700;color:var(--heading)}
    .filter-overlay-close button{font-size:1.4rem;color:var(--text-dim)}
    .shop-search{margin-bottom:20px}
    .shop-search input{width:100%;padding:10px 14px;border-radius:8px;border:1.5px solid var(--border);font-size:0.84rem;background:var(--bg-soft);color:var(--heading);outline:none;transition:all .2s}
    .shop-search input:focus{border-color:var(--blue);background:#fff;box-shadow:0 0 0 3px rgba(26,110,232,0.08)}
    .filter-group{margin-bottom:24px}
    .filter-group h4{font-size:0.72rem;font-weight:700;text-transform:uppercase;letter-spacing:0.8px;color:var(--text-dim);margin-bottom:12px}
    .filter-cat-btn{display:flex;align-items:center;justify-content:space-between;width:100%;padding:8px 10px;border-radius:8px;margin-bottom:4px;font-size:0.84rem;font-weight:500;color:var(--text);transition:all .15s;background:transparent}
    .filter-cat-btn:hover{background:var(--bg-soft);color:var(--heading)}
    .filter-cat-btn.active{background:var(--blue-light);color:var(--blue);font-weight:700}
    .filter-cat-count{font-size:0.7rem;background:var(--bg-soft);padding:2px 6px;border-radius:100px;color:var(--text-dim)}
    .filter-cat-btn.active .filter-cat-count{background:rgba(26,110,232,0.12);color:var(--blue)}
    .price-range{display:flex;align-items:center;gap:8px}
    .price-range input{flex:1;padding:8px 10px;border-radius:8px;border:1.5px solid var(--border);font-size:0.82rem;background:var(--bg-soft);color:var(--heading);outline:none;transition:all .2s}
    .price-range input:focus{border-color:var(--blue)}
    .price-range span{color:var(--text-dim);font-size:0.8rem}
    .filter-reset-btn{width:100%;padding:10px;border-radius:8px;border:1px solid var(--border);color:var(--text);font-size:0.82rem;font-weight:600;transition:all .2s;background:var(--bg-soft)}
    .filter-reset-btn:hover{border-color:var(--blue);color:var(--blue);background:var(--blue-light)}
    .shop-header{display:flex;align-items:center;justify-content:space-between;margin-bottom:20px}
    .shop-count{font-size:0.84rem;color:var(--text-dim);font-weight:500}
    #shopSort{padding:8px 12px;border-radius:8px;border:1px solid var(--border);font-size:0.82rem;background:#fff;color:var(--heading);outline:none;cursor:pointer}
    .shop-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:20px}
    .mobile-filter-toggle{display:none;width:100%;padding:11px;border:1px solid var(--border);border-radius:8px;font-size:0.84rem;font-weight:600;color:var(--text);margin-bottom:16px;background:#fff;transition:all .2s}
    .mobile-filter-toggle:hover{border-color:var(--blue);color:var(--blue)}

    /* ===== PRODUCT DETAIL ===== */
    .product-detail{position:fixed;inset:0;z-index:950;background:var(--bg);overflow-y:auto;transform:translateX(100%);transition:transform .35s cubic-bezier(0.4,0,0.2,1)}
    .product-detail.open{transform:translateX(0)}
    .pd-topbar{position:sticky;top:0;z-index:10;background:rgba(255,255,255,0.97);backdrop-filter:blur(16px);border-bottom:1px solid var(--border);display:flex;align-items:center;justify-content:space-between;padding:0 24px;height:56px;box-shadow:var(--shadow-sm)}
    .pd-back{font-size:0.84rem;font-weight:600;color:var(--text);padding:7px 14px;border-radius:8px;background:var(--bg-soft);border:1px solid var(--border);transition:all .2s}
    .pd-back:hover{color:var(--blue);border-color:var(--blue);background:var(--blue-light)}
    .pd-content{max-width:1000px;margin:0 auto;padding:40px 24px 80px}
    .pd-grid{display:grid;grid-template-columns:1fr 1fr;gap:48px;align-items:start}
    .pd-images{position:sticky;top:80px}
    .pd-main-img{width:100%;aspect-ratio:1;background:var(--bg-soft);border-radius:var(--r-lg);overflow:hidden;margin-bottom:12px;border:1px solid var(--border);cursor:zoom-in;display:flex;align-items:center;justify-content:center;padding:24px}
    .pd-main-img img{max-height:100%;max-width:100%;object-fit:contain}
    .pd-thumbs{display:flex;gap:10px;flex-wrap:wrap}
    .pd-thumb{width:72px;height:72px;border-radius:8px;overflow:hidden;border:2px solid var(--border);cursor:pointer;transition:all .2s;background:var(--bg-soft);display:flex;align-items:center;justify-content:center;padding:4px}
    .pd-thumb img{width:100%;height:100%;object-fit:contain}
    .pd-thumb.active,.pd-thumb:hover{border-color:var(--blue)}
    .pd-info h1{font-family:'Exo 2',sans-serif;font-size:1.9rem;font-weight:800;color:var(--heading);margin-bottom:8px;line-height:1.2}
    .pd-cat{font-size:0.72rem;text-transform:uppercase;letter-spacing:1px;color:var(--blue);font-weight:700;margin-bottom:14px;display:block}
    .pd-price{font-size:2rem;font-weight:900;color:var(--heading);margin-bottom:4px}
    .pd-price-orig{font-size:0.9rem;color:var(--text-dim);text-decoration:line-through;margin-bottom:20px;display:block}
    .pd-desc{font-size:0.92rem;color:var(--text);line-height:1.8;margin-bottom:24px}
    .pd-specs{margin-bottom:28px}
    .pd-specs h3{font-size:0.72rem;text-transform:uppercase;letter-spacing:0.8px;color:var(--text-dim);font-weight:700;margin-bottom:10px}
    .pd-spec-row{display:flex;gap:8px;padding:10px 0;border-bottom:1px solid var(--bg-soft);font-size:0.86rem}
    .pd-spec-key{color:var(--text-dim);min-width:130px;font-weight:500}
    .pd-spec-val{color:var(--heading);font-weight:600}
    .pd-actions{display:flex;gap:12px;flex-wrap:wrap}
    .pd-add-btn{flex:1;min-width:160px;padding:14px 24px;background:var(--grad);color:#fff;border-radius:10px;font-size:0.9rem;font-weight:700;transition:all .2s;box-shadow:var(--shadow-blue)}
    .pd-add-btn:hover{transform:translateY(-2px);box-shadow:0 10px 32px rgba(26,110,232,0.4)}
    .pd-wish-btn{padding:14px 16px;border-radius:10px;border:1.5px solid var(--border);color:var(--text-dim);font-size:0.9rem;font-weight:600;transition:all .2s;background:#fff}
    .pd-wish-btn:hover,.pd-wish-btn.wished{border-color:#ef4444;color:#ef4444;background:#fef2f2}

    /* ===== LIGHTBOX ===== */
    .lightbox{position:fixed;inset:0;background:rgba(0,0,0,0.92);z-index:3000;display:none;align-items:center;justify-content:center;cursor:zoom-out}
    .lightbox.open{display:flex}
    .lightbox img{max-width:90vw;max-height:90vh;object-fit:contain;border-radius:8px}
    .lightbox-close{position:absolute;top:20px;right:24px;font-size:2rem;color:rgba(255,255,255,0.6);transition:color .2s}
    .lightbox-close:hover{color:#fff}

    /* ===== SERVICES ===== */
    .services-list{display:flex;flex-direction:column;gap:1px;background:var(--border);border-radius:var(--r-xl);overflow:hidden;border:1px solid var(--border)}
    .service-row{display:grid;grid-template-columns:64px 1fr auto;gap:24px;align-items:center;padding:28px 32px;background:#fff;transition:all .22s;cursor:default}
    .service-row:hover{background:var(--bg-soft)}
    .svc-icon-box{width:56px;height:56px;border-radius:16px;display:flex;align-items:center;justify-content:center;font-size:1.5rem;flex-shrink:0}
    .svc-icon-box.blue{background:var(--blue-light);border:1.5px solid var(--border-blue)}
    .svc-icon-box.orange{background:#fff7ed;border:1.5px solid #fed7aa}
    .svc-icon-box.green{background:#f0fdf4;border:1.5px solid #bbf7d0}
    .svc-icon-box.purple{background:#faf5ff;border:1.5px solid #e9d5ff}
    .svc-body h3{font-family:'Exo 2',sans-serif;font-size:1.05rem;font-weight:800;color:var(--heading);margin-bottom:4px;letter-spacing:0.2px}
    .svc-body p{font-size:0.86rem;color:var(--text);line-height:1.65}
    .svc-tag{padding:4px 12px;border-radius:100px;font-size:0.72rem;font-weight:700;background:var(--blue-light);color:var(--blue);white-space:nowrap}

    /* ===== WHY US / FEATURES ===== */
    .why-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:24px}
    .why-card{padding:32px 28px;border-radius:var(--r-xl);border:1.5px solid var(--border);background:#fff;transition:all .25s;position:relative;overflow:hidden}
    .why-card::before{content:'';position:absolute;top:0;left:0;right:0;height:3px;background:var(--grad)}
    .why-card:hover{transform:translateY(-5px);box-shadow:var(--shadow-lg);border-color:var(--border-blue)}
    .why-num{font-family:'Exo 2',sans-serif;font-size:3.5rem;font-weight:900;background:var(--grad);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;line-height:1;margin-bottom:12px;opacity:0.18;position:absolute;top:20px;right:24px}
    .why-icon{font-size:2rem;margin-bottom:16px}
    .why-card h3{font-family:'Exo 2',sans-serif;font-size:1.1rem;font-weight:800;color:var(--heading);margin-bottom:8px}
    .why-card p{font-size:0.85rem;color:var(--text);line-height:1.7}

    /* ===== ABOUT ===== */
    .about-wrap{display:grid;grid-template-columns:1fr 1fr;gap:72px;align-items:center}
    .about-img-col{position:relative}
    .about-img-main{border-radius:20px;overflow:hidden;box-shadow:var(--shadow-lg);border:1px solid var(--border)}
    .about-img-main img{width:100%;height:460px;object-fit:cover;display:block}
    .about-img-accent{position:absolute;bottom:-24px;right:-24px;width:180px;height:130px;border-radius:14px;overflow:hidden;border:4px solid #fff;box-shadow:var(--shadow-lg)}
    .about-img-accent img{width:100%;height:100%;object-fit:cover}
    .about-stat-chip{position:absolute;top:24px;left:-24px;background:#fff;border-radius:14px;padding:16px 20px;box-shadow:var(--shadow-lg);border:1px solid var(--border);text-align:center}
    .about-stat-chip .chip-num{font-family:'Exo 2',sans-serif;font-size:1.6rem;font-weight:900;color:var(--blue);line-height:1}
    .about-stat-chip .chip-lbl{font-size:0.7rem;color:var(--text-dim);font-weight:600;margin-top:3px}
    .about-text-col .section-title{margin-bottom:16px}
    .about-text-col p{font-size:0.94rem;color:var(--text);line-height:1.82;margin-bottom:14px}
    .about-feats{display:grid;grid-template-columns:1fr 1fr;gap:10px;margin:24px 0 32px}
    .about-feat{display:flex;align-items:center;gap:10px;font-size:0.84rem;font-weight:600;color:var(--heading)}
    .ck{background:var(--blue);color:#fff;width:20px;height:20px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:0.65rem;flex-shrink:0}
    .about-ctas{display:flex;gap:12px;flex-wrap:wrap}

    /* ===== REVIEWS ===== */
    .reviews-summary{display:flex;align-items:center;gap:20px;background:var(--blue-light);border:1.5px solid var(--border-blue);border-radius:16px;padding:20px 28px;margin-bottom:40px}
    .rev-big-num{font-family:'Exo 2',sans-serif;font-size:3.5rem;font-weight:900;color:var(--blue);line-height:1}
    .rev-stars{font-size:1.2rem;color:var(--gold);letter-spacing:2px;margin-bottom:4px}
    .rev-count{font-size:0.84rem;color:var(--text-dim);font-weight:500}
    .reviews-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:20px}
    .review-card{background:#fff;border:1.5px solid var(--border);border-radius:var(--r-lg);padding:24px;transition:all .22s;border-left:4px solid var(--blue)}
    .review-card:hover{box-shadow:var(--shadow);border-color:var(--border-blue)}
    .review-stars{color:var(--gold);font-size:0.9rem;margin-bottom:12px;letter-spacing:1px}
    .review-text{font-size:0.87rem;color:var(--text);line-height:1.75;margin-bottom:18px}
    .review-author{display:flex;align-items:center;gap:12px}
    .review-avatar{width:38px;height:38px;border-radius:50%;background:var(--grad);color:#fff;display:flex;align-items:center;justify-content:center;font-weight:800;font-size:1rem;flex-shrink:0}
    .review-name{font-weight:700;font-size:0.87rem;color:var(--heading)}
    .review-source{font-size:0.74rem;color:var(--text-dim)}

    /* ===== CTA BANNER ===== */
    .cta-banner{background:var(--grad);border-radius:var(--r-xl);padding:64px 48px;display:grid;grid-template-columns:1fr auto;gap:32px;align-items:center;position:relative;overflow:hidden;box-shadow:0 16px 56px rgba(26,110,232,0.3)}
    .cta-banner::after{content:'';position:absolute;right:-80px;top:-80px;width:320px;height:320px;border-radius:50%;background:rgba(255,255,255,0.06)}
    .cta-banner::before{content:'';position:absolute;right:120px;bottom:-60px;width:200px;height:200px;border-radius:50%;background:rgba(255,255,255,0.04)}
    .cta-text h2{font-family:'Exo 2',sans-serif;font-size:2.2rem;font-weight:900;color:#fff;margin-bottom:10px;position:relative;z-index:1;letter-spacing:0.3px}
    .cta-text p{color:rgba(255,255,255,0.75);font-size:0.98rem;position:relative;z-index:1}
    .cta-actions{display:flex;gap:12px;flex-shrink:0;position:relative;z-index:1}
    .cta-actions .btn{background:#fff;color:var(--blue);padding:13px 28px;font-size:0.88rem}
    .cta-actions .btn:hover{transform:translateY(-2px);box-shadow:0 8px 28px rgba(0,0,0,0.15)}
    .cta-actions .btn-ghost{background:rgba(255,255,255,0.12);color:#fff;border:1.5px solid rgba(255,255,255,0.3)}
    .cta-actions .btn-ghost:hover{background:rgba(255,255,255,0.2)}

    /* ===== CONTACT ===== */
    .contact-wrap{display:grid;grid-template-columns:1fr 1fr;gap:48px;align-items:start}
    .contact-info-col{}
    .contact-info-block{margin-bottom:32px}
    .contact-info-block h3{font-family:'Exo 2',sans-serif;font-size:1rem;font-weight:800;color:var(--heading);margin-bottom:16px;letter-spacing:0.2px}
    .contact-chips{display:flex;flex-direction:column;gap:10px}
    .contact-chip{display:flex;align-items:center;gap:12px;padding:14px 18px;border-radius:12px;background:#fff;border:1.5px solid var(--border);font-size:0.86rem;transition:all .2s}
    .contact-chip:hover{border-color:var(--border-blue);background:var(--blue-light)}
    .contact-chip .chip-icon{width:36px;height:36px;border-radius:10px;background:var(--blue-light);display:flex;align-items:center;justify-content:center;font-size:1rem;flex-shrink:0}
    .contact-chip .chip-body{}
    .contact-chip .chip-label{font-size:0.68rem;color:var(--text-dim);font-weight:600;text-transform:uppercase;letter-spacing:0.5px}
    .contact-chip a{color:var(--heading);font-weight:600;transition:color .2s}
    .contact-chip a:hover{color:var(--blue)}
    .area-row{display:flex;flex-wrap:wrap;gap:8px;margin-bottom:24px}
    .area-pill{padding:5px 14px;border-radius:100px;font-size:0.74rem;font-weight:700;background:var(--blue-light);color:var(--blue);border:1px solid var(--border-blue)}
    .svc-pill{padding:5px 14px;border-radius:100px;font-size:0.74rem;font-weight:600;background:var(--bg-soft);color:var(--text);border:1px solid var(--border)}
    .contact-fb-btn{display:flex;align-items:center;gap:10px;padding:14px 22px;background:#1877f2;color:#fff;border-radius:12px;font-weight:700;font-size:0.88rem;transition:all .2s;box-shadow:0 4px 16px rgba(24,119,242,0.3)}
    .contact-fb-btn:hover{background:#0e66d0;transform:translateY(-2px)}
    .contact-form-col{}
    .contact-card{background:#fff;border:1.5px solid var(--border);border-radius:var(--r-xl);padding:32px;box-shadow:var(--shadow-sm)}
    .contact-card h3{font-family:'Exo 2',sans-serif;font-size:1.2rem;font-weight:800;color:var(--heading);margin-bottom:20px;letter-spacing:0.3px}
    .form-group{margin-bottom:16px}
    .form-group label{display:block;font-size:0.72rem;font-weight:700;color:var(--text-dim);margin-bottom:6px;text-transform:uppercase;letter-spacing:0.4px}
    .form-group input,.form-group textarea{width:100%;padding:11px 14px;border-radius:8px;border:1.5px solid var(--border);font-size:0.88rem;background:#fff;color:var(--heading);outline:none;transition:all .2s;font-family:inherit}
    .form-group input:focus,.form-group textarea:focus{border-color:var(--blue);box-shadow:0 0 0 3px rgba(26,110,232,0.08)}
    .form-group textarea{resize:vertical;min-height:100px}
    .contact-map{margin-top:32px;border-radius:var(--r-xl);overflow:hidden;border:1.5px solid var(--border);box-shadow:var(--shadow-sm)}
    .contact-map iframe{display:block;width:100%;height:300px;border:none}

    /* ===== FAQ ===== */
    .faq-grid{display:grid;grid-template-columns:1fr 1fr;gap:0;background:var(--border);border-radius:var(--r-xl);overflow:hidden;border:1px solid var(--border)}
    .faq-item{border-bottom:1px solid var(--border);background:#fff}
    .faq-item:nth-child(odd){border-right:1px solid var(--border)}
    .faq-item:last-child,.faq-item:nth-last-child(2):nth-child(odd){border-bottom:none}
    .faq-q{width:100%;padding:22px 24px;display:flex;align-items:center;justify-content:space-between;font-size:0.92rem;font-weight:700;color:var(--heading);text-align:left;transition:color .2s;gap:12px}
    .faq-q:hover{color:var(--blue)}
    .faq-icon{font-size:1.2rem;color:var(--blue);font-weight:700;transition:transform .3s;flex-shrink:0}
    .faq-q.open .faq-icon{transform:rotate(45deg)}
    .faq-a{max-height:0;overflow:hidden;transition:max-height .3s ease}
    .faq-a.open{max-height:300px}
    .faq-a-inner{padding:0 24px 20px;font-size:0.88rem;color:var(--text);line-height:1.75}

    /* ===== FOOTER ===== */
    .footer{background:var(--heading);color:rgba(255,255,255,0.5);padding:64px 0 0}
    .footer-top{display:grid;grid-template-columns:2.2fr 1fr 1fr 1fr;gap:48px;padding-bottom:48px}
    .footer-brand .logo{font-family:'Exo 2',sans-serif;font-size:1.8rem;font-weight:900;color:#fff;letter-spacing:1px;margin-bottom:10px}
    .footer-brand p{font-size:0.83rem;line-height:1.75;margin-bottom:6px}
    .footer-col h4{font-size:0.68rem;text-transform:uppercase;letter-spacing:1.2px;font-weight:700;color:rgba(255,255,255,0.8);margin-bottom:16px}
    .footer-col ul li{margin-bottom:9px}
    .footer-col ul li a{font-size:0.83rem;color:rgba(255,255,255,0.38);transition:color .2s}
    .footer-col ul li a:hover{color:#fff}
    .footer-bottom{border-top:1px solid rgba(255,255,255,0.07);padding:20px 0;display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:12px}
    .footer-bottom p{font-size:0.77rem}
    .footer-legal{display:flex;gap:20px}
    .footer-legal a{font-size:0.77rem;color:rgba(255,255,255,0.35);transition:color .2s}
    .footer-legal a:hover{color:rgba(255,255,255,0.7)}
    .footer-social{display:flex;gap:10px;margin-top:16px}
    .footer-social a{width:34px;height:34px;border-radius:8px;background:rgba(255,255,255,0.07);color:rgba(255,255,255,0.4);display:flex;align-items:center;justify-content:center;transition:all .2s}
    .footer-social a:hover{background:var(--blue);color:#fff}

    /* ===== CART / WISHLIST ===== */
    .cart-overlay,.wish-overlay{position:fixed;inset:0;background:rgba(0,0,0,0.4);z-index:1100;display:none;backdrop-filter:blur(4px)}
    .cart-overlay.open,.wish-overlay.open{display:block}
    .cart-drawer,.wish-drawer{position:fixed;top:0;right:0;bottom:0;width:380px;max-width:92vw;z-index:1200;background:#fff;box-shadow:-4px 0 40px rgba(15,23,42,0.12);transform:translateX(100%);transition:transform .32s cubic-bezier(0.4,0,0.2,1);display:flex;flex-direction:column}
    .cart-drawer.open,.wish-drawer.open{transform:translateX(0)}
    .cart-header{display:flex;align-items:center;justify-content:space-between;padding:20px 24px;border-bottom:1px solid var(--border)}
    .cart-header h3{font-size:1rem;font-weight:800;color:var(--heading)}
    .cart-close{font-size:1.5rem;color:var(--text-dim);transition:color .2s}
    .cart-close:hover{color:var(--heading)}
    .cart-body{flex:1;overflow-y:auto;padding:16px 24px}
    .cart-empty{text-align:center;color:var(--text-dim);padding:40px 20px;font-size:0.88rem}
    .cart-item{display:flex;gap:14px;padding:14px 0;border-bottom:1px solid var(--bg-soft)}
    .cart-item-img{width:64px;height:64px;border-radius:8px;overflow:hidden;background:var(--bg-soft);flex-shrink:0;border:1px solid var(--border)}
    .cart-item-img img{width:100%;height:100%;object-fit:contain;padding:6px}
    .cart-item-info{flex:1}
    .cart-item-name{font-size:0.84rem;font-weight:600;color:var(--heading);line-height:1.4;margin-bottom:4px}
    .cart-item-price{font-size:0.88rem;font-weight:800;color:var(--blue)}
    .cart-item-actions{display:flex;align-items:center;gap:8px;margin-top:8px}
    .cart-qty-btn{width:26px;height:26px;border-radius:6px;border:1px solid var(--border);font-size:0.9rem;display:flex;align-items:center;justify-content:center;transition:all .15s;color:var(--heading)}
    .cart-qty-btn:hover{border-color:var(--blue);color:var(--blue);background:var(--blue-light)}
    .cart-qty{font-size:0.84rem;font-weight:700;color:var(--heading);min-width:20px;text-align:center}
    .cart-item-remove{font-size:0.7rem;color:#ef4444;font-weight:600;margin-left:auto;transition:opacity .2s}
    .cart-item-remove:hover{opacity:0.7}
    .cart-footer{padding:20px 24px;border-top:1px solid var(--border);background:var(--bg-soft)}
    .cart-total{display:flex;justify-content:space-between;align-items:center;margin-bottom:16px;font-weight:800}
    .cart-total span:first-child{font-size:0.84rem;color:var(--text-dim);text-transform:uppercase;letter-spacing:0.5px}
    .cart-total span:last-child{font-size:1.2rem;color:var(--heading)}
    .cart-checkout-btn{width:100%;padding:13px;border-radius:10px;background:var(--grad);color:#fff;font-size:0.88rem;font-weight:700;transition:all .2s;box-shadow:var(--shadow-blue)}
    .cart-checkout-btn:hover{transform:translateY(-2px);box-shadow:0 8px 28px rgba(26,110,232,0.4)}

    /* ===== COMPARE ===== */
    .compare-bar{position:fixed;bottom:24px;left:50%;transform:translateX(-50%);background:var(--heading);color:rgba(255,255,255,0.8);padding:14px 24px;border-radius:100px;z-index:900;display:none;align-items:center;gap:14px;font-size:0.84rem;box-shadow:var(--shadow-lg);border:1px solid rgba(255,255,255,0.08)}
    .compare-bar.show{display:flex}
    .compare-btn-go{padding:7px 18px;border-radius:100px;background:var(--grad);color:#fff;font-size:0.78rem;font-weight:700;transition:all .2s}
    .compare-btn-go:hover{transform:scale(1.03)}
    .compare-btn-clear{font-size:0.78rem;color:rgba(255,255,255,0.4);transition:color .2s}
    .compare-btn-clear:hover{color:#fff}
    .compare-modal{position:fixed;inset:0;background:rgba(0,0,0,0.5);z-index:2000;display:none;align-items:center;justify-content:center;backdrop-filter:blur(8px)}
    .compare-modal.open{display:flex}
    .compare-content{background:#fff;border-radius:var(--r-lg);padding:28px;max-width:92vw;max-height:90vh;overflow:auto;box-shadow:var(--shadow-lg);color:var(--heading)}
    .compare-table{width:100%;border-collapse:collapse;font-size:0.84rem}
    .compare-table th,.compare-table td{padding:12px 16px;border:1px solid var(--border);vertical-align:top}
    .compare-table th{background:var(--bg-soft);font-weight:700;color:var(--text-dim);font-size:0.72rem;text-transform:uppercase;letter-spacing:0.5px}

    /* ===== TOAST ===== */
    .toast-container{position:fixed;bottom:24px;right:24px;z-index:9999;display:flex;flex-direction:column;gap:10px;max-width:320px}
    .toast{position:relative;padding:14px 44px 14px 16px;border-radius:12px;display:flex;align-items:center;gap:12px;background:var(--heading);color:#fff;box-shadow:var(--shadow-lg);animation:toastIn .3s ease;font-size:0.85rem;font-weight:500;overflow:hidden}
    .toast.success{border-left:3px solid #22c55e}
    .toast.error{border-left:3px solid #ef4444}
    .toast.info{border-left:3px solid var(--blue)}
    @keyframes toastIn{from{opacity:0;transform:translateY(10px) scale(0.95)}to{opacity:1;transform:translateY(0) scale(1)}}
    .toast-icon{font-size:1.1rem;flex-shrink:0}
    .toast-msg{font-size:0.82rem;color:rgba(255,255,255,0.85)}
    .toast-close{position:absolute;top:50%;right:14px;transform:translateY(-50%);cursor:pointer;color:rgba(255,255,255,0.4);font-size:1rem;padding:4px;transition:color .2s}
    .toast-close:hover{color:#fff}
    .toast-progress{position:absolute;bottom:0;left:0;height:3px;background:rgba(255,255,255,0.2);animation:toastProgress 3s linear forwards}
    @keyframes toastProgress{0%{width:100%}100%{width:0}}

    /* ===== SCROLL TOP ===== */
    .scroll-top-btn{position:fixed;bottom:24px;right:24px;width:40px;height:40px;border-radius:50%;background:var(--grad);color:#fff;z-index:800;display:flex;align-items:center;justify-content:center;font-size:1.1rem;box-shadow:var(--shadow-blue);opacity:0;visibility:hidden;transform:translateY(10px);transition:all .3s}
    .scroll-top-btn.show{opacity:1;visibility:visible;transform:translateY(0)}
    .scroll-top-btn:hover{transform:translateY(-3px);box-shadow:0 10px 32px rgba(26,110,232,0.4)}

    /* ===== RESPONSIVE ===== */
    @media(max-width:1024px){
      .shop-layout{grid-template-columns:1fr}
      .shop-sidebar{position:fixed;left:-100%;top:0;bottom:0;width:300px;border-radius:0;z-index:200;overflow-y:auto;transition:left .3s}
      .shop-sidebar.mobile-open{left:0}
      .filter-overlay-close{display:flex}
      .mobile-filter-toggle{display:block}
      .hero-split{grid-template-columns:1fr}
      .hero-img-col{display:none}
      .why-grid{grid-template-columns:1fr 1fr}
      .cta-banner{grid-template-columns:1fr}
      .faq-grid{grid-template-columns:1fr}
    }
    @media(max-width:768px){
      .navbar .container{height:58px}
      .nav-links{display:none}
      .nav-search{display:none}
      .hamburger{display:flex}
      .hero{min-height:500px}
      .hero-inner h1{font-size:clamp(2.2rem,8vw,3rem)}
      .hero-slide .container{padding-top:56px;padding-bottom:56px}
      .section{padding:64px 0}
      .cat-tiles-section{padding:60px 0}
      .about-wrap{grid-template-columns:1fr;gap:40px}
      .about-img-col{order:-1}
      .about-img-accent,.about-stat-chip{display:none}
      .contact-wrap{grid-template-columns:1fr}
      .footer-top{grid-template-columns:1fr 1fr;gap:32px}
      .pd-grid{grid-template-columns:1fr}
      .pd-images{position:static}
      .stats-inner{grid-template-columns:repeat(3,1fr)}
      .stat-item:nth-child(n+4){display:none}
      .why-grid{grid-template-columns:1fr}
      .service-row{grid-template-columns:48px 1fr;gap:16px}
      .svc-tag{display:none}
    }
    @media(max-width:480px){
      .featured-grid{grid-template-columns:1fr 1fr;gap:14px}
      .shop-grid{grid-template-columns:1fr 1fr;gap:14px}
      .footer-top{grid-template-columns:1fr}
      .cta-text h2{font-size:1.8rem}
      .hero-buttons{flex-direction:column}
      .hero-buttons .btn{width:100%;justify-content:center}
      .section-header{margin-bottom:36px}
      .reviews-summary{flex-direction:column;text-align:center}
      .stats-inner{grid-template-columns:repeat(2,1fr)}
      .stat-item:last-child{display:none}
    }
"""

html = re.sub(r'<style>.*?</style>', f'<style>{NEW_CSS}  </style>', html, flags=re.DOTALL)

# ── 2. ADD ANNOUNCEMENT BAR before <nav ──────────────────────────────────────
old_nav = '  <!-- NAVBAR -->\n  <nav class="navbar">'
new_nav = '''  <!-- ANNOUNCEMENT BAR -->
  <div class="topbar-announce">
    &#128205; Now Open at Arbortowne Plaza II, Valenzuela &nbsp;&bull;&nbsp; Mon–Sat 10AM–7PM
    <span class="sep">|</span> 0976 002 1202 &nbsp;&bull;&nbsp;
    <a href="https://www.facebook.com/profile.php?id=61556399064773" target="_blank" rel="noopener">Facebook</a>
  </div>

  <!-- NAVBAR -->
  <nav class="navbar">'''
html = html.replace(old_nav, new_nav, 1)

# ── 3. HERO SECTION: hero-bg + split layout with floating badges ──────────────
old_hero_section = '''<section class="hero" id="hero">
    <div class="hero-bg-img"></div>
    <div class="hero-grid-overlay"></div>
    <div class="hero-slides" id="heroSlides">
      <div class="hero-slide hero-slide-1">
        <div class="container">
          <div class="hero-split">
            <div class="hero-inner">
              <div class="hero-badge"><span class="dot"></span> Valenzuela's #1 PC Hub</div>
              <h1>Hanap. Usap. <span class="grad">Build.</span></h1>
              <p class="hero-desc">Your one-stop shop for custom PC builds and quality computer parts in Valenzuela, Philippines. Expert team. Unbeatable prices.</p>
              <div class="hero-buttons">
                <a href="/shop" class="btn btn-primary" onclick="event.preventDefault();navigateTo('/shop')">Shop Now</a>
                <a href="/contact" class="btn btn-outline" onclick="event.preventDefault();navigateTo('/contact')">Contact Us</a>
              </div>
            </div>
            <div class="hero-img-wrap">
              <div class="hero-img-glow"></div>
              <img src="/hero-parts.jpg" alt="Custom PC Parts — H.U.B Valenzuela" loading="eager">
            </div>
          </div>
        </div>
      </div>'''

new_hero_section = '''<section class="hero" id="hero">
    <div class="hero-bg-img"></div>
    <div class="hero-slides" id="heroSlides">
      <div class="hero-slide hero-slide-1">
        <div class="container">
          <div class="hero-split">
            <div class="hero-inner">
              <div class="hero-eyebrow">
                <div class="hero-badge"><span class="dot"></span> Valenzuela's #1 PC Hub</div>
              </div>
              <h1>Hanap. Usap. <span class="grad">Build.</span></h1>
              <p class="hero-desc">Your one-stop shop for custom PC builds and quality computer parts in Valenzuela, Philippines.</p>
              <div class="hero-buttons">
                <a href="/shop" class="btn btn-primary" onclick="event.preventDefault();navigateTo('/shop')">
                  <svg width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><circle cx="9" cy="21" r="1"/><circle cx="20" cy="21" r="1"/><path d="M1 1h4l2.68 13.39a2 2 0 002 1.61h9.72a2 2 0 002-1.61L23 6H6"/></svg>
                  Shop Now
                </a>
                <a href="/contact" class="btn btn-outline" onclick="event.preventDefault();navigateTo('/contact')">Get a Free Quote</a>
              </div>
              <div class="hero-trust">
                <div class="hero-trust-item"><span class="hero-trust-icon">&#9733;</span> 5.0 — 413 Reviews</div>
                <div class="hero-trust-item"><span class="hero-trust-icon">&#10003;</span> Brand New Parts</div>
                <div class="hero-trust-item"><span class="hero-trust-icon">&#128222;</span> Free Consult</div>
              </div>
            </div>
            <div class="hero-img-col">
              <div class="hero-img-frame">
                <img src="/hero-parts.jpg" alt="Custom PC Parts — H.U.B Valenzuela" loading="eager">
              </div>
              <div class="hero-float-badge">
                <svg width="24" height="24" fill="#1a6ee8" viewBox="0 0 24 24"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/></svg>
                <div><div class="fb-num">24K+</div><div class="fb-lbl">Facebook<br>Followers</div></div>
              </div>
              <div class="hero-float-badge2">
                <div class="fb2-label">Reviews</div>
                <div class="fb2-val">100%<br>Recommend</div>
              </div>
            </div>
          </div>
        </div>
      </div>'''

html = html.replace(old_hero_section, new_hero_section, 1)

# ── 4. STATS BAR: replace inner markup ───────────────────────────────────────
old_stats = '''  <!-- STATS BAR -->
  <div class="stats-bar">
    <div class="container">
      <div class="stats-grid">
        <div class="stat-item"><div class="stat-num">100%</div><div class="stat-label">Recommend</div></div>
        <div class="stat-item"><div class="stat-num">413+</div><div class="stat-label">Reviews</div></div>
        <div class="stat-item"><div class="stat-num">24K+</div><div class="stat-label">Followers</div></div>
        <div class="stat-item"><div class="stat-num">50+</div><div class="stat-label">Products</div></div>
        <div class="stat-item"><div class="stat-num">Valenzuela</div><div class="stat-label">Philippines</div></div>
      </div>
    </div>
  </div>'''

new_stats = '''  <!-- STATS BAR -->
  <div class="stats-bar">
    <div class="container">
      <div class="stats-inner">
        <div class="stat-item"><div class="stat-num">100%</div><div class="stat-label">Recommend</div></div>
        <div class="stat-item"><div class="stat-num">413+</div><div class="stat-label">5-Star Reviews</div></div>
        <div class="stat-item"><div class="stat-num">24K+</div><div class="stat-label">FB Followers</div></div>
        <div class="stat-item"><div class="stat-num">50+</div><div class="stat-label">Products</div></div>
        <div class="stat-item"><div class="stat-num">#1</div><div class="stat-label">PC Hub Valenzuela</div></div>
      </div>
    </div>
  </div>'''
html = html.replace(old_stats, new_stats, 1)

# ── 5. SECTION HEADERS: update section-label/section-title structure ──────────
# Update categories section header
old_cat_header = '''      <div class="section-header fade-in">
        <p class="section-label">What Are You Looking For?</p>
        <h2 class="section-title">Explore Our Parts</h2>
        <p class="section-desc">From GPUs to complete PC builds. Pick a category and find your next upgrade.</p>
      </div>'''
new_cat_header = '''      <div class="section-header center fade-in">
        <div class="section-eyebrow center"><div class="section-line"></div><span class="section-tag">Shop by Category</span><div class="section-line"></div></div>
        <h2 class="section-title">Explore Our Parts</h2>
        <p class="section-desc">From GPUs to complete PC builds. Pick a category and find your next upgrade.</p>
      </div>'''
html = html.replace(old_cat_header, new_cat_header, 1)

# Update featured section header
old_feat_header = '''      <div class="section-header fade-in">
        <p class="section-label">Top Picks</p>
        <h2 class="section-title">Featured Products</h2>
        <p class="section-desc">Hand-picked deals and popular builds from H.U.B.</p>
      </div>'''
new_feat_header = '''      <div class="section-header center fade-in">
        <div class="section-eyebrow center"><div class="section-line"></div><span class="section-tag">Featured</span><div class="section-line"></div></div>
        <h2 class="section-title">Top Picks This Week</h2>
        <p class="section-desc">Hand-picked deals and popular builds from H.U.B.</p>
      </div>'''
html = html.replace(old_feat_header, new_feat_header, 1)

# ── 6. SERVICES: replace grid with horizontal list + add "Why Us" ─────────────
old_services_section = '''  <!-- SERVICES -->
  <section class="section section-alt" id="services">
    <div class="container">
      <div class="section-header fade-in">
        <p class="section-label">What We Offer</p>
        <h2 class="section-title">Our Services</h2>
        <p class="section-desc">Everything you need for your PC under one roof in Valenzuela.</p>
      </div>
      <div class="services-grid">
        <div class="service-card glass fade-in"><div class="svc-icon">&#128187;</div><h3>Custom PC Builds</h3><p>From budget school rigs to high-end gaming monsters. Our team builds PCs tailored to your needs and budget. Hanap, Usap, Build!</p></div>
        <div class="service-card glass fade-in"><div class="svc-icon">&#128295;</div><h3>PC Repair & Upgrades</h3><p>Slow performance? Hardware issues? We diagnose and fix problems fast. RAM, SSD, GPU upgrades — we handle it all.</p></div>
        <div class="service-card glass fade-in"><div class="svc-icon">&#9889;</div><h3>Parts Sales</h3><p>Shop the latest CPUs, GPUs, RAM, and more from top brands. Brand new and quality pre-owned at competitive prices.</p></div>
        <div class="service-card glass fade-in"><div class="svc-icon">&#128172;</div><h3>Free Consultation</h3><p>Not sure what to buy? Our team will help you pick the right parts for your budget and use case. Walk in or message us!</p></div>
      </div>
    </div>
  </section>'''

new_services_section = '''  <!-- SERVICES -->
  <section class="section section-alt" id="services">
    <div class="container">
      <div style="display:grid;grid-template-columns:1fr 1fr;gap:64px;align-items:start" class="fade-in">
        <div>
          <div class="section-eyebrow"><div class="section-line"></div><span class="section-tag">What We Offer</span></div>
          <h2 class="section-title">Services at H.U.B</h2>
          <p class="section-desc" style="margin-bottom:32px">From custom builds to quick repairs — everything your PC needs, right here in Valenzuela.</p>
          <div class="services-list">
            <div class="service-row">
              <div class="svc-icon-box blue">&#128187;</div>
              <div class="svc-body"><h3>Custom PC Builds</h3><p>From budget school rigs to high-end gaming monsters. We build PCs tailored to your needs and budget.</p></div>
              <span class="svc-tag">Most Popular</span>
            </div>
            <div class="service-row">
              <div class="svc-icon-box orange">&#128295;</div>
              <div class="svc-body"><h3>PC Repair & Upgrades</h3><p>Slow performance? Hardware issues? RAM, SSD, GPU upgrades — we diagnose and fix fast.</p></div>
              <span class="svc-tag">Same Day</span>
            </div>
            <div class="service-row">
              <div class="svc-icon-box green">&#9889;</div>
              <div class="svc-body"><h3>Parts Sales</h3><p>Latest CPUs, GPUs, RAM and more. Brand new and quality pre-owned at competitive prices.</p></div>
              <span class="svc-tag">50+ Products</span>
            </div>
            <div class="service-row">
              <div class="svc-icon-box purple">&#128172;</div>
              <div class="svc-body"><h3>Free Consultation</h3><p>Not sure what to buy? Our team will help you pick the right parts for your budget. Walk in or message us!</p></div>
              <span class="svc-tag">Free</span>
            </div>
          </div>
        </div>
        <div>
          <div class="section-eyebrow"><div class="section-line"></div><span class="section-tag">Why Choose H.U.B</span></div>
          <h2 class="section-title">Built for PC Lovers</h2>
          <div class="why-grid" style="margin-top:28px;grid-template-columns:1fr 1fr">
            <div class="why-card fade-in">
              <div class="why-num">01</div>
              <div class="why-icon">&#127881;</div>
              <h3>Expert Team</h3>
              <p>Our staff are PC builders themselves — we know what works and what's worth your money.</p>
            </div>
            <div class="why-card fade-in">
              <div class="why-num">02</div>
              <div class="why-icon">&#128176;</div>
              <h3>Honest Prices</h3>
              <p>No hidden markups. Competitive pricing on parts from trusted brands.</p>
            </div>
            <div class="why-card fade-in">
              <div class="why-num">03</div>
              <div class="why-icon">&#128222;</div>
              <h3>After-Sales Support</h3>
              <p>Got a question after purchase? Reach us on Facebook or call us anytime.</p>
            </div>
            <div class="why-card fade-in">
              <div class="why-num">04</div>
              <div class="why-icon">&#128666;</div>
              <h3>Delivery Available</h3>
              <p>Metro Manila delivery available. We ship via Lalamove or Grab — same day if needed.</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </section>'''

html = html.replace(old_services_section, new_services_section, 1)

# ── 7. ABOUT: new layout (image left, text right with accent image) ────────────
old_about = '''  <!-- ABOUT -->
  <section class="section" id="about">
    <div class="container">
      <div class="about-grid fade-in">
        <div>
          <p class="section-label">Who We Are</p>
          <h2 class="section-title">About H.U.B</h2>
          <div class="about-text">
            <p>H.U.B (Hanap.Usap.Build) is your local PC builder and computer parts store in Valenzuela, Philippines. Our name says it all — you Hanap (find) the parts you need, Usap (talk) to our expert team, and we Build your dream PC together.</p>
            <p>Whether you're a student building your first PC, a gamer chasing higher frames, or a professional needing a workstation, H.U.B has the parts, expertise, and deals right here in Valenzuela.</p>
          </div>
          <div class="about-features">
            <div class="about-feat"><span class="ck">&#10003;</span>Custom PC builds</div>
            <div class="about-feat"><span class="ck">&#10003;</span>Quality PC parts</div>
            <div class="about-feat"><span class="ck">&#10003;</span>Expert consultation</div>
            <div class="about-feat"><span class="ck">&#10003;</span>Trusted by thousands</div>
            <div class="about-feat"><span class="ck">&#10003;</span>Delivery available</div>
            <div class="about-feat"><span class="ck">&#10003;</span>Valenzuela-based</div>
          </div>
        </div>
        <div class="about-right">
          <div class="about-img-wrap">
            <img src="/about-circuit.jpg" alt="H.U.B — Custom PC Builds" loading="lazy">
          </div>
          <div class="about-stats">
            <div class="about-stat glass"><div class="num">100%</div><div class="lbl">Recommend Rate</div></div>
            <div class="about-stat glass"><div class="num">413+</div><div class="lbl">5-Star Reviews</div></div>
            <div class="about-stat glass"><div class="num">24K+</div><div class="lbl">FB Followers</div></div>
            <div class="about-stat glass"><div class="num">#1</div><div class="lbl">PC Hub Valenzuela</div></div>
          </div>
        </div>
      </div>
    </div>
  </section>'''

new_about = '''  <!-- ABOUT -->
  <section class="section" id="about">
    <div class="container">
      <div class="about-wrap fade-in">
        <div class="about-img-col">
          <div class="about-img-main">
            <img src="/hero-parts.jpg" alt="H.U.B PC Parts — Valenzuela" loading="lazy">
          </div>
          <div class="about-img-accent">
            <img src="/about-circuit.jpg" alt="Circuit Board" loading="lazy">
          </div>
          <div class="about-stat-chip">
            <div class="chip-num">24K+</div>
            <div class="chip-lbl">Facebook Followers</div>
          </div>
        </div>
        <div class="about-text-col">
          <div class="section-eyebrow"><div class="section-line"></div><span class="section-tag">Who We Are</span></div>
          <h2 class="section-title">Valenzuela's Go-To <span class="grad">PC Hub</span></h2>
          <p>H.U.B (Hanap.Usap.Build) is your local PC builder and computer parts store right here in Valenzuela, Philippines. Our name says it all — <strong>Hanap</strong> the parts, <strong>Usap</strong> with our expert team, and we <strong>Build</strong> your dream PC together.</p>
          <p>Whether you're a student on a budget, a gamer chasing higher frames, or a professional needing a workstation — H.U.B has the parts, expertise, and deals to get you there.</p>
          <div class="about-feats">
            <div class="about-feat"><span class="ck">&#10003;</span>Custom PC builds</div>
            <div class="about-feat"><span class="ck">&#10003;</span>Quality PC parts</div>
            <div class="about-feat"><span class="ck">&#10003;</span>Free consultation</div>
            <div class="about-feat"><span class="ck">&#10003;</span>Trusted by thousands</div>
            <div class="about-feat"><span class="ck">&#10003;</span>Delivery available</div>
            <div class="about-feat"><span class="ck">&#10003;</span>Valenzuela-based</div>
          </div>
          <div class="about-ctas">
            <a href="/shop" class="btn btn-primary" onclick="event.preventDefault();navigateTo('/shop')">Browse Products</a>
            <a href="https://www.facebook.com/profile.php?id=61556399064773" target="_blank" rel="noopener" class="btn btn-outline">Message Us</a>
          </div>
        </div>
      </div>
    </div>
  </section>'''

html = html.replace(old_about, new_about, 1)

# ── 8. REVIEWS: add summary bar ───────────────────────────────────────────────
old_reviews_header = '''      <div class="section-header fade-in">
        <p class="section-label">Facebook Reviews</p>
        <h2 class="section-title">What Our Customers Say</h2>
        <div class="reviews-big"><span class="num">5.0</span><div><div class="stars">&#9733;&#9733;&#9733;&#9733;&#9733;</div><p style="font-size:0.78rem;color:var(--text-dim)">Based on 413+ reviews &bull; 100% Recommend</p></div></div>
      </div>'''
new_reviews_header = '''      <div class="section-header center fade-in">
        <div class="section-eyebrow center"><div class="section-line"></div><span class="section-tag">Facebook Reviews</span><div class="section-line"></div></div>
        <h2 class="section-title">What Our Customers Say</h2>
      </div>
      <div class="reviews-summary fade-in">
        <div class="rev-big-num">5.0</div>
        <div>
          <div class="rev-stars">&#9733;&#9733;&#9733;&#9733;&#9733;</div>
          <div style="font-weight:700;font-size:0.95rem;color:var(--heading);margin-bottom:4px">Rated 5.0 out of 5</div>
          <div class="rev-count">Based on 413+ Facebook reviews &bull; 100% Recommend Rate</div>
        </div>
        <a href="https://www.facebook.com/profile.php?id=61556399064773" target="_blank" rel="noopener" class="btn btn-primary" style="margin-left:auto">See All Reviews</a>
      </div>'''
html = html.replace(old_reviews_header, new_reviews_header, 1)

# ── 9. CTA BANNER: two-column layout ─────────────────────────────────────────
old_cta = '''  <!-- CTA BANNER -->
  <section class="section">
    <div class="container">
      <div class="cta-banner fade-in">
        <h2>Ready to Build Your Dream Setup?</h2>
        <p>Visit H.U.B at Arbortowne Plaza or message us on Facebook. We're here to help!</p>
        <a href="/contact" class="btn" onclick="event.preventDefault();navigateTo('/contact')">Get In Touch</a>
      </div>
    </div>
  </section>'''
new_cta = '''  <!-- CTA BANNER -->
  <section class="section">
    <div class="container">
      <div class="cta-banner fade-in">
        <div class="cta-text">
          <h2>Ready to Build Your Dream Setup?</h2>
          <p>Visit us at Arbortowne Plaza or message on Facebook. We're ready to help!</p>
        </div>
        <div class="cta-actions">
          <a href="/shop" class="btn" onclick="event.preventDefault();navigateTo('/shop')">Shop Now</a>
          <a href="https://www.facebook.com/profile.php?id=61556399064773" target="_blank" rel="noopener" class="btn btn-ghost">Message Us</a>
        </div>
      </div>
    </div>
  </section>'''
html = html.replace(old_cta, new_cta, 1)

# ── 10. CONTACT: new layout ──────────────────────────────────────────────────
old_contact = '''  <!-- CONTACT & LOCATION -->
  <section class="section section-alt" id="contact">
    <div class="container">
      <div class="section-header fade-in">
        <p class="section-label">Get In Touch</p>
        <h2 class="section-title">Store Location & Contact</h2>
        <p class="section-desc">Visit us in Valenzuela or reach out directly.</p>
      </div>
      <div class="findus-grid fade-in">
        <div>
          <div class="loc-card glass">
            <h3>&#128205; H.U.B Store — Valenzuela</h3>
            <p class="addr">3/F Unit 306 Arbortowne Plaza II, Karuhatan Road, Gen. T. de Leon, Valenzuela, Philippines 1442</p>
            <a href="https://maps.google.com/?q=Arbortowne+Plaza+II+Karuhatan+Road+Valenzuela" target="_blank" rel="noopener" class="loc-link">&#10132; Open in Google Maps</a>
          </div>
          <div class="loc-tags">
            <div class="loc-tags-label">Areas Served</div>
            <div class="area-tags">
              <span class="area-tag">Valenzuela</span><span class="area-tag">Bulacan</span><span class="area-tag">Caloocan</span><span class="area-tag">Metro Manila</span>
            </div>
            <div class="loc-tags-label" style="margin-top:14px">Available Services</div>
            <div class="svc-tags">
              <span class="svc-tag">Delivery</span><span class="svc-tag">In-Store</span><span class="svc-tag">Reservations</span><span class="svc-tag">Pickup</span>
            </div>
          </div>
          <div class="contact-block" style="margin-top:24px">
            <div class="contact-block-title">Contact Us</div>
            <div class="contact-methods">
              <div class="contact-chip"><span class="icon">&#128222;</span><a href="tel:09760021202">0976 002 1202</a></div>
              <div class="contact-chip contact-chip-email"><span class="icon">&#9993;</span><a href="mailto:hanap.usap.build@gmail.com">hanap.usap.build@gmail.com</a></div>
            </div>
            <div class="contact-actions">
              <a href="https://www.facebook.com/profile.php?id=61556399064773" target="_blank" rel="noopener" class="btn btn-primary" style="padding:11px 28px;font-size:0.82rem">
                <svg width="16" height="16" fill="currentColor" viewBox="0 0 24 24"><path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z"/></svg>
                Message on Facebook
              </a>
            </div>
          </div>
        </div>
        <div>
          <form class="contact-form glass" onsubmit="handleSubmit(event)">
            <h3 style="font-family:\'Exo 2\',sans-serif;font-size:1.2rem;font-weight:700;color:var(--heading);margin-bottom:16px;letter-spacing:0.5px">Send Us a Message</h3>
            <div class="form-group">
              <label>Your Name</label>
              <input type="text" name="name" placeholder="Juan dela Cruz" required>
            </div>
            <div class="form-group">
              <label>Email Address</label>
              <input type="email" name="email" placeholder="juan@example.com" required>
            </div>
            <div class="form-group">
              <label>Phone (Optional)</label>
              <input type="text" name="phone" placeholder="09XX XXX XXXX">
            </div>
            <div class="form-group">
              <label>Message</label>
              <textarea name="message" rows="4" placeholder="Tell us what you need..." required></textarea>
            </div>
            <button type="submit" class="btn btn-primary" style="width:100%;justify-content:center">Send Message</button>
          </form>
        </div>
      </div>
      <div class="findus-map fade-in">
        <iframe src="https://maps.google.com/maps?q=Arbortowne+Plaza+II,+Karuhatan+Road,+Valenzuela+City,+Metro+Manila,+Philippines&output=embed" allowfullscreen="" loading="lazy"></iframe>
      </div>
    </div>
  </section>'''

new_contact = '''  <!-- CONTACT & LOCATION -->
  <section class="section section-alt" id="contact">
    <div class="container">
      <div class="section-header center fade-in">
        <div class="section-eyebrow center"><div class="section-line"></div><span class="section-tag">Get In Touch</span><div class="section-line"></div></div>
        <h2 class="section-title">Store Location & Contact</h2>
        <p class="section-desc">Visit us in Valenzuela, give us a call, or message us on Facebook.</p>
      </div>
      <div class="contact-wrap fade-in">
        <div class="contact-info-col">
          <div class="contact-info-block">
            <h3>&#128205; Find Us</h3>
            <div class="contact-chips">
              <div class="contact-chip">
                <div class="chip-icon">&#128205;</div>
                <div class="chip-body">
                  <div class="chip-label">Address</div>
                  <a href="https://maps.google.com/?q=Arbortowne+Plaza+II+Karuhatan+Road+Valenzuela" target="_blank" rel="noopener">3/F Unit 306 Arbortowne Plaza II, Karuhatan Rd, Valenzuela 1442</a>
                </div>
              </div>
              <div class="contact-chip">
                <div class="chip-icon">&#128222;</div>
                <div class="chip-body">
                  <div class="chip-label">Phone / Viber</div>
                  <a href="tel:09760021202">0976 002 1202</a>
                </div>
              </div>
              <div class="contact-chip">
                <div class="chip-icon">&#9993;</div>
                <div class="chip-body">
                  <div class="chip-label">Email</div>
                  <a href="mailto:hanap.usap.build@gmail.com">hanap.usap.build@gmail.com</a>
                </div>
              </div>
              <div class="contact-chip">
                <div class="chip-icon">&#128336;</div>
                <div class="chip-body">
                  <div class="chip-label">Store Hours</div>
                  <span>Mon – Sat &nbsp; 10:00 AM – 7:00 PM</span>
                </div>
              </div>
            </div>
          </div>
          <div class="contact-info-block">
            <h3>Areas Served</h3>
            <div class="area-row">
              <span class="area-pill">Valenzuela</span><span class="area-pill">Bulacan</span><span class="area-pill">Caloocan</span><span class="area-pill">Metro Manila</span>
            </div>
            <h3>Fulfillment Options</h3>
            <div class="area-row">
              <span class="svc-pill">Delivery</span><span class="svc-pill">In-Store Pickup</span><span class="svc-pill">Reservations</span><span class="svc-pill">Lalamove</span>
            </div>
          </div>
          <a href="https://www.facebook.com/profile.php?id=61556399064773" target="_blank" rel="noopener" class="contact-fb-btn">
            <svg width="20" height="20" fill="#fff" viewBox="0 0 24 24"><path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z"/></svg>
            Message Us on Facebook
          </a>
          <div class="contact-map" style="margin-top:24px">
            <iframe src="https://maps.google.com/maps?q=Arbortowne+Plaza+II,+Karuhatan+Road,+Valenzuela+City,+Metro+Manila,+Philippines&output=embed" allowfullscreen="" loading="lazy"></iframe>
          </div>
        </div>
        <div class="contact-form-col">
          <div class="contact-card">
            <h3>Send Us a Message</h3>
            <form onsubmit="handleSubmit(event)">
              <div class="form-group">
                <label>Your Name</label>
                <input type="text" name="name" placeholder="Juan dela Cruz" required>
              </div>
              <div class="form-group">
                <label>Email Address</label>
                <input type="email" name="email" placeholder="juan@example.com" required>
              </div>
              <div class="form-group">
                <label>Phone (Optional)</label>
                <input type="text" name="phone" placeholder="09XX XXX XXXX">
              </div>
              <div class="form-group">
                <label>Message</label>
                <textarea name="message" rows="5" placeholder="Tell us what you need — budget, specs, or a question about parts..." required></textarea>
              </div>
              <button type="submit" class="btn btn-primary" style="width:100%;justify-content:center;padding:13px">
                <svg width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><line x1="22" y1="2" x2="11" y2="13"/><polygon points="22 2 15 22 11 13 2 9 22 2"/></svg>
                Send Message
              </button>
            </form>
          </div>
        </div>
      </div>
    </div>
  </section>'''

html = html.replace(old_contact, new_contact, 1)

# ── 11. FAQ: 2-col grid layout ────────────────────────────────────────────────
old_faq = '''  <!-- FAQ -->
  <section class="section" id="faq">
    <div class="container">
      <div class="section-header fade-in">
        <p class="section-label">FAQ</p>
        <h2 class="section-title">Frequently Asked Questions</h2>
      </div>
      <div class="faq-list">'''
new_faq = '''  <!-- FAQ -->
  <section class="section section-alt" id="faq">
    <div class="container">
      <div class="section-header center fade-in">
        <div class="section-eyebrow center"><div class="section-line"></div><span class="section-tag">FAQ</span><div class="section-line"></div></div>
        <h2 class="section-title">Frequently Asked Questions</h2>
        <p class="section-desc">Got questions? We've got answers. Reach out on Facebook for anything else.</p>
      </div>
      <div class="faq-grid fade-in">'''
html = html.replace(old_faq, new_faq, 1)

old_faq_close = '      </div>\n    </div>\n  </section>\n\n  <!-- FOOTER -->'
new_faq_close = '      </div>\n    </div>\n  </section>\n\n  <!-- FOOTER -->'
# The faq-list close tag becomes faq-grid close (same </div> structure, just rename)

# ── 12. FOOTER: updated structure ─────────────────────────────────────────────
old_footer_grid = '''    <div class="footer-grid">
        <div class="footer-brand">
          <div class="logo">H.U.B</div>
          <p>Hanap.Usap.Build — Your local PC builder and computer parts store in Valenzuela, Philippines.</p>
          <p style="margin-top:8px;font-size:0.78rem;color:rgba(255,255,255,0.35)">&#128205; 3/F Unit 306 Arbortowne Plaza II, Valenzuela</p>
        </div>'''
new_footer_grid = '''    <div class="footer-top">
        <div class="footer-brand">
          <div class="logo">H.U.B</div>
          <p>Hanap.Usap.Build — Your local PC builder and computer parts store in Valenzuela, Philippines.</p>
          <p style="margin-top:6px;font-size:0.78rem;color:rgba(255,255,255,0.3)">&#128205; 3/F Unit 306 Arbortowne Plaza II, Valenzuela</p>
          <div class="footer-social">
            <a href="https://www.facebook.com/profile.php?id=61556399064773" target="_blank" rel="noopener" title="Facebook"><svg width="14" height="14" fill="currentColor" viewBox="0 0 24 24"><path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z"/></svg></a>
          </div>
        </div>'''
html = html.replace(old_footer_grid, new_footer_grid, 1)

html = html.replace('      </div>\n      <div class="footer-bottom">', '      </div>\n      <div class="footer-bottom">', 1)

old_footer_bottom = '''      <div class="footer-bottom">
        <p>&copy; 2026 Hanap.Usap.Build (H.U.B). All rights reserved.</p>
        <div class="footer-social">
          <a href="https://www.facebook.com/profile.php?id=61556399064773" target="_blank" rel="noopener" title="Facebook"><svg width="14" height="14" fill="currentColor" viewBox="0 0 24 24"><path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z"/></svg></a>
        </div>
      </div>'''
new_footer_bottom = '''      <div class="footer-bottom">
        <p>&copy; 2026 Hanap.Usap.Build (H.U.B). All rights reserved.</p>
        <div class="footer-legal">
          <a href="/privacy">Privacy Policy</a>
          <a href="/data-deletion">Data Deletion</a>
        </div>
      </div>'''
html = html.replace(old_footer_bottom, new_footer_bottom, 1)

with open('public/index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Done! White redesign applied.")
