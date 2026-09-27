import os
import glob
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# 1. பழைய தற்காலிக பைல்களை நீக்கும் லாஜிக்
def clean_download_folder(download_dir):
    if not os.path.exists(download_dir):
        os.makedirs(download_dir)
        return
    for file in glob.glob(os.path.join(download_dir, '*')):
        try:
            os.remove(file)
        except Exception:
            pass
    print("பழைய பைல்கள் நீக்கப்பட்டு போல்டர் தயாராக உள்ளது.\n")

def run_automation():
    chrome_options = Options()
    
    # Page load strategy: HTML கிடைத்தவுடனே இயங்கத் தொடங்கும்
    chrome_options.page_load_strategy = 'eager' 
    
    # PythonAnywhere-க்கான Headless மற்றும் மெமரி அமைப்புகள்
    chrome_options.add_argument("--headless") 
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu") 
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--disable-software-rasterizer")
    
    # பிரவுசரை சாதாரண Windows கம்ப்யூட்டர் போல காட்ட User-Agent
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

    # tngscsteta அக்கவுண்டில் உள்ள டவுன்லோடு போல்டர் பாத்
    download_dir = "./downloads"
    clean_download_folder(download_dir)

    prefs = {'download.default_directory': download_dir}
    chrome_options.add_experimental_option('prefs', prefs)

    # Service-ஐ வெளிப்படையாகக் கொடுத்து பிரவுசரை துவக்குதல்
    try:
        service = Service("/usr/local/bin/chromedriver") 
        driver = webdriver.Chrome(service=service, options=chrome_options)
    except Exception:
        driver = webdriver.Chrome(options=chrome_options)
    
    # Angular தளம் லோட் ஆக 40 வினாடிகள் காத்திருப்பு
    wait = WebDriverWait(driver, 40)
    
    try:
        # ==========================================
        # STEP 1: EMIS தளத்தில் லாகின் செய்து டவுன்லோடு செய்தல்
        # ==========================================
        print("EMIS தளத்தில் லாகின் செய்யப்படுகிறது...")
        driver.get("https://tnemis.tnschools.gov.in/auth/login") 
        
        # [முக்கிய மாற்றம்]: HTML ID-ஐ பயன்படுத்தி பெட்டிகள் திரையில் தோன்றும் வரை காத்திருத்தல்
        username_box = wait.until(EC.visibility_of_element_located((By.ID, "exampleInputEmail1")))
        username_box.clear()
        username_box.send_keys("21406834")
        
        password_box = wait.until(EC.visibility_of_element_located((By.ID, "exampleInputPassword1")))
        password_box.clear()
        password_box.send_keys("Msms@2716")
        
        submit_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Login') or @type='submit']")))
        
        # Headless-ல் பட்டன் சரியாக அழுத்தப்படுவதை உறுதி செய்ய JavaScript Click
        driver.execute_script("arguments[0].click();", submit_btn)
        
        print("லாகின் பட்டன் அழுத்தப்பட்டது! லோட் ஆக காத்திருக்கிறது...")
        time.sleep(5) 
        
        print("டவுன்லோடு பக்கத்திற்குச் செல்லப்படுகிறது...")
        driver.get("https://tnemis.tnschools.gov.in/downloads")
        time.sleep(3)
        
        dropdown_elem = wait.until(EC.presence_of_element_located((By.ID, "report_level")))
        dropdown = Select(dropdown_elem)
        dropdown.select_by_visible_text("Profile Validation Reports")
        time.sleep(3)
        
        print("ரிப்போர்ட்டுகள் டவுன்லோடு செய்யப்படுகின்றன...")
        for row in [2, 3, 4, 5]:
            download_btn = wait.until(EC.element_to_be_clickable((By.XPATH, f"//table/tbody/tr[{row}]/td[5]/a")))
            download_btn.click()
            time.sleep(8) 
            
        print("4 ரிப்போர்ட்டுகளும் tngscsteta சர்வரில் வெற்றிகரமாக டவுன்லோடு செய்யப்பட்டன.\n")

        # ==========================================
        # STEP 2: Thamaraiselvan தளத்தில் பதிவேற்றம் செய்தல்
        # ==========================================
        print("Thamaraiselvan Django தளத்தில் பைல்களை பதிவேற்றும் பணி துவங்குகிறது...")

        downloaded_files = glob.glob(os.path.join(download_dir, '*'))
        
        file_mapping = {
            "Primary_Stu_profile_validation_rpt": {"path": "", "id": "file_primary"},
            "Middle_Stu_profile_validation_rpt": {"path": "", "id": "file_middle"},
            "High_Stu_profile_validation_rpt": {"path": "", "id": "file_high"},
            "Hr_Sec_Stu_profile_validation_rpt": {"path": "", "id": "file_hrsec"}
        }

        for file in downloaded_files:
            for key in file_mapping:
                if key in file:
                    file_mapping[key]["path"] = file
        
        if all(val["path"] for val in file_mapping.values()):
            
            for file_type, info in file_mapping.items():
                driver.get("https://thamaraiselvan.pythonanywhere.com/aadhaar_emis/")
                time.sleep(3) 
                
                input_element = wait.until(EC.presence_of_element_located((By.ID, info["id"])))
                input_element.send_keys(info["path"])
                
                upload_btn = driver.find_element(By.XPATH, f"//input[@id='{info['id']}']/ancestor::form//button[@type='submit']")
                upload_btn.click()
                
                short_name = file_type.split('_')[0]
                print(f"-> {short_name} Schools பைல் பதிவேற்றப்பட்டது.")
                time.sleep(5) 

            print("\nஅனைத்து பைல்களையும் Merge செய்யும் பணி துவங்குகிறது...")
            driver.get("https://thamaraiselvan.pythonanywhere.com/aadhaar_emis/")
            time.sleep(3)
            
            merge_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Merge All 4 Files') or contains(., 'Merge')]")))
            driver.execute_script("arguments[0].click();", merge_btn)
            time.sleep(10) 
            
            print("வெற்றி! அனைத்து பைல்களும் Thamaraiselvan தளத்தில் பதிவேற்றப்பட்டு வெற்றிகரமாக Merge செய்யப்பட்டுவிட்டது.")
            
        else:
            print("பிழை: 4 பைல்களும் முழுமையாக டவுன்லோடு ஆகவில்லை அல்லது பெயர்கள் பொருந்திப் போகவில்லை.")
            
    except Exception as e:
        # பிழை ஏற்பட்டால் HTML-ஐ சேமிக்கும் லாஜிக்
        print(f"\nஏதோ பிழை ஏற்பட்டுள்ளது: {type(e).__name__}")
        try:
            html_content = driver.page_source
            with open("/home/tngscsteta/emis_error_page.html", "w", encoding="utf-8") as f:
                f.write(html_content)
            print("உங்களின் Files பகுதியில் 'emis_error_page.html' என்ற பைல் உருவாக்கப்பட்டுள்ளது. அதில் பிழைக்கான காரணம் இருக்கும்.")
            driver.save_screenshot("/home/tngscsteta/emis_error_screenshot.png")
        except Exception:
            pass
    finally:
        try:
            driver.quit()
        except Exception:
            pass

if __name__ == "__main__":
    run_automation()
