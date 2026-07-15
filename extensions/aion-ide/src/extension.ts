import * as fs from "fs";
import * as http from "http";
import * as path from "path";
import * as vscode from "vscode";

const HEARTBEAT_MS = 20_000;
const WEB_OPEN_FILES_URL = "http://127.0.0.1:3860/api/open-files";

function workspaceRoot(): string | undefined {
  const folder = vscode.workspace.workspaceFolders?.[0];
  return folder?.uri.fsPath;
}

function relativePath(root: string, filePath: string): string {
  const rel = path.relative(root, filePath);
  if (!rel || rel.startsWith("..") || path.isAbsolute(rel)) {
    return filePath;
  }
  return rel.split(path.sep).join("/");
}

function collectOpenFiles(root: string): { path: string; cursor_line?: number }[] {
  const seen = new Set<string>();
  const files: { path: string; cursor_line?: number }[] = [];

  for (const editor of vscode.window.visibleTextEditors) {
    if (editor.document.uri.scheme !== "file") {
      continue;
    }
    const rel = relativePath(root, editor.document.uri.fsPath);
    if (seen.has(rel)) {
      continue;
    }
    seen.add(rel);
    files.push({
      path: rel,
      cursor_line: editor.selection.active.line + 1,
    });
  }

  const active = vscode.window.activeTextEditor;
  if (active && active.document.uri.scheme === "file") {
    const rel = relativePath(root, active.document.uri.fsPath);
    if (!seen.has(rel)) {
      files.unshift({
        path: rel,
        cursor_line: active.selection.active.line + 1,
      });
    }
  }

  return files;
}

function writeSidecar(root: string, files: { path: string; cursor_line?: number }[]): void {
  const dir = path.join(root, ".aion");
  fs.mkdirSync(dir, { recursive: true });
  const payload = {
    updated_at: Date.now() / 1000,
    files,
  };
  fs.writeFileSync(
    path.join(dir, "open_files.json"),
    JSON.stringify(payload, null, 2),
    "utf8"
  );
}

function postWebOpenFiles(paths: string[]): void {
  const body = JSON.stringify({ paths });
  const req = http.request(
    WEB_OPEN_FILES_URL,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Content-Length": Buffer.byteLength(body),
      },
      timeout: 500,
    },
    (res) => {
      res.resume();
    }
  );
  req.on("error", () => {
    /* agent web optional */
  });
  req.write(body);
  req.end();
}

function syncOpenFiles(showMessage = false): void {
  const root = workspaceRoot();
  if (!root) {
    if (showMessage) {
      vscode.window.showWarningMessage("Aion: open a workspace folder first.");
    }
    return;
  }
  const files = collectOpenFiles(root);
  writeSidecar(root, files);
  postWebOpenFiles(files.map((f) => f.path));
  if (showMessage) {
    vscode.window.showInformationMessage(
      `Aion: synced ${files.length} open file(s) to .aion/open_files.json`
    );
  }
}

export function activate(context: vscode.ExtensionContext): void {
  const syncCmd = vscode.commands.registerCommand("aion.syncOpenFiles", () => {
    syncOpenFiles(true);
  });

  const onEditor = vscode.window.onDidChangeActiveTextEditor(() => syncOpenFiles());
  const onVisible = vscode.window.onDidChangeVisibleTextEditors(() => syncOpenFiles());
  const heartbeat = setInterval(() => syncOpenFiles(), HEARTBEAT_MS);

  context.subscriptions.push(syncCmd, onEditor, onVisible, {
    dispose: () => clearInterval(heartbeat),
  });

  syncOpenFiles();
}

export function deactivate(): void {
  /* noop */
}
