import fsExtra from 'fs-extra';
import { copyFileSync, existsSync, lstatSync, unlinkSync } from 'fs';
const { copySync, ensureDirSync, removeSync } = fsExtra;
import { join } from 'path';
import chalk from 'chalk';
import ora from 'ora';
import { pkgRoot, claudeDir, skillsRegistry, profiles } from './utils.js';

const EXCLUDE_PATTERNS = ['venv', '__pycache__', 'node_modules', 'outputs', 'uploads', '.DS_Store'];

function shouldExclude(src, root) {
  const relative = src.slice(root.length);
  return EXCLUDE_PATTERNS.some(p => relative.includes(`/${p}`));
}

export async function install(opts) {
  const { skills: skillsArg, profile, dryRun, force, hooks: withHooks = true } = opts;
  const registry = skillsRegistry();
  const allProfiles = profiles();

  // Resolve skill list
  let skillNames = [];
  if (profile) {
    skillNames = allProfiles[profile] ?? [];
    if (!skillNames.length) {
      console.error(chalk.red(`Unknown profile: ${profile}`));
      console.log(`Available: ${Object.keys(allProfiles).join(', ')}`);
      process.exit(1);
    }
  } else if (skillsArg) {
    skillNames = skillsArg.split(',').map(s => s.trim()).filter(Boolean);
    const unknown = skillNames.filter(s => !registry[s]);
    if (unknown.length) {
      console.error(chalk.red(`Unknown skills: ${unknown.join(', ')}`));
      console.log(`Available: ${Object.keys(registry).join(', ')}`);
      process.exit(1);
    }
  }

  const dest = claudeDir();
  const src = pkgRoot();

  if (dryRun) {
    console.log(chalk.yellow('\n[DRY RUN] — nothing will be written\n'));
  }

  console.log(chalk.bold('\nbclaude Installer'));
  console.log(chalk.dim(`→ Destination: ${dest}\n`));

  const spinner = ora();

  // 1. Base dirs
  const dirs = ['skills', 'agents', 'rules', 'commands', 'hooks', 'memory'];
  dirs.forEach(d => {
    if (!dryRun) ensureDirSync(join(dest, d));
  });

  // 2. CLAUDE.md
  spinner.start('Installing CLAUDE.md');
  await copyTemplate('CLAUDE.md', dest, src, dryRun, force);
  spinner.succeed(chalk.green('CLAUDE.md'));

  // 3. settings.json
  spinner.start('Installing settings.json');
  await copyTemplate('settings.json', dest, src, dryRun, force);
  spinner.succeed(chalk.green('settings.json'));

  // 3b. USAGE.md
  spinner.start('Installing USAGE.md');
  await copyTemplate('USAGE.md', dest, src, dryRun, force);
  spinner.succeed(chalk.green('USAGE.md'));

  // 4. Agents (always install all)
  spinner.start('Installing agents');
  if (!dryRun) {
    copySync(join(src, 'agents'), join(dest, 'agents'), {
      overwrite: force,
      filter: p => !shouldExclude(p, src),
    });
  }
  spinner.succeed(chalk.green('agents/ (all)'));

  // 5. Rules
  spinner.start('Installing rules');
  if (!dryRun) {
    copySync(join(src, 'rules'), join(dest, 'rules'), {
      overwrite: force,
      filter: p => !shouldExclude(p, src),
    });
  }
  spinner.succeed(chalk.green('rules/'));

  // 6. Skills
  if (skillNames.length) {
    console.log(chalk.bold(`\nInstalling ${skillNames.length} skill(s):`));
    const postInstallNotes = [];

    for (const name of skillNames) {
      const meta = registry[name];
      const skillSrc = join(src, 'skills', name);
      const skillDest = join(dest, 'skills', name);

      if (!existsSync(skillSrc)) {
        console.log(chalk.yellow(`  ! ${name} — not found in package, skipping`));
        continue;
      }

      spinner.start(`  ${name}`);
      if (!dryRun) {
        // Remove symlink or file at dest so fs-extra can copy a directory in its place
        if (existsSync(skillDest) || lstatSync(skillDest, { throwIfNoEntry: false })) {
          const stat = lstatSync(skillDest, { throwIfNoEntry: false });
          if (stat?.isSymbolicLink() || stat?.isFile()) unlinkSync(skillDest);
        }
        copySync(skillSrc, skillDest, {
          overwrite: force,
          filter: p => !shouldExclude(p, src),
        });
      }
      spinner.succeed(chalk.green(`  ${name}`) + chalk.dim(` — ${meta?.description ?? ''}`));

      if (meta?.postInstall) {
        postInstallNotes.push({ name, note: meta.postInstall });
      }
    }

    if (postInstallNotes.length) {
      console.log(chalk.yellow('\nPost-install steps required:'));
      postInstallNotes.forEach(({ name, note }) => {
        console.log(chalk.dim(`  [${name}]`), note);
      });
    }
  } else {
    console.log(chalk.dim('\nNo skills selected. Use --skills or --profile to install skills.'));
  }

  console.log(chalk.bold.green('\nDone!'));
  if (dryRun) {
    console.log(chalk.yellow('(dry run — no files were written)'));
  }
}

async function copyTemplate(filename, dest, src, dryRun, force) {
  const srcPath = join(src, 'templates', filename);
  const destPath = join(dest, filename);
  if (!dryRun) {
    if (!force && existsSync(destPath)) return; // skip if exists and not forcing
    copyFileSync(srcPath, destPath);
  }
}
