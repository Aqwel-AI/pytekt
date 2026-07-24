#!/usr/bin/env python3
"""
Aqwel-Aion - Git Integration
=============================

Git repository operations via GitPython: status, commit history, branches,
diffs, file history. Optional dependency; install with: pip install gitpython.
"""

import os
from typing import List, Dict, Optional, Tuple
import tempfile
import shutil

try:
    from git import Repo, GitCommandError  # pyright: ignore [reportMissingImports]
    from git.objects.commit import Commit  # pyright: ignore [reportMissingImports]
    from git.refs.remote import RemoteReference  # pyright: ignore [reportMissingImports]
    GIT_AVAILABLE = True
except ImportError:
    GIT_AVAILABLE = False
    class Repo:
        pass
    class GitCommandError:
        pass
    class Commit:
        pass
    class RemoteReference:
        pass

class GitManager:
    """Git repository operations: status, history, branches, diff, file history."""

    def __init__(self, repo_path: str = None):
        """Open repo at repo_path (default: current directory)."""
        self.repo_path = repo_path or os.getcwd()
        self.repo = None
        self._initialize_repo()

    def _initialize_repo(self):
        if not GIT_AVAILABLE:
            raise ValueError("GitPython is not available. Install with: pip install gitpython")
        
        try:
            self.repo = Repo(self.repo_path)
        except Exception as e:
            self.repo = None
            raise ValueError(f"Not a Git repository: {self.repo_path}")
    
    def get_status(self) -> Dict[str, any]:
        """Return current branch, working_dir_clean, staged_files, untracked_files, repo_path."""
        if not self.repo:
            return {"error": "Not a Git repository"}
        try:
            current_branch = self.repo.active_branch.name
            working_dir_clean = not self.repo.is_dirty()
            staged_files = [item.a_path for item in self.repo.index.diff("HEAD")]
            untracked_files = self.repo.untracked_files
            return {
                "current_branch": current_branch,
                "working_dir_clean": working_dir_clean,
                "staged_files": staged_files,
                "untracked_files": untracked_files,
                "repo_path": self.repo_path
            }
        except Exception as e:
            return {"error": str(e)}
    
    def get_commit_history(self, max_commits: int = 10) -> List[Dict[str, any]]:
        """Return list of dicts: hash, author, date, message, files_changed (up to max_commits)."""
        if not self.repo:
            return []
        
        try:
            commits = []
            for commit in self.repo.iter_commits('HEAD', max_count=max_commits):
                commits.append({
                    "hash": commit.hexsha[:8],
                    "author": commit.author.name,
                    "date": commit.committed_datetime.isoformat(),
                    "message": commit.message.strip(),
                    "files_changed": len(commit.stats.files)
                })
            return commits
        except Exception as e:
            return [{"error": str(e)}]
    
    def get_branches(self) -> List[Dict[str, any]]:
        """Return list of dicts: name, is_active, last_commit, last_commit_date."""
        if not self.repo:
            return []
        
        try:
            branches = []
            for branch in self.repo.branches:
                branches.append({
                    "name": branch.name,
                    "is_active": branch.name == self.repo.active_branch.name,
                    "last_commit": branch.commit.hexsha[:8],
                    "last_commit_date": branch.commit.committed_datetime.isoformat()
                })
            return branches
        except Exception as e:
            return [{"error": str(e)}]
    
    def get_diff(self, commit_hash: str = None) -> str:
        """Return diff for commit_hash (vs parent) or working directory if commit_hash is None."""
        if not self.repo:
            return "Not a Git repository"
        try:
            if commit_hash:
                commit = self.repo.commit(commit_hash)
                parent = commit.parents[0] if commit.parents else None
                if parent:
                    return self.repo.git.diff(parent.hexsha, commit.hexsha)
                return "Initial commit - no diff available"
            return self.repo.git.diff()
        except Exception as e:
            return f"Error getting diff: {str(e)}"
    
    def get_file_history(self, file_path: str, max_commits: int = 5) -> List[Dict[str, any]]:
        """Return list of commits touching file_path: hash, date, message, author."""
        if not self.repo:
            return []
        
        try:
            commits = []
            for commit in self.repo.iter_commits('HEAD', paths=file_path, max_count=max_commits):
                commits.append({
                    "hash": commit.hexsha[:8],
                    "date": commit.committed_datetime.isoformat(),
                    "message": commit.message.strip(),
                    "author": commit.author.name
                })
            return commits
        except Exception as e:
            return [{"error": str(e)}]

