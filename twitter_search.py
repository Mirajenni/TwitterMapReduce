import tweepy
from tweepy import OAuthHandler
import json
import datetime as dt
import time
import os
import sys
import pika


#código utilizado do github.com/agalea91

connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()
channel.queue_declare(queue='coronavirus')


def load_api():
    consumer_key = '' #ADICIONAR O SEU!
    consumer_secret = '' #ADICIONAR O SEU!
    access_token = '' #ADICIONAR O SEU!
    access_secret = '' #ADICIONAR O SEU!
    auth = OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_secret)
    # load the twitter API via tweepy
    return tweepy.API(auth)

    
def tweet_search(api, query, max_tweets, max_id, since_id, lang):

    searched_tweets = []
    while len(searched_tweets) < max_tweets:
        remaining_tweets = max_tweets - len(searched_tweets)
        try:
            new_tweets = api.search(q=query, count=remaining_tweets,
                                    since_id=str(since_id),
				                    max_id=str(max_id-1), lang=lang, tweet_mode='extended')
            print('encontrados',len(new_tweets),'tweets')
            if not new_tweets:
                print('tweet não encontrado')
                break
            searched_tweets.extend(new_tweets)
            max_id = new_tweets[-1].id
        except tweepy.TweepError:
            print('execeção, esperando 15 minutos')
            print('(até:', dt.datetime.now()+dt.timedelta(minutes=15), ')')
            time.sleep(15*60)
            break # stop the loop
    return searched_tweets, max_id


def get_tweet_id(api, date='', days_ago=9, query='a'):
    if date:
        # return an ID from the start of the given day
        td = date + dt.timedelta(days=1)
        tweet_date = '{0}-{1:0>2}-{2:0>2}'.format(td.year, td.month, td.day)
        tweet = api.search(q=query, count=1, until=tweet_date)
    else:
        # return an ID from __ days ago
        td = dt.datetime.now() - dt.timedelta(days=days_ago)
        tweet_date = '{0}-{1:0>2}-{2:0>2}'.format(td.year, td.month, td.day)
        # get list of up to 10 tweets
        tweet = api.search(q=query, count=10, until=tweet_date)
        print('procurar o limite (start/stop):',tweet[0].created_at)
        # return the id of the first tweet in the list
        return tweet[0].id


def write_tweets(tweets, filename):
    #escreve o arquivo json e manda pro consumidor

    with open(filename, 'a') as f:
        for tweet in tweets:
            print('\n')
            msg = tweet.full_text
            print(msg)
            channel.basic_publish(exchange='', routing_key='coronavirus', body=msg)
            json.dump(tweet._json, f)
            f.write('\n')


def main():
    search_phrases = ['coronavirus']
    time_limit = 1.5                            # tempo em horas
    max_tweets = 5                              # número máximo de tweets por busca (é iterado)
                                               
    min_days_old, max_days_old = 0, 3           # do dia de hoje até 3 dias                                                                                     
    PT = "pt"                                   # língua
    

    # para cada palavra-chave pesquisada iterar
    for search_phrase in search_phrases:

        print('Procurando frase =', search_phrase)

        #variáveis do json
        name = search_phrase.split()[0]
        json_file_root = name + '/'  + name
        os.makedirs(os.path.dirname(json_file_root), exist_ok=True)
        read_IDs = False
        
        # abre um arquivo pra escrever
        if max_days_old - min_days_old == 1:
            d = dt.datetime.now() - dt.timedelta(days=min_days_old)
            day = '{0}-{1:0>2}-{2:0>2}'.format(d.year, d.month, d.day)
        else:
            d1 = dt.datetime.now() - dt.timedelta(days=max_days_old-1)
            d2 = dt.datetime.now() - dt.timedelta(days=min_days_old)
            day = '{0}-{1:0>2}-{2:0>2}_to_{3}-{4:0>2}-{5:0>2}'.format(
                  d1.year, d1.month, d1.day, d2.year, d2.month, d2.day)
        json_file = json_file_root + '_' + day + '.json'
        if os.path.isfile(json_file):
            print('Adicionando tweets ao arquivo: ',json_file)
            read_IDs = True
        
        # authorize and load the twitter API
        api = load_api()
        
        # set the 'starting point' ID for tweet collection
        if read_IDs:
            # open the json file and get the latest tweet ID
            with open(json_file, 'r') as f:
                lines = f.readlines()
                max_id = json.loads(lines[-1])['id']
                print('Procurando do ID final no arquivo')
        else:
            # get the ID of a tweet that is min_days_old
            if min_days_old == 0:
                max_id = -1
            else:
                max_id = get_tweet_id(api, days_ago=(min_days_old-1))
        # set the smallest ID to search for
        since_id = get_tweet_id(api, days_ago=(max_days_old-1))
        print('max id (ponto de início) =', max_id)
        print('since id (último ponto) =', since_id)
        


        ''' tweet gathering loop  '''
        start = dt.datetime.now()
        end = start + dt.timedelta(hours=time_limit)
        count, exitcount = 0, 0
        while dt.datetime.now() < end:
            count += 1
            print('quantidade =',count)
            # collect tweets and update max_id
            tweets, max_id = tweet_search(api, search_phrase, max_tweets,
                                          max_id=max_id, since_id=since_id,
                                          lang = PT)
            # write tweets to file in JSON format
            if tweets:
                write_tweets(tweets, json_file)
                exitcount = 0
            else:
                exitcount += 1
                if exitcount == 3:
                    if search_phrase == search_phrases[-1]:
                        sys.exit('Número máximo de tweets vazios alcançado - fechando')
                    else:
                        print('Número máximo de tweets vazios alcançado - quebrandoo')
                        break

if __name__ == "__main__":
    main()
    connection.close()
