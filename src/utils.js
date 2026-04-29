import { createRequire } from 'module';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';
import { readFileSync } from 'fs';

const __dirname = dirname(fileURLToPath(import.meta.url));
const ROOT = join(__dirname, '..');

export function loadJSON(relativePath) {
  return JSON.parse(readFileSync(join(ROOT, relativePath), 'utf8'));
}

export function pkgRoot() {
  return ROOT;
}

export function claudeDir() {
  return join(process.cwd(), '.claude');
}

export function skillsRegistry() {
  return loadJSON('skills-registry.json');
}

export function profiles() {
  return loadJSON('profiles.json');
}
