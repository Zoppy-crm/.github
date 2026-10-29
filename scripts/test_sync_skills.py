#!/usr/bin/env python3
"""Offline regression coverage for the shell used by sync-rules.yml.

Run: python3 scripts/test_sync_skills.py (requires bash, jq, rsync and PyYAML).
No network, remote repositories or pushes are used.
"""

import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

import yaml


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/sync-skills.sh"
WORKFLOW = yaml.safe_load((ROOT / ".github/workflows/sync-rules.yml").read_text())
RUN = WORKFLOW["jobs"]["sync"]["steps"][1]["run"]


class SyncSkillsTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="sync-skills-test-")
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.source = self.base / "source"
        self.skill = self.source / "skills/shared/kept"
        self.skill.mkdir(parents=True)
        (self.skill / "SKILL.md").write_text("current\n")
        (self.skill / ".hidden").write_text("hidden\n")
        (self.skill / "empty").mkdir()
        self.classic = self.base / "classic-repo"
        self.agents = self.base / "agents-repo"
        self.classic.mkdir()
        self.agents.mkdir()

    def command(self, *args, cwd=None, ok=True, env=None):
        result = subprocess.run(
            args, cwd=cwd, env=env, text=True, stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT, check=False,
        )
        if ok:
            self.assertEqual(result.returncode, 0, result.stdout)
        return result

    def sync(self, repo, path, ok=True):
        return self.command("bash", str(SCRIPT), str(self.source), path, "shared", cwd=repo, ok=ok)

    def shell(self, code, *args, cwd=None, ok=True):
        return self.command("bash", "-euc", code, "test", *map(str, args), cwd=cwd, ok=ok)

    def snapshot(self, repo):
        return {
            str(path.relative_to(repo)): ("link", os.readlink(path)) if path.is_symlink()
            else ("dir",) if path.is_dir() else ("file", path.read_bytes())
            for path in repo.rglob("*")
        }

    def test_mirror_prune_marker_and_idempotence_in_both_destinations(self):
        for repo, path in ((self.classic, ".claude/skills"), (self.agents, ".agents/skills")):
            with self.subTest(path=path):
                target = repo / path
                (target / "kept/old-dir").mkdir(parents=True)
                (target / "kept/old.txt").write_text("stale")
                (target / "kept/old-dir/stale").write_text("stale")
                (target / "orphan").mkdir()
                (target / "orphan/SKILL.md").write_text("orphan")
                (target / "local-note.txt").write_text("keep root file")
                (repo / "outside.txt").write_text("untouched")
                result = self.sync(repo, path)
                self.assertIn("pruned orphan skill: orphan", result.stdout)
                print(f"{path}: {result.stdout.strip()}")
                self.assertFalse((target / "orphan").exists())
                self.assertFalse((target / "kept/old.txt").exists())
                self.assertFalse((target / "kept/old-dir").exists())
                self.assertEqual((target / "kept/SKILL.md").read_text(), "current\n")
                self.assertEqual((target / "kept/.hidden").read_text(), "hidden\n")
                self.assertTrue((target / "kept/empty").is_dir())
                self.assertEqual((target / "local-note.txt").read_text(), "keep root file")
                self.assertEqual((repo / "outside.txt").read_text(), "untouched")
                self.assertEqual((target / ".synced-from-org").read_text(),
                                 "# Skills synced from Zoppy-crm/.github\n# Groups: shared\nkept\n")
                if path == ".agents/skills":
                    self.assertEqual(os.readlink(repo / ".claude/skills"), "../.agents/skills")
                    self.assertEqual((repo / ".claude/skills/kept/SKILL.md").read_text(), "current\n")
                before = self.snapshot(repo)
                self.sync(repo, path)
                self.assertEqual(self.snapshot(repo), before)

    def test_real_claude_directory_fails_before_any_write(self):
        (self.agents / ".claude/skills/local").mkdir(parents=True)
        (self.agents / ".claude/skills/local/SKILL.md").write_text("preserve")
        (self.agents / ".agents/skills/orphan").mkdir(parents=True)
        before = self.snapshot(self.agents)
        result = self.sync(self.agents, ".agents/skills", ok=False)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("diretório real", result.stdout)
        self.assertEqual(self.snapshot(self.agents), before)
        print(result.stdout.strip())

    def test_wrong_symlink_and_symlinked_canonical_skill_fail_without_writes(self):
        (self.agents / ".claude").mkdir()
        (self.agents / ".claude/skills").symlink_to("../elsewhere")
        before = self.snapshot(self.agents)
        self.assertNotEqual(self.sync(self.agents, ".agents/skills", ok=False).returncode, 0)
        self.assertEqual(self.snapshot(self.agents), before)
        target = self.classic / ".claude/skills"
        target.mkdir(parents=True)
        (target / "kept").symlink_to(self.skill)
        before = self.snapshot(self.classic)
        self.assertNotEqual(self.sync(self.classic, ".claude/skills", ok=False).returncode, 0)
        self.assertEqual(self.snapshot(self.classic), before)

    def test_config_defaults_and_same_repo_groups(self):
        result = self.shell('source "$1"; load_sync_config "$2"; '
                            'for repo in "${!REPO_SKILLS_PATHS[@]}"; do '
                            'printf "%s=%s\\n" "$repo" "${REPO_SKILLS_PATHS[$repo]}"; done; '
                            '[[ "${REPO_FOLDERS[zoppy-FE]}" == *angular* ]]; '
                            '[[ "${REPO_FOLDERS[zoppy-FE]}" == *e2e-jornadas* ]]',
                            SCRIPT, ROOT / "skills/sync-config.json")
        paths = dict(line.split("=", 1) for line in result.stdout.splitlines())
        self.assertEqual(paths.pop("zoppy-os"), ".agents/skills")
        self.assertTrue(paths)
        self.assertEqual(set(paths.values()), {".claude/skills"})

    def test_conflicting_paths_and_exclusive_folders_rejected(self):
        config = self.base / "conflict.json"
        data = {"groups": {
            "a": {"folders": ["shared"], "repos": ["same"]},
            "b": {"folders": ["shared"], "repos": ["same"], "skillsPath": ".agents/skills"},
        }}
        config.write_text(json.dumps(data))
        result = self.shell('source "$1"; load_sync_config "$2"', SCRIPT, config, ok=False)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Destinos de skills conflitantes para same", result.stdout)
        print(result.stdout.strip())
        data["groups"]["b"].pop("skillsPath")
        config.write_text(json.dumps(data))
        self.shell('source "$1"; load_sync_config "$2"', SCRIPT, config)
        data["groups"]["a"]["folders"] = ["angular"]
        data["groups"]["b"]["folders"] = ["react"]
        data["exclusiveFolders"] = [["angular", "react"]]
        config.write_text(json.dumps(data))
        result = self.shell('source "$1"; load_sync_config "$2"', SCRIPT, config, ok=False)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("mutuamente exclusivas", result.stdout)

    def test_extra_branch_only_for_zoppy_os(self):
        for repo in ("zoppy-os", "zoppy-api", "zoppy-FE"):
            result = self.shell('source "$1"; sync_target_branches "$2"', SCRIPT, repo)
            expected = ["development", "staging", "master", "mirror"]
            if repo == "zoppy-os":
                expected.append("zoppy-os-v2")
            self.assertEqual(result.stdout.splitlines(), expected)
        print("Branches: zoppy-os=development,staging,master,mirror,zoppy-os-v2; demais=development,staging,master,mirror")

    def test_workflow_dry_run_and_conflict_before_repo_filter(self):
        code = RUN.replace("${{ inputs.dry_run || 'false' }}", "true")
        code = code.replace("${{ inputs.repos || 'all' }}", "zoppy-os,zoppy-api")
        env = dict(os.environ, GITHUB_WORKSPACE=str(ROOT))
        result = self.command("bash", "-c", code, cwd=ROOT, env=env)
        self.assertIn("Repos a sincronizar: 2", result.stdout)
        self.assertIn("→ .agents/skills", result.stdout)
        self.assertIn("→ .claude/skills", result.stdout)
        self.assertIn("[DRY RUN]", result.stdout)
        self.assertIn("Failed: 0", result.stdout)
        config = self.source / "skills/sync-config.json"
        config.write_text(json.dumps({"groups": {
            "a": {"folders": ["shared"], "repos": ["unselected"]},
            "b": {"folders": ["shared"], "repos": ["unselected"], "skillsPath": ".agents/skills"},
        }}))
        result = self.command("bash", "-c", code, cwd=self.source, env=env, ok=False)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Destinos de skills conflitantes para unselected", result.stdout)
        self.assertNotIn("Filtro ativo", result.stdout)

    def test_workflow_hooks_preserve_link_and_settings(self):
        self.sync(self.agents, ".agents/skills")
        settings = self.agents / ".claude/settings.json"
        settings.write_text(json.dumps({"localSetting": True, "hooks": {}}))
        # Execute the workflow's actual merge block; leave Git staging to the workflow.
        hook_code = RUN.split("# Merge hooks-template.json", 1)[1]
        hook_code = hook_code[hook_code.index("HOOKS_TEMPLATE="):]
        hook_code = hook_code.split("# REVIEW.md", 1)[0]
        hook_code = "\n".join(line for line in hook_code.splitlines() if "git add" not in line)
        env = dict(os.environ, GITHUB_WORKSPACE=str(ROOT))
        self.command("bash", "-euc", hook_code, cwd=self.agents, env=env)
        merged = json.loads(settings.read_text())
        self.assertTrue(merged["localSetting"])
        self.assertEqual(merged["hooks"], json.loads((ROOT / "config/hooks-template.json").read_text())["hooks"])
        self.assertEqual(os.readlink(self.agents / ".claude/skills"), "../.agents/skills")
        self.assertEqual((self.agents / ".claude/skills/kept/SKILL.md").read_text(), "current\n")

    def test_git_discovers_ignored_destination_and_records_symlink(self):
        self.sync(self.agents, ".agents/skills")
        self.command("git", "init", "-q", cwd=self.agents)
        ignore = self.agents / ".gitignore"
        ignore.write_text(".agents/\n.claude/\n")
        # Use the same discovery expression as the workflow, including ignored files.
        discovery = RUN.split('$(git ls-files --others -- ', 1)[1].split(')"', 1)[0]
        result = self.shell('SKILLS_PATH=.agents/skills; git ls-files --others -- ' + discovery, cwd=self.agents)
        self.assertIn(".agents/skills/kept/SKILL.md", result.stdout)
        self.assertIn(".claude/skills", result.stdout)
        # A normal local add verifies link handling without executing forced Git operations.
        ignore.write_text("")
        self.command("git", "add", "--", ".agents/skills", ".claude", cwd=self.agents)
        result = self.command("git", "ls-files", "--stage", cwd=self.agents)
        self.assertRegex(result.stdout, r"120000 [^\n]+\t.claude/skills")
        self.assertIn(".agents/skills/kept/.hidden", result.stdout)
        self.assertNotIn(".claude/skills/kept/", result.stdout)
        self.assertIn('git add -fA "$SKILLS_PATH" .claude .github/copilot-instructions.md', RUN)
        self.assertIn('git diff --cached --quiet', RUN)


if __name__ == "__main__":
    unittest.main(verbosity=2)
