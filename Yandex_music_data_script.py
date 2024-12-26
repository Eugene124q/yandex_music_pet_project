#!/usr/bin/env python
# coding: utf-8

# In[1]:


print('Старт работы скрипта')


# ### Imports

# In[2]:


from yandex_music import Client
import pandas as pd
import ast
import os
import numpy as np
import json
from datetime import datetime, timedelta
from sqlalchemy import *
from dotenv import load_dotenv, dotenv_values 


# In[3]:


pd.set_option('display.max_columns', None)


# ### Token

# In[4]:


load_dotenv() 


# In[5]:


api_key = os.getenv('MY_KEY')


# In[6]:


client = Client(api_key).init()


# ### Метод получения понравившихся артстов

# In[7]:


artists_data = client.users_likes_artists() # метод получения понравившихся артистов


# In[8]:


type(artists_data)


# In[9]:


df = pd.DataFrame(artists_data)


# In[10]:


df # df, содержащий всех понравившихся артистов


# In[11]:


df1 = pd.json_normalize(df['artist']) # "разворачиваю колонку artist"


# In[12]:


user_likes_artists = df1.rename(columns = {'id' : 'artist_id'})


# In[13]:


user_likes_artists # будет использоваться для получения списка id понравившихся артистов


# ### Список всех ID понравившихся артистов

# In[14]:


list_id = user_likes_artists['artist_id'].tolist()


# ### Получение всех треков понравившихся исполнителей

# In[15]:


empty_df = pd.DataFrame(columns = ['artist_id','tracks', 'pager']) # Явно задаем все нужные колонки
for i in list_id:
    data = client.artists_tracks(i, page_size = 1000)
    data_dict = ast.literal_eval(str(data))
    for key, value in data_dict.items():
        if isinstance(value, (dict, list)):
            data_dict[key] = str(value)
    temp_df = pd.DataFrame.from_dict(data_dict, orient = 'index').fillna(np.nan)
    temp_df = temp_df.T # Транспонируем только после преобразования в DataFrame
    temp_df['artist_id'] = i # Добавляем artist_id как колонку
    empty_df = pd.concat([empty_df, temp_df], axis = 0, ignore_index=True)  # Используем ignore_index для сброса индексов


# In[16]:


first_tracks_df = empty_df.reset_index(drop = True)


# In[17]:


first_tracks_df


# In[18]:


first_tracks_df['tracks'].apply(type).value_counts()


# ### Фукнция преобразования столбцов DataFrame в объект список/словарь

# In[19]:


def safe_literal_eval(val):
    if pd.notnull(val):  # Проверка на NaN
        try:
            return ast.literal_eval(val)  # Преобразуем строку в объект (список/словарь)
        except (ValueError, SyntaxError):
            return None  # Если не удалось распарсить, вернем None
    return None


# ### Разворачиваю столбец tracks

# In[20]:


first_tracks_df['tracks'] = first_tracks_df['tracks'].apply(safe_literal_eval)


# In[21]:


parsed_tracks_column = first_tracks_df.explode('tracks').reset_index(drop=True)


# In[22]:


parsed_tracks_column_normalize = pd.json_normalize(parsed_tracks_column['tracks'])


# In[23]:


second_tracks_df = parsed_tracks_column_normalize


# In[24]:


second_tracks_df


# ### Объединяю полученный DataFrame со списком id понравившихся артистов

# In[25]:


tracks = pd.concat(
    [parsed_tracks_column[['artist_id']].reset_index(drop=True), parsed_tracks_column_normalize], axis=1)


# In[26]:


tracks


# ### Заменяю названия столбцов с . на _

# In[27]:


tracks.columns = tracks.columns.str.replace('.', '_', regex=False)


# ### Удаляю ненужные столбцы с вложенностью

# In[28]:


tracks.drop(['artists', 'albums'], axis =1, inplace = True)


# In[29]:


tracks


# ### Заменяю название колонки id на track_id

# In[30]:


tracks.rename(columns = {'id' : 'track_id'}, inplace=True)


