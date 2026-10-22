// mediapipe_handdraw.js
//
// Draws both hands received from the tracker, and, while the tracker starts,
// a short list of what it is doing, then tells the user to show their hands.
//
// Messages:
//   left <63 floats>, right <63 floats>   hand landmarks (x, y, z per joint)
//   status <step>                         from run_mediapipe.js:
//       starting, loading, model, camera, ready,
//       stopped, not_found, camera_denied, stopped_unexpectedly, error
//   clear                                 camera off: forget hands and steps
//   bang                                  redraw (animation)

mgraphics.init();
mgraphics.relative_coords = 0;
mgraphics.autofill = 0;

var leftHand = [];
var rightHand = [];
var leftTime = 0;
var rightTime = 0;

var CONNECTIONS = [
    [0,1],[1,2],[2,3],[3,4],
    [0,5],[5,6],[6,7],[7,8],
    [0,9],[9,10],[10,11],[11,12],
    [0,13],[13,14],[14,15],[15,16],
    [0,17],[17,18],[18,19],[19,20],
    [5,9],[9,13],[13,17]
];

// ── Start-up steps ───────────────────────────────────────────────────────────

var STEPS = [
    { key: "starting", text: "Starting the hand tracker" },
    { key: "loading",  text: "Loading MediaPipe" },
    { key: "model",    text: "Loading the hand model" },
    { key: "camera",   text: "Opening the camera" }
];

var MESSAGES = {
    idle:                 ["Camera off", "Turn the camera on to start."],
    ready:                ["Camera ready", "Show your hands to the camera."],
    not_found:            ["Tracker not found", "The Max console lists the places searched."],
    camera_denied:        ["Camera not available",
                           "Allow camera access in System Settings > Privacy & Security > Camera, then turn the camera on again."],
    stopped_unexpectedly: ["The tracker stopped", "See the Max console, then turn the camera on again."],
    error:                ["The tracker could not start", "See the Max console for details."]
};

var phase = "idle";      // "idle", "steps", "ready", or a key of MESSAGES
var stepIndex = -1;      // current step while phase is "steps"
var stepSince = 0;       // when the current step began (ms)
var handSeen = false;    // at least one hand since the tracker became ready

var HAND_TIMEOUT_MS = 400;   // a hand not updated for this long is gone
var HINT_AFTER_MS = 1500;    // remind the user to show their hands
var SLOW_STEP_MS = 8000;     // reassure the user during a long first launch

// Neutral greys on the dark panel
var TEXT_MAIN = [0.88, 0.88, 0.88, 1.0];
var TEXT_DIM = [0.55, 0.55, 0.55, 1.0];
var FONT = "Arial";
var MARGIN = 36;

function now()
{
    return new Date().getTime();
}

// ── Messages ──────────────────────────────────────────────────────────────────

function left()
{
    leftHand = arrayfromargs(arguments);
    leftTime = now();
    handArrived();
}

function right()
{
    rightHand = arrayfromargs(arguments);
    rightTime = now();
    handArrived();
}

function handArrived()
{
    // Hands prove the tracker is running, even if no status was received
    phase = "ready";
    handSeen = true;
    refresh();
}

function status(step)
{
    var i;

    for (i = 0; i < STEPS.length; i++)
    {
        if (STEPS[i].key === step)
        {
            if (phase !== "steps" || i > stepIndex)
            {
                phase = "steps";
                stepIndex = i;
                stepSince = now();
            }
            refresh();
            return;
        }
    }

    if (step === "ready")
    {
        phase = "ready";
        handSeen = false;
    }
    else if (step === "stopped")
    {
        resetToIdle();
    }
    else if (MESSAGES[step])
    {
        phase = step;
    }

    refresh();
}

function clear()
{
    resetToIdle();
    refresh();
}

function resetToIdle()
{
    leftHand = [];
    rightHand = [];
    phase = "idle";
    stepIndex = -1;
    handSeen = false;
}

function bang()
{
    refresh();
}

// ── Drawing ───────────────────────────────────────────────────────────────────

function paint()
{
    var w = box.rect[2] - box.rect[0];
    var h = box.rect[3] - box.rect[1];
    var t = now();

    // transparent background

    if (phase === "steps")
    {
        drawSteps(w, h, t);
        return;
    }

    if (phase !== "ready")
    {
        drawMessage(w, h, MESSAGES[phase] || MESSAGES.idle, true);
        return;
    }

    var leftVisible = t - leftTime < HAND_TIMEOUT_MS;
    var rightVisible = t - rightTime < HAND_TIMEOUT_MS;

    if (leftVisible)
        drawHand(leftHand, w, h, 0.882, 0.588, 0.008, 1.0);

    if (rightVisible)
        drawHand(rightHand, w, h, 0.365, 0.420, 0.886, 1.0);

    if (leftVisible || rightVisible)
        return;

    if (!handSeen)
        drawMessage(w, h, MESSAGES.ready, true);
    else if (t - Math.max(leftTime, rightTime) > HINT_AFTER_MS)
        drawMessage(w, h, ["", MESSAGES.ready[1]], false);
}

