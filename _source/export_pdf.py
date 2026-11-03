from pathlib import Path
from playwright.sync_api import sync_playwright
root=Path(__file__).resolve().parents[1]
src=(root/'textbook.html').resolve().as_uri()
out=root/'assets/Algebra_KR1_2026_LEFT_TO_RIGHT_FULL.pdf'
with sync_playwright() as p:
 b=p.chromium.launch(headless=True)
 page=b.new_page(viewport={'width':1150,'height':900},device_scale_factor=1)
 page.goto(src,wait_until='load',timeout=90000)
 page.add_style_tag(content='''@page{size:A4;margin:15mm 13mm 17mm}
 @media print{html,body{background:#fff!important;scroll-behavior:auto;color:#101b18}
 .site-nav,.book-sidebar,.footer{display:none!important}
 .book-hero{padding:12mm 0 9mm;max-width:100%;break-after:page}
 .book-hero h1{font-size:39px}.book-hero p,.notice{font-size:12px}
 .book-layout{display:block;max-width:100%;padding:0;margin:0}
 .book{border:0!important;box-shadow:none!important;padding:0;margin:0;overflow:visible!important;max-width:100%;background:white}
 .book>h1{font-size:27px;margin-top:24px;break-after:avoid}
 .book>h1:first-child{break-before:auto}
 .book h2,.book h3{break-after:avoid}
 .book p,.book li{font-size:14px;line-height:1.53}
 .book blockquote{break-inside:avoid}
 .book .math.display{font-size:14px;break-inside:avoid}
 .book table{max-width:100%;font-size:10px}
 }''')
 page.pdf(path=str(out),format='A4',print_background=True,prefer_css_page_size=True,display_header_footer=False,scale=1.0)
 b.close()
print('CREATED',out.stat().st_size,str(out))
