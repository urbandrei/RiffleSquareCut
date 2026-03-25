(function () {
  "use strict";

  // ── Configuration ──────────────────────────────────────────────
  // Detect the server origin from the script tag src
  var scripts = document.getElementsByTagName("script");
  var scriptSrc = "";
  for (var i = 0; i < scripts.length; i++) {
    if (scripts[i].src && scripts[i].src.indexOf("widget.js") !== -1) {
      scriptSrc = scripts[i].src;
      break;
    }
  }
  var SERVER_ORIGIN = scriptSrc
    ? scriptSrc.replace(/\/static\/widget\.js.*$/, "")
    : window.location.origin;

  var WS_URL =
    SERVER_ORIGIN.replace(/^http/, "ws") + "/ws";
  var STATUS_URL = SERVER_ORIGIN + "/api/status";

  // ── Design Tokens ──────────────────────────────────────────────
  var C = {
    black: "#0a0a0f",
    red: "#EF3B38",
    blue: "#4EC8ED",
    darkGray: "#1a1a24",
    medGray: "#2a2a34",
    lightGray: "#888",
    white: "#ffffff",
    panelBg: "#0d0d14",
    inputBg: "#14141e",
  };

  // ── State ──────────────────────────────────────────────────────
  var ws = null;
  var sessionId = sessionStorage.getItem("rsc_chat_session");
  var isOpen = false;
  var staffOnline = false;
  var connected = false;
  var pendingMessage = "";
  var messageHistory = [];
  var unreadCount = 0;

  // ── DOM refs ───────────────────────────────────────────────────
  var container,
    bubble,
    bubbleDot,
    bubbleBadge,
    panel,
    header,
    messagesArea,
    inputArea,
    textInput,
    sendBtn,
    emailOverlay;

  // ── Inject Fonts ───────────────────────────────────────────────
  var fontLink = document.createElement("link");
  fontLink.href =
    "https://fonts.googleapis.com/css2?family=Rajdhani:wght@500;700&family=Inter:wght@400;500&display=swap";
  fontLink.rel = "stylesheet";
  document.head.appendChild(fontLink);

  // ── Inject Styles ─────────────────────────────────────────────
  var style = document.createElement("style");
  style.textContent = [
    "#rsc-chat-container { position: fixed; bottom: 20px; right: 20px; z-index: 999999; font-family: 'Inter', sans-serif; }",
    "#rsc-chat-container * { box-sizing: border-box; margin: 0; padding: 0; }",

    /* Bubble */
    "#rsc-chat-bubble { width: 60px; height: 60px; border-radius: 50%; background: " + C.red + "; cursor: pointer; display: flex; align-items: center; justify-content: center; box-shadow: 0 4px 20px rgba(239,59,56,0.4); transition: transform 0.2s, box-shadow 0.2s; position: relative; }",
    "#rsc-chat-bubble:hover { transform: scale(1.08); box-shadow: 0 4px 28px rgba(239,59,56,0.6); }",
    "#rsc-chat-bubble svg { width: 28px; height: 28px; fill: " + C.white + "; }",
    "#rsc-chat-bubble-dot { width: 12px; height: 12px; border-radius: 50%; position: absolute; top: 2px; right: 2px; border: 2px solid " + C.black + "; transition: background 0.3s; }",
    "#rsc-chat-bubble-badge { position: absolute; top: -4px; left: -4px; min-width: 20px; height: 20px; border-radius: 10px; background: " + C.blue + "; color: " + C.black + "; font-size: 11px; font-weight: 700; display: none; align-items: center; justify-content: center; padding: 0 5px; }",

    /* Panel */
    "#rsc-chat-panel { display: none; width: 380px; height: 520px; background: " + C.panelBg + "; border-radius: 16px 16px 12px 12px; overflow: hidden; flex-direction: column; box-shadow: 0 8px 40px rgba(0,0,0,0.6); margin-bottom: 12px; border: 1px solid #1e1e2a; }",
    "#rsc-chat-panel.open { display: flex; }",

    /* Header */
    "#rsc-chat-header { background: " + C.black + "; padding: 14px 16px; display: flex; align-items: center; justify-content: space-between; border-bottom: 2px solid " + C.red + "; }",
    "#rsc-chat-header-title { font-family: 'Rajdhani', sans-serif; font-weight: 700; font-size: 16px; color: " + C.white + "; letter-spacing: 2px; text-transform: uppercase; }",
    "#rsc-chat-header-status { display: flex; align-items: center; gap: 6px; font-size: 11px; color: " + C.lightGray + "; }",
    "#rsc-chat-header-status-dot { width: 8px; height: 8px; border-radius: 50%; }",
    "#rsc-chat-close { background: none; border: none; color: " + C.lightGray + "; font-size: 20px; cursor: pointer; padding: 0 4px; line-height: 1; }",
    "#rsc-chat-close:hover { color: " + C.white + "; }",

    /* Messages */
    "#rsc-chat-messages { flex: 1; overflow-y: auto; padding: 16px; display: flex; flex-direction: column; gap: 8px; }",
    "#rsc-chat-messages::-webkit-scrollbar { width: 6px; }",
    "#rsc-chat-messages::-webkit-scrollbar-track { background: " + C.darkGray + "; }",
    "#rsc-chat-messages::-webkit-scrollbar-thumb { background: " + C.red + "; border-radius: 3px; }",

    /* Message bubbles */
    ".rsc-msg { max-width: 80%; padding: 10px 14px; border-radius: 12px; font-size: 14px; line-height: 1.45; word-wrap: break-word; }",
    ".rsc-msg-visitor { align-self: flex-end; background: " + C.red + "; color: " + C.white + "; border-bottom-right-radius: 4px; }",
    ".rsc-msg-staff { align-self: flex-start; background: " + C.medGray + "; color: " + C.white + "; border-bottom-left-radius: 4px; }",
    ".rsc-msg-staff-name { font-size: 11px; color: " + C.blue + "; margin-bottom: 3px; font-weight: 500; }",
    ".rsc-msg-system { align-self: center; background: " + C.darkGray + "; color: " + C.lightGray + "; font-size: 12px; text-align: center; border-radius: 8px; padding: 8px 14px; }",
    ".rsc-msg-time { font-size: 10px; color: " + C.lightGray + "; margin-top: 4px; text-align: right; }",

    /* Timeout prompt */
    ".rsc-timeout-prompt { align-self: center; background: " + C.darkGray + "; border: 1px solid #2e2e3a; border-radius: 10px; padding: 12px 16px; text-align: center; font-size: 13px; color: " + C.lightGray + "; }",
    ".rsc-timeout-prompt p { margin-bottom: 10px; }",
    ".rsc-timeout-btns { display: flex; gap: 8px; justify-content: center; }",
    ".rsc-timeout-btn { padding: 6px 14px; border-radius: 6px; border: none; cursor: pointer; font-size: 12px; font-weight: 500; font-family: 'Inter', sans-serif; }",
    ".rsc-timeout-btn-wait { background: " + C.medGray + "; color: " + C.white + "; }",
    ".rsc-timeout-btn-email { background: " + C.blue + "; color: " + C.black + "; }",

    /* Input area */
    "#rsc-chat-input { display: flex; padding: 12px; gap: 8px; background: " + C.black + "; border-top: 1px solid #1e1e2a; }",
    "#rsc-chat-text { flex: 1; background: " + C.inputBg + "; border: 1px solid #2a2a36; border-radius: 8px; padding: 10px 12px; color: " + C.white + "; font-size: 14px; font-family: 'Inter', sans-serif; outline: none; resize: none; }",
    "#rsc-chat-text::placeholder { color: " + C.lightGray + "; }",
    "#rsc-chat-text:focus { border-color: " + C.red + "; }",
    "#rsc-chat-send { width: 40px; height: 40px; background: " + C.red + "; border: none; border-radius: 8px; cursor: pointer; display: flex; align-items: center; justify-content: center; transition: background 0.2s; }",
    "#rsc-chat-send:hover { background: #d63230; }",
    "#rsc-chat-send svg { width: 18px; height: 18px; fill: " + C.white + "; }",

    /* Email overlay */
    "#rsc-email-overlay { display: none; position: absolute; bottom: 0; left: 0; right: 0; background: " + C.panelBg + "; padding: 20px 16px; border-top: 2px solid " + C.blue + "; }",
    "#rsc-email-overlay.show { display: block; }",
    "#rsc-email-overlay p { font-size: 13px; color: " + C.lightGray + "; margin-bottom: 12px; line-height: 1.4; }",
    "#rsc-email-input { width: 100%; background: " + C.inputBg + "; border: 1px solid #2a2a36; border-radius: 8px; padding: 10px 12px; color: " + C.white + "; font-size: 14px; font-family: 'Inter', sans-serif; outline: none; margin-bottom: 10px; }",
    "#rsc-email-input:focus { border-color: " + C.blue + "; }",
    "#rsc-email-submit { width: 100%; padding: 10px; background: " + C.blue + "; color: " + C.black + "; border: none; border-radius: 8px; font-size: 14px; font-weight: 600; cursor: pointer; font-family: 'Inter', sans-serif; }",
    "#rsc-email-submit:hover { background: #3ab5d9; }",
    "#rsc-email-cancel { width: 100%; padding: 8px; background: none; color: " + C.lightGray + "; border: none; font-size: 12px; cursor: pointer; margin-top: 6px; font-family: 'Inter', sans-serif; }",

    /* Welcome message */
    ".rsc-welcome { text-align: center; padding: 30px 20px; color: " + C.lightGray + "; }",
    ".rsc-welcome h3 { font-family: 'Rajdhani', sans-serif; font-size: 20px; color: " + C.white + "; margin-bottom: 8px; font-weight: 700; }",
    ".rsc-welcome p { font-size: 13px; line-height: 1.5; }",

    /* Responsive */
    "@media (max-width: 440px) { #rsc-chat-panel { width: calc(100vw - 24px); height: calc(100vh - 100px); border-radius: 12px; } #rsc-chat-container { bottom: 12px; right: 12px; } }",
  ].join("\n");
  document.head.appendChild(style);

  // ── Build DOM ──────────────────────────────────────────────────
  function build() {
    container = el("div", { id: "rsc-chat-container" });

    // Panel
    panel = el("div", { id: "rsc-chat-panel" });

    // Header
    header = el("div", { id: "rsc-chat-header" });
    var headerLeft = el("div", { style: "display:flex;align-items:center;gap:10px;" });
    var title = el("span", { id: "rsc-chat-header-title" }, "RIFFLE SQUARE CUT");
    var statusWrap = el("div", { id: "rsc-chat-header-status" });
    var statusDot = el("div", { id: "rsc-chat-header-status-dot" });
    var statusText = el("span", {}, "Offline");
    statusWrap.appendChild(statusDot);
    statusWrap.appendChild(statusText);
    headerLeft.appendChild(title);
    headerLeft.appendChild(statusWrap);

    var closeBtn = el("button", { id: "rsc-chat-close" }, "\u00d7");
    closeBtn.addEventListener("click", togglePanel);

    header.appendChild(headerLeft);
    header.appendChild(closeBtn);

    // Messages area
    messagesArea = el("div", { id: "rsc-chat-messages" });

    // Welcome message
    var welcome = el("div", { className: "rsc-welcome" });
    var wh = el("h3", {}, "Welcome!");
    var wp = el("p", {}, "Send us a message and we'll get back to you as soon as possible.");
    welcome.appendChild(wh);
    welcome.appendChild(wp);
    messagesArea.appendChild(welcome);

    // Input area
    inputArea = el("div", { id: "rsc-chat-input" });
    textInput = el("textarea", {
      id: "rsc-chat-text",
      placeholder: "Type a message...",
      rows: "1",
    });
    textInput.addEventListener("keydown", function (e) {
      if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        doSend();
      }
    });

    sendBtn = el("button", { id: "rsc-chat-send" });
    sendBtn.innerHTML =
      '<svg viewBox="0 0 24 24"><path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"/></svg>';
    sendBtn.addEventListener("click", doSend);

    inputArea.appendChild(textInput);
    inputArea.appendChild(sendBtn);

    // Email overlay
    emailOverlay = el("div", { id: "rsc-email-overlay" });

    panel.appendChild(header);
    panel.appendChild(messagesArea);
    panel.appendChild(inputArea);
    panel.appendChild(emailOverlay);
    panel.style.position = "relative";

    // Bubble
    bubble = el("div", { id: "rsc-chat-bubble" });
    bubble.innerHTML =
      '<svg viewBox="0 0 24 24"><path d="M20 2H4c-1.1 0-2 .9-2 2v18l4-4h14c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2z"/></svg>';
    bubbleDot = el("div", { id: "rsc-chat-bubble-dot" });
    bubbleBadge = el("div", { id: "rsc-chat-bubble-badge" }, "0");
    bubble.appendChild(bubbleDot);
    bubble.appendChild(bubbleBadge);
    bubble.addEventListener("click", togglePanel);

    container.appendChild(panel);
    container.appendChild(bubble);
    document.body.appendChild(container);

    updateStatusIndicator();
  }

  // ── Helpers ────────────────────────────────────────────────────
  function el(tag, attrs, text) {
    var e = document.createElement(tag);
    if (attrs) {
      for (var k in attrs) {
        if (k === "className") e.className = attrs[k];
        else e.setAttribute(k, attrs[k]);
      }
    }
    if (text) e.textContent = text;
    return e;
  }

  function togglePanel() {
    isOpen = !isOpen;
    if (isOpen) {
      panel.classList.add("open");
      bubble.style.display = "none";
      textInput.focus();
      unreadCount = 0;
      updateBadge();
      if (!ws || ws.readyState !== WebSocket.OPEN) {
        connect();
      }
    } else {
      panel.classList.remove("open");
      bubble.style.display = "flex";
    }
  }

  function updateStatusIndicator() {
    var dot = document.getElementById("rsc-chat-header-status-dot");
    var text = document.getElementById("rsc-chat-header-status");
    if (!dot) return;
    dot.style.background = staffOnline ? C.blue : "#555";
    if (text && text.lastChild) {
      text.lastChild.textContent = staffOnline ? "Online" : "Offline";
    }
    bubbleDot.style.background = staffOnline ? C.blue : "#555";
  }

  function updateBadge() {
    if (unreadCount > 0 && !isOpen) {
      bubbleBadge.textContent = unreadCount > 9 ? "9+" : unreadCount;
      bubbleBadge.style.display = "flex";
    } else {
      bubbleBadge.style.display = "none";
    }
  }

  function scrollToBottom() {
    messagesArea.scrollTop = messagesArea.scrollHeight;
  }

  function addMessage(sender, name, text) {
    // Remove welcome message on first real message
    var welcome = messagesArea.querySelector(".rsc-welcome");
    if (welcome) welcome.remove();

    var wrap = el("div", { className: "rsc-msg rsc-msg-" + sender });

    if (sender === "staff" && name) {
      var nameEl = el("div", { className: "rsc-msg-staff-name" }, name);
      wrap.appendChild(nameEl);
    }

    var textEl = document.createTextNode(text);
    wrap.appendChild(textEl);

    var time = el("div", { className: "rsc-msg-time" }, formatTime(new Date()));
    wrap.appendChild(time);

    messagesArea.appendChild(wrap);
    scrollToBottom();

    if (sender === "staff" && !isOpen) {
      unreadCount++;
      updateBadge();
    }

    messageHistory.push({ sender: sender, name: name, text: text });
  }

  function addSystemMessage(text) {
    var msg = el("div", { className: "rsc-msg rsc-msg-system" }, text);
    messagesArea.appendChild(msg);
    scrollToBottom();
  }

  function formatTime(d) {
    var h = d.getHours();
    var m = d.getMinutes();
    var ampm = h >= 12 ? "PM" : "AM";
    h = h % 12 || 12;
    return h + ":" + (m < 10 ? "0" : "") + m + " " + ampm;
  }

  // ── Send Message ───────────────────────────────────────────────
  function doSend() {
    var text = textInput.value.trim();
    if (!text) return;
    if (!ws || ws.readyState !== WebSocket.OPEN) return;

    ws.send(JSON.stringify({ action: "message", text: text }));
    addMessage("visitor", null, text);
    textInput.value = "";
    textInput.focus();
  }

  // ── Email Prompt ───────────────────────────────────────────────
  function showEmailPrompt(reason) {
    emailOverlay.innerHTML = "";
    emailOverlay.classList.add("show");

    var p = el("p", {}, reason || "Leave your email and we'll follow up.");
    var input = el("input", {
      id: "rsc-email-input",
      type: "email",
      placeholder: "your@email.com",
    });
    var submit = el("button", { id: "rsc-email-submit" }, "Send");
    var cancel = el("button", { id: "rsc-email-cancel" }, "Cancel");

    submit.addEventListener("click", function () {
      var email = input.value.trim();
      if (!email || email.indexOf("@") === -1) {
        input.style.borderColor = C.red;
        return;
      }
      if (ws && ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify({ action: "email", email: email }));
      }
      emailOverlay.classList.remove("show");
    });

    cancel.addEventListener("click", function () {
      emailOverlay.classList.remove("show");
    });

    emailOverlay.appendChild(p);
    emailOverlay.appendChild(input);
    emailOverlay.appendChild(submit);
    emailOverlay.appendChild(cancel);

    setTimeout(function () {
      input.focus();
    }, 100);
  }

  function showTimeoutPrompt() {
    var existing = messagesArea.querySelector(".rsc-timeout-prompt");
    if (existing) existing.remove();

    var wrap = el("div", { className: "rsc-timeout-prompt" });
    var p = el("p", {}, "Still waiting for a response. Would you like to continue waiting or leave your email for follow-up?");
    var btns = el("div", { className: "rsc-timeout-btns" });

    var waitBtn = el("button", { className: "rsc-timeout-btn rsc-timeout-btn-wait" }, "Keep Waiting");
    waitBtn.addEventListener("click", function () {
      wrap.remove();
    });

    var emailBtn = el("button", { className: "rsc-timeout-btn rsc-timeout-btn-email" }, "Leave Email");
    emailBtn.addEventListener("click", function () {
      wrap.remove();
      showEmailPrompt("Leave your email and we'll follow up as soon as possible.");
    });

    btns.appendChild(waitBtn);
    btns.appendChild(emailBtn);
    wrap.appendChild(p);
    wrap.appendChild(btns);
    messagesArea.appendChild(wrap);
    scrollToBottom();
  }

  // ── WebSocket ──────────────────────────────────────────────────
  function connect() {
    if (ws && (ws.readyState === WebSocket.OPEN || ws.readyState === WebSocket.CONNECTING)) {
      return;
    }

    try {
      ws = new WebSocket(WS_URL);
    } catch (e) {
      return;
    }

    ws.onopen = function () {
      connected = true;
      ws.send(
        JSON.stringify({
          action: "connect",
          session_id: sessionId,
        })
      );
    };

    ws.onmessage = function (event) {
      var data;
      try {
        data = JSON.parse(event.data);
      } catch (e) {
        return;
      }

      switch (data.type) {
        case "connected":
          sessionId = data.session_id;
          sessionStorage.setItem("rsc_chat_session", sessionId);
          staffOnline = data.staff_online;
          updateStatusIndicator();
          break;

        case "message":
          addMessage("staff", data.name, data.text);
          break;

        case "staff_status":
          staffOnline = data.online;
          updateStatusIndicator();
          break;

        case "timeout_prompt":
          showTimeoutPrompt();
          break;

        case "email_required":
          showEmailPrompt(data.reason);
          break;

        case "email_confirmed":
          addSystemMessage(data.message);
          break;

        case "session_closed":
          addSystemMessage("Chat session ended. Thank you!");
          sessionStorage.removeItem("rsc_chat_session");
          sessionId = null;
          break;
      }
    };

    ws.onclose = function () {
      connected = false;
      // Reconnect after 3 seconds if panel is still open
      setTimeout(function () {
        if (isOpen) connect();
      }, 3000);
    };

    ws.onerror = function () {
      // onclose will fire after this
    };
  }

  // ── Staff Status Polling ───────────────────────────────────────
  function pollStatus() {
    fetch(STATUS_URL)
      .then(function (r) {
        return r.json();
      })
      .then(function (data) {
        staffOnline = data.staff_online;
        updateStatusIndicator();
      })
      .catch(function () {});
  }

  // ── Init ───────────────────────────────────────────────────────
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }

  function init() {
    build();
    pollStatus();
    setInterval(pollStatus, 30000);
  }
})();
