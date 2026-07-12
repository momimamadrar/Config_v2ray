import os
import re
import base64
import requests

# لیست کانال‌های تلگرام (منبع اول)[span_0](start_span)[span_0](end_span)
TELEGRAM_CHANNELS = [
    "ARv2ray", "Awlix_ir", "azadi_az_inja_migzare", "BegzarProxy", "BestV2rang", "bright_vpn",
    "Capital_NET", "CloudCityy", "ConfigsHUB", "crgaming7", "customv2ray", "CUSTOMVPNSERVER",
    "DigiV2ray", "DirectVPN", "FalconPolV2rayNG", "flyv2ray", "fnet00", "FreakConfig",
    "free1_vpn", "free4allVPN", "free_v2rayn1", "free_v2rayyy", "frev2ray", "God_CONFIG",
    "hashmakvpn", "Helix_Servers", "Hope_Net", "INIT1984", "iP_CF", "ipV2Ray", "IRN_VPN",
    "iSegaro", "L_AGVPN13", "lightning6", "Lockey_vpn", "LoRd_uL4mo", "lrnbymaa", "MehradLearn",
    "melov2ray", "MsV2ray", "MTConfig", "NIM_VPN_ir", "oneclickvpnkeys", "Outline_Vpn",
    "Outlinev2rayNG", "OutlineVpnOfficial", "PAINB0Y", "Parsashonam", "polproxy", "PrivateVPNs",
    "Proxy_PJ", "proxystore11", "proxyymeliii", "prrofile_purple", "rayvps", "reality_daily",
    "Royalping_ir", "rxv2ray", "SafeNet_Server", "serveriran11", "ServerNett", "ShadowProxy66",
    "ShadowSocks_s", "shh_proxy", "shopingv2ray", "UnlimitedDev", "v2_team", "v2Line",
    "V2parsin", "V2pedia", "v2ray1_ng", "v2ray_outlineir", "v2ray_swhil", "v2ray_vpn_ir",
    "V2rayCollectorDonate", "v2rayng_config_amin", "V2rayng_Fast", "v2rayNG_Matsuri",
    "v2rayng_vpnrog", "V2rayNGmat", "V2rayNGn", "V2rayngninja", "v2rayngvpn", "V2RayTz",
    "vless_vmess", "VlessConfig", "vmess_vless_v2rayng", "vmessorg", "VmessProtocol",
    "VPNCLOP", "VPNCUSTOMIZE", "VpnFreeSec", "vpnmasi", "VpnProSec", "WebShecan", "XsV2ray",
    "yaney_01", "zen_cloud"
]

# لیست لینک‌های گیت‌هاب و منابع دیگر (منبع دوم)[span_1](start_span)[span_1](end_span)
URL_SOURCES = [
    "https://raw.githubusercontent.com/ShatakVPN/ConfigForge-V2Ray/main/configs/all.txt"
]

# تعریف فایل‌های خروجی و الگوهای شناسایی آن‌ها
OUTPUT_FILES = {
    "vmess.txt": [r"vmess://"],
    "vless.txt": [r"vless://(?!.*reality)"], # جلوگیری از تداخل vless معمولی با reality
    "trojan.txt": [r"trojan://"],
    "ss.txt": [r"ss://"],
    "tuic.txt": [r"tuic://"],
    "reality.txt": [r"vless://.*reality.*", r"reality://"], # تفکیک کانفیگ‌های ریالیتی
    "hysteria.txt": [r"hysteria://", r"hy2://"]
}

# دیکشنری برای نگهداری کانفیگ‌های یکتا
collected_configs = {file: set() for file in OUTPUT_FILES}

def decode_base64_safely(data):
    """تلاش برای دکود کردن رشته‌های Base64 احتمالی منابع"""
    try:
        missing_padding = len(data) % 4
        if missing_padding:
            data += '=' * (4 - missing_padding)
        return base64.b64decode(data).decode('utf-8', errors='ignore')
    except Exception:
        return data

def process_text_and_sort(text):
    """استخراج کانفیگ‌ها بر اساس پروتکل‌ها و قرار دادن در ست مربوطه"""
    # گشتن به دنبال هر چیزی که شبیه پروتکل پروکسی است
    pattern = r'(vmess|vless|ss|trojan|tuic|hysteria|hy2)://[^\s<>"]+'
    matches = re.findall(pattern, text, re.IGNORECASE)
    
    # پیدا کردن کل خط لینک برای بررسی دقیق‌تر
    full_links = re.findall(r'(?:vmess|vless|ss|trojan|tuic|hysteria|hy2)://[^\s<>"]+', text, re.IGNORECASE)
    
    for link in full_links:
        link_lower = link.lower()
        matched_any = False
        
        # اولویت سنجی برای تفکیک Reality از VLess معمولی
        if "reality" in link_lower:
            collected_configs["reality.txt"].add(link)
            continue
            
        for filename, regex_list in OUTPUT_FILES.items():
            if filename == "reality.txt":
                continue
            for r_pattern in regex_list:
                if re.search(r_pattern, link, re.IGNORECASE):
                    collected_configs[filename].add(link)
                    matched_any = True
                    break
            if matched_any:
                break

# ۱. دریافت اطلاعات از لینک‌های وب و گیت‌هاب
print("Starting to fetch from URL sources...")
for url in URL_SOURCES:
    try:
        response = requests.get(url, timeout=15)
        if response.status_code == 200:
            content = response.text
            process_text_and_sort(content)
            # بررسی اینکه آیا کل فایل base64 شده بوده یا نه
            decoded_content = decode_base64_safely(content)
            if decoded_content != content:
                process_text_and_sort(decoded_content)
    except Exception as e:
        print(f"Error fetching URL {url}: {e}")

# ۲. دریافت اطلاعات از پیش‌نمایش وب کانال‌های تلگرام
print("Starting to fetch from Telegram channels...")
for channel in TELEGRAM_CHANNELS:
    try:
        # استفاده از آدرس تگ /s/ برای دیدن پیش‌نمایش بدون نیاز به ادمین یا api تلگرام
        tg_url = f"https://t.me/s/{channel}"
        response = requests.get(tg_url, timeout=15)
        if response.status_code == 200:
            # اسکراپ کردن متن‌های داخل کد یا پیام‌ها
            process_text_and_sort(response.text)
    except Exception as e:
        print(f"Error scraping Telegram channel {channel}: {e}")

# ۳. ذخیره نتایج در فایل‌های مشخص شده
print("Saving configs into files...")
for filename, configs in collected_configs.items():
    # باز کردن فایل و نوشتن کانفیگ‌ها به صورت خط به خط
    with open(filename, "w", encoding="utf-8") as f:
        if configs:
            f.write("\n".join(sorted(list(configs))) + "\n")
        else:
            f.write("") # اگر کانفیگی نبود فایل خالی بماند
    print(f"Saved {len(configs)} unique configs to {filename}")

print("Done!")
