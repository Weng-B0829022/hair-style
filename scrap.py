from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time

def setup_driver():
    """設置並返回一個配置好的Chrome WebDriver實例"""
    chrome_options = Options()
    # 取消註釋下一行以無頭模式運行Chrome
    # chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-notifications")
    chrome_options.add_argument("--disable-popup-blocking")
    
    # 設置user-agent以避免被檢測為機器人
    chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36")
    
    # 初始化Chrome WebDriver
    driver = webdriver.Chrome(options=chrome_options)
    
    return driver

def access_instagram_profile(driver, profile_name):
    """直接訪問Instagram個人資料頁面並處理初始彈窗"""
    try:
        # 訪問個人資料頁面
        driver.get(f"https://www.instagram.com/{profile_name}/")
        print(f"成功訪問 {profile_name} 的個人資料頁面")
        
        # 等待頁面加載
        time.sleep(3)
        
        # 使用JavaScript方法處理彈窗
        handle_popups_with_js(driver)
        
        return True
    except Exception as e:
        print(f"訪問個人資料頁面失敗: {e}")
        return False

def handle_popups_with_js(driver):
    """使用JavaScript方法處理Instagram彈窗"""
    print("正在使用JavaScript方法處理彈窗...")
    
    # 方法1: 使用JS查找所有關閉按鈕並點擊
    js_find_close_buttons = """
    function findCloseButtons() {
        // 查找所有包含"關閉"或"Close"的按鈕和SVG
        const svgButtons = Array.from(document.querySelectorAll('svg[aria-label="關閉"], svg[aria-label="Close"]'));
        const closeButtons = Array.from(document.querySelectorAll('button[aria-label*="Close"], button[aria-label*="關閉"]'));
        
        // 將SVG元素轉換為它們的父按鈕
        const svgParents = svgButtons.map(svg => {
            // 向上查找最近的按鈕或可點擊元素
            let parent = svg.parentElement;
            while (parent && parent.tagName !== 'BUTTON' && parent.tagName !== 'A' && !parent.onclick) {
                parent = parent.parentElement;
            }
            return parent || svg.parentElement;
        });
        
        // 合併所有找到的按鈕
        return [...closeButtons, ...svgParents].filter(el => el);
    }
    
    // 查找並點擊關閉按鈕
    const buttons = findCloseButtons();
    if (buttons.length > 0) {
        console.log('找到', buttons.length, '個關閉按鈕');
        for (let i = 0; i < buttons.length; i++) {
            try {
                buttons[i].click();
                console.log('成功點擊按鈕:', i);
                return true;
            } catch (e) {
                console.log('點擊失敗:', e);
            }
        }
    } else {
        console.log('未找到關閉按鈕');
    }
    return false;
    """
    
    try:
        result = driver.execute_script(js_find_close_buttons)
        if result:
            print("JavaScript成功點擊了關閉按鈕")
            time.sleep(1)
            return True
    except Exception as e:
        print(f"JavaScript點擊失敗: {e}")
    
    # 方法2: 使用JS直接點擊特定類別的元素
    js_click_by_attributes = """
    // 嘗試點擊符合特定屬性的元素
    function clickElementsByAttributes() {
        // 嘗試通過各種屬性和類名查找關閉按鈕
        const selectors = [
            'svg[aria-label="關閉"]',
            'svg[aria-label="Close"]',
            'button[aria-label*="Close"]',
            'button[aria-label*="關閉"]',
            'div.x6s0dn4 svg',
            'div.x78zum5 svg',
            'div[role="dialog"] button svg',
            '[aria-role="presentation"] button'
        ];
        
        for (const selector of selectors) {
            const elements = document.querySelectorAll(selector);
            for (const el of elements) {
                try {
                    // 嘗試點擊元素或其父元素
                    if (el.tagName === 'BUTTON' || el.onclick) {
                        el.click();
                        return true;
                    } else if (el.parentElement) {
                        // 如果元素不是按鈕，嘗試點擊其父元素
                        el.parentElement.click();
                        return true;
                    }
                } catch (e) {
                    console.log('點擊失敗:', e);
                }
            }
        }
        return false;
    }
    
    return clickElementsByAttributes();
    """
    
    try:
        result = driver.execute_script(js_click_by_attributes)
        if result:
            print("JavaScript成功通過屬性點擊了關閉按鈕")
            time.sleep(1)
            return True
    except Exception as e:
        print(f"JavaScript點擊失敗: {e}")
    
    # 方法3: 使用更激進的方法 - 移除所有彈窗
    js_remove_dialogs = """
    // 嘗試移除所有可能的彈窗元素
    function removeDialogs() {
        // 查找可能的對話框/彈窗元素
        const dialogSelectors = [
            'div[role="dialog"]',
            'div[role="presentation"]',
            'div.x1n2onr6.x1iorvi4',
            'div.x78zum5.xdt5ytf.x1n2onr6'
        ];
        
        let removed = false;
        
        for (const selector of dialogSelectors) {
            const dialogs = document.querySelectorAll(selector);
            for (const dialog of dialogs) {
                // 檢查這是否像是一個模態窗口或彈窗
                if (dialog.offsetWidth > 100 && dialog.offsetHeight > 100) {
                    dialog.remove();
                    removed = true;
                    console.log('已移除彈窗元素');
                }
            }
        }
        
        // 移除任何可能的覆蓋層
        const overlays = document.querySelectorAll('.x1n2onr6, .x9f619');
        for (const overlay of overlays) {
            if (overlay.style.position === 'fixed' || 
                window.getComputedStyle(overlay).position === 'fixed') {
                overlay.style.display = 'none';
                removed = true;
                console.log('已隱藏覆蓋層');
            }
        }
        
        return removed;
    }
    
    return removeDialogs();
    """
    
    try:
        result = driver.execute_script(js_remove_dialogs)
        if result:
            print("JavaScript成功移除了彈窗元素")
            time.sleep(1)
            return True
    except Exception as e:
        print(f"JavaScript移除彈窗失敗: {e}")
    
    # 備用方法: 使用Selenium的方法
    print("嘗試使用Selenium方法...")
    return handle_close_buttons_selenium(driver)

