## https://intoli.com/blog/running-selenium-with-headless-chrome/
## http://srome.github.io/Parsing-HTML-Tables-in-Python-with-BeautifulSoup-and-pandas/
## https://www.scrapehero.com/how-to-prevent-getting-blacklisted-while-scraping/


import datetime
import platform
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver

class HTMLTableParser:
    
    ## setting up chrome agnet
    def browser_startup(self):
        user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.50 Safari/537.36'
        options = webdriver.ChromeOptions()
        options.add_argument('headless')
        options.add_argument('window-size=1920x1080')
        options.add_argument(f'user-agent={user_agent}')
        br = webdriver.Chrome(chrome_options=options)
        return br

    ## parsing a certain number of day from TODAY
    ## positive number from today and after, negative from today and before
    def parse_url(self, getNumDay):
        br_parse = self.browser_startup()
        today = datetime.datetime.now()
        dateOne = datetime.timedelta(days=1)
        
        ## get date from PURE mindbody and set up schedule link
        if getNumDay > 0:
            for day in range(getNumDay):
                date = today + dateOne * day 
                self.parse_initilizer(today, date, br_parse)
        else:
            for day in range(0,getNumDay,-1):
                date = today + dateOne * day               
                self.parse_initilizer(today, date, br_parse)
                
        br_parse.quit()

    ## parsing a period of days
    ## from yyyymmdd to yyyymmdd
    def parse_url_period(self, getDate1, getDate2):      
        br_parse = self.browser_startup()
        dateOne= datetime.timedelta(days=1)
        gd1 = datetime.datetime.strptime(str(getDate1)+'000000000000', "%Y%m%d%H%M%S%f")
        gd2 = datetime.datetime.strptime(str(getDate2)+'000000000000', "%Y%m%d%H%M%S%f")
       
        ## check and set up input date
        if gd1 < gd2:
            dateEnd = gd2
            dateStart = gd1
        else:
            dateEnd = gd1
            dateStart = gd2
        dateCounter = dateStart
        dateControl = dateEnd - dateStart

        ## get date from PURE mindbody and set up schedule link
        for day in range(dateControl.days+1):
            self.parse_initilizer(dateStart, dateCounter, br_parse)
            dateCounter += dateOne
                
        br_parse.quit()

    def parse_initilizer(self, dateCheck, d, b):
        url_schedule = 'https://clients.mindbodyonline.com/classic/mainclass?studioid=81&tg=&vt=&lvl=&stype=&view=&trn=0&page=&catid=&prodid=&date=' + str(d.month) + '%2f' + str(d.day) + '%2f' + str(d.year) + '&classid=0&prodGroupId=&sSU=&optForwardingLink=&qParam=&justloggedin=&nLgIn=&pMode=0'
        b.get(url_schedule)

        ## always wait fo=- input when run the frist time in order to manually gets by CAPTCHA
        if dateCheck == d:
            input('click "enter" when done with CAPTCHA')
            b.get(url_schedule) 

        ## soup get to the main schedule body
        soup = BeautifulSoup(b.page_source, "html.parser")
        class_schedule = soup.find(id ='classSchedule-mainTable')
        self.parse_html_table(class_schedule, d)
        print('done pracing ' + str(d.year) + str(d.month) + str(d.day) + '...')
        
    def parse_html_table(self, cs, d):
        ## ==============================================================
        ## table html code
        ## tr = row  |  td = column  |  th = thead
        ## ==============================================================
        n_columns = 0
        n_rows = 0
        column_names=[]
        
        # find number of rows and columns
        # also find column titles if we can, not yet going through table content
        for row in cs.find_all('tr'):
            td_tags = row.find_all('td')
            if len(td_tags) > 0:
                    n_rows+=1
            ## handle column names if available
            th_tags = row.find_all('th')
            if len(th_tags) > 0 and len(column_names) == 0:
                for th in th_tags:
                    column_names.append(th.get_text())
            if n_columns == 0:
                n_columns = len(th_tags)

        ## safegaurd on column titles
        if len(column_names) > 0 and len(column_names) != n_columns:
            raise Exception('column titles do not match the number of columns')

        ## initialize and fill table, now going through the table content
        columns = column_names if len(column_names) > 0 else range(0,n_columns)
        df = pd.DataFrame(columns=columns, index=range(0,n_rows))
        row_marker = 0
        for row in cs.find_all('tr'):
            column_marker = 0
            columns = row.find_all('td')
            for column in columns:
                df.iat[row_marker,column_marker] = column.get_text()
                column_marker += 1
            if len(columns) > 0:
                row_marker += 1
                
        ## save dataFrame to csv
        df.to_csv('/Users/sun/Dropbox/_shared/_code/_pure/pure scrap/schedule/' + str(d.strftime("%Y")) + str(d.strftime("%m")) + str(d.strftime("%d")) + '.csv')
        ## return df


hp = HTMLTableParser()
## hp.parse_url(5)
hp.parse_url_period(20180730,20180812)

# navigate to my visit history
##br_login.get('https://clients.mindbodyonline.com/ASP/my_vh.asp')

# screenshot
# br_login.get_screenshot_as_file('main-page.png')






