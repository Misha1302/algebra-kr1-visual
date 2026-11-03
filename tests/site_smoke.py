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
        assert desktop.locator("section.chapter").count() == 7
        assert desktop.locator(".formal[id]").count() == 26
        assert desktop.locator(".quickcheck").count() == 7
        for id in ["D01","D04","D12","D18","D26"]:
            expect(desktop.locator("#"+id)).to_be_visible()
        desktop.locator('#base-matrix button[data-i="1"][data-j="2"]').click()
        assert "a₂₃ = 6" in desktop.locator("#base-explain").inner_text()
        desktop.locator('#mul-C button[data-i="0"][data-j="1"]').click()
        for _ in range(3): desktop.locator("#mul-next").click()
        assert "= 64" in desktop.locator("#mul-equation").inner_text()
        no_overflow(desktop,"course desktop")
        desktop.screenshot(path="/tmp/algebra-course-desktop.png",full_page=True)

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
        print("PASS: 7 detailed chapters, 26 anchored definitions, 8 auxiliary labs, mobile widths, 0 JS errors")
        browser.close()
if __name__=="__main__":
    run()
