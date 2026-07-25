import os
import random
import re
import sys
import time
from datetime import datetime

from playwright.sync_api import sync_playwright

from Net2JSON import Netscape2json


def fetch_shipment(context, ref):
    page = context.new_page()
    paid_on = []
    shipment_completed = []
    order_completed = []
    for i in ref:
        page.goto("https://www.aliexpress.com/p/order/detail.html?orderId=" + i)
        container = page.locator(
            "div.order-detail-info-item.order-detail-order-info "
            "> div.order-detail-info-content.has-switch.expand-info"
        )
        divs = container.locator("> div")

        texts = []
        for i in range(1, 5):
            div = divs.nth(i)
            span_count = div.locator("span").count()
            full_text = div.inner_text()
            if span_count > 0:
                span_text = div.locator("span").first.inner_text()
                text_only = full_text.replace(span_text, "").strip()
            else:
                text_only = full_text.strip()
            texts.append(text_only)
        paid_on.append(texts[1])
        shipment_completed.append(texts[2])
        order_completed.append(texts[3])

    for i in sorted([i for i, val in enumerate(order_completed) if val == "PayPal"], reverse=True):
        del paid_on[i]
        del shipment_completed[i]
        del order_completed[i]
        del ref[i]
    
    paid_on_dt = [datetime.strptime(d, "%b %d, %Y") for d in paid_on]                        # noqa: DTZ007
    shipment_completed_dt = [datetime.strptime(d, "%b %d, %Y") for d in shipment_completed]  # noqa: DTZ007
    order_completed_dt = [datetime.strptime(d, "%b %d, %Y") for d in order_completed]        # noqa: DTZ007

    combined = list(zip(paid_on_dt, shipment_completed_dt, order_completed_dt))
    seen = set()
    keep_indices = []
    for i, triple in enumerate(combined):
        if triple not in seen:
            seen.add(triple)
            keep_indices.append(i)
    
    paid_on_dt = [paid_on_dt[i] for i in keep_indices]
    shipment_completed_dt = [shipment_completed_dt[i] for i in keep_indices]
    order_completed_dt = [order_completed_dt[i] for i in keep_indices]

    days_paid_to_shipment = [
        (ship - paid).days
        for paid, ship in zip(paid_on_dt, shipment_completed_dt)
    ]
    days_shipment_to_arrival = [
        (order - ship).days
        for ship, order in zip(shipment_completed_dt, order_completed_dt)
    ]
    return days_paid_to_shipment, days_shipment_to_arrival


def parse_shippments(browser, context):
    print("Parsing AE shipments...")
    page = context.new_page()
    page.goto("https://www.aliexpress.com/p/order/index.html")

    while page.get_by_role("button", name="View orders").is_visible():
        page.get_by_role("button", name="View orders").click()
        time.sleep(random.uniform(0.5, 1))

    status = [] # Status
    date = [] # Date
    price = [] # Price
    ref = [] # Ref. Numbers

    outer_container = page.locator(".comet-checkbox-group")
    cards = outer_container.locator("> div")

    count = cards.count()
    for i in range(count):
        card = cards.nth(i)
        child_divs = card.locator("> div")

        # Refunded
        if child_divs.count() != 3:
            continue

        first_div = child_divs.nth(0)
        inner_divs_of_first = first_div.locator("> div")  # 2a and 2b

        span_2a = inner_divs_of_first.nth(0).locator("span").first
        if span_2a.count() > 0:
            status.append(span_2a.inner_text())

        div_2b = inner_divs_of_first.nth(1)
        div_3 = div_2b.locator("> div").first
        div_4_children = div_3.locator("> div")

        if div_4_children.count() > 0:
            div_4a = div_4_children.nth(0)
            date.append(div_4a.inner_text())
            div_4b = div_4_children.nth(1)
            ref.append(div_4b.inner_text())
        
        third_div = child_divs.nth(2)
        inner_div_of_third = third_div.locator("> div").nth(1)
        div_3_children = inner_div_of_third.locator("> div")

        if div_3_children.count() > 0:
            div_3a = div_3_children.nth(0)
            span_3a = div_3a.locator("span").first
            if span_3a.count() > 0:
                price.append(span_3a.inner_text())
                
    if not status or not date or not price or not ref:
        print("No Items could be fetched")
        context.close()
        browser.close()
        sys.exit()

    if not (len(status) == len(date) == len(price) == len(ref)):
        print("Something went wrong while fetching, aborting")
        context.close()
        browser.close()
        sys.exit()

    for i in sorted([i for i, val in enumerate(status) if val != "Completed"], reverse=True):
        del status[i]
        del date[i]
        del price[i]
        del ref[i]

    def clean_price_list(s):
        match = re.search(r"-?\d+[.,]\d+", s)
        if match:
            return float(match.group().replace(",", "."))
        return None

    def clean_ref_number(s):
        match = re.search(r'\d+', s)
        if match:
            return match.group()
        return None

    clean_price = [clean_price_list(x) for x in price]
    clean_ref = [clean_ref_number(x) for x in ref]

    for i in sorted([i for i, val in enumerate(clean_price) if val == 0.01], reverse=True):
        del status[i]
        del date[i]
        del clean_price[i]
        del clean_ref[i]

    if not (len(status) == len(date) == len(clean_price) == len(clean_ref)):
        print("Something went wrong while proccesing, aborting")
        context.close()
        browser.close()
        sys.exit()

    print("Fetched ", len(status), " Items")

    avg_price = sum(clean_price) / len(clean_price)
    avg_price = round(avg_price, 2)
    min_price = min(clean_price)
    max_price = max(clean_price)

    print(f"Max Price: {max_price}, Min Price: {min_price}, Avg Price: {avg_price}")

    pts, sta = fetch_shipment(context, clean_ref)

    if len(pts) != len(sta):
        print("ERROR: fetching or proccesing failed!")
        context.close()
        browser.close()
        sys.exit()
    total_days = [p2s + s2o for p2s, s2o in zip(pts, sta)]
    avg_time = sum(total_days) / len(total_days)
    avg_time = round(avg_time, 1)
    min_time = min(total_days)
    max_time = max(total_days)

    print(f"Max Delivery Time: {max_time} days, Min Delivery Time: {min_time} days, Avg Delivery Time: {avg_time} days")

    print("Finished!")
    
    context.close()
    browser.close()

if os.path.isfile("cookie.json"):
     with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(storage_state="cookie.json")
        parse_shippments(browser, context)

elif os.path.isfile("cookie.txt"):
    cookies = Netscape2json("cookie.txt")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        context.add_cookies(cookies)
        parse_shippments(browser, context)
else:
    print("Cookie file not found. Please log in first to create the cookie.json file.")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        page.goto("https://www.aliexpress.com/p/ug-login-page/login.html")

        save = input("Please log in manually and then press y to continue: ")

        if save.lower() == 'y':
            # Save cookies to a file
            context.storage_state(path="cookie.json")

            print("Login successful. Cookies saved to cookie.json.")
            print("You can now run the script again to parse shipments.")

            context.close()
            browser.close()