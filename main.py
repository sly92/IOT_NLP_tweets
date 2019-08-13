import sys
import boto3
import tweepy
from gtts import gTTS
import os
import RPi.GPIO as GPIO
import time
try:
    import json
except ImportError:
    import simplejson as json

def setup():
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(16, GPIO.OUT)
    GPIO.setup(20, GPIO.OUT)
    GPIO.setup(21, GPIO.OUT)
    # Variables that contains the user credentials to access Twitter API
    TWITTER_ACCESS_TOKEN = 'XXX'
    TWITTER_ACCESS_SECRET = 'XXX'
    TWITTER_CONSUMER_KEY = 'XXX'
    TWITTER_CONSUMER_SECRET = 'XXX'
    # Setup tweepy to authenticate with Twitter credentials:
    auth = tweepy.OAuthHandler(TWITTER_CONSUMER_KEY, TWITTER_CONSUMER_SECRET)
    auth.set_access_token(TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_SECRET)
    # Create the api to connect to twitter with your creadentials
    api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True, compression=True)
    return api
    
def quit_properly():
    GPIO.output(16, GPIO.LOW)
    GPIO.output(20, GPIO.LOW)
    GPIO.output(21, GPIO.LOW)


def loop(api, hashtag="trump", debug=False):
    nb_tweets=2
    print("Recovering "+ str(nb_tweets) + " tweets from hashtag : " + str(hashtag))
    for tweet in tweepy.Cursor(api.search, q=hashtag).items(nb_tweets):
        text = tweet._json["text"]
        if debug:
            print(">>> DEBUG text : " + str(text))
        comprehend = boto3.client(service_name='comprehend', region_name='eu-west-1')
        lang = json.loads(json.dumps(comprehend.detect_dominant_language(Text=text), sort_keys=True, indent=4))["Languages"][0]["LanguageCode"]
        if debug:
            print(">>> DEBUG language : " + str(lang))
        sentiment = json.loads(json.dumps(comprehend.detect_sentiment(Text=text, LanguageCode=lang), sort_keys=True, indent=4))["Sentiment"]
        if sentiment == "NEGATIVE":
            if debug:
                print(">>> DEBUG Sentiment : " + str(sentiment))
            GPIO.output(20, GPIO.HIGH)
        elif sentiment == "POSITIVE":
            if debug:
                print(">>> DEBUG Sentiment : " + str(sentiment))
            GPIO.output(21, GPIO.HIGH)
        elif sentiment == "NEUTRAL":
            if debug:
                print(">>> DEBUG Sentiment : " + str(sentiment))
            GPIO.output(16, GPIO.HIGH)
        else:
            if debug:
                print(">>> DEBUG Sentiment : " + str(sentiment))
            GPIO.output(16, GPIO.HIGH)
            GPIO.output(20, GPIO.HIGH)
            GPIO.output(21, GPIO.HIGH)
        
        tts=gTTS(text=text,lang=lang)
        tts.save("tmp.mp3")
        os.system("mpg321 tmp.mp3")

        if sentiment == "NEGATIVE":
            if debug:
                print(">>> DEBUG Sentiment : " + str(sentiment))
            GPIO.output(20, GPIO.LOW)
        elif sentiment == "POSITIVE":
            if debug:
                print(">>> DEBUG Sentiment : " + str(sentiment))
            GPIO.output(21, GPIO.LOW)
        elif sentiment == "NEUTRAL":
            if debug:
                print(">>> DEBUG Sentiment : " + str(sentiment))
            GPIO.output(16, GPIO.LOW)
        else:
            if debug:
                print(">>> DEBUG Sentiment : " + str(sentiment))
            GPIO.output(16, GPIO.LOW)
            GPIO.output(20, GPIO.LOW)
            GPIO.output(21, GPIO.LOW)


if __name__ == "__main__":
    if len(sys.argv) > 3:
        print("Error too much arguments is pass to the function")
        print("usage : python " + str(sys.argv[0]) + " <hashtag>  <debug>")
    api=setup()
    if len(sys.argv) == 2:
        loop(api=api, hashtag=sys.argv[1], debug=False)
    if len(sys.argv) == 3:
        loop(api=api, hashtag=sys.argv[1], debug=True)
    else:
        loop(api=api)

    quit_properly()
