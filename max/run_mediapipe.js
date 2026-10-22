// run_mediapipe.js
//
// One launcher for the GestureCap tracker, for a Max patch, a Max Project
// or a Max standalone application. Load it with [node.script run_mediapipe.js].
//
// Finding the tracker, in this order:
// 1. "trackerpath <path>", if it was set by hand;
// 2. starting from this script's folder and going up at most 4 folders:
//        tracker/doublehand_mp/doublehand_mp
//        dist/doublehand_mp/doublehand_mp
// 3. inside a standalone: <App>.app/Contents/Resources/tracker/doublehand_mp/.
//
// Keep the tracker OUTSIDE a Max Project folder: a Max Project moves every
// file inside its folder into its own subfolders, which breaks the tracker.
// For example:
//     MyWork/
//     ├── MyProject/          (the Max Project, launcher in code/)
//     └── tracker/doublehand_mp/
//
// Messages:  camera_on, camera_off, trackerpath <path>, where
// Outlet:    status starting | running | stopped | not_found | error
//
// The tracker never outlives Max: camera_off stops it, quitting Max stops it,
// and the tracker also stops by itself if Max or this script disappears
// (see utils/parent_watch.py).

const Max = require("max-api");
const { spawn } = require("child_process");
const fs = require("fs");
const path = require("path");

const EXECUTABLE = process.platform === "win32" ? "doublehand_mp.exe" : "doublehand_mp";
const CANDIDATES = [
    path.join("tracker", "doublehand_mp", EXECUTABLE),
    path.join("dist", "doublehand_mp", EXECUTABLE),
];
const MAX_LEVELS_UP = 4;
const KILL_AFTER_MS = 3000;

let tracker = null;
let manualPath = null;

function searchUpFrom(startDir, searched) {
    let dir = startDir;
    for (let level = 0; level <= MAX_LEVELS_UP; level++) {
        for (const candidate of CANDIDATES) {
            const full = path.join(dir, candidate);
            searched.push(full);
            if (fs.existsSync(full)) {
                return full;
            }
        }
        const parent = path.dirname(dir);
        if (parent === dir) {
            break;
        }
        dir = parent;
    }
    return null;
}

// Inside a standalone, this script and Node both live in the application
function searchAppBundle(searched) {
    for (const start of [__dirname, process.execPath]) {
        const index = start.indexOf(".app" + path.sep);
        if (index < 0) {
            continue;
        }
        const full = path.join(start.slice(0, index + 4), "Contents", "Resources",
            "tracker", "doublehand_mp", EXECUTABLE);
        if (!searched.includes(full)) {
            searched.push(full);
            if (fs.existsSync(full)) {
                return full;
            }
        }
    }
    return null;
}

function findTracker() {
    if (manualPath) {
        return { found: fs.existsSync(manualPath) ? manualPath : null, searched: [manualPath] };
    }
    const searched = [];
    const found = searchUpFrom(__dirname, searched) || searchAppBundle(searched);
    return { found, searched };
}

function stopTracker() {
    const child = tracker;
    tracker = null;
    if (!child || child.exitCode !== null || child.signalCode !== null) {
        return;
    }

    const signalTracker = (signal) => {
        try {
            if (process.platform === "win32") {
                child.kill(signal);
            } else {
                process.kill(-child.pid, signal); // the tracker's process group
            }
        } catch (error) {
            if (error.code !== "ESRCH") {
                Max.post("Could not stop the tracker: " + error.message);
            }
        }
    };

    signalTracker("SIGTERM");
    const timer = setTimeout(() => signalTracker("SIGKILL"), KILL_AFTER_MS);
    timer.unref();
    child.once("close", () => clearTimeout(timer));
}

function startTracker() {
    if (tracker) {
        Max.post("The tracker is already running.");
        return;
    }

    const { found, searched } = findTracker();
    if (!found) {
        Max.post("Tracker not found. Places searched:");
        searched.forEach((place) => Max.post("  " + place));
        Max.outlet("status", "not_found");
        return;
    }

    Max.post("Starting the tracker: " + found);
    Max.outlet("status", "starting");

    const child = spawn(found, [], {
        cwd: path.dirname(found),
        stdio: ["ignore", "pipe", "pipe"],
        detached: process.platform !== "win32",
    });
    tracker = child;

    const onOutput = (data) => {
        data.toString().split("\n").forEach((line) => {
            if (!line.trim()) {
                return;
            }
            Max.post(line);
            if (tracker === child && line.startsWith("Streaming hand landmarks")) {
                Max.outlet("status", "running");
            }
        });
    };
    child.stdout.on("data", onOutput);
    child.stderr.on("data", onOutput);

    child.on("error", (error) => {
        Max.post("Tracker error: " + error.message);
        if (tracker === child) {
            tracker = null;
            Max.outlet("status", "error");
        }
    });

    child.on("close", (code, signal) => {
        Max.post("Tracker stopped (" + (signal ? "signal " + signal : "exit code " + code) + ").");
        if (tracker === child) {
            tracker = null;
        }
        Max.outlet("status", "stopped");
    });
}

Max.addHandler("camera_on", startTracker);

Max.addHandler("camera_off", () => {
    Max.post("Stopping the tracker...");
    stopTracker();
});

Max.addHandler("trackerpath", (...parts) => {
    manualPath = parts.length ? parts.join(" ") : null;
    Max.post("Tracker path set to: " + (manualPath || "automatic search"));
});

Max.addHandler("where", () => {
    const { found } = findTracker();
    Max.post("Tracker: " + (found || "not found"));
});

// Quitting Max, closing the patch or restarting this script stops the tracker
for (const signal of ["SIGTERM", "SIGINT", "SIGHUP"]) {
    process.once(signal, () => {
        stopTracker();
        process.exit(0);
    });
}
process.on("exit", stopTracker);

Max.post("GestureCap launcher ready. Tracker: " + (findTracker().found || "not found yet"));
