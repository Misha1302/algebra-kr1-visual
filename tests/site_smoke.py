from pathlib import Path
from playwright.sync_api import sync_playwright, expect

ROOT = Path(__file__).resolve().parents[1]
def open_local(page, name):
    page.goto((ROOT/name.split("#")[0]).as_uri() + (("#"+name.split("#",1)[1]) if "#" in name else ""), wait_until="load")
    page.wait_for_timeout(150)

def no_overflow(page, name):
    values=page.evaluate("({scroll:document.documentElement.scrollWidth,client:document.documentElement.clientWidth})")
    assert values["scroll"] <= values["client"]+3, f"{name}: horizontal overflow {values}"

def run():
    with sync_playwright() as pw:
        browser=pw.chromium.launch(headless=True)
        desktop=browser.new_page(viewport={"width":1365,"height":900}, device_scale_factor=1)
        errors=[]
        desktop.on("pageerror", lambda error: errors.append(str(error)))
        open_local(desktop, "index.html")
        expect(desktop.locator("#what-is-matrix")).to_be_visible()
        expect(desktop.locator(".first-definition")).to_contain_text("элемент")
        desktop.locator('#matrix-c button[data-i="0"][data-j="1"]').click()
        assert "64" in desktop.locator("#calc-equation").inner_text()
        assert desktop.locator("a[href='./definitions.html']").count() >= 1
        no_overflow(desktop,"index desktop")
        desktop.screenshot(path="/tmp/algebra-home-desktop.png",full_page=True)

        open_local(desktop, "definitions.html")
        assert desktop.locator("article.def").count() == 26,desktop.locator("#result").inner_text()
        for id in ["D01","D04","D12","D18","D26"]:
            expect(desktop.locator("#"+id)).to_be_visible()
        desktop.locator("#search").fill("D12")
        assert desktop.locator("article.def").count()==1
        assert "Союзная" in desktop.locator("#definitions").inner_text()
        desktop.locator("#search").fill("")
        desktop.locator('button[data-filter="Ранг и линейная зависимость"]').click()
        assert desktop.locator("article.def").count()>=8
        desktop.locator('button[data-filter="Все"]').click()
        no_overflow(desktop,"glossary desktop")
        desktop.screenshot(path="/tmp/algebra-dictionary-desktop.png",full_page=True)

        open_local(desktop,"lab.html")
        expect(desktop.locator("section.theory")).to_be_visible()
        expect(desktop.locator("section.theory")).to_contain_text("Матрица")
        assert desktop.locator("section.theory ol li").count()>=3
        for i in range(8):
            desktop.locator(".tab").nth(i).click()
            assert desktop.locator("section.theory").count()==1,f"missing theory in tab {i+1}"
            assert len(desktop.locator("section.theory").inner_text())>=180
            assert desktop.locator(".theory-example").count()>=1
        open_local(desktop,"lab.html#adj")
        assert "Минор" in desktop.locator("h2").inner_text()
        assert "определитель" in desktop.locator("section.theory").inner_text().lower()
        open_local(desktop,"lab.html#dimensions")
        desktop.locator("#dimselect").select_option("bad")
        assert "3 ≠ 2" in desktop.locator(".work").inner_text()
        open_local(desktop,"lab.html#matrix")
        desktop.locator('button[data-act="next-pair"]').click()
        assert "Шаг 1" in desktop.locator(".controls").inner_text()
        no_overflow(desktop,"lab desktop")
        desktop.screenshot(path="/tmp/algebra-lab-desktop.png",full_page=True)

        mobile=browser.new_page(viewport={"width":390,"height":844}, device_scale_factor=1)
        mobile.on("pageerror",lambda error: errors.append("mobile:"+str(error)))
        for name in ["index.html","definitions.html","lab.html"]:
            open_local(mobile,name)
            no_overflow(mobile,name+" mobile")
            mobile.screenshot(path="/tmp/algebra-"+name.replace(".html","")+"-mobile.png",full_page=True)
        assert not errors,errors
        print("PASS: 26 definitions, all 8 theory tabs, deep links, dimensions, multiplication, search, mobile widths, 0 JS errors")
        browser.close()
if __name__=="__main__":
    run()
