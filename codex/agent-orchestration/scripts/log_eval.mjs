#!/usr/bin/env node
// log_eval.mjs — sole write path for the agent-orchestration evaluation store.
// Subcommands:
//   add    append one evaluation (validates schema) and regenerate SCOREBOARD.md
//   regen  regenerate SCOREBOARD.md from evaluations.jsonl
//   kinds  list allowed task kinds
// Data dir resolution: --data-dir > AGENT_ORCH_DATA env > data-dir.txt next to
// this script > ~/.agent-orchestration

import fs from "node:fs";
import path from "node:path";
import os from "node:os";
import { fileURLToPath } from "node:url";

const SCRIPT_DIR = path.dirname(fileURLToPath(import.meta.url));
const DEFAULT_KINDS = [
  "codebase_exploration",
  "research_primary_sources",
  "planning_architecture",
  "implementation_clear_spec",
  "implementation_ambiguous",
  "bug_diagnosis",
  "code_review",
  "test_verification",
  "ui_computer_use",
  "migration_mechanical",
  "docs",
  "data_analysis",
];
const VERDICTS = ["accepted", "accepted_with_edits", "rejected", "escalated", "blocked"];
const EFFORTS = ["minimal", "low", "medium", "high", "xhigh", "max", "unknown"];

function parseArgs(argv) {
  const args = { _: [] };
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (a.startsWith("--")) {
      const key = a.slice(2);
      const next = argv[i + 1];
      if (next === undefined || next.startsWith("--")) args[key] = true;
      else { args[key] = next; i++; }
    } else args._.push(a);
  }
  return args;
}

function resolveDataDir(args) {
  if (args["data-dir"]) return path.resolve(args["data-dir"]);
  if (process.env.AGENT_ORCH_DATA) return path.resolve(process.env.AGENT_ORCH_DATA);
  const hint = path.join(SCRIPT_DIR, "data-dir.txt");
  if (fs.existsSync(hint)) {
    const p = fs.readFileSync(hint, "utf8").trim();
    if (p) return p;
  }
  return path.join(os.homedir(), ".agent-orchestration");
}

function loadKinds(dataDir) {
  const f = path.join(dataDir, "task_kinds.json");
  if (fs.existsSync(f)) return JSON.parse(fs.readFileSync(f, "utf8"));
  return [...DEFAULT_KINDS];
}

function loadEvals(dataDir) {
  const f = path.join(dataDir, "evaluations.jsonl");
  if (!fs.existsSync(f)) return [];
  return fs
    .readFileSync(f, "utf8")
    .split("\n")
    .filter((l) => l.trim())
    .map((l, i) => {
      try { return JSON.parse(l); }
      catch { throw new Error(`Corrupt JSONL line ${i + 1} in ${f}`); }
    });
}

function score(args, name) {
  const v = Number(args[name]);
  if (!Number.isInteger(v) || v < 1 || v > 10)
    fail(`--${name} must be an integer 1-10 (got: ${args[name]})`);
  return v;
}

function fail(msg) {
  console.error(`error: ${msg}`);
  process.exit(1);
}

function cmdAdd(args, dataDir) {
  fs.mkdirSync(dataDir, { recursive: true });
  let kinds = loadKinds(dataDir);

  for (const req of ["model", "task-kind", "correctness", "taste", "efficiency", "verdict", "learning"])
    if (args[req] === undefined) fail(`--${req} is required`);

  const kind = args["task-kind"];
  if (!kinds.includes(kind)) {
    if (args["new-kind"]) {
      kinds.push(kind);
      fs.writeFileSync(path.join(dataDir, "task_kinds.json"), JSON.stringify(kinds, null, 2) + "\n");
      console.error(`registered new task kind: ${kind}`);
    } else {
      fail(`unknown task kind "${kind}". Allowed: ${kinds.join(", ")}. Use --new-kind to register it deliberately.`);
    }
  }
  const verdict = args.verdict;
  if (!VERDICTS.includes(verdict)) fail(`--verdict must be one of: ${VERDICTS.join(", ")}`);
  const effort = args.effort ?? "unknown";
  if (!EFFORTS.includes(effort)) fail(`--effort must be one of: ${EFFORTS.join(", ")}`);

  const entry = {
    ts: new Date().toISOString(),
    source: "eval",
    model: String(args.model),
    effort,
    task_kind: kind,
    project: args.project ? String(args.project) : null,
    correctness: score(args, "correctness"),
    taste: score(args, "taste"),
    efficiency: score(args, "efficiency"),
    verdict,
    exploration: Boolean(args.exploration),
    duration_min: args["duration-min"] !== undefined ? Number(args["duration-min"]) : null,
    learning: String(args.learning).slice(0, 500),
  };

  fs.appendFileSync(path.join(dataDir, "evaluations.jsonl"), JSON.stringify(entry) + "\n");
  cmdRegen(dataDir);
  console.log(`logged: ${entry.model} / ${entry.task_kind} / ${entry.verdict} (c${entry.correctness} t${entry.taste} e${entry.efficiency})`);
}

const avg = (xs) => xs.reduce((a, b) => a + b, 0) / xs.length;
const fmt = (n) => (Math.round(n * 10) / 10).toFixed(1);

function cmdRegen(dataDir) {
  const evals = loadEvals(dataDir);
  const real = evals.filter((e) => e.source === "eval");
  const priors = evals.filter((e) => e.source === "prior");

  const lines = [];
  lines.push("# Model Scoreboard");
  lines.push("");
  lines.push(`Generated ${new Date().toISOString()} from ${real.length} evaluations. Do not edit by hand — regenerate via log_eval.mjs.`);
  lines.push("");
  lines.push("Rows with n >= 5 are trustworthy for routing; below that, treat as cold-start and consult the priors.");

  // Per task kind × model
  const byKind = new Map();
  for (const e of real) {
    if (!byKind.has(e.task_kind)) byKind.set(e.task_kind, new Map());
    const m = byKind.get(e.task_kind);
    if (!m.has(e.model)) m.set(e.model, []);
    m.get(e.model).push(e);
  }
  lines.push("");
  lines.push("## By task kind");
  if (byKind.size === 0) lines.push("", "_No evaluated runs yet._");
  for (const [kind, models] of [...byKind.entries()].sort()) {
    lines.push("", `### ${kind}`, "");
    lines.push("| model | n | correctness | taste | efficiency | overall | expl | accepted% |");
    lines.push("|---|---|---|---|---|---|---|---|");
    const rows = [...models.entries()].map(([model, es]) => {
      const overall = avg(es.map((e) => (e.correctness + e.taste + e.efficiency) / 3));
      const acc = es.filter((e) => e.verdict === "accepted" || e.verdict === "accepted_with_edits").length / es.length;
      return { model, es, overall, acc };
    }).sort((a, b) => b.overall - a.overall);
    for (const r of rows) {
      lines.push(
        `| ${r.model} | ${r.es.length} | ${fmt(avg(r.es.map((e) => e.correctness)))} | ${fmt(avg(r.es.map((e) => e.taste)))} | ${fmt(avg(r.es.map((e) => e.efficiency)))} | ${fmt(r.overall)} | ${r.es.filter((e) => e.exploration).length} | ${Math.round(r.acc * 100)}% |`
      );
    }
  }

  // Effort comparison (does xhigh/max ever pay off?)
  const byEffort = new Map();
  for (const e of real) {
    if (!byEffort.has(e.effort)) byEffort.set(e.effort, []);
    byEffort.get(e.effort).push(e);
  }
  lines.push("", "## By reasoning effort", "");
  lines.push("| effort | n | overall | accepted% |");
  lines.push("|---|---|---|---|");
  for (const [effort, es] of [...byEffort.entries()].sort()) {
    const overall = avg(es.map((e) => (e.correctness + e.taste + e.efficiency) / 3));
    const acc = es.filter((e) => e.verdict === "accepted" || e.verdict === "accepted_with_edits").length / es.length;
    lines.push(`| ${effort} | ${es.length} | ${fmt(overall)} | ${Math.round(acc * 100)}% |`);
  }

  // Priors
  lines.push("", "## Priors (cold-start defaults, source: video + research doc)", "");
  lines.push("| model | intelligence | taste | cost-friendliness | note |");
  lines.push("|---|---|---|---|---|");
  for (const p of priors)
    lines.push(`| ${p.model} | ${p.intelligence ?? "-"} | ${p.taste ?? "-"} | ${p.cost ?? "-"} | ${p.note ?? ""} |`);

  // Recent learnings
  lines.push("", "## Recent learnings", "");
  for (const e of real.slice(-15).reverse())
    lines.push(`- **${e.model}** (${e.task_kind}, ${e.verdict}): ${e.learning}`);
  if (real.length === 0) lines.push("_None yet._");
  lines.push("");

  fs.mkdirSync(dataDir, { recursive: true });
  fs.writeFileSync(path.join(dataDir, "SCOREBOARD.md"), lines.join("\n"));
}

const args = parseArgs(process.argv.slice(2));
const cmd = args._[0];
const dataDir = resolveDataDir(args);

if (cmd === "add") cmdAdd(args, dataDir);
else if (cmd === "regen") { cmdRegen(dataDir); console.log(`regenerated ${path.join(dataDir, "SCOREBOARD.md")}`); }
else if (cmd === "kinds") console.log(loadKinds(dataDir).join("\n"));
else fail("usage: log_eval.mjs <add|regen|kinds> [--data-dir path] [options]");
