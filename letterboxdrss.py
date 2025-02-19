import feedparser
import csv
import re
import random
import datetime as dt

REVIEW_REGEX = re.compile("letterboxd-review-[0-9]+")
SUMMARY_REGEX = re.compile('^(<p><img src=\".*\" \/><\/p> )?<p>(.*)<\/p>$')

class Review:
  date = "",
  name = "",
  year = 1971
  letterboxd_uri = ""
  rating = 0
  rewatch = False,
  review = ""
  tags = "",
  watched_date = ""
  
  def __init__(self, date, name, year, letterboxd_uri, rating, rewatch, review, tags, watched_date):
    self.date = date
    self.name = name
    self.year = year
    self.letterboxd_uri = letterboxd_uri
    self.rating = rating
    self.rewatch = rewatch
    self.review = review
    self.tags = tags
    self.watched_date = watched_date
    
  def __repr__(self):
    if self.rating != "":
      return f"{self.name} ({self.year}) - {self.rating:g}/5: {self.review}"
    else:
      return f"{self.name} ({self.year}) - No rating: {self.review}"
    
  def __eq__(self, other) -> bool:
    return self.watched_date == other.watched_date and self.name == other.name
  
  def to_list(self):
    return [self.date, self.name, self.year, self.letterboxd_uri, self.rating, 'Yes' if self.rewatch else 'No', self.review, self.tags, self.watched_date]
      

class LetterboxdRSS:
  feed = None
  
  reviews = []
  
  data_timestamp = dt.datetime.now()
  data_timeout = 300
  
  def __init__(self, letterboxd_id, csvpath):
    self.rss_url = f"https://letterboxd.com/{letterboxd_id}/rss"
    self.csvpath = csvpath
    
    self.parse_csv_entries()
    self.parse_rss_entries()
    self.save_to_csv()
    
    self.data_timestamp = dt.datetime.now()
    
  def update_if_necessary(self):
    if (self.data_timestamp is None) or ((dt.datetime.now() - self.data_timestamp).total_seconds() > self.data_timeout):
      self.data_timestamp = dt.datetime.now()
      self.update()
    
  def update(self):
    self.parse_rss_entries()
    self.save_to_csv()
    
  def parse_csv_entries(self):
    with open(self.csvpath, 'r', newline='', encoding='utf8') as csvfile:
      reviewreader = csv.reader(csvfile, delimiter=',', quotechar="\"")
      for row in reviewreader:
        rating = '' if row[4] == '' else float(row[4])
        self.reviews.append(Review(row[0], row[1], row[2], row[3], rating, row[5] == "Yes", row[6], row[7], row[8]))
    
  def parse_rss_entries(self):
    self.feed = feedparser.parse(self.rss_url)
    for entry in self.feed.entries:
      if not REVIEW_REGEX.match(entry.get('guid', "")):
        continue
      
      date = ""
      name = entry.get('letterboxd_filmtitle', "Missing title")
      year = entry.get('letterboxd_filmyear', 'No year')
      uri = ""
      rating = entry.get('letterboxd_memberrating', None)
      rewatch = entry.get('letterboxd_rewatch', None) == 'Yes'
      review = SUMMARY_REGEX.match(entry['summary']).group(2)
      tags = ""
      watched_date = entry.get('letterboxd_watcheddate', "Date missing")
      
      reviewobj = Review(date, name, year, uri, rating, rewatch, review, tags, watched_date)
      
      add = True
      for r in self.reviews:
        if r == reviewobj:
          add = False
          break
        
      if add:
        self.reviews.append(reviewobj)
        
  def save_to_csv(self):
    with open(self.csvpath, 'w', newline='', encoding='utf8') as csvfile:
      reviewwriter = csv.writer(csvfile, delimiter=',', quotechar='"')
      for r in self.reviews:
        reviewwriter.writerow(r.to_list())
        
  def get_random_review(self):
    self.update_if_necessary()
    
    index = random.randint(0, len(self.reviews) - 1)
    
    return str(self.reviews[index])
  
  def get_review_from_title(self, title):
    self.update_if_necessary() 
    
    for r in self.reviews:
      if r.name == title:
        return r
    return None
      
      
if __name__ == '__main__':
  rss = LetterboxdRSS("itswill", './data/reviews.csv')
  
  for r in rss.reviews:
    if len(str(r)) > 400:
      print(f'{len(str(r))} - {str(r)[:100]} ... {str(r)[350:395]}...')