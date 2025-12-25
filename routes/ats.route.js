import express from "express";
import multer from "multer";
import { spawn } from "child_process";
import fs from "fs";
import path from "path";

const router = express.Router();
const uploadDir = "uploads";
if (!fs.existsSync(uploadDir)) {
  fs.mkdirSync(uploadDir);
}
const upload = multer({ dest: uploadDir,
    limits: { fileSize: 2 * 1024 * 1024 }, // 2MB
  fileFilter: (req, file, cb) => {
    if (file.mimetype !== "application/pdf") {
      cb(new Error("Only PDF files are allowed"));
    }
    cb(null, true);
  }
 });




router.post("/check", upload.single("resume"), (req, res) => {
  try {
    

    const resumePath = req.file.path;
    const jobDescription = req.body.job_description;

    const pythonScript = path.join(
      process.cwd(),
      "ats_checker",
      "ats_checker.py"
    );
    // const pythonExe = "C:\\ProgramData\\anaconda3\\python.exe";
    const pythonExe = process.env.PYTHON_PATH || "python";

    const python = spawn(pythonExe, [pythonScript, resumePath]);


    let output = "";
    let error = "";

    python.stdout.on("data", (data) => {
      output += data.toString();
    });

    python.stderr.on("data", (data) => {
      error += data.toString();
    });

    python.stdin.write(jobDescription);
    python.stdin.end();

    python.on("close", () => {
      fs.unlinkSync(resumePath);

      if (error) {
        return res.status(500).json({ error });
      }

      try {
        const parsed = JSON.parse(output);
        return res.json(parsed);
      } catch {
        return res.status(500).json({
          error: "Invalid response from ATS engine",
          raw: output,
        });
      }
    });
  } catch (err) {
    return res.status(500).json({ error: "ATS route failed" });
  }
});

export default router;
