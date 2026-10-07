#!/usr/bin/env node
// Validate every bank listed in banks/manifest.js. Exit 1 on any error.
// Run from learning/quiz:  node check-banks.js
const fs = require("fs"), vm = require("vm"), path = require("path");
const here = __dirname;
const ctx = { window: {} }; vm.createContext(ctx);
vm.runInContext(fs.readFileSync(path.join(here, "banks/manifest.js"), "utf8"), ctx);
const files = ctx.window.QUIZ_BANK_FILES || [];
let errors = 0, totQ = 0, totKP = 0;
const err = (m) => { console.log("ERROR " + m); errors++; };
for (const f of files) {
  const fp = path.join(here, "banks", f);
  if (!fs.existsSync(fp)) { err(f + ": listed in manifest but missing"); continue; }
  const c = { window: { QUIZ_BANKS: [] } }; vm.createContext(c);
  try { vm.runInContext(fs.readFileSync(fp, "utf8"), c); } catch (e) { err(f + ": " + e.message); continue; }
  const b = c.window.QUIZ_BANKS[0]; if (!b) { err(f + ": pushes nothing"); continue; }
  for (const k of ["topic", "section", "notePath", "knowledgePoints", "questions"]) if (!b[k]) err(f + ": missing " + k);
  if (!fs.existsSync(path.join(here, b.notePath))) err(f + ": notePath not found " + b.notePath);
  const ids = new Set(), per = {};
  for (const q of b.questions || []) {
    const tag = f + " " + q.id;
    if (ids.has(q.id)) err(tag + ": duplicate id"); ids.add(q.id);
    if (!b.knowledgePoints[q.kp]) err(tag + ": unknown kp " + q.kp); per[q.kp] = (per[q.kp] || 0) + 1;
    if (!q.prompt || !q.explanation || !q.source) err(tag + ": needs prompt, explanation, source");
    const t = q.template;
    if (t) {
      for (const n in (t.values || {})) { const v = t.values[n]; if (typeof v === "object" && !("orin" in v && "thor" in v)) err(tag + ": template value " + n + " lacks a board"); }
      if (q.type === "numeric" && !t.answerFrom) err(tag + ": numeric template needs answerFrom");
      if (q.type === "mcq" && !t.answerByBoard && !Number.isInteger(q.answer)) err(tag + ": mcq template needs answerByBoard or answer");
    } else {
      if (q.type === "mcq" && !(Array.isArray(q.choices) && Number.isInteger(q.answer) && q.answer >= 0 && q.answer < q.choices.length)) err(tag + ": bad mcq");
      if (q.type === "multi" && !(Array.isArray(q.answer) && q.answer.every(i => Number.isInteger(i) && i >= 0 && i < q.choices.length))) err(tag + ": bad multi");
      if (q.type === "numeric" && typeof q.answer !== "number") err(tag + ": numeric answer must be a number");
      if (q.type === "tf" && typeof q.answer !== "boolean") err(tag + ": tf answer must be boolean");
      if (!["mcq", "multi", "numeric", "tf"].includes(q.type)) err(tag + ": unknown type " + q.type);
    }
  }
  for (const k in b.knowledgePoints) if ((per[k] || 0) < 2) console.log("warn  " + f + ": kp " + k + " has " + (per[k] || 0) + " question(s)");
  totQ += (b.questions || []).length; totKP += Object.keys(b.knowledgePoints).length;
}
console.log(`${files.length} banks, ${totKP} knowledge points, ${totQ} questions, ${errors} error(s)`);
process.exit(errors ? 1 : 0);
