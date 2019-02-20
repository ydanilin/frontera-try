# Crawling Big Classified Ads Multipaged Portal with Frontera and Scrapy

Sometimes customers ask to extract data from websites, stuffed with tons of classifieds like companies advertisments, job offerings, goods listings etc. We call such websites Classified Ads Multipaged Portal and will name it here just **portal** for simplicity.

Often such portals have a **search** box in the main page, which leads you to **listing pages** when you enter a search criteria. Every classified ad on the listing (which we will refer as **item**) contains mostly brief information like name, address, web, which we need to scrape. Also, the customer may ask you to grab additional details from item **details page**, which you can get when you click on a classified ad.

## Problem Statement: Why do we need a "Job State Persistency" in our Scraper

If we’re talking about scraping a portal, which contains hundreds of thousands records, **it is unlikely that we will do all our job in a single session**. Several reasons may be for that – perhaps we want to inspect the portion of the data collected before proceeding further (which is definitely a good practice!) or we know that, if we exceed some amount of requests the site will temporary ban us so we need to stop and recharge the session after waiting some time, etc.

That is why we need to maintain persistency in our scraper - to be able to start exactly from the point where we finished before.

**After some experience with "handmade" solutions, we considered to use [Scrapinghub's open source](https://scrapinghub.com/open-source) [Frontera](https://github.com/scrapinghub/frontera) package, which does exactly what we need: keeps the scraping job state persistent in a database so we can keep calm that scraper will restart exactly from where it stopped and nothing will be missed.**

This repo is our experiments with the Frontera package.
See `Makefile` for commands how to start
