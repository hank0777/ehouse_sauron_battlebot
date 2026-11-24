"use strict";

// Project overview and editing guide: see the module docstring at the top of server.py.
// This file owns USB Gamepad/keyboard input, axis selection, normalization,
// /input polling, and SVG/stat display. The steering algorithm belongs in Python.
// Browser axis indices are device-dependent; CH labels below are only guesses.
// Selector/invert settings are not saved. Browser input is not a motor safety system.

const $ = (id) => document.getElementById(id);
const axisNames = ["CH1 X", "CH2 Y", "CH3 Z", "CH4 rotX", "CH5 rotY", "CH6 rotZ", "CH7 dial", "CH8 slider"];
const keys = new Set();
let lastDevice = "";
let busy = false;

function availablePads() {
  return Array.from(navigator.getGamepads?.() ?? []).filter(Boolean);
}

function refreshDevices() {
  const pads = availablePads();
  const current = $("gamepad").value;
  const signature = pads.map(p => `${p.index}:${p.id}:${p.axes.length}`).join("|");
  if (signature !== lastDevice) {
    $("gamepad").replaceChildren();
    if (!pads.length) $("gamepad").add(new Option("No controller detected", ""));
    for (const pad of pads) $("gamepad").add(new Option(`${pad.id} (${pad.axes.length} axes)`, pad.index));
    if (pads.some(p => String(p.index) === current)) $("gamepad").value = current;
    lastDevice = signature;
  }
  const pad = pads.find(p => String(p.index) === $("gamepad").value);
  const previousLeft = $("left-axis").value;
  const previousRight = $("right-axis").value;
  const axisCount = pad?.axes.length ?? 4;
  if ($("left-axis").options.length !== axisCount) {
    for (const id of ["left-axis", "right-axis"]) {
      const select = $(id);
      select.replaceChildren();
      for (let i = 0; i < axisCount; i++) select.add(new Option(`${i}: ${axisNames[i] ?? "axis"}`, i));
    }
    $("left-axis").value = previousLeft && Number(previousLeft) < axisCount ? previousLeft : String(Math.min(2, axisCount - 1));
    $("right-axis").value = previousRight && Number(previousRight) < axisCount ? previousRight : String(Math.min(1, axisCount - 1));
  }
  $("connection").textContent = pad ? `Connected: ${pad.id}` : "No USB joystick detected (keyboard available)";
  $("raw-axes").textContent = pad
    ? "Raw axes: " + pad.axes.map((v, i) => `${i}: ${v.toFixed(2)}`).join("   |   ")
    : "Raw axes: no controller connected.";
  return pad;
}

function normalized(axis, invert = false) {
  return Math.max(0, Math.min(100, 50 + (invert ? -1 : 1) * axis * 50));
}

function channelsFrom(pad) {
  const channels = {left_x: 50, left_y: 50, right_x: 50, right_y: 50};
  if (pad) {
    // EdgeTX Classic AETR: CH1=Ail, CH2=Ele, CH3=Thr, CH4=Rud.
    channels.left_x = normalized(pad.axes[3] ?? 0);
    channels.right_x = normalized(pad.axes[0] ?? 0);
    channels.left_y = normalized(pad.axes[Number($("left-axis").value)] ?? 0, $("left-invert").checked);
    channels.right_y = normalized(pad.axes[Number($("right-axis").value)] ?? 0, $("right-invert").checked);
    return {channels, active: true, source: "USB joystick"};
  }
  const left = Number(keys.has("KeyW")) - Number(keys.has("KeyS"));
  const right = Number(keys.has("ArrowUp")) - Number(keys.has("ArrowDown"));
  channels.left_y = 50 + 50 * left;
  channels.right_y = 50 + 50 * right;
  return {channels, active: Boolean(left || right), source: "Keyboard"};
}

function display(state) {
  const c = state.channels;
  $("bot").setAttribute("transform", `translate(${state.x} ${state.y}) rotate(${state.heading * 180 / Math.PI})`);
  $("left-label").textContent = `${Math.round(state.left_motor)}%`;
  $("right-label").textContent = `${Math.round(state.right_motor)}%`;
  $("left-stick").textContent = `${c.left_x.toFixed(1)} / ${c.left_y.toFixed(1)}`;
  $("right-stick").textContent = `${c.right_x.toFixed(1)} / ${c.right_y.toFixed(1)}`;
  $("left-motor").textContent = `${state.left_motor.toFixed(1)}%`;
  $("right-motor").textContent = `${state.right_motor.toFixed(1)}%`;
  $("heading").textContent = `${(state.heading * 180 / Math.PI).toFixed(0)}°`;
  $("source").textContent = state.active ? state.source : "Idle";
}

async function tick() {
  if (busy) return;
  busy = true;
  try {
    const pad = refreshDevices();
    const response = await fetch("/input", {
      method: "POST", headers: {"Content-Type": "application/json"},
      body: JSON.stringify(channelsFrom(pad)),
    });
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    display(await response.json());
  } catch (error) {
    $("connection").textContent = `Server unavailable: ${error.message}`;
    $("source").textContent = "Offline";
  } finally {
    busy = false;
  }
}

window.addEventListener("keydown", (event) => {
  if (["KeyW", "KeyS", "ArrowUp", "ArrowDown"].includes(event.code)
      && !["SELECT", "INPUT"].includes(document.activeElement?.tagName)) {
    event.preventDefault();
    keys.add(event.code);
  }
});
window.addEventListener("keyup", event => keys.delete(event.code));
window.addEventListener("blur", () => keys.clear());
$("reset").addEventListener("click", async () => {
  const response = await fetch("/reset", {method: "POST"});
  if (response.ok) display(await response.json());
});
refreshDevices();
setInterval(tick, 40);
