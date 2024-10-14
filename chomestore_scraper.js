const puppeteer = require('puppeteer');

const sleep = ms => new Promise(res => setTimeout(res, ms));

async function scrapeChromeCommunicationExtensions() {
    const browser = await puppeteer.launch({
        headless: false,
        args: ["--proxy-server=http://127.0.0.1:7890"]
    });
    const page = await browser.newPage();
    const url = 'https://chromewebstore.google.com/category/extensions/productivity/communication';

    await page.goto(url, { waitUntil: 'networkidle0' });

    let hasMoreItems = true;
    const extractedItems = [];

    while (hasMoreItems) {
        // Wait for the items to load
        await page.waitForSelector('[data-item-id]', { visible: true });

        // Extract current items
        const newItems = await page.evaluate(() => {
            const items = document.querySelectorAll('[data-item-id]');


            return Array.from(items).map(item => {
                const titleElem = item.querySelector('[role="heading"]')
                const parent = titleElem.parentElement
                return ({
                    image: titleElem.previousSibling.src.trim(),
                    title: titleElem.innerText,
                    description: parent.lastChild.textContent.trim()
                    // description: item.querySelector('div[class*="e3ZUqe"]')?.textContent.trim(),
                    // rating: item.querySelector('div[aria-label*="Rated"]')?.getAttribute('aria-label'),
                    // users: item.querySelector('div[class*="e3ZUqe"] + div')?.textContent.trim()
                })
            
            });
        });
        console.log(newItems.length);

        extractedItems.push(...newItems);

        // Scroll to bottom
        await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight));
        await sleep(2000);
        // await page.waitForTimeout(2000); // Wait for potential new content to load

        // Check if "Show more" button exists and click it
        const showMoreButton = await page.$('button[jsaction*="show-more-items"]');
        if (showMoreButton) {
            await showMoreButton.click();
            await page.waitForTimeout(2000); // Wait for new items to load
        } else {
            hasMoreItems = false;
        }
    }

    await browser.close();
    return extractedItems;
}

scrapeChromeCommunicationExtensions()
    .then(items => console.log(JSON.stringify(items, null, 2)))
    .catch(error => console.error('Scraping failed:', error));