# # Data Frame со всеми ТРЕКАМИ понравившихся исполнителей

# In[31]:


tracks


# ### Получение всех альбомов понравившихся исполнителей

# In[32]:


empty_df = pd.DataFrame(columns=['artist_id', 'albums', 'pager'])  # Явно задаем все нужные колонки
for i in list_id:
    albums_data = client.artists_direct_albums(i, page_size=2000)
    albums_data_dict = ast.literal_eval(str(albums_data))
    for key, value in albums_data_dict.items():
        if isinstance(value, (dict, list)):
            albums_data_dict[key] = str(value)
    temp_df = pd.DataFrame.from_dict(albums_data_dict, orient='index').fillna(np.nan)
    temp_df = temp_df.T  # Транспонируем только после преобразования в DataFrame
    temp_df['artist_id'] = i # Добавляем artist_id как колонку
    empty_df = pd.concat([empty_df, temp_df], axis=0, ignore_index=True)  # Используем ignore_index для сброса индексов


# In[33]:


first_albums_df = empty_df.reset_index(drop = True)


# In[34]:


first_albums_df


# In[35]:


first_albums_df['albums'].apply(type).value_counts()


# ### Разворачиваю столбец albums

# In[36]:


first_albums_df['albums'] = first_albums_df['albums'].apply(safe_literal_eval)


# In[37]:


parsed_albums_column = first_albums_df.explode('albums').reset_index(drop=True)


# In[38]:


parsed_albums_column_normalize = pd.json_normalize(parsed_albums_column['albums'])


# In[39]:


second_albums_df = parsed_albums_column_normalize


# In[40]:


second_albums_df


# ### Объединяю полученный DataFrame со списком id понравившихся артистов

# In[41]:


albums_df1 = pd.concat(
    [parsed_albums_column[['artist_id']].reset_index(drop=True), parsed_albums_column_normalize], axis=1)


# In[42]:


albums_df1


# ### Заменяю название колонки id на album_id

# In[43]:


albums_df1.rename(columns = {'id' : 'album_id'}, inplace=True)


# ### Меняю числовой тип колонки likes_count

# In[44]:


albums_df1['likes_count'] = albums_df1['likes_count'].fillna(0).astype(int)


# In[45]:


albums_df1


# ### Разворачиваю колонку labels

# In[46]:


labels_df1 = pd.json_normalize(albums_df1['labels']).drop([1,2], axis = 1)


# In[47]:


labels_df1


# In[48]:


labels_df2 = pd.json_normalize(labels_df1[0])


# In[49]:


labels_df2


# In[50]:


labels_df2['id'] = labels_df2['id'].fillna(0).astype(int)


# In[51]:


labels_df2.rename(columns = {'id' : 'label_id', 'name' : 'label_name'}, inplace=True)


# In[52]:


labels_df2


# ### Объединяю колонку labels c albums_df

# In[53]:


albums = pd.concat([albums_df1, labels_df2], axis = 1)


# In[54]:


albums


# ### Удаляю ненужные колонки

# In[55]:


albums.drop(['artists', 'labels'], axis =1, inplace = True)


# In[56]:


albums = albums.applymap(lambda x: str(x) if isinstance(x, (dict, list, tuple)) else x)


# # Data Frame со всеми АЛЬБОМАМИ понравившихся исполнителей

# In[57]:


albums


# ### Дополнительная информация о понравившихся артистах

# In[58]:


empty_df = pd.DataFrame(columns = ['artist_id','artist', 'albums', 'playlists', 'also_albums', 'last_release_ids', 'last_releases', 
                                   'popular_tracks', 'similar_artists', 'all_covers', 'concerts', 'videos', 'vinyls', 
                                   'has_promotions', 'playlist_ids', 'tracks_in_chart'])
