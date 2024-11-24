import playwright
from playwright.sync_api import sync_playwright
import time
import logging
from tqdm import tqdm
import json
import sys

logging.basicConfig(
    format='%(asctime)s - %(message)s', level=logging.INFO, datefmt='%H:%M:%S'
)


def load_words(dictionary_path='words2.txt', min_length=4, min_unique_letters=4):
    with open(dictionary_path, 'r', encoding='utf-8') as file:
        return {
            word
            for line in file
            for word in [line.strip().lower()]
            if len(word) >= min_length
            and word.isalpha()
            and len(set(word)) >= min_unique_letters
        }


def monitor_progress(page):
    current_title = page.locator('.current-title').text_content()
    next_left = page.locator('.next-left').text_content()
    next_title = page.locator('.next-title').text_content()
    return current_title, next_left, next_title


def setup_progress_monitoring(page):
    page.evaluate(
        """() => {
        const progressDiv = document.querySelector('.block-progress__text');
        if (!progressDiv) return;
        let lastUpdate = '';

        const observer = new MutationObserver((mutations) => {
            const currentTitle = document.querySelector('.current-title')?.textContent;
            const nextLeft = document.querySelector('.next-left')?.textContent;
            const nextTitle = document.querySelector('.next-title')?.textContent;

            const update = JSON.stringify({currentTitle, nextLeft, nextTitle});
            if (update !== lastUpdate) {
                lastUpdate = update;
                const event = new CustomEvent('progressUpdate', {
                    detail: {currentTitle, nextLeft, nextTitle}
                });
                document.dispatchEvent(event);
            }
        });

        observer.observe(progressDiv, {
            childList: true,
            characterData: true,
            subtree: true
        });
    }"""
    )


def solve_spelling_bee():
    all_words = load_words()

    with sync_playwright() as p:
        mobile_config = {
            'viewport': {'width': 380, 'height': 800},
            'device_scale_factor': 3,
            'is_mobile': True,
            'has_touch': True,
            'user_agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/604.1',
        }

        context = p.chromium.launch(headless=True).new_context(**mobile_config)
        page = context.new_page()
        page.goto('https://spellbee.org/unlimited')
        page.wait_for_selector('#hexGrid', state='visible', timeout=10_000)
        time.sleep(1)

        setup_progress_monitoring(page)

        page.evaluate(
            """() => {
            document.addEventListener('progressUpdate', (event) => {
                console.log('PROGRESS_UPDATE:' + JSON.stringify(event.detail));
            });
        }"""
        )

        current_title, next_left, next_title = monitor_progress(page)

        center = page.locator('#center-letter p').text_content().lower()
        letters = {p.text_content().lower() for p in page.locator('#hexGrid p').all()}
        letters_set = letters | {center}

        valid_words = []
        pangrams = []

        for word in all_words:
            if center in word and not (word_set := set(word)) - letters_set:
                if word_set >= letters:
                    pangrams.append(word)
                else:
                    valid_words.append(word)

        sorted_words = sorted(pangrams, key=len, reverse=True) + sorted(
            valid_words, key=len, reverse=True
        )
        found_words = len(sorted_words)

        print(f'Center letter: {center.upper()}')
        print(f'All letters: {", ".join(sorted(l.upper() for l in letters))}')
        print(f'Found {found_words} valid words ({len(pangrams)} pangrams)')
        print("\033[?25l")  # Hide cursor
        print(f"{current_title} - {next_left} points to {next_title}")

        submit_button = page.locator('#submit_button')
        pbar = tqdm(sorted_words, desc='Trying words', ncols=80, leave=False)

        def handle_console(msg):
            if msg.text.startswith('PROGRESS_UPDATE:'):
                status = json.loads(msg.text.replace('PROGRESS_UPDATE:', ''))
                sys.stdout.write("\033[F\033[K")  # Move up and clear line
                sys.stdout.write(
                    f"{status['currentTitle']} - {status['nextLeft']} points to {status['nextTitle']}\n"
                )
                sys.stdout.flush()

        page.on("console", handle_console)

        try:
            for word in pbar:
                page.keyboard.type(word)

                if submit_button.is_visible():
                    submit_button.click()

                for _ in range(len(word)):
                    page.keyboard.press('Backspace')

                time.sleep(0.05)
        finally:
            print("\033[?25h")  # Show cursor again
            pbar.close()

        input("\nPress Enter to close the browser...")
        context.close()


if __name__ == '__main__':
    try:
        start = time.time()
        solve_spelling_bee()
        logging.info(f"Completed in {time.time() - start:.1f}s")
    except playwright._impl._errors.TargetClosedError:
        logging.info("Browser closed by user")
