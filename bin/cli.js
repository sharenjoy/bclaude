#!/usr/bin/env node
import { program } from 'commander';
import { readFileSync } from 'fs';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';
import { runInteractive } from '../src/interactive.js';
import { install } from '../src/installer.js';

const __dirname = dirname(fileURLToPath(import.meta.url));
const pkg = JSON.parse(readFileSync(join(__dirname, '../package.json'), 'utf8'));

program
  .name('claude-boilerplate')
  .description('Install personal Claude Code configuration — skills, agents, rules, hooks')
  .version(pkg.version)
  .option('-s, --skills <list>', 'comma-separated skill names (e.g. commit,deploy)')
  .option('-p, --profile <name>', 'profile name: general | fullstack | laravel | all')
  .option('-d, --dry-run', 'preview what would be installed without writing files')
  .option('-f, --force', 'overwrite existing files without prompting')
  .option('--no-hooks', 'skip hooks configuration in settings.json')
  .action(async (opts) => {
    // No args → interactive mode
    if (!opts.skills && !opts.profile) {
      await runInteractive(opts);
    } else {
      await install(opts);
    }
  });

program.parse();