def handle_close_buttons_selenium(driver):
    """使用Selenium方法處理各種關閉按鈕"""
    print("使用Selenium方法尋找並處理關閉按鈕...")
    
    # 定義多個選擇器來查找關閉按鈕
    close_button_selectors = [
        "//button[contains(@aria-label, 'Close')]",
        "//button[.//svg[contains(@aria-label, 'Close')]]",
        "//div[contains(@class, 'x6s0dn4')]//svg[contains(@aria-label, '關閉') or contains(@aria-label, 'Close')]",
        "//div[contains(@class, 'x6s0dn4') and contains(@class, 'x78zum5')]//svg",
        "//div[contains(@role, 'dialog')]//button[.//svg]",
        "//svg[@aria-label='關閉']/parent::*",
        "//svg[contains(@aria-label, '關閉')]/parent::button",
        "//div[contains(@class, 'x6s0dn4')]//svg/parent::*"
    ]
    
    for selector in close_button_selectors:
        try:
            close_buttons = driver.find_elements(By.XPATH, selector)
            
            if close_buttons:
                print(f"找到 {len(close_buttons)} 個可能的關閉按鈕")
                
                # 嘗試點擊每個按鈕直到有一個成功
                for i, btn in enumerate(close_buttons):
                    try:
                        # 確保按鈕可見
                        driver.execute_script("arguments[0].scrollIntoView(true);", btn)
                        time.sleep(0.5)
                        
                        # 嘗試使用JavaScript點擊，這對於隱藏/覆蓋元素更可靠
                        print(f"嘗試點擊第 {i+1} 個關閉按鈕...")
                        driver.execute_script("arguments[0].click();", btn)
                        print(f"成功點擊關閉按鈕！")
                        time.sleep(1)  # 等待查看操作是否產生效果
                        return True
                    except Exception as e:
                        print(f"點擊按鈕失敗，錯誤: {e}")
                        continue
        except Exception as e:
            print(f"使用選擇器 {selector} 查找關閉按鈕時出錯: {e}")
            continue
    
    print("未找到可點擊的關閉按鈕")
    return False

