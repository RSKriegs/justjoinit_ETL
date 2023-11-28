UPDATE 26-28.11.2023: Added a prototype of a justjoin.it web crawler. Has some unadressed issues that I would like to improve in a future. Navigate to ```/scraper``` directory.

UPDATE 17.11.2023: it seems that justjoin.it has shut down its API, so this script won't work anymore :( the only option left is to write some web scraping code instead.

UPDATE 14.11.2022: At this point I am treating the project as finished, despite its liabilities described below. I might come back to it if I find more time. I have added the 2nd version of dashboard with deduplicated data, and some dbt files from the environment I worked with. I will try to update data until the end of the year.

---------

This is an ETL that extracts data from justjoin.it (a Polish IT jobboard) website API into local machine, transforms it locally, and loads into Google BigQuery. <del>The dataset from BigQuery fuels two Looker Studio dashboards below</del> The dashboards are no longer working as BigQuery tables expired. Here is a short demo on Youtube:
https://youtu.be/1OY9RX3LoHk

And the final dataset that I've published on Kaggle:
https://www.kaggle.com/datasets/kriegsmaschine/polish-it-job-board-data-from-2022

If you still want to access dashboards, here are the links:

https://datastudio.google.com/reporting/ce85abd5-19c5-4fa4-9ae9-83db79f1ea32 (with deduplicated data)

https://datastudio.google.com/reporting/aff55800-36a9-45a0-b1ee-c88c193a0a92 (without deduplication)

It should be visible to anybody on the internet. If not, try to log into your free Google account.
As for now, the data range starts from February 2022. The script is scheduled on my local machine (sample script in Powershell that triggers the ETL is included in a repo) and is turned on everytime I run it. 

