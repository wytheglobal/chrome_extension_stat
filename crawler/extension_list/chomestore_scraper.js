const puppeteer = require('puppeteer');
const categories = require('./config/category');
const fs = require('fs');
const path = require('path');
const sleep = ms => new Promise(res => setTimeout(res, ms));

const IS_TEST = !!process.env.TEST

async function scrapeChromeCommunicationExtensions() {
    const browser = await puppeteer.launch({
        // headless: false,
        args: ["--proxy-server=http://127.0.0.1:7890"]
    });
    const page = await browser.newPage();
    const url = 'https://chromewebstore.google.com/category/extensions/productivity/communication';

    await page.goto(url, { waitUntil: 'networkidle0' });

    let hasMoreItems = true;
    // const extractedItems = [];
    // Wait for the items to load
    await page.waitForSelector('[data-item-id]', { visible: true });
    let pageNum = 0;

    while (hasMoreItems) {
        console.log(`page ${pageNum++} start`);
        // Scroll to bottom
        await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight));
        await sleep(200);
        // await page.waitForTimeout(2000); // Wait for potential new content to load

        // Check if "Show more" button exists and click it
        const showMoreButton = await page.$('.mUIrbf-LgbsSe');
        console.log(showMoreButton);
        if (!IS_TEST && showMoreButton) {
            // await showMoreButton.click();
            await showMoreButton.evaluate(b => b.click());
            await sleep(2000);
            // await page.waitForTimeout(2000); // Wait for new items to load
        } else {
            hasMoreItems = false;
        }
    }

    // Extract current items
    const extractedItems = await page.evaluate(() => {
        const items = document.querySelectorAll('[data-item-id]');


        return Array.from(items).map(item => {
            const titleElem = item.querySelector('[role="heading"]')
            const parent = titleElem.parentElement
            return ({
                title: titleElem.innerText,
                itemId: item.getAttribute('data-item-id'),
                detailUrl: parent.previousSibling.getAttribute('href'),
                // description: item.querySelector('div[class*="e3ZUqe"]')?.textContent.trim(),
                // rating: item.querySelector('div[aria-label*="Rated"]')?.getAttribute('aria-label'),
                // users: item.querySelector('div[class*="e3ZUqe"] + div')?.textContent.trim()
            })
        
        });
    });
    console.log(extractedItems.length);

    await browser.close();
    return extractedItems;
}



async function doScrape() {
    const tasks = []
    Object.keys(categories).forEach(category => {
        categories[category].forEach(subCategory => {
            tasks.push({
                category: category,
                subCategory: subCategory,
                url: `https://chromewebstore.google.com/category/extensions/${category}/${subCategory}`
            })
        });
    });

    for (const task of tasks.slice(0, 1)) {
        await scrapeCategory(task.category, task.subCategory);
    }
}

doScrape();

async function scrapeCategory(category, subCategory) {
    const url = `https://chromewebstore.google.com/category/extensions/${category}/${subCategory}`
    console.log(`start scraping ${url}`)
    const startAt = formatTime(new Date(), 'YYYY-MM-DD HH:mm:ss');

    scrapeChromeCommunicationExtensions()
        .then(items => {
            console.log(JSON.stringify(items, null, 2))
            saveItemsToFile({
                category: category,
                subCategory: subCategory,
                items: items,
                startAt: startAt,
                endAt: formatTime(new Date(), 'YYYY-MM-DD HH:mm:ss'),
            }, category, subCategory);
        })
        .catch(error => console.error('Scraping failed:', error));
}


// Function to format time with configurable parameters
function formatTime(date, format = 'HH-mm-zz') {
  let map = {}
  date && (map = {
    YYYY: date.getFullYear(),
    MM: String(date.getMonth() + 1).padStart(2, '0'),
    DD: String(date.getDate()).padStart(2, '0'),
    HH: String(date.getHours()).padStart(2, '0'),
    mm: String(date.getMinutes()).padStart(2, '0'),
    ss: String(date.getSeconds()).padStart(2, '0')
  })
  for (const key in map) {
    format = format.replace(key, map[key])
  }

  return format
}

function saveItemsToFile(data, category, subCategory) {
    // Generate filename with category, subCategory, and formatted timestamp
    const now = new Date();
    const formattedDate = formatTime(now, 'YYYY-MM-DD'); // YYYY-MM-DD

    // Create data directory if it doesn't exist
    const dataDir = path.join(process.cwd(), `data/extension_list/${formattedDate}`);
    if (!fs.existsSync(dataDir)) {
        fs.mkdirSync(dataDir, {recursive: true});
    }


    const formattedTime = formatTime(now, 'HH-mm-ss'); // User can configure the format here
    const filename = `${category}_${subCategory}_${formattedTime}.json`;
    const filePath = path.join(dataDir, filename);

    // Write items to file
    fs.writeFile(filePath, JSON.stringify(data, null, 2), (err) => {
        if (err) {
            console.error(`Error writing file ${filename}:`, err);
        } else {
            console.log(`Successfully saved ${data.items.length} items to ${filename}`);
        }
    });
}