const { launch } = require('puppeteer');
const puppeteer = require('puppeteer');

(async () => {
  const browser = await puppeteer.launch();
  const page = await browser.newPage();
  await page.goto('https://www.mtickets.com/');


  let event_link_res = /https:\/\/www.mtickets.com\/buy\/[\w\d/-]+/;
  var page_links = await page.$$eval('li > a[href]', event_links => event_links.map(event_link => event_link.href));
  
  //   get all event links
    let event_links = page_links.filter(link => Boolean(link.match(event_link_res)));

    event_links.forEach(async (element) => {
      await page.goto(element)
      
    });



  console.log(event_links);
  await browser.close();
})();