for i in list_id:
    artist_data = client.artists_brief_info(i)
    artist_data_dict = ast.literal_eval(str(artist_data))
    for key, value in artist_data_dict.items():
        if isinstance(value, (dict, list)):
            artist_data_dict[key] = str(value)
    temp_df = pd.DataFrame.from_dict(artist_data_dict, orient = 'index').fillna(np.nan)
    temp_df = temp_df.T  # Транспонируем только после преобразования в DataFrame
    temp_df['artist_id'] = i  # Добавляем artist_id как колонку
    empty_df = pd.concat([empty_df, temp_df], axis = 0, ignore_index=True)


# In[59]:


artists_info_df = empty_df.reset_index(drop = True)


# ### Data Frame c доп. информацией о понравившихся артистах

# In[60]:


artists_info_df


# ### Разворачиваю столбец artist

# In[61]:


artists_info_df['artist'] = artists_info_df['artist'].apply(lambda x: ast.literal_eval(x))


# In[62]:


df_artists_expanded = pd.json_normalize(artists_info_df['artist'])


# In[63]:


df_artists_expanded.columns = df_artists_expanded.columns.str.replace('.', '_', regex=False)


# In[64]:


artists = df_artists_expanded.rename(columns = {'id' : 'artist_id'})


# In[65]:


artists['ratings_day'] = artists['ratings_day'].fillna(0).astype(int)


# In[66]:


artists = artists.applymap(lambda x: str(x) if isinstance(x, (dict, list, tuple)) else x)


# # Data Frame с информацией о всех понравившихся АРТИСТАХ

# In[67]:


artists


# ### Разворачиваю столбец popular_tracks

# In[68]:


artists_info_df['popular_tracks'] = artists_info_df['popular_tracks'].apply(safe_literal_eval)


# In[69]:


parsed_popular_tracks_column = artists_info_df.explode('popular_tracks').reset_index(drop=True)


# In[70]:


parsed_popular_tracks_column_normalize = pd.json_normalize(parsed_popular_tracks_column['popular_tracks'])


# In[71]:


parsed_popular_tracks_column_normalize


# ### Объединяю полученный DataFrame со списком id понравившихся артистов

# In[72]:


popular_tracks = pd.concat(
    [parsed_popular_tracks_column[['artist_id']].reset_index(drop=True), parsed_popular_tracks_column_normalize], axis=1)


# In[73]:


popular_tracks.columns = popular_tracks.columns.str.replace('.', '_', regex=False)


# In[74]:


popular_tracks.drop(['artists', 'albums'], axis =1, inplace = True)


# In[75]:


popular_tracks.rename(columns = {'id' : 'popular_track_id'}, inplace=True)


# # DataFrame со всеми ПОПУЛРЯНЫМИ ТРЕКАМИ исполнителей

# In[76]:


popular_tracks


# ### Разворачиваю столбец similar_artists

# In[77]:


artists_info_df['similar_artists'] = artists_info_df['similar_artists'].apply(safe_literal_eval)


# In[78]:


parsed_similar_artists_column = artists_info_df.explode('similar_artists').reset_index(drop=True)


# In[79]:


parsed_similar_artists_column_normalize = pd.json_normalize(parsed_similar_artists_column['similar_artists'])


# In[80]:


parsed_similar_artists_column_normalize


# ### Объединяю полученный DataFrame со списком id понравившихся артистов

# In[81]:


similar_artists = pd.concat(
    [parsed_similar_artists_column[['artist_id']].reset_index(drop=True), parsed_similar_artists_column_normalize], axis=1)


# In[82]:


similar_artists.columns = similar_artists.columns.str.replace('.', '_', regex=False)


# In[83]:


similar_artists.rename(columns = {'id' : 'similar_artist_id'}, inplace=True)


# In[116]:


similar_artists_useful_columns = ['artist_id', 'similar_artist_id', 'error', 'reason', 'name', 'various',
       'composer', 'genres', 'og_image', 'op_image', 'no_pictures_from_search',
       'available', 'ratings', 'links', 'tickets_available', 'likes_count',
       'popular_tracks', 'regions', 'decomposed', 'full_names',
       'hand_made_description', 'description', 'countries',
       'en_wikipedia_link', 'db_aliases', 'aliases', 'init_date', 'end_date',
       'ya_money_id', 'cover_type', 'cover_uri', 'cover_items_uri',
       'cover_dir', 'cover_version', 'cover_custom', 'cover_is_custom',
       'cover_copyright_name', 'cover_copyright_cline', 'cover_prefix',
       'cover_error', 'counts_tracks', 'counts_direct_albums',
       'counts_also_albums', 'counts_also_tracks']