// The list of start-up steps: done steps are dim with a check mark, the
// current step is bright with a pulsing dot and moving ellipsis.
function drawSteps(w, h, t)
{
    var lineHeight = 26;
    var count = stepIndex + 1;
    var slow = t - stepSince > SLOW_STEP_MS;
    var blockHeight = count * lineHeight + (slow ? lineHeight : 0);
    var y = (h - blockHeight) * 0.5 + 18;
    var x = MARGIN;
    var i;

    mgraphics.select_font_face(FONT);
    mgraphics.set_font_size(14);

    for (i = 0; i < count; i++)
    {
        var current = (i === stepIndex);

        if (current)
        {
            var pulse = 0.55 + 0.45 * Math.sin(t / 250.0);
            setColor(TEXT_MAIN, pulse);
            mgraphics.arc(x + 5, y - 5, 3.5, 0, Math.PI * 2);
            mgraphics.fill();

            setColor(TEXT_MAIN, 1.0);
            mgraphics.move_to(x + 20, y);
            mgraphics.show_text(STEPS[i].text + ellipsis(t));
        }
        else
        {
            setColor(TEXT_DIM, 1.0);
            drawCheck(x, y);
            mgraphics.move_to(x + 20, y);
            mgraphics.show_text(STEPS[i].text);
        }

        y += lineHeight;
    }

    if (slow)
    {
        mgraphics.set_font_size(12);
        setColor(TEXT_DIM, 1.0);
        mgraphics.move_to(x + 20, y);
        mgraphics.show_text("The first launch can take up to a minute.");
    }
}

// A title and a wrapped detail line, centred
function drawMessage(w, h, message, withTitle)
{
    var maxWidth = w - 2 * MARGIN;
    var lines;
    var i;
    var y;

    mgraphics.select_font_face(FONT);
    mgraphics.set_font_size(13);
    lines = wrap(message[1], maxWidth);

    var titleHeight = (withTitle && message[0]) ? 30 : 0;
    y = (h - (titleHeight + lines.length * 18)) * 0.5 + 14;

    if (titleHeight)
    {
        mgraphics.set_font_size(18);
        setColor(TEXT_MAIN, 1.0);
        drawCentred(message[0], w, y);
        y += titleHeight;
    }

    mgraphics.set_font_size(13);
    setColor(TEXT_DIM, 1.0);
    for (i = 0; i < lines.length; i++)
    {
        drawCentred(lines[i], w, y);
        y += 18;
    }
}

function drawCentred(text, w, y)
{
    var size = mgraphics.text_measure(text);
    mgraphics.move_to((w - size[0]) * 0.5, y);
    mgraphics.show_text(text);
}

function drawCheck(x, y)
{
    mgraphics.set_line_width(1.5);
    mgraphics.move_to(x + 1, y - 5);
    mgraphics.line_to(x + 4, y - 2);
    mgraphics.line_to(x + 10, y - 9);
    mgraphics.stroke();
}

function ellipsis(t)
{
    var n = Math.floor(t / 400) % 4;
    return "...".substring(0, n);
}

function wrap(text, maxWidth)
{
    var words = text.split(" ");
    var lines = [];
    var line = "";
    var i;

    for (i = 0; i < words.length; i++)
    {
        var candidate = line ? line + " " + words[i] : words[i];
        if (line && mgraphics.text_measure(candidate)[0] > maxWidth)
        {
            lines.push(line);
            line = words[i];
        }
        else
        {
            line = candidate;
        }
    }
    if (line)
        lines.push(line);
    return lines;
}

function setColor(c, alpha)
{
    mgraphics.set_source_rgba(c[0], c[1], c[2], c[3] * alpha);
}

function drawHand(hand, w, h, r, g, b, a)
{
    if(hand.length < 63)
        return;

    mgraphics.set_source_rgba(r, g, b, a);
    mgraphics.set_line_width(2);

    // skeleton

    for(var i = 0; i < CONNECTIONS.length; i++)
    {
        var p1 = CONNECTIONS[i][0];
        var p2 = CONNECTIONS[i][1];

        var x1 = hand[p1 * 3] * w;
        var y1 = (1 - hand[p1 * 3 + 1]) * h;

        var x2 = hand[p2 * 3] * w;
        var y2 = (1 - hand[p2 * 3 + 1]) * h;

        mgraphics.move_to(x1, y1);
        mgraphics.line_to(x2, y2);
    }

    mgraphics.stroke();

    // landmarks

    for(var i = 0; i < 21; i++)
    {
        var x = hand[i * 3] * w;
        var y = (1 - hand[i * 3 + 1]) * h;

        mgraphics.arc(
            x,
            y,
            4,
            0,
            Math.PI * 2
        );

        mgraphics.fill();
    }
}
