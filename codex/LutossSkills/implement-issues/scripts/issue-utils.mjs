import { existsSync, readdirSync, readFileSync, statSync } from "node:fs";
import path from "node:path";

export function markdownFilesIn(dir) {
  if (!existsSync(dir)) return [];
  return readdirSync(dir, { withFileTypes: true })
    .filter((entry) => entry.isFile() && entry.name.toLowerCase().endsWith(".md"))
    .map((entry) => path.join(dir, entry.name))
    .sort((a, b) => a.localeCompare(b, undefined, { numeric: true }));
}

export function findIssueFiles(targetsToScan, root = process.cwd()) {
  if (targetsToScan.length === 0) {
    const scratch = path.resolve(root, ".scratch");
    if (!existsSync(scratch)) return [];
    return readdirSync(scratch, { withFileTypes: true })
      .filter((entry) => entry.isDirectory())
      .flatMap((entry) => markdownFilesIn(path.join(scratch, entry.name, "issues")));
  }

  return targetsToScan.flatMap((target) => {
    const resolved = path.resolve(root, target);
    if (!existsSync(resolved)) return [];
    const stats = statSync(resolved);
    if (stats.isFile()) return [resolved];
    const issuesDir = path.basename(resolved) === "issues" ? resolved : path.join(resolved, "issues");
    return markdownFilesIn(issuesDir);
  });
}

export function readMarkdown(file) {
  return readFileSync(file, "utf8").replace(/^\uFEFF/, "");
}

export function firstMatch(text, regex, fallback = "") {
  const match = text.match(regex);
  return match ? match[1].trim() : fallback;
}

export function parseLabels(raw) {
  return raw
    .split(",")
    .map((label) => label.trim())
    .filter(Boolean);
}