def open_first_post(driver):
    """嘗試打開第一篇貼文"""
    print("嘗試打開第一篇貼文...")
    
    # 使用JavaScript找到並點擊第一篇貼文
    js_open_first_post = """
    function findFirstPost() {
        // 嘗試各種可能的選擇器來找到第一篇貼文
        const selectors = [
            'article a', 
            'div._aagu a', 
            'div.x1iyjqo2 a', 
            'div[role="tablist"] + div a',
            'a[href*="/p/"]',
            'a[href*="/reel/"]'
        ];
        
        for (const selector of selectors) {
            const posts = document.querySelectorAll(selector);
            if (posts && posts.length > 0) {
                // 確保我們找到的是一個帖子鏈接
                for (const post of posts) {
                    if (post.href && (post.href.includes('/p/') || post.href.includes('/reel/'))) {
                        post.scrollIntoView({behavior: 'smooth', block: 'center'});
                        setTimeout(() => post.click(), 500);
                        return true;
                    }
                }
            }
        }
        return false;
    }
    
    return findFirstPost();
    """
    
    try:
        time.sleep(3)  # 確保頁面完全加載
        result = driver.execute_script(js_open_first_post)
        if result:
            print("JavaScript成功點擊了第一篇貼文")
            time.sleep(3)  # 等待貼文打開
            return True
        else:
            print("JavaScript未找到第一篇貼文，嘗試使用Selenium方法")
            return selenium_open_first_post(driver)
    except Exception as e:
        print(f"JavaScript打開貼文失敗: {e}")
        return selenium_open_first_post(driver)

def selenium_open_first_post(driver):
    """使用Selenium方法嘗試打開第一篇貼文"""
    try:
        # 等待一下確保頁面加載完成
        time.sleep(3)
        
        # 嘗試多個選擇器找到第一篇貼文
        selectors = [
            "//div[contains(@class, '_ac7v')]//a",
            "//div[contains(@class, 'x1iyjqo2')]//a",
            "//article//div[contains(@class, '_aagu')]",
            "//div[@role='tablist']/following-sibling::div//a",
            "//article//a[contains(@href, '/p/') or contains(@href, '/reel/')]",
            "//a[contains(@href, '/p/')]",
            "//a[contains(@href, '/reel/')]"
        ]
        
        for selector in selectors:
            try:
                posts = driver.find_elements(By.XPATH, selector)
                if posts:
                    for post in posts:
                        try:
                            # 滾動到元素
                            driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", post)
                            time.sleep(1)
                            
                            # 點擊帖子
                            driver.execute_script("arguments[0].click();", post)
                            print(f"成功點擊第一篇貼文！")
                            time.sleep(3)  # 等待貼文打開
                            return True
                        except Exception as e:
                            print(f"點擊帖子失敗: {e}")
                            continue
            except Exception:
                continue
        
        print("無法找到並點擊第一篇貼文")
        return False
    except Exception as e:
        print(f"嘗試打開第一篇貼文時出錯: {e}")
        return False

def main():
    # 目標個人資料
    profile_name = "hoyu_professional"
    
    # 設置WebDriver
    driver = setup_driver()
    driver.maximize_window()  # 最大化窗口以便更容易找到元素
    
    try:
        # 訪問Instagram個人資料頁面並處理初始彈窗
        success = access_instagram_profile(driver, profile_name)
        
        if success:
            print("\n")
            print("="*50)
            print(f"已成功訪問 {profile_name} 的個人資料頁面並處理初始彈窗")
            
            # 添加選項讓使用者選擇是否要打開第一篇貼文
            choice = input("是否要嘗試打開第一篇貼文？(y/n): ")
            if choice.lower() == 'y':
                post_success = open_first_post(driver)
                if post_success:
                    print("成功打開第一篇貼文！")
                else:
                    print("無法打開第一篇貼文")
            
            print("您現在可以查看網頁！")
            print("="*50)
            
            # 保持瀏覽器打開一段時間以便查看結果
            input("按Enter鍵關閉瀏覽器...")
        else:
            print("無法完成指定操作")
        
    except Exception as e:
        print(f"發生錯誤: {e}")
    
    finally:
        # 關閉瀏覽器
        print("正在關閉瀏覽器...")
        driver.quit()

if __name__ == "__main__":
    main()