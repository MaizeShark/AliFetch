# AliFetch

Fetches Prices and Delivery Time of bought Items on AliExpress.

Output will look something like this (yeah *i need help*):
```
Parsing AE shipments...
Fetched 153 Items
Max Price: 119.56€, Min Price: 0.7€, Avg Price: 6.19€, Total Spending: 947.82€
Total Money spent by Year:
2023: 28.48€
2024: 141.92€
2025: 540.07€
2026: 237.35€
|████████████████████████████████████████| 155/155 [100%] in 4:12.7 (0.60/s)
Max Delivery Time: 38 days, Min Delivery Time: 5 days, Avg Delivery Time: 9.7 days
Finished!
```


``-n`` / ``--no-fetch`` skips fetching each item individually, with it you only get price data (so spent per year, max price, min price and avarage price), without it you will also get Max Delivery Time, Min Delivery Time and the Average Delivery Time.  
Fetching each item individually takes the most time (for me 4/5 minutes).

## Cookie

This Tool authenticates itself as you, for that it needs your Cookies, i personally used [cookies.txt](https://addons.mozilla.org/en-US/firefox/addon/cookies-txt/) for that.

> [!WARNING]
> Automating user accounts is against AliExpresses TOS (6.3 f) and may result in you getting banned.
> I do not provide any warranty or take responsibility for any consequences (including but not limited to account suspension or bans) resulting from the use of this tool. Use at your own risk.

> This project is not affiliated with AliExpress