export function section(text, heading) {
  const lines = text.split(/\r?\n/);
  const headingRegex = new RegExp(`^##\\s+${heading.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")}\\s*$`, "i");
  const start = lines.findIndex((line) => headingRegex.test(line));
  if (start === -1) return "";

  const collected = [];
  for (let i = start + 1; i < lines.length; i += 1) {
    if (/^##\s+/.test(lines[i])) break;
    collected.push(lines[i]);
  }

  return collected.join("\n").trim();
}

export function countAcceptanceCriteria(text) {
  const criteria = section(text, "Acceptance Criteria") || section(text, "Acceptance criteria");
  if (!criteria) return 0;
  return criteria
    .split(/\r?\n/)
    .filter((line) => /^\s*-\s+(?:\[[ xX]\]\s+)?\S/.test(line))
    .length;
}

export function priorityRank(issue) {
  const haystack = `${issue.title} ${issue.status} ${issue.labels.join(" ")} ${issue.category}`.toLowerCase();
  if (/(critical|bug|bugfix|regression|hotfix)/.test(haystack)) return 1;
  if (/(infra|infrastructure|test|typecheck|lint|build|dev script|tooling)/.test(haystack)) return 2;
  if (/(tracer|slice|vertical|feature)/.test(haystack)) return 3;
  if (/(polish|quick win|copy|ui|ux|cleanup)/.test(haystack)) return 4;
  if (/(refactor|architecture|deep module)/.test(haystack)) return 5;
  return 3;
}

export function issueNumberFromFile(file) {
  const match = path.basename(file, ".md").match(/^0*(\d+)(?:\D|$)/);
  return match ? match[1] : "";
}

export function normalizeReference(reference) {
  return reference
    .toLowerCase()
    .replace(/[`*_]/g, "")
    .replace(/\\/g, "/")
    .replace(/\.md\b/g, "")
    .trim();
}

export function issueMatchesReference(issue, reference) {
  const normalized = normalizeReference(reference);
  if (!normalized) return false;

  if (normalized.includes(issue.stem.toLowerCase())) return true;
  if (normalized.includes(issue.file.replace(/\\/g, "/").replace(/\.md$/i, "").toLowerCase())) return true;

  if (issue.number) {
    const numberPattern = new RegExp(`(^|[^0-9])0*${issue.number}([^0-9]|$)`);
    if (numberPattern.test(normalized)) return true;
  }

  return false;
}

export function unfinishedBlockersFor(issue, issues, completedFiles = new Set()) {
  return issue.blockedBy.filter((reference) => {
    const matches = issues.filter((candidate) => issueMatchesReference(candidate, reference));
    if (matches.length === 0) return true;
    return matches.some((candidate) => !candidate.done && !completedFiles.has(candidate.file));
  });
}

export function sortIssues(a, b) {
  return a.priority - b.priority || a.file.localeCompare(b.file, undefined, { numeric: true });
}

export function parseIssue(file, root = process.cwd()) {
  const text = readMarkdown(file);
  const stem = path.basename(file, ".md");
  const number = issueNumberFromFile(file);
  const title = firstMatch(text, /^#\s+(.+)$/m, path.basename(file, ".md"));
  const status = firstMatch(text, /^Status:\s*(.+)$/m, "missing");
  const implementation = firstMatch(text, /^Implementation:\s*(.+)$/m, "pending");
  const labels = parseLabels(firstMatch(text, /^Labels?:\s*(.+)$/m, ""));
  const category = firstMatch(text, /^Category:\s*(.+)$/m, "");
  const blockedByText = section(text, "Blocked by");
  const blockedBy = blockedByText
    .split(/\r?\n/)
    .map((line) => line.replace(/^[-*]\s*/, "").trim())
    .filter((line) => line && !/^none\b/i.test(line));
  const acceptanceCriteria = countAcceptanceCriteria(text);
  const ready = status === "ready-for-agent" || labels.includes("ready-for-agent");
  const hitl =
    status === "ready-for-human" ||
    status === "needs-info" ||
    status === "needs-triage" ||
    labels.includes("ready-for-human") ||
    labels.includes("needs-info") ||
    labels.includes("needs-triage");
  const done = /^(done|complete|completed)$/i.test(implementation);

  const issue = {
    file: path.relative(root, file),
    absoluteFile: file,
    stem,
    number,
    title,
    status,
    labels,
    category,
    implementation,
    ready,
    hitl,
    done,
    blocked: blockedBy.length > 0,
    blockedBy,
    unfinishedBlockers: blockedBy,
    acceptanceCriteria,
    priority: 3,
  };
  issue.priority = priorityRank(issue);
  return issue;
}

export function buildParallelBatches(issues) {
  const completedFiles = new Set(issues.filter((issue) => issue.done).map((issue) => issue.file));
  const remaining = new Map(
    issues
      .filter((issue) => issue.ready && !issue.hitl && !issue.done)
      .map((issue) => [issue.file, issue]),
  );
  const batches = [];

  while (remaining.size > 0) {
    const batch = [...remaining.values()]
      .filter((issue) => unfinishedBlockersFor(issue, issues, completedFiles).length === 0)
      .sort(sortIssues);

    if (batch.length === 0) break;

    batches.push(batch);
    for (const issue of batch) {
      completedFiles.add(issue.file);
      remaining.delete(issue.file);
    }
  }

  return batches;
}

export function buildQueues(files, root = process.cwd()) {
  const issues = files.map((file) => parseIssue(file, root));
  const completedFiles = new Set(issues.filter((issue) => issue.done).map((issue) => issue.file));

  for (const issue of issues) {
    issue.unfinishedBlockers = unfinishedBlockersFor(issue, issues, completedFiles);
    issue.blocked = issue.unfinishedBlockers.length > 0;
  }

  const parallelBatches = buildParallelBatches(issues);
  const currentBatch = parallelBatches[0] || [];
  const readyQueue = currentBatch;
  const batchFiles = new Set(parallelBatches.flat().map((issue) => issue.file));
  const skipped = issues.filter((issue) => !batchFiles.has(issue.file));

  return { issues, readyQueue, currentBatch, parallelBatches, skipped };
}
