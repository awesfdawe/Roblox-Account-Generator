import os
import random
import string
from rich.console import Console
from rich.prompt import IntPrompt
from playwright.sync_api import sync_playwright

console = Console()


def generate_password(length=20):
    alphabet = string.ascii_letters + string.digits + string.punctuation
    return ''.join(random.choice(alphabet) for _ in range(length))


def generate_nickname():
    # Generates a random nickname by combining a word from the file with a random number
    try:
        with open('nicknames.txt', 'r') as file:
            words = [line.strip() for line in file.readlines()]
            return random.choice(words) + str(random.randint(10000, 999999))
    except FileNotFoundError:
        console.log('[bold red]Error:[/] nicknames.txt file not found!')
        console.print('[bold]Press enter to exit...[/]')
        console.input()
        exit()


def clear():
    # Clears the console screen and adds the name at the beginning
    os.system('cls' if os.name == 'nt' else 'clear')
    console.rule('[bold red]Roblox Account Generator[/]')


def registration():
    with sync_playwright() as pw:
        nickname = generate_nickname()
        password = generate_password()
        browser = pw.firefox.launch(headless=False)  # * Don't try to use chromium browsers because they got detected by roblox as bot.
        context = browser.new_context()
        page = context.new_page()
        page.set_viewport_size({"width": 640, "height": 480})
        page.route('https://apis.roblox.com/universal-app-configuration/v1/behaviors/cookie-policy/content', lambda route: route.abort()) # Blocks cookies banner
        page.goto('https://www.roblox.com')
        page.locator('//*[@id="MonthDropdown"]').select_option('January')
        page.locator('//*[@id="DayDropdown"]').select_option('01')
        page.locator('//*[@id="YearDropdown"]').select_option('1999')
        
        while True:
            # Checks username valid
            with page.expect_response('https://auth.roblox.com/v1/usernames/validate') as username_validate:
                page.locator('//*[@id="signup-username"]').fill(nickname)
            if username_validate.value.json().get('code') == 0:
                break
            else:
                nickname = generate_nickname()

        page.locator('//*[@id="signup-password"]').fill(password)
        page.locator('//*[@id="MaleButton"]').click()

        with page.expect_response('https://auth.roblox.com/v2/signup') as signup_validate:
            page.locator('//*[@id="signup-button"]').click(timeout=0)
        if signup_validate.value.status == 429:
            browser.close()
            console.log('[bold red]Error:[/] too many requests! Try to change your IP (you can use VPN, preferably paid)')
            console.print('[bold]Press enter to continue...[/]')
            console.input()
            return None
        else:
            with page.expect_response('https://client-api.arkoselabs.com/fc/gt2/public_key/**') as signup_validate:
                pass
            if signup_validate.value.ok:
                page.wait_for_url('https://www.roblox.com/home?nu=true', timeout=0)
            else:
                browser.close()
                console.log('[bold red]Error:[/] Unknown error! Try to change your IP (you can use VPN, preferably paid)')
                console.print('[bold]Press enter to continue...[/]')
                console.input()
                return None

        with open('cookies.txt', 'a') as file:
            cookies = context.cookies()
            roblosecurity_cookie = next((cookie for cookie in cookies if cookie['name'] == '.ROBLOSECURITY'),None)  # Finds .ROBLOSECURITY cookies
            if roblosecurity_cookie:
                roblos_data_value = roblosecurity_cookie['value']
                file.write(f'{roblos_data_value}\n')

        with open('accounts.txt', 'a') as file:
            file.write(f'{nickname}:{password}\n')
        console.log('[bold green]Account generated successfully[/]', ':white_check_mark:')
        browser.close()
        return None


def main():
    try:
        clear()
        amount = IntPrompt.ask('Enter how many accounts to generate')
        clear()
        for _ in range(amount):
            with console.status('Generating...', spinner='line'):
                registration()
    except BaseException:
        pass

if __name__ == '__main__':
    main()
