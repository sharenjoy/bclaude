#!/usr/bin/env node
/**
 * sync.js — 從 ~/.claude 同步 skills/agents/rules/scripts 到本專案
 *
 * 使用方式:
 *   npm run sync           # 只同步檔案
 *   npm run sync:commit    # 同步 + git commit
 *   npm run sync:push      # 同步 + git commit + npm publish
 */

import { execSync } from 'child_process';
import { cpSync, mkdirSync, existsSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const ROOT = join(__dirname, '..');
const CLAUDE = join(process.env.HOME, '.claude');
const PUSH = process.argv.includes('--push');
const COMMIT = process.argv.includes('--commit') || PUSH;

const SYNC_TARGETS = [
  { src: 'skills',  dest: 'skills',  excludes: ['venv', '__pycache__', 'outputs', 'uploads', 'node_modules'] },
  { src: 'agents',  dest: 'agents',  excludes: [] },
  { src: 'rules',   dest: 'rules',   excludes: [] },
  { src: 'scripts', dest: 'scripts', excludes: ['__pycache__'] },
];

const TEMPLATE_FILES = [
  { src: 'claude.md',     dest: 'templates/CLAUDE.md' },
  { src: 'settings.json', dest: 'templates/settings.json' },
  { src: 'USAGE.md',      dest: 'templates/USAGE.md' },
];

function syncDir(srcPath, destPath, excludes) {
  if (!existsSync(srcPath)) {
    console.log(`  skip ${srcPath} (not found)`);
    return 0;
  }
  mkdirSync(destPath, { recursive: true });
  const excludeArgs = excludes.map(e => `--exclude='${e}/'`).join(' ');
  // --delete 只刪除 src 沒有的檔案，但 bin/ 目錄不在同步範圍內所以不受影響
  execSync(
    `rsync -aL --delete ${excludeArgs} --exclude='.DS_Store' --exclude='*.pyc' "${srcPath}/" "${destPath}/"`,
    { stdio: 'pipe' }
  );
  const result = execSync(
    `rsync -aLinL --delete ${excludeArgs} --exclude='.DS_Store' --exclude='*.pyc' "${srcPath}/" "${destPath}/"`,
    { encoding: 'utf8' }
  );
  return result.trim().split('\n').filter(l => l.trim()).length;
}

// ── 主流程 ──────────────────────────────────────────────────

console.log('Syncing ~/.claude → claude-boilerplate\n');
let totalChanges = 0;

for (const { src, dest, excludes } of SYNC_TARGETS) {
  process.stdout.write(`  ${src.padEnd(10)} `);
  const changes = syncDir(join(CLAUDE, src), join(ROOT, dest), excludes);
  console.log(changes > 0 ? `✔ (${changes} changed)` : '✔ (up to date)');
  totalChanges += changes;
}

process.stdout.write(`  ${'templates'.padEnd(10)} `);
for (const { src, dest } of TEMPLATE_FILES) {
  const s = join(CLAUDE, src);
  if (existsSync(s)) cpSync(s, join(ROOT, dest));
}
console.log('✔');

console.log(`\nDone. Total changed: ${totalChanges} file(s).`);

if (!COMMIT) process.exit(0);

// ── git commit ────────────────────────────────────────────

if (totalChanges === 0) {
  console.log('\nNo changes — skipping commit.');
  process.exit(0);
}

console.log('\nCommitting...');
const date = new Date().toISOString().slice(0, 10);
execSync('git add -A', { cwd: ROOT, stdio: 'inherit' });
execSync(`git commit -m "sync: update from ~/.claude (${date})"`, { cwd: ROOT, stdio: 'inherit' });

if (!PUSH) process.exit(0);

// ── npm version patch + publish ───────────────────────────

console.log('\nPublishing to npm...');
execSync('npm version patch --no-git-tag-version', { cwd: ROOT, stdio: 'inherit' });
execSync('git add package.json package-lock.json', { cwd: ROOT, stdio: 'inherit' });
execSync('git commit -m "chore: bump version"', { cwd: ROOT, stdio: 'inherit' });
execSync('git push', { cwd: ROOT, stdio: 'inherit' });
execSync('npm publish', { cwd: ROOT, stdio: 'inherit' });

console.log('\nPublished!');