(NOTE: BigQuery table expiration date without free tier is 60 days. If above dashboards won't work properly, it might have occured due to table expiration)

This is how one of dashboards looks like, as for 17th May 2022:

![image](https://user-images.githubusercontent.com/75480707/168835022-cd8f87de-9fe6-497f-9afb-dca8d9dd8702.png)

Some manual tips regarding a dashboard:
- the salary range slider might not come handy at first due to the fact that there are some records with salary being over 100k PLN. That's the issue but I haven't got time to think about it. Try to filter out some records to be able to specify a more detailed salary range.
- salary-wise, all of the salaries are valued in PLN. If there are any offerings in other currencies, they are automatically converted into a PLN with a current rate at the time of appending the deduplicated record into a dataset (with a help of forex_python package). The 'expected salary' metric on a graph is a mean of lower and upper ranges of salary range, for all mentioned employment types.
- the 'Job Title', 'Company' and 'Skills' searchbars filter if a given record contains an entered phrase. Data Studio also comes with a possibility of applying advanced search bars, with which you could also apply regular expressions, but that option seemed quite buggy.
- speaking about 'Skills' searchbar, Skills are gathered into a list. if you want to mark the beginning and end of the phrase, remember about placing a ',' separator. For example, if you want to search after specifically Java skill, write 'java,', otherwise you'll get results for Javascript and the others as well :)
- regarding the last previous two - also remember that 'Job Title' and 'Company' fields are case-sensitive, however, in case of 'Skills' field, always look after lower characters.

If you want to get more info regarding how I handled deduplication, look into /dbt files. I also included two views that I used for some visualizations in dashboards (I have joined these views with original table on dashboards). On Looker Studio, I also created 2 custom metrics - one is "expected_salary", which is simply an average of all proposed salaries for given offer (those could vary if they proposed multiple employment options), and "company_size_groups", where I group companies based on their size as given in job adverts.

Sample interesting insights, specifically for data engineers:
![Image](https://user-images.githubusercontent.com/75480707/201771367-d5e2e059-7307-43c3-8adf-953276be30fe.png)

Median expected salary for data engineer (all levels) as per job adverts is ~20.5k PLN (~4.5K USD) monthly. Almost 3/4 of adverts are fully remote and contain salary range.

![image](https://user-images.githubusercontent.com/75480707/201771425-07b136d9-7175-4c74-b6e1-849543d54508.png)

Most demanded skills - crucial for roles - are Python & SQL. Spark slightly wins a battle with AWS for a 3rd place. (Both Spark and cloud technologies can be mentioned in various formulas) (Side note - I believe that a prevalence of 'English' should be understood as the employers putting the biggest emphasis on English as compared to other skills, relatively)

![image](https://preview.redd.it/ky3kq045jzz91.png?width=1065&format=png&auto=webp&s=b4070aad40839192066cc45b9c03eac9f1682b5e)

Most of data engineering jobs fall under 'Data' section. If we include the rest of data professionals, we can see a relatively stronger emphasis on skills such as 'English', 'ETL' and Power BI.

![image](https://preview.redd.it/uz8s0i3xjzz91.png?width=1072&format=png&auto=webp&s=49a7aed1e79e0f0040c72503b66635717dbeda13)

Other insights from the dashboard, such as companies, experience level, or % of offers from other countries than Poland. Side note - B2B contracting is very popularized among IT industry in Poland. Also - companies included as best paying are not necessarily the best paying on the market, some companies do not display their salaries or don't bother with job postings on such websites (not mentioning relatively low record count).

-------------------------------------------------

If you want to run an ETL script, look into a code in Powershell scripts to find about a logic. First you'll need to install and configure Python virtual environment along with dependencies, then you can run a script. For more instructions, run a command:

python justjoinit_ETL.py --help

A project was developed with a goal in mind to deliver insights regarding Polish IT job market. Technically wise, I have not wanted to utilize any cloud tools, that either are paid, or provide a free tier on certain conditions - as I expected the data to be small enough to store & transform it locally and wanted to actually use them for my own reporting use cases, I did not want to be dependent on anything as a retail developer. Nevertheless, I have decided to load data into Google BigQuery, which offers some free tier service without providing billing data. On a top of that, I have created Looker Studio (formerly Google Data Studio) reports - which is free, and also applied dbt (which also has a free option) transformations on a data warehouse - although very basic, which I could implement in BigQuery solely, but I wanted to grasp some basics of this tool.

The project architecture looks like this:

![image](https://i.imgur.com/JK4d9PC.png)

The data was scheduled to be loaded into BigQuery from my PC, but as I've changed to laptop and became more "mobile" I dismissed this idea, and data loads have become irregular ever since.

Overall, I see a lot of room for further development. Some of the shortcomings & potential improvements that I see:

- Implementing SCDs level 2.

I did not consider it while developing a solution - due to that there are some issues with time series analysis for each advert (it includes the latest timestamp for each event rather than the earliest - and some job postings are retained for a long time). Instead of appending records and keeping their history, I have kept a single record that intended to be the earliest, or overwrite it if it was changed. This approach does not address the shortcomings of justjoin.it api and SCDs level 2 would do a trick.

- Deployment of ETL in a cloud.

That would make the process more scalable and independent from user's machine. However, I couldn't find any decent option that would suit to the ETL's nature and
wouldn't require billing data or significant limitations.

- Applying more advanced duplicates policy.

As for now, the ETL drops duplicates basing solely on justjoin.it ID provided in API, but I have suspicions that in a future the new offers could replace the ones
published a long time ago (let's say, 3 months or so) - ergo, those ID's might not be unique. But we also don't want to subset the publishing date in removal process
as the offers data tends to change too often, with publishing date being overwritten.
Update 23.05.2022: I've just noticed some changes in offers policy - namely speaking, offers containing multiple locations are displayed as a single offer at justjoin.it website, but they are displayed separately in API. That might cause some skew in a data, although the number of such offers is low. It is to be considered in future development.
Update 14.11.2022: I have approached to resolve that issue as addressed in dbt views. However I am not 100% sure that this approach is valid.

- Applying automatized backup policy.

I've implemented some sort of policy on my computer but it is not included in a script. Good idea would be to utilize f.e. Google Drive API to retain data in a cloud (or of course some paid option f.e. Cloud Storage).

- Making script resilient to OS/hardware issues.

I had not considered it while developing script, and I actually paid for that once and needed to restore the data and process it once again, as the incoming offers did not save into final dataset.

- More advanced data testing.

I did not bother with it that much aside of some pinpoints in ETL script - to be considered.

- Implementing and integrating web scrapers.

The justjoin.it API does not provide all the data. I can especially think of skills data, which could have up to 12 fields on a job ad rather than 3, and also of advert's descriptions on a website, that could embrace some potentially interesting features. It is also possible to integrate dataset with other websites.

- Optimization of pipeline.

My current solution iterates through Pandas dataframe which is an anti-pattern. However, the runtime was tolerable and I desired better control over my code as I needed to apply nested logic for each selected row. Retrospectively, I would improve it, but I haven't got time for it as for now. I would try to apply either raw Python data structures if possible rather than Pandas dataframe or apply vertical transformations on given columns.

- Running Dockerfile instead of Powershell script.

I am a Windows user, so it was quite logical for me to develop a simple Powershell script back since. However, 'Dockerizing' script would be better and more flexible as it would not require any resources to be installed locally and could be run on any OS. This should be relatively quick as well, but I did not have time to implement that as well.

- Utilizing tables instead of views in dbt build.

It would enable better dashboards performance, but it would require me to interact with dbt via dbt cli, which could be implemented in an ETL script, whereas materialized views would not work with deduplication script.

- ...and more of them, as always :)