def get_git_status(repo_path: str = None) -> Dict[str, any]:
    """Get Git status for a repository."""
    if not GIT_AVAILABLE:
        return {"error": "GitPython is not available. Install with: pip install gitpython"}
    
    try:
        git_mgr = GitManager(repo_path)
        return git_mgr.get_status()
    except Exception as e:
        return {"error": str(e)}

def get_recent_commits(repo_path: str = None, max_commits: int = 10) -> List[Dict[str, any]]:
    """Return recent commit history for the repository."""
    if not GIT_AVAILABLE:
        return [{"error": "GitPython is not available. Install with: pip install gitpython"}]
    
    try:
        git_mgr = GitManager(repo_path)
        return git_mgr.get_commit_history(max_commits)
    except Exception as e:
        return [{"error": str(e)}]

def list_branches(repo_path: str = None) -> List[Dict[str, any]]:
    """Return all branches in the repository."""
    if not GIT_AVAILABLE:
        return [{"error": "GitPython is not available. Install with: pip install gitpython"}]
    
    try:
        git_mgr = GitManager(repo_path)
        return git_mgr.get_branches()
    except Exception as e:
        return [{"error": str(e)}]

# ------------------------------------------------------------
# Additional Git utility functions
# ------------------------------------------------------------

def clone_repository(url: str, dest_path: str = None, depth: int = None) -> Dict[str, any]:
    """Clone a remote repository.

    Args:
        url: Remote repository URL.
        dest_path: Destination directory. If None, a temporary directory is created.
        depth: Optional shallow clone depth.
    Returns:
        Dict with keys 'success', 'data' (path), and 'error'.
    """
    if not GIT_AVAILABLE:
        return {"success": False, "error": "GitPython not available"}
    try:
        if dest_path is None:
            dest_path = tempfile.mkdtemp()
        clone_args = [url, dest_path]
        if depth is not None:
            clone_args.extend(["--depth", str(depth)])
        Repo.clone_from(*clone_args)
        return {"success": True, "data": dest_path}
    except Exception as e:
        return {"success": False, "error": str(e)}

def checkout_branch(repo_path: str, branch_name: str, create_if_missing: bool = False) -> Dict[str, any]:
    """Checkout a branch, optionally creating it if missing."""
    try:
        mgr = GitManager(repo_path)
        if branch_name in mgr.repo.branches:
            mgr.repo.git.checkout(branch_name)
            return {"success": True}
        if create_if_missing:
            mgr.repo.git.checkout('-b', branch_name)
            return {"success": True, "message": "branch created"}
        return {"success": False, "error": f"Branch '{branch_name}' not found"}
    except Exception as e:
        return {"success": False, "error": str(e)}

def create_branch(repo_path: str, new_branch: str, start_point: str = "HEAD") -> Dict[str, any]:
    """Create a new branch from a start point."""
    try:
        mgr = GitManager(repo_path)
        mgr.repo.git.branch(new_branch, start_point)
        return {"success": True}
    except Exception as e:
        return {"success": False, "error": str(e)}

def merge_branch(repo_path: str, source_branch: str, target_branch: str = None, commit_message: str = None, no_fast_forward: bool = False) -> Dict[str, any]:
    """Merge source_branch into target_branch (or current)."""
    try:
        mgr = GitManager(repo_path)
        if target_branch:
            mgr.repo.git.checkout(target_branch)
        args = [source_branch]
        if no_fast_forward:
            args.insert(0, "--no-ff")
        if commit_message:
            args.extend(["-m", commit_message])
        mgr.repo.git.merge(*args)
        return {"success": True}
    except GitCommandError as e:
        return {"success": False, "error": e.stderr or str(e)}
    except Exception as e:
        return {"success": False, "error": str(e)}

def stash_changes(repo_path: str, message: str = None) -> Dict[str, any]:
    """Stash current changes with an optional message."""
    try:
        mgr = GitManager(repo_path)
        if message:
            mgr.repo.git.stash('save', message)
        else:
            mgr.repo.git.stash()
        return {"success": True}
    except Exception as e:
        return {"success": False, "error": str(e)}