# # DataFrame с ПОХОЖИМИ ИСПОЛНИТЕЛЯМИ

# In[84]:


similar_artists


# # DataFrame Artists_metrics

# In[85]:


artists_metrics = artists[['artist_id', 'likes_count', 'ratings_month', 'ratings_week', 'ratings_day']]


# In[86]:


start = datetime.utcnow()


# In[87]:


start


# In[88]:


start + timedelta(hours = 7)


# In[89]:


time = (start + timedelta(hours = 7))


# In[90]:


time


# In[91]:


artists_metrics['dt'] = time


# # DataFrame с МЕТРИКАМИ АРТИСТОВ

# In[92]:


artists_metrics


# # DataFrame Albums_metrics

# In[93]:


albums_metrics = albums[['album_id', 'likes_count']]


# In[94]:


albums_metrics['dt'] = time


# # DataFrame с МЕТРИКАМИ АЛЬБОМОВ

# In[95]:


albums_metrics


# # Удаляю столбцы, задйствованные в таблицах artists/albums_metrics

# In[96]:


artists = artists.drop(['likes_count', 'ratings_month', 'ratings_week', 'ratings_day'], axis = 1)


# In[97]:


albums = albums.drop('likes_count', axis = 1)


# # RESULTS

# In[98]:


artists


# In[99]:


tracks


# In[100]:


albums


# In[101]:


popular_tracks


# In[102]:


similar_artists


# In[103]:


artists_metrics


# In[104]:


albums_metrics


# # Подключение к базе данных

# In[105]:


login = os.getenv('BD_LOGIN')
password = os.getenv('BD_PASSWORD')
host = os.getenv('BD_HOST')
schema = os.getenv('BD_SCHEMA')


# In[106]:


connection_string = f'postgresql+psycopg2://{login}:{password}@{host}/{schema}' 


# In[107]:


engine = create_engine(connection_string)


# # Подгрузка данных в БД

# ### artists_metrics

# In[108]:


artists_metrics.to_sql('artists_metrics', engine, if_exists='append', index = False)


# ### albums_metrics

# In[109]:


albums_metrics.to_sql('albums_metrics', engine, if_exists='append', index = False)


# ### artitsts

# In[110]:


# Очистка всех данных из таблицы artists, не затрагивая её структуру и зависимости
with engine.connect() as conn:
    conn.execute(text('TRUNCATE artists;'))
    conn.commit() # Фиксация изменений

# Добавление новых данных в таблицу artists
artists.to_sql('artists', engine, if_exists='append', index=False)

# В этом случае созданные представления на основе таблицы 'artists' останутся доступными, 
# и Superset сможет без прерываний использовать их для построения графиков.


# ### tracks

# In[111]:


with engine.connect() as conn:
    conn.execute(text('TRUNCATE tracks;'))
    conn.commit()
tracks.to_sql('tracks', engine, if_exists='append', index = False)


# ### albums

# In[112]:


with engine.connect() as conn:
    conn.execute(text('TRUNCATE albums;'))
    conn.commit()
albums.to_sql('albums', engine, if_exists='append', index = False)


# ### popular_tracks

# In[113]:


with engine.connect() as conn:
    conn.execute(text('TRUNCATE popular_tracks;'))
    conn.commit()
popular_tracks.to_sql('popular_tracks', engine, if_exists='append', index = False)


# ### similar_artists

# In[117]:


with engine.connect() as conn:
    conn.execute(text('TRUNCATE similar_artists;'))
    conn.commit()
similar_artists[similar_artists_useful_columns].to_sql('similar_artists', engine, if_exists='append', index = False)


# In[ ]:


print('Конец работы скрипта')


# In[ ]:




