#!/usr/bin/env node

import { execFileSync } from "node:child_process";
import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import path from "node:path";
import { buildQueues, findIssueFiles, readMarkdown } from "./issue-utils.mjs";

const args = process.argv.slice(2);
const targets = [];
let assignedIssue = "";
for (let i = 0; i < args.length; i += 1) {
  if (args[i] === "--issue") {
    assignedIssue = args[i + 1] || "";
    i += 1;
  } else {
    targets.push(args[i]);
  }
}
const root = process.cwd();
const skillDir = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const basePrompt = readFileSync(path.join(skillDir, "PROMPT.md"), "utf8");

function recentCommits() {
  try {
    return execFileSync("git", ["log", "-n", "5", "--format=%H%n%ad%n%B---", "--date=short"], {
      cwd: root,
      encoding: "utf8",
      stdio: ["ignore", "pipe", "ignore"],
    }).trim();
  } catch {
    return "No commits found";
  }
}

const files = findIssueFiles(targets, root);
const { currentBatch, parallelBatches, skipped } = buildQueues(files, root);
const assignedPath = assignedIssue ? path.resolve(root, assignedIssue) : "";
const assigned = assignedPath
  ? [...currentBatch, ...parallelBatches.flat(), ...skipped].find((issue) => path.resolve(root, issue.file) === assignedPath || issue.absoluteFile === assignedPath)
  : null;

if (assignedPath && !assigned) {
  console.error(`Assigned issue not found in scanned targets: ${assignedIssue}`);
  process.exit(1);
}

console.log("# Previous Commits");
console.log("");
console.log(recentCommits());
console.log("");

if (assigned) {
  console.log("# Assigned Issue");
  console.log("");
  console.log(`## ${assigned.file}`);
  console.log("");
  console.log(readMarkdown(assigned.absoluteFile).trim());
  console.log("");
} else {
  console.log("# Current Parallel Batch");
  console.log("");
  if (currentBatch.length === 0) {
    console.log("No ready AFK issues found.");
    console.log("");
  } else {
    for (const issue of currentBatch) {
      console.log(`## ${issue.file}`);
      console.log("");
      console.log(readMarkdown(issue.absoluteFile).trim());
      console.log("");
    }
  }

  if (parallelBatches.length > 1) {
    console.log("# Future Dependency Batches");
    console.log("");
    for (let i = 1; i < parallelBatches.length; i += 1) {
      console.log(`## Batch ${i + 1}`);
      for (const issue of parallelBatches[i]) {
        console.log(`- ${issue.file}: ${issue.title}`);
      }
      console.log("");
    }
  }
}

console.log("# Skipped Issues");
console.log("");
if (skipped.length === 0) {
  console.log("None.");
} else {
  for (const issue of skipped) {
    const reasons = [];
    if (!issue.ready) reasons.push(`status=${issue.status}`);
    if (issue.hitl) reasons.push("hitl");
    if (issue.done) reasons.push(`implementation=${issue.implementation}`);
    if (issue.blocked) reasons.push(`blocked=${issue.unfinishedBlockers.join("; ")}`);
    console.log(`- ${issue.file}: ${reasons.join(", ")}`);
  }
}

console.log("");
console.log("# Agent Instructions");
console.log("");
console.log(basePrompt.trim());
