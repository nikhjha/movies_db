import express from "express";
import path from "path";
import { fileURLToPath } from "url";
import sqlite3 from "sqlite3";
import multer from "multer";

//Path variables
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

//Express app initialization
const app = express();
const port = process.env.PORT || 8080;

//Database initialization
const dbfile = "/movies.db";
const connection = sqlite3.verbose();
const db = new connection.Database(path.join(__dirname, dbfile), (err) => {
  if (err) {
    console.log("Error connecting to database");
    console.log(err);
  } else {
    console.log("Connected to database");
  }
});

//Express Body Parsing
app.use(express.urlencoded({ extended: true }));
app.use(express.json());
const upload = multer({});
app.use(upload.none());

//Handling Header of all requests
app.all("/*", function (req, res, next) {
  res.header("Access-Control-Allow-Origin", "*");
  res.header(
    "Access-Control-Allow-Headers",
    "Content-Type,accept,access_token,X-Requested-With"
  );
  next();
});

// A function to run queries on database
const execute = (query) => {
  return new Promise((resolve, reject) => {
    db.run(query, (result, err) => {
      if (err) {
        reject(err);
        return;
      }
      resolve(result);
    });
  });
};
// A function to read from database
const read = (query) => {
  return new Promise((resolve, reject) => {
    db.all(query, (err, result) => {
      if (err) {
        reject(err);
        return;
      }
      resolve(result);
    });
  });
};

//Format string to title Case
const title = (str) => {
  if (!str || str.trim() === "") {
    return null;
  }
  const words = str.split(" ");
  let result = "";
  words.forEach((word) => {
    result += word[0].toUpperCase() + word.slice(1) + " ";
  });
  return result.trim();
};

const getMoviesDetail = async (movie) => {
  const result = { title: movie.title, year: movie.year };
  const starsData = await read(
    `SELECT * FROM stars JOIN people ON stars.person_id = people.id WHERE stars.movie_id = ${movie.id}`
  );
  starsData.forEach((starData, i) => {
    result[`star${i + 1}_name`] = starData.name;
    result[`star${i + 1}_birth`] = starData.birth;
  });
  try {
    const directorData = await read(
      `SELECT * FROM directors JOIN people ON directors.person_id = people.id WHERE directors.movie_id = ${movie.id}`
    );
    result["director_name"] = directorData[0].name;
    result["director_birth"] = directorData[0].birth;
  } catch (e) {
    console.log(e);
    result["director_name"] = "NULL";
    result["director_birth"] = "NULL";
  }
  try {
    const ratingData = await read(
      `SELECT * FROM ratings WHERE ratings.movie_id = ${movie.id}`
    );
    result["rating"] = ratingData[0].rating;
    result["votes"] = ratingData[0].votes;
  } catch (e) {
    console.log(e);
    result["rating"] = "NULL";
    result["votes"] = "NULL";
  }
  return result;
};

//Api for searching movies with it's name
app.post("/movie_name", async (req, res) => {
  const movie_title = req.body["movie_title"];
  try {
    const query = `SELECT * FROM movies WHERE title = '${title(movie_title)}'`;
    const movie = await read(query);
    if (movie.length === 0) {
      res.status(200).send('"Movie Not Found"');
      return;
    }
    const result = await getMoviesDetail(movie[0]);
    res.status(200).send(result);
  } catch (e) {
    console.log(e);
    res.status(400).send("Server error");
  }
});

//Api for searching movies through actor's name
app.post("/actor_name", async (req, res) => {
  const actor1_name = req.body["actor1_name"];
  const actor2_name = req.body["actor2_name"];
  const limit = req.body["limit"];
  let person1 = null;
  if (actor1_name !== "" && actor1_name) {
    const isPresent = await read(
      `SELECT * FROM people WHERE name = '${title(actor1_name)}'`
    );
    if (isPresent.length === 0) {
      res.status(200).send('"Actor1 Not Found"');
      return;
    }
    person1 = isPresent[0].id;
  }
  let person2 = null;
  if (actor2_name !== "" && actor2_name) {
    const isPresent = await read(
      `SELECT * FROM people WHERE name = '${title(actor2_name)}'`
    );
    if (isPresent.length === 0) {
      res.status(200).send('"Actor2 Not Found"');
      return;
    }
    person2 = isPresent[0].id;
  }
  const movies = await read(
    `SELECT * FROM movies JOIN stars ON stars.movie_id = movies.id WHERE person_id = '${person1}' OR person_id = '${person2}'`
  );

  const movie_list = [];
  const memo = {};
  movies.forEach((movie) => {
    if (!memo[movie.id]) {
      memo[movie.id] = { count: 1, movie: movie };
      return;
    }
    memo[movie.id] = { count: 2, movie: movie };
  });
  for (let [_, { count, movie }] of Object.entries(memo)) {
    if (count === 1 && (!person1 || !person2)) {
      movie_list.push(movie);
    }
    if (count === 2 && person1 && person2) {
      movie_list.push(movie);
    }
  }
  const sliced_list = movie_list.slice(0,limit);
  const results = [];
    for (let movie of sliced_list) {
      const result = await getMoviesDetail(movie);
      results.push(result);
    }
  res.status(200).send(results);
});

//Serving Frontend File
app.get("/", (req, res) => {
  res.sendFile(path.join(__dirname, "/templates/index.html"));
});

//Invoking the app to listen on a port number
app.listen(port, () => {
  console.log(`App listening on port no. : ${port}`);
});
