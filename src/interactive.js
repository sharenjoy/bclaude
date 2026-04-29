import inquirer from 'inquirer';
import chalk from 'chalk';
import { skillsRegistry, profiles } from './utils.js';
import { install } from './installer.js';

export async function runInteractive(baseOpts) {
  const registry = skillsRegistry();
  const allProfiles = profiles();

  console.log(chalk.bold('\nbclaude Installer'));
  console.log(chalk.dim('Interactive setup\n'));

  const { mode } = await inquirer.prompt([
    {
      type: 'list',
      name: 'mode',
      message: '安裝模式',
      choices: [
        { name: '全裝所有 skills', value: 'all' },
        { name: '依 Profile 安裝', value: 'profile' },
        { name: '手動選擇 Skills', value: 'manual' },
      ],
    },
  ]);

  let skillNames = [];

  if (mode === 'all') {
    skillNames = Object.keys(registry);
  } else if (mode === 'profile') {
    const { profile } = await inquirer.prompt([
      {
        type: 'list',
        name: 'profile',
        message: '選擇 Profile',
        choices: Object.keys(allProfiles).map(p => ({
          name: `${p} — ${allProfiles[p].join(', ')}`,
          value: p,
        })),
      },
    ]);
    skillNames = allProfiles[profile];
  } else {
    const { selected } = await inquirer.prompt([
      {
        type: 'checkbox',
        name: 'selected',
        message: '選擇要安裝的 Skills（空白選取，Enter 確認）',
        choices: Object.entries(registry).map(([name, meta]) => ({
          name: `${name.padEnd(22)} ${chalk.dim(meta.description)}`,
          value: name,
          checked: meta.defaultSelected ?? false,
        })),
        pageSize: 20,
      },
    ]);
    skillNames = selected;
  }

  const { force } = await inquirer.prompt([
    {
      type: 'confirm',
      name: 'force',
      message: '覆蓋已存在的檔案?',
      default: false,
    },
  ]);

  await install({ ...baseOpts, skills: skillNames.join(','), dryRun: false, force });
}
