import sqlite3
from flask import Flask, flash, json, jsonify, redirect, render_template, request, session

app = Flask(__name__)


app.config["TEMPLATES_AUTO_RELOAD"] = True

@app.after_request
def after_request(response):
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Expires"] = 0
        response.headers["Pragma"] = "no-cache"
        return response


# When Movie title is given
@app.route("/movie_name", methods=["GET", "POST"])
def movie_name():
    dbfile = 'movies.db'

    con = sqlite3.connect(dbfile, check_same_thread=False)
    con.row_factory = sqlite3.Row

    cur = con.cursor()

    ret_data = {}
    movie_title = request.form.get("movie_title")
    movies_table = [a for a in cur.execute(f"SELECT * FROM movies WHERE title = '{movie_title}'")]
    if not movies_table:
        cur.close()
        return jsonify("Movie Not Found")
    else:
        movies_table = movies_table[0]
    movie_id = movies_table['id']

    ret_data['title'] = movies_table['title']
    ret_data['year'] = movies_table['year']

    stars_table = [a for a in cur.execute(f"SELECT * FROM stars JOIN people ON stars.person_id = people.id WHERE stars.movie_id = {movie_id}")]

    for i in range(min(len(stars_table), 5)):
        ret_data[f'star{i+1}_name'] = stars_table[i]['name']
        ret_data[f'star{i+1}_birth'] = stars_table[i]['birth']

    try:
        directors_table = [a for a in cur.execute(f"SELECT * FROM directors JOIN people ON directors.person_id = people.id WHERE directors.movie_id = {movie_id}")]
        
        for i in range(min(len(directors_table), 5)):
            ret_data['director_name'] = directors_table[i]['name']
            ret_data['director_birth'] = directors_table[i]['birth']
    
    except:
        ret_data["director_name"] = None
        ret_data["director_birth"] = None

        

    try:
        ratings_table = [a for a in cur.execute(f"SELECT * FROM ratings WHERE ratings.movie_id = {movie_id}")][0]
        
        ret_data['rating'] = ratings_table['rating']
        ret_data['votes'] = ratings_table['votes']
    
    except:
        ret_data["rating"] = None
        ret_data["votes"] = None

    cur.close()
    return jsonify(ret_data)
    
def movie_with_actor_id(movie_title, actor_id):
    # If actor ID is given
    dbfile = 'movies.db'

    con = sqlite3.connect(dbfile, check_same_thread=False)
    con.row_factory = sqlite3.Row

    cur = con.cursor()
    if "'" in movie_title:
        movie_title = movie_title.replace("'", "")
    movies_table = [a for a in cur.execute(f"SELECT * FROM movies JOIN stars ON stars.movie_id = movies.id WHERE title = '{movie_title}' AND stars.person_id = {actor_id}")]
    
    if not movies_table:
        cur.close()
        return ("Movie Not Found")
    else:
        movies_table = movies_table[0]
    movie_id = movies_table['id']
    ret_data = {}
    ret_data['title'] = movies_table['title']
    ret_data['year'] = movies_table['year']

    stars_table = [a for a in cur.execute(f"SELECT * FROM stars JOIN people ON stars.person_id = people.id WHERE stars.movie_id = {movie_id}")]

    for i in range(min(len(stars_table), 5)):
        ret_data[f'star{i+1}_name'] = stars_table[i]['name']
        ret_data[f'star{i+1}_birth'] = stars_table[i]['birth']

    try:
        directors_table = [a for a in cur.execute(f"SELECT * FROM directors JOIN people ON directors.person_id = people.id WHERE directors.movie_id = {movie_id}")]
        
        for i in range(min(len(directors_table), 5)):
            ret_data['director_name'] = directors_table[i]['name']
            ret_data['director_birth'] = directors_table[i]['birth']
    
    except:
        ret_data["director_name"] = None
        ret_data["director_birth"] = None


    try:
        ratings_table = [a for a in cur.execute(f"SELECT * FROM ratings WHERE ratings.movie_id = {movie_id}")][0]
        
        ret_data['rating'] = ratings_table['rating']
        ret_data['votes'] = ratings_table['votes']
    
    except:
        ret_data["rating"] = None
        ret_data["votes"] = None

    return ret_data

# When actors Names are given
@app.route("/actor_name", methods=["GET", "POST"])
def actor_name():
    dbfile = 'movies.db'

    con = sqlite3.connect(dbfile, check_same_thread=False)
    con.row_factory = sqlite3.Row

    cur = con.cursor()


    ret_data = {}
    actor1_name = request.form.get("actor1_name")
    actor2_name = request.form.get("actor2_name")
    limit = request.form.get("limit")

    people_table = [a for a in cur.execute(f"SELECT * FROM people WHERE name = '{actor1_name}'")]

    if not people_table:
        cur.close()
        return jsonify("Actor1 Not Found")
    else:
        people_table = people_table[0]

    person1_id = people_table['id']
    ret_data['actor1_name'] = people_table['name']
    ret_data['actor1_birth'] = people_table['birth']

    if actor2_name == "" or len(actor2_name) == 0 or actor2_name == None:
        movies_table = [a for a in cur.execute(f"SELECT * FROM movies JOIN stars ON stars.movie_id = movies.id WHERE person_id = {person1_id} LIMIT {limit}")]
        ans = []
        for movie in movies_table:
            ans.append(movie_with_actor_id(movie['title'], person1_id))
        
        cur.close()

        return jsonify(ans)
    

    else:
        people_table = [a for a in cur.execute(f"SELECT * FROM people WHERE name = '{actor2_name}'")]
        if not people_table:
            cur.close()
            return jsonify("Actor2 Not Found")
        else:
            people_table = people_table[0]

        person2_id = people_table['id']
        ret_data['actor2_name'] = people_table['name']
        ret_data['actor2_birth'] = people_table['birth']

        actor1_movies = [a for a in cur.execute(f"SELECT * FROM movies JOIN stars ON stars.movie_id = movies.id WHERE person_id = {person1_id}")]
        actor2_movies = [a for a in cur.execute(f"SELECT * FROM movies JOIN stars ON stars.movie_id = movies.id WHERE person_id = {person2_id}")]

        actor1_movieID = []

        for i in actor1_movies:
            actor1_movieID.append(i['id'])

        movies_together = []

        for i in actor2_movies:
            if i['id'] in actor1_movieID:
                movies_together.append(i['title'])
        
        ans = []
        for movie in movies_together:
            ans.append((movie_with_actor_id(movie, person1_id)))
        cur.close()
        return jsonify(ans)

@app.route("/")
def home() :
    return render_template("index.html")

if __name__ == "__main__":
    app.run()
    
    