UPDATE 20.10.2022: As I've changed my main computer - and do not want to stage the process on it - the data loads will be irregular. If I manage to find some spare time, I will try to migrate the process into a cloud.

This is an ETL that extracts data from justjoin.it (a Polish IT jobboard) website API into local machine, transforms it locally, and loads into Google BigQuery. The dataset from BigQuery fuels the Google Data Studio dashboard below (which is up to the further development - there is one simple page as for now):

https://datastudio.google.com/reporting/aff55800-36a9-45a0-b1ee-c88c193a0a92

It should be visible to anybody on the internet. If not, try to log into your free Google account.
As for now, the data range starts from February 2022. The script is scheduled on my local machine (sample script in Powershell that triggers the ETL is included in a repo) and is turned on everytime I run it. 

This is how a dashboard looks like, as for 17th May 2022:

![image](https://user-images.githubusercontent.com/75480707/168835022-cd8f87de-9fe6-497f-9afb-dca8d9dd8702.png)

Some manual tips regarding a dashboard:
- the salary range slider might not come handy at first due to the fact that there are some records with salary being over 100k PLN. That's the issue but I haven't got time to think about it. Try to filter out some records to be able to specify a more detailed salary range.
- salary-wise, all of the salaries are valued in PLN. If there are any offerings in other currencies, they are automatically converted into a PLN with a current rate at the time of appending the deduplicated record into a dataset (with a help of forex_python package). The 'expected salary' metric on a graph is a mean of lower and upper ranges of salary range, for all mentioned employment types.
- the 'Job Title', 'Company' and 'Skills' searchbars filter if a given record contains an entered phrase. Data Studio also comes with a possibility of applying advanced search bars, with which you could also apply regular expressions, but that option seemed quite buggy.
- speaking about 'Skills' searchbar, Skills are gathered into a list. if you want to mark the beginning and end of the phrase, remember about placing a ',' separator. For example, if you want to search after specifically Java skill, write 'java,', otherwise you'll get results for Javascript and the others as well :)
- regarding the last previous two - also remember that 'Job Title' and 'Company' fields are case-sensitive, however, in case of 'Skills' field, always look after lower characters.

If you want to run an ETL script, look into a code in Powershell scripts to find about a logic. First you'll need to install and configure Python virtual environment along with dependencies, then you can run a script. For more instructions, run a command:

python justjoinit_ETL.py --help

Features to be added:

- Deployment of ETL in a cloud.

That would make the process more scalable and independent from user's machine. However, I couldn't find any decent option that would suit to the ETL's nature and
wouldn't require billing data (as GCP services do, despite giving great free tier option) - and I want to avoid giving that information, if unnecessary.
It should be possible to implement that in Cloud Functions, or even Airflow/Composer with proper modification.

- Applying more advanced duplicates policy.

As for now, the ETL drops duplicates basing solely on justjoin.it ID provided in API, but I have suspicions that in a future the new offers could replace the ones
published a long time ago (let's say, 3 months or so) - ergo, those ID's might not be unique. But we also don't want to subset the publishing date in removal process
as the offers data tends to change too often, with publishing date being overwritten.
Update 23.05.2022: I've just noticed some changes in offers policy - namely speaking, offers containing multiple locations are displayed as a single offer at justjoin.it website, but they are displayed separately in API. That might cause some skew in a data, although the number of such offers is low. It is to be considered in future development.

- Implementing and integrating web scrapers.

The justjoin.it API does not provide all the data. I can especially think of skills data, which could have up to 12 fields on a job ad rather than 3, and also of advert's descriptions on a website, that could embrace some potentially interesting features. However I haven't got time to implement that.

- More advanced testing.

Honestly - haven't got more time for that recently, and I haven't got any issues with a script as for now.

- Rewriting the script to be run within Docker's image, with adding tools such as Airflow, or Spark.

That would be cool, although I think that this is the overkill for the data of that size :)

- Optimization of pipeline.

My current solution iterates through Pandas dataframe which is an anti-pattern. However, the runtime was tolerable and I desired better control over my code as I needed to apply nested logic for each selected row. Retrospectively, I would improve it, but I haven't got time for it as for now. I would try to apply either raw Python data structures if possible rather than Pandas dataframe or apply vertical transformations on given columns.
