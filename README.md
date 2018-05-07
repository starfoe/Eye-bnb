

# Eye BnB

## Business Prospect

•	This project will help users find their favorite lodging during their travel, based on images or some descriptions uploaded by the users

•	It will provide value to:

  o	People who are looking for adding more fun, passion and excitement to their travel 
  
  o	Apartment owners who want to know how many apartments in the same city looks like theirs so that they can make their apartments   either discriminative or closer to the apartments which are already popular. 

## Data sources

•	Airbnb publicized their own datasets which provide lists of all the apartments in certain cities in the U.S. with lots details (http://insideairbnb.com/get-the-data.html)

•	With the lists above, images and highlight tags of each apartment are scraped by urllib2

## Data Preparation

•	*Online collection*

  o	Raw data is the basic information of Airbnb apartment (location, descriptions, price range, webpage URL) which can be found in the datasets publicated by Airbnb.It will be saved in MongoDB on AWS
  
  o	With the webpage URL gotten from above, images of each apartment will be scraped by BeautifulSoup and Request
  
  o	Highlight tags and some reviews will also be scraped and saved
  
  o	All the data will be saved to MongoDB on AWS

•	*Offline processing*

  o	For each apartment in the DB, extract certain features from its images and save to an excel spreadsheet (with its ID) 
  
  o	Put highlight reviews to the excel spreadsheet for further uses
  
## Modeling

•	*Similarities calculation*

  o	Eculidean Distance
  
  o	Cosine Distance
  
•	*Image feature extraction*
  
  o	Histgram
  
  o	GIST
  
  o CNN
  
  o	others

## Evaluation

• *Model Validation*：Image features and similarity measurements will be tested on a subset of Indoor Scene Recognition dataset publicated by MIT, for more details: http://web.mit.edu/torralba/www/indoor.html

• After being tested on the dataset above, the feature and similarity measurement will be employed in the recommendation process

•	*Visualization*: look at all the recommendations and conceptually check if they make sense

## Deployment

•	Step1: given a picture, the system can return places looks similar (of the same style)

•	Step2: users can add some word descriptions to what they dream of going ( industrial style, splendid..) to make the searching more precise

## Techiques 

•	MongoDB

•	AWS EC2 and S3

• Tensorflow




