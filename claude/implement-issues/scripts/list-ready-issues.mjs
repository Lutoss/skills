#!/usr/bin/env node

import { buildQueues, findIssueFiles } from "./issue-utils.mjs";

const args = process.argv.slice(2);
const json = args.includes("--json");
const targets = args.filter((arg) => arg !== "--json");
const root = process.cwd();

const { currentBatch, parallelBatches, skipped } = buildQueues(findIssueFiles(targets, root), root);

if (json) {
  console.log(JSON.stringify({ currentBatch, parallelBatches, skipped }, null, 2));
} else {
  console.log("Current parallel batch:");
  if (currentBatch.length === 0) {
    console.log("  (none)");
  }
  for (const issue of currentBatch) {
    console.log(`  - ${issue.file} :: ${issue.title} (${issue.acceptanceCriteria} criteria, priority ${issue.priority})`);
  }

  if (parallelBatches.length > 1) {
    console.log("");
    console.log("Future dependency batches:");
    for (let i = 1; i < parallelBatches.length; i += 1) {
      console.log(`  Batch ${i + 1}:`);
      for (const issue of parallelBatches[i]) {
        console.log(`    - ${issue.file} :: ${issue.title}`);
      }
    }
  }

  console.log("");
  console.log("Skipped:");
  if (skipped.length === 0) {
    console.log("  (none)");
  }
  for (const issue of skipped) {
    const reasons = [];
    if (!issue.ready) reasons.push(`status=${issue.status}`);
    if (issue.hitl) reasons.push("hitl");
    if (issue.done) reasons.push(`implementation=${issue.implementation}`);
    if (issue.blocked) reasons.push(`blocked=${issue.unfinishedBlockers.join("; ")}`);
    console.log(`  - ${issue.file} :: ${issue.title} [${reasons.join(", ")}]`);
  }
}
