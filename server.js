const express = require("express");
const bodyParser = require("body-parser");
const { spawn } = require("child_process"); // To run the Python script
const fs = require("fs"); // To read the JSON file
const cors = require("cors");

const multer = require("multer");
const storage = multer.diskStorage({
  destination: (req, file, cb) => {
    cb(null, "./uploads");
  },
  filename: (req, file, cb) => {
    cb(null, Date.now() + "-" + file.originalname);
  },
});

const upload = multer({ storage: storage });

const app = express();
app.use(bodyParser.json());

require("dotenv").config();
const { Pool } = require("pg");

// PostgreSQL Connection Pool
const pool = new Pool({
  user: process.env.DB_USER,
  host: process.env.DB_HOST,
  database: process.env.DB_DATABASE,
  password: process.env.DB_PASSWORD,
  port: process.env.DB_PORT,
});

app.use(
  cors({
    origin: "http://localhost:5173",
    credentials: true,
  })
);

app.post("/api/transform-data", upload.single("file"), (req, res) => {
  try {
    const file = req.file;
    const selectedOption = req.body.selectedOption;
    const filterSize = req.body.filterSize;
    const windowType = req.body.windowType;
    const overlap = req.body.overlap;

    // console.log("File uploaded:", file);
    // console.log("Selected Option:", selectedOption);
    // console.log("Filter Size:", filterSize);
    // console.log("Window Type:", windowType);
    // console.log("Overlap:", overlap);

    // Save the uploaded file to a temporary location
    const tempFilePath = req.file.path;
    fs.readFile(tempFilePath, (err) => {
      if (err) {
        console.error(err);
      } else {
        // Run Python script using `spawn`
        const pythonProcess = spawn("python", [
          "./script.py",
          "transform",
          tempFilePath,
          "./output.json",
          selectedOption,
          filterSize,
          windowType,
          overlap,
        ]);

        // Capture any output from the Python script (optional for logging)
        pythonProcess.stdout.on("data", (data) => {
          console.log(`Python Output: ${data}`);
        });

        // Capture errors from the Python script
        pythonProcess.stderr.on("data", (data) => {
          console.error(`Python Error: ${data}`);
        });

        // When the Python script finishes
        pythonProcess.on("close", (code) => {
          console.log(`Python script exited with code ${code}`);

          // Read the generated JSON file
          fs.readFile("./output.json", "utf8", (err, jsonData) => {
            if (err) {
              return res
                .status(500)
                .json({ error: "Error reading the output JSON file" });
            }

            // Send the JSON data as a response
            // try {
            //   const fftData = JSON.parse(jsonData);

            //   // Insert the FFT data into PostgreSQL
            //   const query = `
            //             INSERT INTO fft_results (analysis_data)
            //             VALUES ($1)
            //             RETURNING id;
            //         `;
            //   const values = [jsonData];

            //   pool.query(query, values, (error, result) => {
            //     if (error) {
            //       console.log("Error inserting data into PostgreSQL:", error);
            //       return res
            //         .status(500)
            //         .json({ error: "Error inserting data into PostgreSQL" });
            //     }
            //     // Respond with the inserted row's ID or any other success message
            //     res.json({ success: true, id: result.rows[0].id });
            //   });
            // } catch (parseError) {
            //   res
            //     .status(500)
            //     .json({ error: "Error parsing the output JSON file" });
            // }

            // Send the JSON data as a response and get it downloaded
            // Send the JSON data as a response and get it downloaded
            res.set(
              "Content-Disposition",
              `attachment; filename="${selectedOption}-transformed.json"`
            );
            res.set("Content-Type", "application/json");
            res.send(jsonData);
          });
        });
      }
    });
  } catch (error) {
    console.error(error);
    res.status(500).json({ error: "Error processing the request" });
  }
});

