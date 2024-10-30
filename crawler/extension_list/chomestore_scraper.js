const puppeteer = require('puppeteer');
const categories = require('./config/category');
const fs = require('fs');
const path = require('path');
const sleep = ms => new Promise(res => setTimeout(res, ms));

const IS_TEST = !!process.env.TEST


class ItemPool {
    constructor() {
        this.items = [];
        this.itemMap = {};
    }

    reset() {
        this.items = [];
        this.itemMap = {};
    }

    batchAdd(items) {
        let added = 0;
        let skipped = 0;
        for (let i = 0; i < items.length; i++) {
            const item = items[i];
            if (this.add(item)) {
                added++;
            } else {
                skipped++;
            }
        }
        return {
            added,
            skipped,
            poolSize: this.items.length,
        }
    }

    add(item) {
        if (this.itemMap[item.id]) {
            this.itemMap[item.id]++;
            return false;
        }
        this.itemMap[item.id] = 1;
        this.items.push(item);
        return true;
    }

    dump() {
        return this.items;
    }

    save() {
        saveItemsToFile(this.dump())
    }
}
const itemPool = new ItemPool();

async function scrapeChromeCommunicationExtensions(url) {
    const browser = await puppeteer.launch({
        headless: false,
        args: ["--proxy-server=http://127.0.0.1:7890"]
    });
    const page = await browser.newPage();
    // const url = 'https://chromewebstore.google.com/category/extensions/productivity/communication';

    await page.goto(url, { waitUntil: 'networkidle0' });

    let hasMoreItems = true;
    // const extractedItems = [];
    
    let pageNum = 0;
    let lastItemCount = 0;
    let noNewItemTime = 0;
    itemPool.reset();

    while (hasMoreItems) {
        // Wait for the items to load
        await page.waitForSelector('[data-item-id]', { visible: true });
        console.log(`page ${pageNum++} ${lastItemCount} start`);


        // parse items
        const parseInfo = await page.evaluate(({ lastItemCount, itemPool }) => {
            const elements = document.querySelectorAll('[data-item-id]');
            const items = []
            for (let i = lastItemCount; i < elements.length; i++) {
                const elem = elements[i];
                const id = elem.getAttribute('data-item-id');
                const href = elem.firstElementChild.getAttribute('href');
                // itemPool.add({
                //     id: id,
                //     href: href,
                // })
                items.push({
                    id: id,
                    href: href,
                })
            }
            return {
                items: items,
                start: lastItemCount,
                end: elements.length,
            }
        }, {
            lastItemCount,
            itemPool,
        })

        // check if items are already scraped
        lastItemCount = parseInfo.end
        const addedInfo = itemPool.batchAdd(parseInfo.items)
        if (addedInfo.skipped === 32  ) {
            noNewItemTime++;
        } else if (addedInfo.added > 0) {
            noNewItemTime = 0;
        }
        console.log(parseInfo.items.map(item => item.id.slice(0, 6)).join(","))
        console.log(addedInfo, 'start: ', parseInfo.start, 'end: ', parseInfo.end)


        // Scroll to bottom
        await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight));
        await sleep(1000);
        // await page.waitForTimeout(2000); // Wait for potential new content to load

        // Check if "Show more" button exists and click it
        const showMoreButton = await page.$('.mUIrbf-LgbsSe');

        if (!IS_TEST && showMoreButton && noNewItemTime < 5) {
            // await showMoreButton.click();
            await showMoreButton.evaluate(b => b.click());
            await sleep(2000);
            // await page.waitForTimeout(2000); // Wait for new items to load
        } else {
            hasMoreItems = false;
        }
    }

    // Extract current items
    await browser.close();
    return itemPool.dump();
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

    // for (const task of tasks) {
    //     console.log(`start scraping ${task.category} ${task.subCategory}`)
    //     await scrapeCategory(task.category, task.subCategory);
    // }

    await scrapeCategory('lifestyle', 'well_being')
}

doScrape();

async function scrapeCategory(category, subCategory) {
    const url = `https://chromewebstore.google.com/category/extensions/${category}/${subCategory}`
    console.log(`start scraping ${url}`)
    const startAt = formatTime(new Date(), 'YYYY-MM-DD HH:mm:ss');

    await scrapeChromeCommunicationExtensions(url)
        .then(items => {
            // console.log(JSON.stringify(items, null, 2))
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
    const filename = category ? `${category}_${subCategory}_${formattedTime}.json` : `default.json`;
    const filePath = path.join(dataDir, filename);

    // Write items to file
    try {
        fs.writeFileSync(filePath, JSON.stringify(data, null, 2));
        console.log(`Successfully saved ${data.length || data.items.length} items to ${filename}`);
    } catch (err) {
        console.error(`Error writing file ${filename}:`, err);
    }
}

// Handle ^C
process.on('SIGINT', () => {
    itemPool.save()
    process.exit(0)
});