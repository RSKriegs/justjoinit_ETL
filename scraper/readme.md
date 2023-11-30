Works on Microsoft Edge. If needed to run on other browsers, change the code with webdriver calls to a driver of choice (and remember to download the particular driver).

In order to use:
1. Download Selenium (running <code>pip install -r requirements.txt</code> will do it)
2. Download the Edgedriver and include its path in <code>driver_path</code> in <code>config.json</code> file parameter
3. Specify the justjoin.it link by which you want to extract data, for example <code>https://justjoin.it/all/data?keyword=data+engineer</code> in <code>main_link</code> parameter
4. Specify the target json file in <code>offers_file</code> parameter
5. Run it
