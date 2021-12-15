import sqlite3

dbfile = 'movies.db'

con = sqlite3.connect(dbfile)
con.row_factory = sqlite3.Row

cur = con.cursor()

# When Movie title is given
def movie_name(movie_title):
    ret_data = {}

    movies_table = [a for a in cur.execute(f"SELECT * FROM movies WHERE title = '{movie_title}'")][0]
    movie_id = movies_table['id']

    ret_data['title'] = movies_table['title']
    ret_data['year'] = movies_table['year']

    stars_table = [a for a in cur.execute(f"SELECT * FROM stars JOIN people ON stars.person_id = people.id WHERE stars.movie_id = {movie_id}")]

    for i in range(min(len(stars_table), 5)):
        ret_data[f'star{i+1}_name'] = stars_table[i]['name']
        ret_data[f'star{i+1}_birth'] = stars_table[i]['birth']

    directors_table = [a for a in cur.execute(f"SELECT * FROM directors JOIN people ON directors.person_id = people.id WHERE directors.movie_id = {movie_id}")]

    for i in range(min(len(directors_table), 5)):
        ret_data['director_name'] = directors_table[i]['name']
        ret_data['director_birth'] = directors_table[i]['birth']

    ratings_table = [a for a in cur.execute(f"SELECT * FROM ratings WHERE ratings.movie_id = {movie_id}")][0]
    ret_data['rating'] = ratings_table['rating']
    ret_data['votes'] = ratings_table['votes']

    return ret_data

# When actor's Name is given
def actor_name(actor1_name, actor2_name, limit):
    ret_data = {}
    people_table = [a for a in cur.execute(f"SELECT * FROM people WHERE name = '{actor1_name}'")][0]

    person_id = people_table['id']
    ret_data['actor1_name'] = people_table['name']
    ret_data['actor1_birth'] = people_table['birth']

    movies_table = [a for a in cur.execute(f"SELECT * FROM movies JOIN stars ON stars.movie_id = movies.id WHERE person_id = {person_id} LIMIT {limit}")]
    for movie in movies_table:
        print(movie['title'])
        print(movie_name(movie['title']))
        print()

actor_name("Ranbir Kapoor", "", 10)

con.close()