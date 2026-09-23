# Railroad volume data scraping

Python scripts for collecting weekly CSX rail volume reports, extracting PDF tables, and plotting the results. This is an exploratory project from 2022.

## What is here

- [rram_webscrape.py](rram_webscrape.py): find report links, extract tables, clean values, and plot data.
- [0000rram_webscrape.py](0000rram_webscrape.py): another working version with additional plotting functions and a 2022 example.
- The PNG files are saved output from the original work. The text copies are older working copies.

The scripts use Selenium and Beautiful Soup to find reports, `tabula-py` to extract PDF tables, pandas to organize the data, and Matplotlib for plots.

## Example output

![Saved railroad volume plot from the original project](line_plot_.png)

This is a historical output image, not a live data feed.

## Running it again

This snapshot needs setup changes before a fresh run:

1. Create a Python environment and install the imported libraries: Selenium, Beautiful Soup, requests, pandas, Matplotlib, PyPDF2, and `tabula-py`. PDF extraction through `tabula-py` also needs Java.
2. Replace the absolute ChromeDriver path in the script with a path appropriate for your machine, or update the Selenium setup.
3. Recheck the source page selectors and PDF table coordinates. Both depend on the report layout used in 2022.
4. Review the example at the bottom before running a script; it opens a browser and makes network requests.

There is no pinned, verified environment or automated test suite yet.

## Next steps

Choose one main script, save a sample PDF for repeatable extraction checks, and add tests for numeric cleanup and missing tables.

The original scraping reference is credited in the source: [How to scrape PDF files from a website](https://www.geeksforgeeks.org/how-to-scrape-all-pdf-files-in-a-website/).