app.get("/api/get-analysis-data", (req, res) => {
  const query = `
    SELECT analysis_data
    FROM fft_results
    ORDER BY id DESC
    LIMIT 1;
  `;

  pool.query(query, (error, result) => {
    if (error) {
      console.log("Error retrieving data from PostgreSQL:", error);
      return res
        .status(500)
        .json({ error: "Error retrieving data from PostgreSQL" });
    }
    // Respond with the retrieved data
    res.json(result.rows[0].analysis_data);
  });
});

app.post("/api/filter", upload.single("file"), (req, res) => {
  try {
    const filterData = req.body;
    const { filterType, order, cutIn, cutOut, sampleRate } = filterData;
    const file = req.file;

    // Validate the input data
    if (!filterType || !order || !cutIn || !cutOut) {
      res.status(400).send({ message: "Invalid input data" });
      return;
    }

    const tempFilePath = req.file.path;
    fs.readFile(tempFilePath, (err) => {
      if (err) {
        console.error(err);
      } else {
        // Run Python script using `spawn`
        const pythonProcess = spawn("python", [
          "./script.py",
          "filter",
          tempFilePath,
          "./output_filter.json",
          filterType,
          order,
          cutIn,
          cutOut,
          sampleRate
        ]);

        // Capture any output from the Python script (optional for logging)
        pythonProcess.stdout.on("data", (data) => {
          console.log(`Python Output: ${data}`);
        });

        // Capture errors from the Python script
        pythonProcess.stderr.on("data", (data) => {
          console.error(`Python Error: ${data}`);
        });

        // When the Python script finishes
        pythonProcess.on("close", (code) => {
          console.log(`Python script exited with code ${code}`);

          // Read the generated JSON file
          fs.readFile("./output_filter.json", "utf8", (err, jsonData) => {
            if (err) {
              return res
                .status(500)
                .json({ error: "Error reading the output JSON file" });
            }

            res.set(
              "Content-Disposition",
              `attachment; filename="${filterType}-filtered.json"`
            );
            res.set("Content-Type", "application/json");
            res.send(jsonData);
          });
        });
      }
    });
  } catch (error) {
    console.error(error);
    res.status(500).json({ error: "Error processing the request" });
  }
});
app.get("/run-fft", (req, res) => {
  const inputFilePath = "./raw.tsv";
  const outputFilePath = "./output.json";

  // Run Python script using `spawn`
  const pythonProcess = spawn("python", [
    "./script.py",
    inputFilePath,
    outputFilePath,
  ]);

  // Capture any output from the Python script (optional for logging)
  pythonProcess.stdout.on("data", (data) => {
    console.log(`Python Output: ${data}`);
  });

  // Capture errors from the Python script
  pythonProcess.stderr.on("data", (data) => {
    console.error(`Python Error: ${data}`);
  });

  // When the Python script finishes
  pythonProcess.on("close", (code) => {
    console.log(`Python script exited with code ${code}`);

    // Read the generated JSON file
    fs.readFile(outputFilePath, "utf8", (err, jsonData) => {
      if (err) {
        return res
          .status(500)
          .json({ error: "Error reading the output JSON file" });
      }

      // Send the JSON data as a response
      try {
        const fftData = JSON.parse(jsonData);

        // Ensure that the data has the correct structure
        if (!fftData.data || !fftData.Sampling_frequency) {
          return res.status(400).json({ error: "Invalid data structure" });
        }

        // Insert the FFT data into PostgreSQL
        const query = `
                      INSERT INTO fft_results_1 (sampling_frequency, fft_data) 
                      VALUES ($1, $2)
                      RETURNING id;
                  `;
        const values = [fftData.Sampling_frequency, fftData.data];

        pool.query(query, values, (error, result) => {
          if (error) {
            console.log("Error inserting data into PostgreSQL:", error);
            return res
              .status(500)
              .json({ error: "Error inserting data into PostgreSQL" });
          }
          // Respond with the inserted row's ID or any other success message
          res.json({ success: true, id: result.rows[0].id });
        });
      } catch (parseError) {
        res.status(500).json({ error: "Error parsing the output JSON file" });
      }
    });
  });
});

const PORT = process.env.PORT || 5000;
app.listen(PORT, () => {
  console.log(`Server is running on port ${PORT}`);
});
