import React, { useEffect, useState } from "react";

const Films = () => {
  const [films, setFilms] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchFilms = async () => {
      try {
        const response = await fetch("http://localhost:8000/api/films/");
        if (!response.ok) {
          throw new Error("Failed to fetch films");
        }
        const data = await response.json();
        setFilms(data);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchFilms();
  }, []);

  if (loading) {
    return <p className="text-center text-lg">Loading films...</p>;
  }

  if (error) {
    return (
      <p className="text-center text-red-500">
        Error fetching films: {error}
      </p>
    );
  }

  return (
    <div className="p-6">
      <h1 className="text-3xl font-bold mb-6">Available Films</h1>
      {films.length === 0 ? (
        <p>No films found.</p>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {films.map((film) => (
            <div
              key={film.id}
              className="border rounded-xl shadow-lg p-4 bg-white hover:shadow-xl transition"
            >
              {film.poster ? (
                <img
                  src={film.poster}
                  alt={film.title}
                  className="w-full h-64 object-cover rounded-lg mb-4"
                />
              ) : (
                <div className="w-full h-64 bg-gray-200 flex items-center justify-center rounded-lg mb-4">
                  <span className="text-gray-500">No Poster</span>
                </div>
              )}

              <h2 className="text-xl font-semibold mb-2">{film.title}</h2>
              <p className="text-sm text-gray-600 mb-2">{film.description}</p>
              <p className="text-sm mb-1">
                <span className="font-semibold">Category:</span>{" "}
                {film.category ? film.category.name : "Uncategorized"}
              </p>
              <p className="text-sm mb-1">
                <span className="font-semibold">Status:</span> {film.status}
              </p>
              <p className="text-sm mb-1">
                <span className="font-semibold">Price:</span> KES {film.price}
              </p>
              {film.trailer_url && (
                <a
                  href={film.trailer_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-block mt-3 text-blue-600 hover:underline"
                >
                  Watch Trailer
                </a>
              )}
              {film.video_file && (
                <video
                  controls
                  className="w-full mt-4 rounded-lg"
                  src={film.video_file}
                >
                  Your browser does not support the video tag.
                </video>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default Films;
