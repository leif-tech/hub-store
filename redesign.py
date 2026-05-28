import re

with open('public/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# ── 1. REPLACE CSS ──────────────────────────────────────────────────────────────
NEW_CSS = """
    *,*::before,*::after{margin:0;padding:0;box-sizing:border-box}
    html{scroll-behavior:smooth;scroll-padding-top:68px}
    body{font-family:'Plus Jakarta Sans',sans-serif;background:var(--bg);color:var(--text);line-height:1.65;overflow-x:hidden}
    a{color:inherit;text-decoration:none}
    img{max-width:100%;display:block}
    ul{list-style:none}
    button{cursor:pointer;border:none;font-family:inherit;background:none}
    .container{max-width:1240px;margin:0 auto;padding:0 24px}

    :root{
      --blue:#1a6ee8;
      --blue-dark:#1255c0;
      --cyan:#38bdf8;
      --gold:#f5c518;
      --bg:#07091c;
      --bg-alt:#0d1120;
      --card:#0d1120;
      --card-alt:#0a0e1a;
      --card-border:rgba(255,255,255,0.07);
      --border:rgba(255,255,255,0.05);
      --border-blue:rgba(26,110,232,0.25);
      --text:#94a3b8;
      --text-dim:#64748b;
      --heading:#f1f5f9;
      --grad:linear-gradient(135deg,#1255c0,#1a6ee8,#38bdf8);
      --shadow-sm:0 2px 8px rgba(0,0,0,0.3);
      --shadow:0 4px 24px rgba(0,0,0,0.4);
      --shadow-lg:0 12px 48px rgba(0,0,0,0.5);
      --shadow-blue:0 6px 24px rgba(26,110,232,0.35);
      --glow-blue:0 0 32px rgba(26,110,232,0.25);
      --r:10px;
      --r-lg:16px;
    }

    /* ===== BUTTONS ===== */
    .btn{display:inline-flex;align-items:center;gap:8px;padding:12px 28px;border-radius:8px;font-weight:700;font-size:0.875rem;letter-spacing:0.3px;transition:all .25s;cursor:pointer;border:none}
    .btn-primary{background:var(--grad);color:#fff;box-shadow:var(--shadow-blue)}
    .btn-primary:hover{transform:translateY(-2px);box-shadow:0 10px 36px rgba(26,110,232,0.5)}
    .btn-outline{background:rgba(255,255,255,0.05);color:rgba(255,255,255,0.85);border:1.5px solid rgba(255,255,255,0.2);backdrop-filter:blur(10px)}
    .btn-outline:hover{border-color:var(--blue);color:#fff;background:rgba(26,110,232,0.15);box-shadow:0 0 20px rgba(26,110,232,0.2)}

    /* ===== SECTIONS ===== */
    .section{padding:96px 0;background:var(--bg)}
    .section-alt{background:var(--bg-alt)}
    .section-header{text-align:center;margin-bottom:56px}
    .section-label{display:inline-block;font-size:0.72rem;font-weight:700;letter-spacing:2px;text-transform:uppercase;color:var(--cyan);margin-bottom:14px;background:rgba(56,189,248,0.1);border:1px solid rgba(56,189,248,0.2);padding:5px 14px;border-radius:100px}
    .section-title{font-family:'Exo 2',sans-serif;font-size:clamp(1.8rem,3.5vw,2.6rem);font-weight:800;color:var(--heading);letter-spacing:0.3px;margin-bottom:14px;line-height:1.15}
    .section-desc{font-size:0.97rem;color:var(--text-dim);max-width:560px;margin:0 auto;line-height:1.7}
    .grad{background:var(--grad);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text}
    .glass{background:rgba(13,17,32,0.7);border:1px solid var(--card-border);backdrop-filter:blur(12px);box-shadow:var(--shadow)}
    .fade-in{opacity:0;transform:translateY(20px);transition:opacity .55s ease,transform .55s ease}
    .fade-in.visible{opacity:1;transform:translateY(0)}

    /* ===== NAVBAR ===== */
    .navbar{position:sticky;top:0;z-index:1000;background:rgba(7,9,28,0.92);backdrop-filter:blur(24px);border-bottom:1px solid var(--border-blue);box-shadow:0 4px 24px rgba(0,0,0,0.4)}
    .navbar .container{display:flex;align-items:center;justify-content:space-between;height:64px;gap:12px}
    .nav-logo img{height:38px;width:auto}
    .nav-links{display:flex;align-items:center;margin-left:auto;margin-right:auto}
    .nav-links a{padding:20px 15px;font-size:0.79rem;font-weight:600;color:var(--text);text-transform:uppercase;letter-spacing:0.6px;transition:color .2s;position:relative}
    .nav-links a:hover,.nav-links a.active{color:#fff}
    .nav-links a::after{content:'';position:absolute;bottom:0;left:15px;right:15px;height:2px;background:var(--grad);transform:scaleX(0);transition:transform .3s;border-radius:2px}
    .nav-links a:hover::after,.nav-links a.active::after{transform:scaleX(1)}
    .nav-links .shop-link{color:var(--cyan);font-weight:700}
    .nav-links .nav-cta{margin-left:8px;padding:8px 18px;border-radius:8px;background:var(--grad);color:#fff !important;box-shadow:0 2px 10px rgba(26,110,232,0.3);font-size:0.79rem}
    .nav-links .nav-cta::after{display:none}
    .nav-links .nav-cta:hover{box-shadow:0 4px 20px rgba(26,110,232,0.5);transform:translateY(-1px)}
    .nav-search{position:relative;flex:1;max-width:260px}
    .nav-search input{width:100%;padding:9px 36px 9px 14px;background:rgba(255,255,255,0.05);border:1.5px solid var(--card-border);border-radius:8px;font-size:0.82rem;color:var(--heading);transition:all .2s;outline:none}
    .nav-search input::placeholder{color:var(--text-dim)}
    .nav-search input:focus{border-color:var(--blue);background:rgba(26,110,232,0.08);box-shadow:0 0 0 3px rgba(26,110,232,0.12)}
    .nav-search-icon{position:absolute;right:12px;top:50%;transform:translateY(-50%);color:var(--text-dim);pointer-events:none}
    .nav-suggest{position:absolute;top:calc(100% + 8px);left:0;right:0;background:#0d1120;border:1px solid var(--card-border);border-radius:12px;box-shadow:var(--shadow-lg);overflow:hidden;z-index:100}
    .nav-suggest-item{padding:11px 16px;font-size:0.84rem;cursor:pointer;transition:background .15s;color:var(--heading);display:flex;align-items:center;gap:8px}
    .nav-suggest-item:hover{background:rgba(26,110,232,0.1)}
    .nav-icons{display:flex;align-items:center;gap:4px}
    .nav-icon-btn{position:relative;width:40px;height:40px;border-radius:10px;display:flex;align-items:center;justify-content:center;color:var(--text);background:rgba(255,255,255,0.05);transition:all .2s;border:1px solid var(--card-border)}
    .nav-icon-btn svg{width:18px;height:18px}
    .nav-icon-btn:hover{background:rgba(26,110,232,0.15);color:var(--cyan);border-color:var(--border-blue)}
    .nav-badge{position:absolute;top:4px;right:4px;background:var(--blue);color:#fff;border-radius:50%;width:16px;height:16px;font-size:0.6rem;font-weight:700;display:none;align-items:center;justify-content:center;border:2px solid var(--bg)}
    .nav-badge.show{display:flex}
    .nav-user-area{display:flex;align-items:center;gap:8px;position:relative}
    .nav-login-btn{display:flex;align-items:center;gap:7px;padding:8px 16px;border-radius:8px;border:1.5px solid var(--card-border);color:var(--text);font-size:0.82rem;font-weight:600;transition:all .2s;background:rgba(255,255,255,0.04)}
    .nav-login-btn:hover{border-color:var(--blue);color:var(--cyan);background:rgba(26,110,232,0.1)}
    .nav-user-avatar{width:36px;height:36px;border-radius:50%;object-fit:cover;cursor:pointer;border:2px solid var(--blue);box-shadow:0 0 12px rgba(26,110,232,0.4)}
    .nav-user-name{font-size:0.82rem;font-weight:600;color:var(--heading);cursor:pointer}
    .nav-user-dropdown{position:absolute;top:calc(100% + 12px);right:0;background:#0d1120;border:1px solid var(--border-blue);border-radius:14px;box-shadow:var(--shadow-lg);min-width:220px;overflow:hidden;z-index:200;display:none}
    .nav-user-dropdown.open{display:block}
    .ud-header{padding:16px 18px 12px;border-bottom:1px solid var(--card-border)}
    .ud-name{font-weight:700;font-size:0.92rem;color:var(--heading)}
    .ud-email{font-size:0.78rem;color:var(--text-dim);margin-top:2px}
    .ud-points{font-size:0.78rem;color:var(--cyan);font-weight:600;margin-top:6px}
    .ud-signout{display:block;width:100%;padding:12px 18px;text-align:left;font-size:0.84rem;font-weight:600;color:#ef4444;transition:background .15s}
    .ud-signout:hover{background:rgba(239,68,68,0.08)}
    .hamburger{display:none;flex-direction:column;gap:5px;padding:8px;cursor:pointer}
    .hamburger span{display:block;width:22px;height:2px;background:var(--heading);border-radius:2px;transition:all .3s}

    /* ===== MOBILE MENU ===== */
    .mobile-menu{display:none;flex-direction:column;background:var(--bg-alt);border-bottom:1px solid var(--border-blue);box-shadow:0 8px 32px rgba(0,0,0,0.4);padding:8px 0;position:sticky;top:64px;z-index:999}
    .mobile-menu.open{display:flex}
    .mobile-menu a{padding:13px 24px;font-size:0.88rem;font-weight:600;color:var(--text);border-bottom:1px solid rgba(255,255,255,0.04);transition:color .2s}
    .mobile-menu a:hover{color:var(--cyan);background:rgba(26,110,232,0.08)}

    /* ===== AUTH OVERLAY ===== */
    .auth-overlay{position:fixed;inset:0;background:rgba(0,0,0,0.65);backdrop-filter:blur(10px);z-index:2000;display:none;align-items:center;justify-content:center}
    .auth-overlay.open{display:flex}
    .auth-modal{background:#0d1120;border:1px solid var(--border-blue);border-radius:20px;padding:40px 36px;max-width:400px;width:90%;box-shadow:0 20px 60px rgba(0,0,0,0.6);position:relative;text-align:center}
    .auth-modal-close{position:absolute;top:16px;right:20px;font-size:1.5rem;color:var(--text-dim);transition:color .2s}
    .auth-modal-close:hover{color:var(--heading)}
    .auth-modal h2{font-family:'Exo 2',sans-serif;font-size:1.5rem;font-weight:800;color:var(--heading);margin-bottom:8px}
    .auth-sub{font-size:0.84rem;color:var(--text-dim);margin-bottom:28px}
    .auth-btn{display:flex;align-items:center;justify-content:center;gap:10px;width:100%;padding:13px 20px;border-radius:10px;font-size:0.88rem;font-weight:600;transition:all .2s;border:1.5px solid var(--card-border);cursor:pointer;margin-bottom:12px;color:var(--heading);background:rgba(255,255,255,0.04)}
    .auth-btn:hover{border-color:var(--blue);background:rgba(26,110,232,0.1)}
    .auth-btn-google:hover{border-color:#4285f4;background:rgba(66,133,244,0.1)}
    .auth-btn-facebook{border-color:#1877f2;background:#1877f2;color:#fff}
    .auth-btn-facebook:hover{background:#0e66d0;border-color:#0e66d0}
    .auth-divider{display:flex;align-items:center;gap:12px;margin:4px 0 12px;font-size:0.78rem;color:var(--text-dim)}
    .auth-divider::before,.auth-divider::after{content:'';flex:1;height:1px;background:var(--card-border)}

    /* ===== HERO ===== */
    .hero{position:relative;min-height:640px;background:var(--bg);overflow:hidden;display:flex;flex-direction:column}
    .hero-bg-img{position:absolute;inset:0;background-image:url('/hero-bg.jpg');background-size:cover;background-position:center;opacity:0.12;pointer-events:none}
    .hero-grid-overlay{position:absolute;inset:0;background-image:linear-gradient(rgba(26,110,232,0.08) 1px,transparent 1px),linear-gradient(90deg,rgba(26,110,232,0.08) 1px,transparent 1px);background-size:60px 60px;pointer-events:none;opacity:0.6}
    .hero::before{content:'';position:absolute;inset:0;background:radial-gradient(ellipse 70% 80% at 75% 30%,rgba(26,110,232,0.18) 0%,transparent 65%),radial-gradient(ellipse 40% 60% at 10% 80%,rgba(56,189,248,0.07) 0%,transparent 60%);pointer-events:none;z-index:1}
    .hero-slides{flex:1;position:relative;z-index:2}
    .hero-slide{position:absolute;inset:0;opacity:0;display:flex;align-items:center;transition:opacity .6s ease}
    .hero-slide.active{opacity:1;position:relative}
    .hero-slide .container{padding-top:80px;padding-bottom:80px}
    .hero-split{display:grid;grid-template-columns:1fr 1fr;gap:48px;align-items:center}
    .hero-inner{max-width:680px}
    .hero-badge{display:inline-flex;align-items:center;gap:8px;background:rgba(26,110,232,0.12);border:1px solid rgba(26,110,232,0.35);color:var(--cyan);padding:6px 16px;border-radius:100px;font-size:0.78rem;font-weight:600;letter-spacing:0.5px;margin-bottom:24px}
    .hero-badge .dot{width:7px;height:7px;background:var(--cyan);border-radius:50%;animation:pulse 2s infinite;box-shadow:0 0 8px var(--cyan)}
    @keyframes pulse{0%,100%{opacity:1;transform:scale(1)}50%{opacity:0.5;transform:scale(1.3)}}
    .hero-inner h1{font-family:'Exo 2',sans-serif;font-size:clamp(2.8rem,7vw,5rem);font-weight:900;color:#fff;line-height:1.05;margin-bottom:20px;letter-spacing:-0.5px}
    .hero-desc{font-size:1.05rem;color:rgba(255,255,255,0.55);line-height:1.75;margin-bottom:36px;max-width:520px}
    .hero-buttons{display:flex;flex-wrap:wrap;gap:14px}
    .hero-img-wrap{position:relative;display:flex;align-items:center;justify-content:center}
    .hero-img-glow{position:absolute;inset:-20%;background:radial-gradient(ellipse 70% 70% at 50% 50%,rgba(26,110,232,0.35) 0%,transparent 70%);pointer-events:none}
    .hero-img-wrap img{width:100%;max-width:540px;border-radius:20px;object-fit:cover;position:relative;z-index:1;filter:drop-shadow(0 20px 60px rgba(26,110,232,0.4));animation:floatImg 6s ease-in-out infinite}
    @keyframes floatImg{0%,100%{transform:translateY(0)}50%{transform:translateY(-12px)}}
    .hero-arrow{position:absolute;top:50%;transform:translateY(-50%);width:44px;height:44px;border-radius:50%;background:rgba(255,255,255,0.06);backdrop-filter:blur(10px);border:1px solid rgba(255,255,255,0.15);color:#fff;display:flex;align-items:center;justify-content:center;font-size:1rem;transition:all .2s;z-index:10}
    .hero-arrow:hover{background:rgba(26,110,232,0.3);border-color:var(--blue)}
    .hero-arrow.prev{left:20px}
    .hero-arrow.next{right:20px}
    .hero-dots{display:flex;justify-content:center;gap:8px;padding:20px;position:relative;z-index:2}
    .hero-dot{width:8px;height:8px;border-radius:50%;background:rgba(255,255,255,0.2);cursor:pointer;transition:all .3s;border:none}
    .hero-dot.active{background:var(--blue);width:24px;border-radius:4px;box-shadow:0 0 10px rgba(26,110,232,0.6)}

    /* ===== STATS BAR ===== */
    .stats-bar{background:var(--bg-alt);padding:28px 0;border-top:1px solid var(--border-blue);border-bottom:1px solid var(--border-blue)}
    .stats-grid{display:flex;justify-content:space-around;flex-wrap:wrap;gap:16px}
    .stat-item{text-align:center}
    .stat-num{font-family:'Exo 2',sans-serif;font-size:1.9rem;font-weight:900;background:var(--grad);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;line-height:1}
    .stat-label{font-size:0.7rem;color:var(--text-dim);text-transform:uppercase;letter-spacing:0.8px;margin-top:4px;font-weight:600}

    /* ===== CATEGORY TILES ===== */
    .cat-tiles-section{padding:96px 0;background:var(--bg)}
    .cat-tiles-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(160px,1fr));gap:16px}
    .cat-tile{border-radius:var(--r-lg);overflow:hidden;cursor:pointer;background:var(--card);border:1px solid var(--card-border);transition:all .28s;box-shadow:var(--shadow-sm)}
    .cat-tile:hover{transform:translateY(-6px);box-shadow:var(--shadow-blue);border-color:var(--border-blue)}
    .cat-tile-img{width:100%;aspect-ratio:1;object-fit:cover;display:block;background:var(--bg-alt)}
    .cat-tile-label{padding:12px;text-align:center;font-size:0.8rem;font-weight:700;color:var(--heading);text-transform:uppercase;letter-spacing:0.5px}

    /* ===== BRAND TICKER ===== */
    .brand-ticker{background:var(--bg-alt);border-top:1px solid var(--card-border);border-bottom:1px solid var(--card-border);overflow:hidden;padding:14px 0}
    .brand-track{display:flex;gap:0;white-space:nowrap;animation:ticker 30s linear infinite}
    @keyframes ticker{0%{transform:translateX(0)}100%{transform:translateX(-50%)}}
    .brand-item{display:inline-flex;align-items:center;gap:8px;padding:0 28px;font-size:0.75rem;font-weight:700;color:var(--text-dim);letter-spacing:1px;text-transform:uppercase}
    .brand-item .dot{width:4px;height:4px;background:var(--blue);border-radius:50%;box-shadow:0 0 6px var(--blue)}

    /* ===== PRODUCT CARDS ===== */
    .product-card{background:var(--card);border:1px solid var(--card-border);border-radius:var(--r-lg);overflow:hidden;transition:all .28s;box-shadow:var(--shadow-sm);display:flex;flex-direction:column}
    .product-card:hover{transform:translateY(-6px);box-shadow:var(--shadow-blue);border-color:var(--border-blue)}
    .product-img-wrap{position:relative;overflow:hidden;aspect-ratio:1;background:var(--bg-alt)}
    .product-img-wrap img{width:100%;height:100%;object-fit:contain;padding:16px;transition:transform .4s ease}
    .product-card:hover .product-img-wrap img{transform:scale(1.07)}
    .product-badge{position:absolute;top:12px;left:12px;background:var(--grad);color:#fff;font-size:0.65rem;font-weight:700;letter-spacing:0.5px;padding:4px 10px;border-radius:100px;text-transform:uppercase}
    .product-wish-btn{position:absolute;top:10px;right:10px;width:34px;height:34px;border-radius:8px;background:rgba(13,17,32,0.85);display:flex;align-items:center;justify-content:center;color:var(--text-dim);transition:all .2s;border:1px solid var(--card-border)}
    .product-wish-btn svg{width:16px;height:16px}
    .product-wish-btn:hover,.product-wish-btn.wished{color:#ef4444;background:rgba(239,68,68,0.1);border-color:rgba(239,68,68,0.3)}
    .product-wish-btn.wished svg{fill:#ef4444}
    .product-info{padding:18px;flex:1;display:flex;flex-direction:column}
    .product-cat{font-size:0.68rem;font-weight:700;text-transform:uppercase;letter-spacing:1px;color:var(--cyan);margin-bottom:6px}
    .product-name{font-size:0.9rem;font-weight:700;color:var(--heading);line-height:1.45;margin-bottom:10px;flex:1}
    .product-price{font-size:1.1rem;font-weight:800;color:var(--blue);margin-bottom:14px}
    .product-price-orig{font-size:0.78rem;font-weight:500;color:var(--text-dim);text-decoration:line-through;margin-left:6px}
    .product-actions{display:flex;gap:8px}
    .product-add-btn{flex:1;padding:10px 14px;background:var(--grad);color:#fff;border-radius:8px;font-size:0.82rem;font-weight:700;transition:all .2s;box-shadow:0 2px 8px rgba(26,110,232,0.25)}
    .product-add-btn:hover{transform:translateY(-1px);box-shadow:0 6px 20px rgba(26,110,232,0.45)}
    .product-compare-btn{padding:10px 12px;border-radius:8px;border:1px solid var(--card-border);color:var(--text-dim);font-size:0.75rem;font-weight:600;transition:all .2s;background:rgba(255,255,255,0.03)}
    .product-compare-btn:hover{border-color:var(--blue);color:var(--cyan);background:rgba(26,110,232,0.08)}

    /* ===== FEATURED GRID ===== */
    .featured-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(240px,1fr));gap:24px}

    /* ===== SHOP PAGE OVERLAY ===== */
    .shop-page{position:fixed;inset:0;z-index:900;background:var(--bg);overflow-y:auto;transform:translateX(100%);transition:transform .35s cubic-bezier(0.4,0,0.2,1)}
    .shop-page.open{transform:translateX(0)}
    .shop-topbar{position:sticky;top:0;z-index:10;background:rgba(7,9,28,0.95);backdrop-filter:blur(16px);border-bottom:1px solid var(--border-blue);box-shadow:var(--shadow-sm)}
    .shop-back{font-size:0.82rem;font-weight:600;color:var(--text);padding:8px 14px;border-radius:8px;background:rgba(255,255,255,0.05);border:1px solid var(--card-border);transition:all .2s}
    .shop-back:hover{color:var(--cyan);border-color:var(--border-blue)}
    .topbar-cart{display:flex;align-items:center;gap:8px;padding:8px 16px;border-radius:8px;background:var(--grad);color:#fff;font-size:0.82rem;font-weight:700;transition:all .2s;box-shadow:var(--shadow-blue)}
    .topbar-cart:hover{transform:translateY(-1px);box-shadow:0 8px 28px rgba(26,110,232,0.5)}
    .topbar-cart-count{font-size:0.7rem;background:rgba(255,255,255,0.2);padding:1px 6px;border-radius:100px}
    .topbar-cart-total{font-size:0.8rem}
    .shop-body{padding:24px 0 80px}
    .shop-layout{display:grid;grid-template-columns:260px 1fr;gap:28px;align-items:start}
    .shop-sidebar{background:var(--card);border:1px solid var(--card-border);border-radius:var(--r-lg);padding:24px;position:sticky;top:80px;box-shadow:var(--shadow-sm)}
    .filter-overlay{display:none;position:fixed;inset:0;background:rgba(0,0,0,0.6);z-index:100}
    .filter-overlay.open{display:block}
    .filter-overlay-close{display:none;justify-content:space-between;align-items:center;margin-bottom:16px}
    .filter-overlay-close h3{font-size:1rem;font-weight:700;color:var(--heading)}
    .filter-overlay-close button{font-size:1.4rem;color:var(--text-dim)}
    .shop-search{margin-bottom:20px}
    .shop-search input{width:100%;padding:10px 14px;border-radius:8px;border:1.5px solid var(--card-border);font-size:0.84rem;background:rgba(255,255,255,0.04);color:var(--heading);outline:none;transition:all .2s}
    .shop-search input:focus{border-color:var(--blue);background:rgba(26,110,232,0.08);box-shadow:0 0 0 3px rgba(26,110,232,0.12)}
    .filter-group{margin-bottom:24px}
    .filter-group h4{font-size:0.72rem;font-weight:700;text-transform:uppercase;letter-spacing:0.8px;color:var(--text-dim);margin-bottom:12px}
    .filter-cat-btn{display:flex;align-items:center;justify-content:space-between;width:100%;padding:8px 10px;border-radius:8px;margin-bottom:4px;font-size:0.84rem;font-weight:500;color:var(--text);transition:all .15s;background:transparent}
    .filter-cat-btn:hover{background:rgba(255,255,255,0.04);color:var(--heading)}
    .filter-cat-btn.active{background:rgba(26,110,232,0.12);color:var(--cyan);font-weight:700}
    .filter-cat-count{font-size:0.7rem;background:rgba(255,255,255,0.06);padding:2px 6px;border-radius:100px;color:var(--text-dim)}
    .filter-cat-btn.active .filter-cat-count{background:rgba(26,110,232,0.2);color:var(--cyan)}
    .price-range{display:flex;align-items:center;gap:8px}
    .price-range input{flex:1;padding:8px 10px;border-radius:8px;border:1.5px solid var(--card-border);font-size:0.82rem;background:rgba(255,255,255,0.04);color:var(--heading);outline:none;transition:all .2s}
    .price-range input:focus{border-color:var(--blue)}
    .price-range span{color:var(--text-dim);font-size:0.8rem}
    .filter-reset-btn{width:100%;padding:10px;border-radius:8px;border:1px solid var(--card-border);color:var(--text);font-size:0.82rem;font-weight:600;transition:all .2s;background:transparent}
    .filter-reset-btn:hover{border-color:var(--blue);color:var(--cyan)}
    .shop-header{display:flex;align-items:center;justify-content:space-between;margin-bottom:20px}
    .shop-count{font-size:0.84rem;color:var(--text-dim);font-weight:500}
    #shopSort{padding:8px 12px;border-radius:8px;border:1px solid var(--card-border);font-size:0.82rem;background:var(--card);color:var(--heading);outline:none;cursor:pointer}
    .shop-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:20px}
    .mobile-filter-toggle{display:none;width:100%;padding:11px;border:1px solid var(--card-border);border-radius:8px;font-size:0.84rem;font-weight:600;color:var(--text);margin-bottom:16px;background:rgba(255,255,255,0.04);transition:all .2s}
    .mobile-filter-toggle:hover{border-color:var(--blue);color:var(--cyan)}

    /* ===== PRODUCT DETAIL OVERLAY ===== */
    .product-detail{position:fixed;inset:0;z-index:950;background:var(--bg);overflow-y:auto;transform:translateX(100%);transition:transform .35s cubic-bezier(0.4,0,0.2,1)}
    .product-detail.open{transform:translateX(0)}
    .pd-topbar{position:sticky;top:0;z-index:10;background:rgba(7,9,28,0.95);backdrop-filter:blur(16px);border-bottom:1px solid var(--border-blue);display:flex;align-items:center;justify-content:space-between;padding:0 24px;height:56px;box-shadow:var(--shadow-sm)}
    .pd-back{font-size:0.84rem;font-weight:600;color:var(--text);padding:7px 14px;border-radius:8px;background:rgba(255,255,255,0.05);border:1px solid var(--card-border);transition:all .2s}
    .pd-back:hover{color:var(--cyan);border-color:var(--border-blue)}
    .pd-content{max-width:1000px;margin:0 auto;padding:40px 24px 80px}
    .pd-grid{display:grid;grid-template-columns:1fr 1fr;gap:48px;align-items:start}
    .pd-images{position:sticky;top:80px}
    .pd-main-img{width:100%;aspect-ratio:1;background:var(--bg-alt);border-radius:var(--r-lg);overflow:hidden;margin-bottom:12px;border:1px solid var(--card-border);cursor:zoom-in;display:flex;align-items:center;justify-content:center;padding:24px}
    .pd-main-img img{max-height:100%;max-width:100%;object-fit:contain}
    .pd-thumbs{display:flex;gap:10px;flex-wrap:wrap}
    .pd-thumb{width:72px;height:72px;border-radius:8px;overflow:hidden;border:2px solid var(--card-border);cursor:pointer;transition:all .2s;background:var(--bg-alt);display:flex;align-items:center;justify-content:center;padding:4px}
    .pd-thumb img{width:100%;height:100%;object-fit:contain}
    .pd-thumb.active,.pd-thumb:hover{border-color:var(--blue);box-shadow:0 0 12px rgba(26,110,232,0.3)}
    .pd-info h1{font-family:'Exo 2',sans-serif;font-size:2rem;font-weight:800;color:var(--heading);margin-bottom:8px;line-height:1.2}
    .pd-cat{font-size:0.72rem;text-transform:uppercase;letter-spacing:1px;color:var(--cyan);font-weight:700;margin-bottom:14px;display:block}
    .pd-price{font-size:2rem;font-weight:900;color:var(--blue);margin-bottom:4px}
    .pd-price-orig{font-size:0.9rem;color:var(--text-dim);text-decoration:line-through;margin-bottom:20px;display:block}
    .pd-desc{font-size:0.92rem;color:var(--text);line-height:1.8;margin-bottom:24px}
    .pd-specs{margin-bottom:28px}
    .pd-specs h3{font-size:0.72rem;text-transform:uppercase;letter-spacing:0.8px;color:var(--text-dim);font-weight:700;margin-bottom:10px}
    .pd-spec-row{display:flex;gap:8px;padding:10px 0;border-bottom:1px solid rgba(255,255,255,0.04);font-size:0.86rem}
    .pd-spec-key{color:var(--text-dim);min-width:130px;font-weight:500}
    .pd-spec-val{color:var(--heading);font-weight:600}
    .pd-actions{display:flex;gap:12px;flex-wrap:wrap}
    .pd-add-btn{flex:1;min-width:160px;padding:14px 24px;background:var(--grad);color:#fff;border-radius:10px;font-size:0.9rem;font-weight:700;transition:all .2s;box-shadow:var(--shadow-blue)}
    .pd-add-btn:hover{transform:translateY(-2px);box-shadow:0 12px 40px rgba(26,110,232,0.5)}
    .pd-wish-btn{padding:14px 16px;border-radius:10px;border:1.5px solid var(--card-border);color:var(--text-dim);font-size:0.9rem;font-weight:600;transition:all .2s;background:rgba(255,255,255,0.04)}
    .pd-wish-btn:hover,.pd-wish-btn.wished{border-color:#ef4444;color:#ef4444;background:rgba(239,68,68,0.08)}

    /* ===== LIGHTBOX ===== */
    .lightbox{position:fixed;inset:0;background:rgba(0,0,0,0.95);z-index:3000;display:none;align-items:center;justify-content:center;cursor:zoom-out}
    .lightbox.open{display:flex}
    .lightbox img{max-width:90vw;max-height:90vh;object-fit:contain;border-radius:8px}
    .lightbox-close{position:absolute;top:20px;right:24px;font-size:2rem;color:rgba(255,255,255,0.5);transition:color .2s}
    .lightbox-close:hover{color:#fff}

    /* ===== SERVICES ===== */
    .services-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));gap:24px}
    .service-card{padding:32px 28px;border-radius:var(--r-lg);transition:all .28s}
    .service-card:hover{transform:translateY(-6px);box-shadow:var(--shadow-blue);border-color:var(--border-blue)}
    .svc-icon{width:52px;height:52px;border-radius:14px;background:rgba(26,110,232,0.12);border:1px solid var(--border-blue);display:flex;align-items:center;justify-content:center;font-size:1.4rem;margin-bottom:18px}
    .service-card h3{font-family:'Exo 2',sans-serif;font-size:1.15rem;font-weight:800;color:var(--heading);margin-bottom:10px;letter-spacing:0.3px}
    .service-card p{font-size:0.87rem;color:var(--text);line-height:1.75}

    /* ===== ABOUT ===== */
    .about-grid{display:grid;grid-template-columns:1fr 1fr;gap:64px;align-items:center}
    .about-text p{font-size:0.95rem;color:var(--text);line-height:1.8;margin-bottom:16px}
    .about-features{display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-top:28px}
    .about-feat{display:flex;align-items:center;gap:10px;font-size:0.85rem;font-weight:600;color:var(--heading)}
    .ck{color:var(--cyan);font-weight:800;background:rgba(56,189,248,0.1);border:1px solid rgba(56,189,248,0.2);width:22px;height:22px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:0.7rem;flex-shrink:0}
    .about-right{display:flex;flex-direction:column;gap:24px}
    .about-img-wrap{position:relative;border-radius:20px;overflow:hidden;border:1px solid var(--border-blue);box-shadow:var(--shadow-blue)}
    .about-img-wrap img{width:100%;height:360px;object-fit:cover;display:block}
    .about-img-wrap::after{content:'';position:absolute;inset:0;background:linear-gradient(to top,rgba(7,9,28,0.6) 0%,transparent 50%);pointer-events:none}
    .about-stats{display:grid;grid-template-columns:1fr 1fr;gap:16px}
    .about-stat{padding:24px 20px;border-radius:var(--r-lg);text-align:center}
    .about-stat .num{font-family:'Exo 2',sans-serif;font-size:2rem;font-weight:900;background:var(--grad);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;line-height:1}
    .about-stat .lbl{font-size:0.78rem;color:var(--text-dim);margin-top:6px;font-weight:500}

    /* ===== REVIEWS ===== */
    .reviews-big{display:flex;align-items:center;gap:16px;justify-content:center;margin-top:20px}
    .reviews-big .num{font-family:'Exo 2',sans-serif;font-size:3rem;font-weight:900;background:var(--grad);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;line-height:1}
    .stars{font-size:1.1rem;color:var(--gold);letter-spacing:2px}
    .reviews-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:24px}
    .review-card{padding:28px;border-radius:var(--r-lg)}
    .review-stars{color:var(--gold);font-size:0.9rem;margin-bottom:14px;letter-spacing:1px}
    .review-text{font-size:0.87rem;color:var(--text);line-height:1.75;margin-bottom:20px;font-style:italic}
    .review-author{display:flex;align-items:center;gap:12px}
    .review-avatar{width:40px;height:40px;border-radius:50%;background:var(--grad);color:#fff;display:flex;align-items:center;justify-content:center;font-weight:800;font-size:1rem;flex-shrink:0;box-shadow:0 0 12px rgba(26,110,232,0.3)}
    .review-name{font-weight:700;font-size:0.88rem;color:var(--heading)}
    .review-source{font-size:0.75rem;color:var(--text-dim)}

    /* ===== CTA BANNER ===== */
    .cta-banner{background:var(--grad);border-radius:var(--r-lg);padding:60px 48px;text-align:center;position:relative;overflow:hidden;box-shadow:0 16px 64px rgba(26,110,232,0.4)}
    .cta-banner::before{content:'';position:absolute;inset:0;background:radial-gradient(ellipse 60% 80% at 80% 50%,rgba(255,255,255,0.08) 0%,transparent 70%)}
    .cta-banner::after{content:'';position:absolute;inset:0;background-image:linear-gradient(rgba(255,255,255,0.05) 1px,transparent 1px),linear-gradient(90deg,rgba(255,255,255,0.05) 1px,transparent 1px);background-size:40px 40px;pointer-events:none}
    .cta-banner h2{font-family:'Exo 2',sans-serif;font-size:2.4rem;font-weight:900;color:#fff;margin-bottom:12px;position:relative;z-index:1;letter-spacing:0.3px}
    .cta-banner p{color:rgba(255,255,255,0.8);margin-bottom:32px;position:relative;z-index:1;font-size:1rem}
    .cta-banner .btn{background:#fff;color:var(--blue);font-size:0.9rem;padding:13px 36px;box-shadow:0 4px 20px rgba(0,0,0,0.2);position:relative;z-index:1}
    .cta-banner .btn:hover{transform:translateY(-2px);box-shadow:0 8px 32px rgba(0,0,0,0.25)}

    /* ===== CONTACT ===== */
    .findus-grid{display:grid;grid-template-columns:1fr 1fr;gap:48px;align-items:start}
    .loc-card{padding:28px;border-radius:var(--r-lg);margin-bottom:20px}
    .loc-card h3{font-size:0.95rem;font-weight:800;color:var(--heading);margin-bottom:10px}
    .addr{font-size:0.87rem;color:var(--text);line-height:1.7;margin-bottom:14px}
    .loc-link{font-size:0.84rem;font-weight:700;color:var(--cyan);display:inline-flex;align-items:center;gap:4px}
    .loc-link:hover{text-decoration:underline}
    .loc-tags{margin-bottom:4px}
    .loc-tags-label{font-size:0.68rem;font-weight:700;text-transform:uppercase;letter-spacing:0.8px;color:var(--text-dim);margin-bottom:8px}
    .area-tags,.svc-tags{display:flex;flex-wrap:wrap;gap:8px}
    .area-tag{padding:4px 12px;border-radius:100px;font-size:0.74rem;font-weight:600;background:rgba(26,110,232,0.12);color:var(--cyan);border:1px solid rgba(26,110,232,0.25)}
    .svc-tag{padding:4px 12px;border-radius:100px;font-size:0.74rem;font-weight:600;background:rgba(255,255,255,0.05);color:var(--text);border:1px solid var(--card-border)}
    .contact-block-title{font-size:0.68rem;font-weight:700;text-transform:uppercase;letter-spacing:0.8px;color:var(--text-dim);margin-bottom:12px}
    .contact-methods{display:flex;flex-direction:column;gap:8px;margin-bottom:16px}
    .contact-chip{display:flex;align-items:center;gap:10px;padding:11px 16px;border-radius:10px;background:rgba(255,255,255,0.04);border:1px solid var(--card-border);font-size:0.84rem;color:var(--heading);font-weight:500}
    .contact-chip a{color:var(--heading);transition:color .2s}
    .contact-chip a:hover{color:var(--cyan)}
    .contact-chip .icon{font-size:1rem}
    .contact-form{padding:28px;border-radius:var(--r-lg)}
    .form-group{margin-bottom:16px}
    .form-group label{display:block;font-size:0.72rem;font-weight:700;color:var(--text-dim);margin-bottom:6px;text-transform:uppercase;letter-spacing:0.4px}
    .form-group input,.form-group textarea{width:100%;padding:11px 14px;border-radius:8px;border:1.5px solid var(--card-border);font-size:0.88rem;background:rgba(255,255,255,0.04);color:var(--heading);outline:none;transition:all .2s;font-family:inherit}
    .form-group input:focus,.form-group textarea:focus{border-color:var(--blue);background:rgba(26,110,232,0.06);box-shadow:0 0 0 3px rgba(26,110,232,0.1)}
    .form-group textarea{resize:vertical;min-height:100px}
    .findus-map{margin-top:40px;border-radius:var(--r-lg);overflow:hidden;border:1px solid var(--border-blue);box-shadow:var(--shadow)}
    .findus-map iframe{display:block;width:100%;height:340px;border:none}

    /* ===== FAQ ===== */
    .faq-list{max-width:760px;margin:0 auto}
    .faq-item{border-bottom:1px solid rgba(255,255,255,0.05)}
    .faq-item:first-child{border-top:1px solid rgba(255,255,255,0.05)}
    .faq-q{width:100%;padding:20px 4px;display:flex;align-items:center;justify-content:space-between;font-size:0.95rem;font-weight:600;color:var(--heading);text-align:left;transition:color .2s}
    .faq-q:hover{color:var(--cyan)}
    .faq-icon{font-size:1.3rem;color:var(--blue);font-weight:700;transition:transform .3s;flex-shrink:0;margin-left:16px}
    .faq-q.open .faq-icon{transform:rotate(45deg)}
    .faq-a{max-height:0;overflow:hidden;transition:max-height .3s ease}
    .faq-a.open{max-height:300px}
    .faq-a-inner{padding:0 4px 20px;font-size:0.9rem;color:var(--text);line-height:1.75}

    /* ===== FOOTER ===== */
    .footer{background:#04060f;color:rgba(255,255,255,0.4);padding:64px 0 0;border-top:1px solid var(--border-blue)}
    .footer-grid{display:grid;grid-template-columns:2fr 1fr 1fr 1fr;gap:48px;padding-bottom:48px}
    .footer-brand .logo{font-family:'Exo 2',sans-serif;font-size:1.8rem;font-weight:900;color:#fff;letter-spacing:1px;margin-bottom:12px}
    .footer-brand p{font-size:0.84rem;line-height:1.75}
    .footer-col h4{font-size:0.7rem;text-transform:uppercase;letter-spacing:1px;font-weight:700;color:rgba(255,255,255,0.7);margin-bottom:18px}
    .footer-col ul li{margin-bottom:10px}
    .footer-col ul li a{font-size:0.84rem;color:rgba(255,255,255,0.35);transition:color .2s}
    .footer-col ul li a:hover{color:var(--cyan)}
    .footer-bottom{border-top:1px solid rgba(255,255,255,0.06);padding:20px 0;display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:12px}
    .footer-bottom p{font-size:0.78rem}
    .footer-social{display:flex;gap:10px}
    .footer-social a{width:34px;height:34px;border-radius:8px;background:rgba(255,255,255,0.05);color:rgba(255,255,255,0.35);display:flex;align-items:center;justify-content:center;transition:all .2s;border:1px solid rgba(255,255,255,0.06)}
    .footer-social a:hover{background:var(--blue);color:#fff;border-color:var(--blue);box-shadow:0 0 16px rgba(26,110,232,0.4)}

    /* ===== CART / WISHLIST DRAWERS ===== */
    .cart-overlay,.wish-overlay{position:fixed;inset:0;background:rgba(0,0,0,0.55);z-index:1100;display:none;backdrop-filter:blur(4px)}
    .cart-overlay.open,.wish-overlay.open{display:block}
    .cart-drawer,.wish-drawer{position:fixed;top:0;right:0;bottom:0;width:380px;max-width:92vw;z-index:1200;background:#0d1120;border-left:1px solid var(--border-blue);box-shadow:-8px 0 48px rgba(0,0,0,0.5);transform:translateX(100%);transition:transform .32s cubic-bezier(0.4,0,0.2,1);display:flex;flex-direction:column}
    .cart-drawer.open,.wish-drawer.open{transform:translateX(0)}
    .cart-header{display:flex;align-items:center;justify-content:space-between;padding:20px 24px;border-bottom:1px solid var(--card-border)}
    .cart-header h3{font-size:1rem;font-weight:800;color:var(--heading)}
    .cart-close{font-size:1.5rem;color:var(--text-dim);transition:color .2s}
    .cart-close:hover{color:var(--heading)}
    .cart-body{flex:1;overflow-y:auto;padding:16px 24px}
    .cart-empty{text-align:center;color:var(--text-dim);padding:40px 20px;font-size:0.88rem}
    .cart-item{display:flex;gap:14px;padding:14px 0;border-bottom:1px solid rgba(255,255,255,0.04)}
    .cart-item-img{width:64px;height:64px;border-radius:8px;overflow:hidden;background:var(--bg-alt);flex-shrink:0;border:1px solid var(--card-border)}
    .cart-item-img img{width:100%;height:100%;object-fit:contain;padding:6px}
    .cart-item-info{flex:1}
    .cart-item-name{font-size:0.84rem;font-weight:600;color:var(--heading);line-height:1.4;margin-bottom:4px}
    .cart-item-price{font-size:0.88rem;font-weight:800;color:var(--blue)}
    .cart-item-actions{display:flex;align-items:center;gap:8px;margin-top:8px}
    .cart-qty-btn{width:26px;height:26px;border-radius:6px;border:1px solid var(--card-border);font-size:0.9rem;display:flex;align-items:center;justify-content:center;transition:all .15s;color:var(--heading)}
    .cart-qty-btn:hover{border-color:var(--blue);color:var(--cyan)}
    .cart-qty{font-size:0.84rem;font-weight:700;color:var(--heading);min-width:20px;text-align:center}
    .cart-item-remove{font-size:0.7rem;color:#ef4444;font-weight:600;margin-left:auto;transition:opacity .2s}
    .cart-item-remove:hover{opacity:0.7}
    .cart-footer{padding:20px 24px;border-top:1px solid var(--card-border);background:var(--bg-alt)}
    .cart-total{display:flex;justify-content:space-between;align-items:center;margin-bottom:16px;font-weight:800}
    .cart-total span:first-child{font-size:0.84rem;color:var(--text-dim);text-transform:uppercase;letter-spacing:0.5px}
    .cart-total span:last-child{font-size:1.2rem;color:var(--heading)}
    .cart-checkout-btn{width:100%;padding:13px;border-radius:10px;background:var(--grad);color:#fff;font-size:0.88rem;font-weight:700;transition:all .2s;box-shadow:var(--shadow-blue)}
    .cart-checkout-btn:hover{transform:translateY(-2px);box-shadow:0 10px 36px rgba(26,110,232,0.5)}

    /* ===== COMPARE BAR & MODAL ===== */
    .compare-bar{position:fixed;bottom:24px;left:50%;transform:translateX(-50%);background:#0d1120;color:rgba(255,255,255,0.8);padding:14px 24px;border-radius:100px;z-index:900;display:none;align-items:center;gap:14px;font-size:0.84rem;box-shadow:var(--shadow-lg);border:1px solid var(--border-blue)}
    .compare-bar.show{display:flex}
    .compare-btn-go{padding:7px 18px;border-radius:100px;background:var(--grad);color:#fff;font-size:0.78rem;font-weight:700;transition:all .2s}
    .compare-btn-go:hover{transform:scale(1.03)}
    .compare-btn-clear{font-size:0.78rem;color:rgba(255,255,255,0.35);transition:color .2s}
    .compare-btn-clear:hover{color:#fff}
    .compare-modal{position:fixed;inset:0;background:rgba(0,0,0,0.7);z-index:2000;display:none;align-items:center;justify-content:center;backdrop-filter:blur(8px)}
    .compare-modal.open{display:flex}
    .compare-content{background:#0d1120;border:1px solid var(--border-blue);border-radius:var(--r-lg);padding:28px;max-width:92vw;max-height:90vh;overflow:auto;box-shadow:var(--shadow-lg);color:var(--heading)}
    .compare-table{width:100%;border-collapse:collapse;font-size:0.84rem}
    .compare-table th,.compare-table td{padding:12px 16px;border:1px solid var(--card-border);vertical-align:top}
    .compare-table th{background:rgba(26,110,232,0.08);font-weight:700;color:var(--text-dim);font-size:0.72rem;text-transform:uppercase;letter-spacing:0.5px}

    /* ===== TOAST ===== */
    .toast-container{position:fixed;bottom:24px;right:24px;z-index:9999;display:flex;flex-direction:column;gap:10px;max-width:320px}
    .toast{position:relative;padding:14px 44px 14px 16px;border-radius:12px;display:flex;align-items:center;gap:12px;background:#0d1120;color:#fff;box-shadow:var(--shadow-lg);animation:toastIn .3s ease;font-size:0.85rem;font-weight:500;border:1px solid var(--card-border);overflow:hidden}
    .toast.success{border-left:3px solid #22c55e}
    .toast.error{border-left:3px solid #ef4444}
    .toast.info{border-left:3px solid var(--blue)}
    @keyframes toastIn{from{opacity:0;transform:translateY(10px) scale(0.95)}to{opacity:1;transform:translateY(0) scale(1)}}
    .toast-icon{font-size:1.1rem;flex-shrink:0}
    .toast-msg{font-size:0.82rem;color:rgba(255,255,255,0.8)}
    .toast-close{position:absolute;top:50%;right:14px;transform:translateY(-50%);cursor:pointer;color:rgba(255,255,255,0.35);font-size:1rem;padding:4px;border-radius:4px;transition:color .2s}
    .toast-close:hover{color:#fff}
    .toast-progress{position:absolute;bottom:0;left:0;height:3px;background:rgba(255,255,255,0.15);border-radius:0 0 12px 12px;animation:toastProgress 3s linear forwards}
    @keyframes toastProgress{0%{width:100%}100%{width:0}}
    @media(max-width:480px){.toast-container{right:12px;left:12px;bottom:16px}}

    /* ===== SCROLL TO TOP ===== */
    .scroll-top-btn{position:fixed;bottom:24px;right:24px;width:40px;height:40px;border-radius:50%;background:var(--grad);color:#fff;z-index:800;display:flex;align-items:center;justify-content:center;font-size:1.1rem;box-shadow:var(--shadow-blue);opacity:0;visibility:hidden;transform:translateY(10px);transition:all .3s}
    .scroll-top-btn.show{opacity:1;visibility:visible;transform:translateY(0)}
    .scroll-top-btn:hover{transform:translateY(-3px);box-shadow:0 10px 36px rgba(26,110,232,0.5)}

    /* ===== RESPONSIVE ===== */
    @media(max-width:1024px){
      .shop-layout{grid-template-columns:1fr}
      .shop-sidebar{position:fixed;left:-100%;top:0;bottom:0;width:300px;border-radius:0;z-index:200;overflow-y:auto;transition:left .3s}
      .shop-sidebar.mobile-open{left:0}
      .filter-overlay-close{display:flex}
      .mobile-filter-toggle{display:block}
      .hero-split{grid-template-columns:1fr}
      .hero-img-wrap{display:none}
    }
    @media(max-width:768px){
      .navbar .container{height:58px}
      .nav-links{display:none}
      .nav-search{display:none}
      .hamburger{display:flex}
      .hero{min-height:500px}
      .hero-inner h1{font-size:clamp(2.2rem,8vw,3rem)}
      .hero-slide .container{padding-top:60px;padding-bottom:60px}
      .section{padding:64px 0}
      .cat-tiles-section{padding:64px 0}
      .about-grid{grid-template-columns:1fr;gap:40px}
      .about-stats{grid-template-columns:1fr 1fr}
      .findus-grid{grid-template-columns:1fr}
      .footer-grid{grid-template-columns:1fr 1fr;gap:32px}
      .pd-grid{grid-template-columns:1fr}
      .pd-images{position:static}
      .cta-banner{padding:44px 28px}
    }
    @media(max-width:480px){
      .featured-grid{grid-template-columns:1fr 1fr;gap:14px}
      .shop-grid{grid-template-columns:1fr 1fr;gap:14px}
      .footer-grid{grid-template-columns:1fr}
      .cta-banner h2{font-size:1.8rem}
      .stats-grid{gap:20px}
      .hero-buttons{flex-direction:column}
      .hero-buttons .btn{width:100%;justify-content:center}
      .section-header{margin-bottom:36px}
    }
"""

html = re.sub(r'<style>.*?</style>', f'<style>{NEW_CSS}  </style>', html, flags=re.DOTALL)

# ── 2. HERO: add bg image + grid overlay divs, update hero-slide-1 to split layout ──
# Insert bg elements right after <section class="hero"
old_hero_open = '<section class="hero" id="hero">\n    <div class="hero-slides"'
new_hero_open = '''<section class="hero" id="hero">
    <div class="hero-bg-img"></div>
    <div class="hero-grid-overlay"></div>
    <div class="hero-slides"'''
html = html.replace(old_hero_open, new_hero_open, 1)

# Replace hero slide 1 inner — swap from simple hero-inner to hero-split layout
old_slide1 = '''      <div class="hero-slide hero-slide-1">
        <div class="container">
          <div class="hero-inner">
            <div class="hero-badge"><span class="dot"></span> Valenzuela's PC Hub</div>
            <h1>Hanap. Usap. <span class="grad">Build.</span></h1>
            <p class="hero-desc">Your one-stop shop for custom PC builds and quality computer parts in Valenzuela, Philippines.</p>
            <div class="hero-buttons">
              <a href="/shop" class="btn btn-primary" onclick="event.preventDefault();navigateTo('/shop')">Shop Now</a>
              <a href="/contact" class="btn btn-outline" onclick="event.preventDefault();navigateTo('/contact')">Contact Us</a>
            </div>
          </div>
        </div>
      </div>'''

new_slide1 = '''      <div class="hero-slide hero-slide-1">
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

html = html.replace(old_slide1, new_slide1, 1)

# ── 3. ABOUT: replace right column (stats only) with image + stats ──
old_about_right = '''        <div class="about-stats">
          <div class="about-stat glass"><div class="num">100%</div><div class="lbl">Recommend Rate</div></div>
          <div class="about-stat glass"><div class="num">413+</div><div class="lbl">5-Star Reviews</div></div>
          <div class="about-stat glass"><div class="num">24K+</div><div class="lbl">FB Followers</div></div>
          <div class="about-stat glass"><div class="num">#1</div><div class="lbl">PC Hub Valenzuela</div></div>
        </div>'''

new_about_right = '''        <div class="about-right">
          <div class="about-img-wrap">
            <img src="/about-circuit.jpg" alt="H.U.B — Custom PC Builds" loading="lazy">
          </div>
          <div class="about-stats">
            <div class="about-stat glass"><div class="num">100%</div><div class="lbl">Recommend Rate</div></div>
            <div class="about-stat glass"><div class="num">413+</div><div class="lbl">5-Star Reviews</div></div>
            <div class="about-stat glass"><div class="num">24K+</div><div class="lbl">FB Followers</div></div>
            <div class="about-stat glass"><div class="num">#1</div><div class="lbl">PC Hub Valenzuela</div></div>
          </div>
        </div>'''

html = html.replace(old_about_right, new_about_right, 1)

with open('public/index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Done! Redesign applied.")
