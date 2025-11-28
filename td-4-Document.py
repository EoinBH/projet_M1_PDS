class Document():

    #Constructor:
    def __init__(self, date, title, author, text, url):
        self.date = date
        self.title = title
        self.author = author
        self.text = text
        self.url = url

    #Get Date:
    def get_date(self):
        return self.date
    
    #Get Title:
    def get_title(self):
        return self.title
    
    #Get Author:
    def get_author(self):
        return self.author
    
    #Get Text:
    def get_text(self):
        return self.text
        
    #Get Url:
    def get_url(self):
        return self.url