def apply_stash(repo_path: str, index: int = 0, drop: bool = False) -> Dict[str, any]:
    """Apply a stash by index; optionally drop it after applying."""
    try:
        mgr = GitManager(repo_path)
        mgr.repo.git.stash('apply', f'stash@{{{index}}}')
        if drop:
            mgr.repo.git.stash('drop', f'stash@{{{index}}}')
        return {"success": True}
    except Exception as e:
        return {"success": False, "error": str(e)}

def stage_files(repo_path: str, paths: List[str]) -> Dict[str, any]:
    """Stage a list of file paths."""
    try:
        mgr = GitManager(repo_path)
        mgr.repo.index.add(paths)
        return {"success": True}
    except Exception as e:
        return {"success": False, "error": str(e)}

def commit_changes(repo_path: str, message: str, author: Tuple[str, str] = None, amend: bool = False) -> Dict[str, any]:
    """Commit staged changes.

    author: (name, email) tuple.
    """
    try:
        mgr = GitManager(repo_path)
        kwargs = {}
        if author:
            kwargs['author'] = f"{author[0]} <{author[1]}>"
        if amend:
            mgr.repo.index.commit(message, amend=True, **kwargs)
        else:
            mgr.repo.index.commit(message, **kwargs)
        return {"success": True, "data": mgr.repo.head.commit.hexsha}
    except Exception as e:
        return {"success": False, "error": str(e)}

def push_to_remote(repo_path: str, remote: str = "origin", branch: str = None, force: bool = False) -> Dict[str, any]:
    """Push current (or specified) branch to a remote."""
    try:
        mgr = GitManager(repo_path)
        push_args = []
        if force:
            push_args.append("--force")
        if branch:
            push_args.append(f"{remote} {branch}")
        else:
            push_args.append(remote)
        mgr.repo.remote(name=remote).push(*push_args)
        return {"success": True}
    except Exception as e:
        return {"success": False, "error": str(e)}

def pull_from_remote(repo_path: str, remote: str = "origin", branch: str = None, rebase: bool = False) -> Dict[str, any]:
    """Pull from a remote, optionally rebasing."""
    try:
        mgr = GitManager(repo_path)
        pull_args = []
        if rebase:
            pull_args.append("--rebase")
        if branch:
            pull_args.append(f"{remote} {branch}")
        else:
            pull_args.append(remote)
        mgr.repo.remote(name=remote).pull(*pull_args)
        return {"success": True}
    except Exception as e:
        return {"success": False, "error": str(e)}

def reset_to_commit(repo_path: str, commit_hash: str, hard: bool = False) -> Dict[str, any]:
    """Reset HEAD to a specific commit."""
    try:
        mgr = GitManager(repo_path)
        mode = "--hard" if hard else "--soft"
        mgr.repo.git.reset(mode, commit_hash)
        return {"success": True}
    except Exception as e:
        return {"success": False, "error": str(e)}

def fetch_remotes(repo_path: str, remote: str = "origin", prune: bool = False) -> Dict[str, any]:
    """Fetch from a remote, optionally pruning stale refs."""
    try:
        mgr = GitManager(repo_path)
        args = []
        if prune:
            args.append("--prune")
        args.append(remote)
        mgr.repo.remote(name=remote).fetch(*args)
        return {"success": True}
    except Exception as e:
        return {"success": False, "error": str(e)}

def list_remotes(repo_path: str) -> List[Dict[str, any]]:
    """List all configured remotes with their URLs."""
    try:
        mgr = GitManager(repo_path)
        remotes = []
        for r in mgr.repo.remotes:
            remotes.append({"name": r.name, "urls": list(r.urls)})
        return remotes
    except Exception as e:
        return [{"error": str(e)}]

def get_remote_url(repo_path: str, remote: str = "origin") -> str:
    """Return the URL of a specific remote."""
    try:
        mgr = GitManager(repo_path)
        return list(mgr.repo.remote(name=remote).urls)[0]
    except Exception as e:
        return ""

