Features to be added:
- Deployment of ETL in a cloud.

That would make the process more scalable and independent from user's machine. However, I couldn't find any decent option that would suit to the ETL's nature and
wouldn't require billing data (as GCP services do)
- Applying more advanced duplicates policy.

As for now, the ETL drops duplicates basing solely on justjoin.it ID provided in API, but I have suspicions that in a future the new offers could replace the ones
published a long time ago (let's say, 3 months or so) - ergo, those ID's might not be unique. But we also don't want to subset the publishing date in removal process
as the offers data tends to change too often.
- Implementing and integrating web scrapers.

The justjoin.it does not provide all the data. I can especially think of skills data, which could have up to 12 fields on a job ad rather than 3, and also of advert's
descriptions on a website, that could embrace some potentially interesting features. However I haven't got time to implement that, and justjoin.it website seems to require some more advanced skills in web scraping than mine.