def get_current_commit(repo_path: str) -> Dict[str, any]:
    """Return details of HEAD commit."""
    try:
        mgr = GitManager(repo_path)
        c = mgr.repo.head.commit
        return {"hash": c.hexsha[:8], "author": c.author.name, "date": c.committed_datetime.isoformat(), "message": c.message.strip()}
    except Exception as e:
        return {"error": str(e)}

def get_repo_root(start_path: str = None) -> str:
    """Walk up to find the repository root (.git)."""
    path = start_path or os.getcwd()
    while path != os.path.dirname(path):
        if os.path.isdir(os.path.join(path, ".git")):
            return path
        path = os.path.dirname(path)
    return ""

def is_git_repository(path: str = None) -> bool:
    """Check if a directory is a Git repo."""
    try:
        repo_path = path or os.getcwd()
        _ = Repo(repo_path)
        return True
    except Exception:
        return False

def tag_commit(repo_path: str, tag_name: str, commit_hash: str = None, message: str = None, force: bool = False) -> Dict[str, any]:
    """Create (or update) a tag on a commit."""
    try:
        mgr = GitManager(repo_path)
        kwargs = {}
        if message:
            kwargs['message'] = message
        if force:
            kwargs['force'] = True
        target = commit_hash or mgr.repo.head.commit.hexsha
        mgr.repo.create_tag(tag_name, ref=target, **kwargs)
        return {"success": True}
    except Exception as e:
        return {"success": False, "error": str(e)}

def delete_branch(repo_path: str, branch_name: str, force: bool = False) -> Dict[str, any]:
    """Delete a local branch."""
    try:
        mgr = GitManager(repo_path)
        mgr.repo.delete_head(branch_name, force=force)
        return {"success": True}
    except Exception as e:
        return {"success": False, "error": str(e)}

def rename_branch(repo_path: str, old_name: str, new_name: str) -> Dict[str, any]:
    """Rename a local branch."""
    try:
        mgr = GitManager(repo_path)
        mgr.repo.git.branch('-m', old_name, new_name)
        return {"success": True}
    except Exception as e:
        return {"success": False, "error": str(e)}

def cherry_pick(repo_path: str, commit_hash: str, onto_branch: str = None, no_commit: bool = False) -> Dict[str, any]:
    """Cherry‑pick a commit onto current (or specified) branch."""
    try:
        mgr = GitManager(repo_path)
        if onto_branch:
            mgr.repo.git.checkout(onto_branch)
        args = [commit_hash]
        if no_commit:
            args.insert(0, "-n")
        mgr.repo.git.cherry_pick(*args)
        return {"success": True}
    except Exception as e:
        return {"success": False, "error": str(e)}

def revert_commit(repo_path: str, commit_hash: str, no_commit: bool = False) -> Dict[str, any]:
    """Revert a commit, optionally without committing the revert."""
    try:
        mgr = GitManager(repo_path)
        args = [commit_hash]
        if no_commit:
            args.insert(0, "-n")
        mgr.repo.git.revert(*args)
        return {"success": True}
    except Exception as e:
        return {"success": False, "error": str(e)}

def amend_last_commit(repo_path: str, message: str = None, author: Tuple[str, str] = None) -> Dict[str, any]:
    """Amend the most recent commit."""
    try:
        mgr = GitManager(repo_path)
        kwargs = {}
        if message:
            kwargs['message'] = message
        if author:
            kwargs['author'] = f"{author[0]} <{author[1]}>"
        mgr.repo.git.commit('--amend', **kwargs)
        return {"success": True}
    except Exception as e:
        return {"success": False, "error": str(e)}

def get_submodule_status(repo_path: str) -> List[Dict[str, any]]:
    """Return status of submodules."""
    try:
        mgr = GitManager(repo_path)
        subs = []
        for sub in mgr.repo.submodules:
            subs.append({"path": sub.path, "url": sub.url, "hexsha": sub.hexsha})
        return subs
    except Exception as e:
        return [{"error": str(e)}]

def init_repository(path: str = None, bare: bool = False) -> Dict[str, any]:
    """Initialize a new Git repository."""
    try:
        repo_path = path or os.getcwd()
        repo = Repo.init(repo_path, bare=bare)
        return {"success": True, "data": repo_path}
    except Exception as e:
        return {"success": False, "error": str(e)}

